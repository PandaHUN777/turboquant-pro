//! TqVector — the PostgreSQL custom type for compressed vectors.

use pgrx::prelude::*;
use serde::{Deserialize, Serialize};

/// The rotation seed every vector written before the format carried one used.
///
/// `tq_compress` has always passed 42, and `decompress` always assumed it, so
/// a row without a `seed` field was rotated with this and must be read back
/// with it. Do not change it: it is the decoding contract for those rows.
pub const LEGACY_ROTATION_SEED: u32 = 42;

/// Format version of a vector written before the version was recorded.
pub const LEGACY_FORMAT_VERSION: u8 = 0;

/// Format version written today: `seed` is present and authoritative.
pub const FORMAT_VERSION: u8 = 1;

fn legacy_seed() -> u32 {
    LEGACY_ROTATION_SEED
}

fn legacy_version() -> u8 {
    LEGACY_FORMAT_VERSION
}

/// A TurboQuant compressed vector.
///
/// Stored as CBOR in PostgreSQL via serde. Display format shows
/// a human-readable summary: `tqvector(1024-dim, 3-bit, 10.5x)`.
///
/// # The seed is part of the data, not of the decoder
///
/// The compressor rotates by a basis derived from a seed, and a vector can
/// only be read back through the same basis. That seed used to live as a
/// literal in `decompress`, while `compress` took it as a parameter: anything
/// compressing with a seed other than 42 produced rows that decompressed to
/// quietly wrong values, with no error and nothing to detect (issue #164).
/// The seed now travels with the vector.
///
/// Rows written before this carry neither field. Serde fills them with
/// `LEGACY_ROTATION_SEED` and `LEGACY_FORMAT_VERSION`, which is exactly how
/// they were encoded, so they keep decoding correctly and no migration is
/// needed.
#[derive(
    Clone, Debug,
    Serialize, Deserialize,
    PostgresType,
)]
#[inoutfuncs]
pub struct TqVector {
    /// Original embedding dimension
    pub dim: u16,
    /// Quantization bit width (2, 3, or 4)
    pub bits: u8,
    /// L2 norm of the original vector
    pub norm: f32,
    /// Bit-packed quantization indices
    pub data: Vec<u8>,
    /// Seed of the rotation basis this vector was compressed under.
    /// Absent in rows written before the format carried it; those are read
    /// with [`LEGACY_ROTATION_SEED`], which is what they were written with.
    #[serde(default = "legacy_seed")]
    pub seed: u32,
    /// Format version. Absent (and so [`LEGACY_FORMAT_VERSION`]) in rows
    /// written before the version was recorded.
    #[serde(default = "legacy_version")]
    pub format_version: u8,
}

impl InOutFuncs for TqVector {
    /// Text input — not supported (use tq_compress instead)
    fn input(_input: &core::ffi::CStr) -> Self
    where
        Self: Sized,
    {
        pgrx::error!(
            "tqvector text input not supported. \
             Use tq_compress(embedding, bits) instead."
        );
    }

    /// Text output — human-readable summary
    fn output(&self, buffer: &mut pgrx::StringInfo) {
        let original = self.dim as f32 * 4.0;
        let compressed = self.data.len() as f32 + 4.0;
        let ratio = original / compressed;
        buffer.push_str(&format!(
            "tqvector({}-dim, {}-bit, norm={:.4}, {:.1}x)",
            self.dim, self.bits, self.norm, ratio
        ));
    }
}

impl TqVector {
    /// Create a new TqVector from components, recording the rotation seed it
    /// was compressed under.
    pub fn new(dim: u16, bits: u8, norm: f32, data: Vec<u8>, seed: u32) -> Self {
        Self {
            dim,
            bits,
            norm,
            data,
            seed,
            format_version: FORMAT_VERSION,
        }
    }

    /// Construct a value shaped like one written before the format recorded a
    /// seed. Only for tests that need to prove old rows still decode.
    #[doc(hidden)]
    pub fn legacy(dim: u16, bits: u8, norm: f32, data: Vec<u8>) -> Self {
        Self {
            dim,
            bits,
            norm,
            data,
            seed: LEGACY_ROTATION_SEED,
            format_version: LEGACY_FORMAT_VERSION,
        }
    }

    /// Calculate packed data size for given dim and bits.
    pub fn packed_size(dim: usize, bits: u8) -> usize {
        match bits {
            2 => (dim + 3) / 4,
            3 => ((dim + 7) / 8) * 3,
            4 => (dim + 1) / 2,
            _ => dim,
        }
    }

    /// Theoretical compression ratio vs float32.
    pub fn compression_ratio(&self) -> f32 {
        let original = self.dim as f32 * 4.0;
        let compressed = self.data.len() as f32 + 4.0;
        original / compressed
    }
}
