// turboquant-pro M1: CPU SIMD batched ADC fast-scan for tq-pro per-dim codes.
//
// Computes, for each query, score[n] = norm[n] * sum_j LUT[j][code[n][j]] over a
// corpus of per-dim codes (<= 4 bits), and returns top-k. The AVX2 path uses the
// faiss-style uint8-LUT pshufb trick (16-entry table lookup, 32 db vectors per
// step). A scalar reference path computes the exact float-LUT score.
//
// Layout and arithmetic (v2, 2026-09-15):
// - Codes are repacked into blocks of 32 vectors x d dims, two 4-bit codes per byte
//   (16 bytes per (block, dim)), half the memory traffic of one byte per code.
// - The SIMD path accumulates uint8 lookups in uint16 for at most ACC_FLUSH dims,
//   then folds into uint32. v1 accumulated all d dims in uint16, which wraps past
//   65535 once d > 257: the wrap hit exactly the highest-scoring vectors (1536-d,
//   2-bit, text-embedding-3-large: recall@10 0.848 vs 0.905 exact).
// - Top-k is streaming: a size-k min-heap and a threshold per query, instead of an
//   N-entry score array plus an N-entry index array sorted per query.
//
// Build: python -m turboquant_pro._adc   (g++ -O3 -march=native -fopenmp ...)

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <algorithm>
#include <cstdint>
#include <limits>
#include <utility>
#include <vector>
#if defined(__AVX2__)
#include <immintrin.h>
#endif

namespace py = pybind11;
static constexpr int BLK = 32;         // db vectors per SIMD step
static constexpr int ACC_FLUSH = 256;  // dims per uint16 accumulation (255*256 < 65536)

// Repack (N, d) row-major codes (1 byte each, 0..15) into [nblk][d][16 bytes]:
// byte i of a (block, dim) strip holds code 2i in its low nibble, code 2i+1 in its high.
static std::vector<uint8_t> repack4(const uint8_t* codes, int64_t N, int d,
                                    int64_t& nblk_out) {
  int64_t nblk = (N + BLK - 1) / BLK;
  nblk_out = nblk;
  std::vector<uint8_t> out((size_t)nblk * d * (BLK / 2), 0);
  for (int64_t b = 0; b < nblk; ++b)
    for (int j = 0; j < d; ++j) {
      uint8_t* dst = &out[((size_t)b * d + j) * (BLK / 2)];
      for (int t = 0; t < BLK; ++t) {
        int64_t n = b * BLK + t;
        uint8_t c = n < N ? (uint8_t)(codes[(size_t)n * d + j] & 0x0F) : 0;
        dst[t / 2] |= (t % 2 == 0) ? c : (uint8_t)(c << 4);
      }
    }
  return out;
}

// Streaming top-k: min-heap of (score, index) holding the best k seen so far.
struct TopK {
  int k;
  std::vector<std::pair<float, int64_t>> heap;  // min-heap on score
  explicit TopK(int k_) : k(k_) { heap.reserve((size_t)k_); }
  void reset() { heap.clear(); }
  float threshold() const {
    return (int)heap.size() < k ? -std::numeric_limits<float>::infinity() : heap.front().first;
  }
  static bool cmp(const std::pair<float, int64_t>& a, const std::pair<float, int64_t>& b) {
    return a.first > b.first;  // makes std::heap a min-heap on score
  }
  void push(float s, int64_t i) {
    if ((int)heap.size() < k) {
      heap.emplace_back(s, i);
      std::push_heap(heap.begin(), heap.end(), cmp);
    } else if (s > heap.front().first) {
      std::pop_heap(heap.begin(), heap.end(), cmp);
      heap.back() = {s, i};
      std::push_heap(heap.begin(), heap.end(), cmp);
    }
  }
  void emit(int64_t* out_idx, float* out_sc) {
    std::sort(heap.begin(), heap.end(),
              [](const std::pair<float, int64_t>& a, const std::pair<float, int64_t>& b) {
                return a.first > b.first || (a.first == b.first && a.second < b.second);
              });
    int m = (int)heap.size();
    for (int i = 0; i < m; ++i) {
      out_idx[i] = heap[i].second;
      out_sc[i] = heap[i].first;
    }
    for (int i = m; i < k; ++i) {
      out_idx[i] = -1;
      out_sc[i] = -1e30f;
    }
  }
};

// Build float LUT[j][s] = q[j]*cent[s]; quantize to uint8 (global scale, per-dim
// bias). Returns scale and total bias so score = scale*accum + bias.
static void build_lut(const float* q, const float* cent, int d, int S,
                      std::vector<uint8_t>& lut_u8, std::vector<float>& lut_f,
                      float& scale, float& bias) {
  std::vector<float> dmin(d);
  float rmax = 1e-20f;
  for (int j = 0; j < d; ++j) {
    float qj = q[j], lo = 1e30f, hi = -1e30f;
    for (int s = 0; s < S; ++s) {
      float v = qj * cent[s];
      lut_f[j * S + s] = v;
      lo = std::min(lo, v);
      hi = std::max(hi, v);
    }
    dmin[j] = lo;
    rmax = std::max(rmax, hi - lo);
  }
  scale = rmax / 255.0f;
  bias = 0.0f;
  // uint8 LUT uses a fixed stride of 16 (pshufb needs a 16-entry table); for
  // codes with S < 16 the unused entries are zero padding.
  for (int j = 0; j < d; ++j) {
    bias += dmin[j];
    for (int s = 0; s < 16; ++s) lut_u8[j * 16 + s] = 0;
    for (int s = 0; s < S; ++s) {
      int u = (int)((lut_f[j * S + s] - dmin[j]) / scale + 0.5f);
      lut_u8[j * 16 + s] = (uint8_t)std::min(255, std::max(0, u));
    }
  }
}

// Scalar reference: exact float-LUT ADC for one block of BLK vectors.
static void scan_ref(const uint8_t* blk, const float* lut_f, int d, int S, float* acc) {
  for (int t = 0; t < BLK; ++t) acc[t] = 0.f;
  for (int j = 0; j < d; ++j) {
    const uint8_t* cj = &blk[(size_t)j * (BLK / 2)];
    const float* lj = &lut_f[(size_t)j * S];
    for (int t = 0; t < BLK; ++t) {
      uint8_t c = (t % 2 == 0) ? (cj[t / 2] & 0x0F) : (cj[t / 2] >> 4);
      acc[t] += lj[c];
    }
  }
}

#if defined(__AVX2__)
// AVX2 pshufb fast-scan for one block (BLK=32), nibble-packed codes, uint8 LUT.
// uint16 lanes are folded into uint32 every ACC_FLUSH dims, so no sum can wrap.
static void scan_simd(const uint8_t* blk, const uint8_t* lut_u8, int d, uint32_t* acc32) {
  const __m128i low4 = _mm_set1_epi8(0x0F);
  for (int t = 0; t < BLK; ++t) acc32[t] = 0;
  uint16_t tmp[BLK];
  for (int j0 = 0; j0 < d; j0 += ACC_FLUSH) {
    int j1 = std::min(d, j0 + ACC_FLUSH);
    __m256i a0 = _mm256_setzero_si256();  // 16 x uint16 (vectors 0..15)
    __m256i a1 = _mm256_setzero_si256();  // 16 x uint16 (vectors 16..31)
    for (int j = j0; j < j1; ++j) {
      __m128i packed = _mm_loadu_si128((const __m128i*)&blk[(size_t)j * (BLK / 2)]);
      __m128i lo = _mm_and_si128(packed, low4);
      __m128i hi = _mm_and_si128(_mm_srli_epi16(packed, 4), low4);
      // codes in vector order: lo0 hi0 lo1 hi1 ... (bytes 0..7), then bytes 8..15
      __m256i codes = _mm256_inserti128_si256(
          _mm256_castsi128_si256(_mm_unpacklo_epi8(lo, hi)), _mm_unpackhi_epi8(lo, hi), 1);
      __m128i lut128 = _mm_loadu_si128((const __m128i*)&lut_u8[(size_t)j * 16]);
      __m256i lut = _mm256_broadcastsi128_si256(lut128);  // same table in both lanes
      __m256i looked = _mm256_shuffle_epi8(lut, codes);     // 32 x uint8 lookups
      a0 = _mm256_add_epi16(a0, _mm256_cvtepu8_epi16(_mm256_castsi256_si128(looked)));
      a1 = _mm256_add_epi16(a1, _mm256_cvtepu8_epi16(_mm256_extracti128_si256(looked, 1)));
    }
    _mm256_storeu_si256((__m256i*)&tmp[0], a0);
    _mm256_storeu_si256((__m256i*)&tmp[16], a1);
    for (int t = 0; t < BLK; ++t) acc32[t] += tmp[t];
  }
}
#endif

// Score model (general cosine over the reconstruction):
//   score[n] = (qbias[qi] + vnorm[n] * adc[n]) * vrnorm[n]
// where adc[n] = sum_j q_rot[j]*cent[code[j]].
py::tuple search(py::array_t<uint8_t, py::array::c_style | py::array::forcecast> codes,
                 py::array_t<float, py::array::c_style | py::array::forcecast> queries,
                 py::array_t<float, py::array::c_style | py::array::forcecast> cent,
                 py::array_t<float, py::array::c_style | py::array::forcecast> vnorm,
                 py::array_t<float, py::array::c_style | py::array::forcecast> vrnorm,
                 py::array_t<float, py::array::c_style | py::array::forcecast> qbias,
                 int k, bool use_simd) {
  auto cb = codes.unchecked<2>();
  auto qb = queries.unchecked<2>();
  int64_t N = cb.shape(0);
  int d = (int)cb.shape(1);
  int Q = (int)qb.shape(0);
  int S = (int)cent.shape(0);
  if (S > 16) throw std::invalid_argument("adc_scan: codes must be <= 4 bits (S <= 16)");
  const float* cptr = cent.data();
  const float* vn = vnorm.data();
  const float* vr = vrnorm.data();
  const float* qbi = qbias.data();
  int64_t nblk;
  std::vector<uint8_t> blocked = repack4(codes.data(), N, d, nblk);

  auto out_idx = py::array_t<int64_t>({(py::ssize_t)Q, (py::ssize_t)k});
  auto out_sc = py::array_t<float>({(py::ssize_t)Q, (py::ssize_t)k});
  int64_t* oi = out_idx.mutable_data();
  float* os = out_sc.mutable_data();
  const size_t strip = (size_t)d * (BLK / 2);

  {
    py::gil_scoped_release release;
#pragma omp parallel
    {
      std::vector<float> lut_f((size_t)d * S);
      std::vector<uint8_t> lut_u8((size_t)d * 16);
      uint32_t acc32[BLK];
      float accf[BLK];
      TopK top(k);
#pragma omp for schedule(dynamic)
      for (int qi = 0; qi < Q; ++qi) {
        float scale, bias;
        build_lut(&qb(qi, 0), cptr, d, S, lut_u8, lut_f, scale, bias);
        float qb_bias = qbi[qi];
        top.reset();
        for (int64_t b = 0; b < nblk; ++b) {
          const uint8_t* blk = &blocked[(size_t)b * strip];
          int64_t base = b * BLK;
          int tmax = (int)std::min<int64_t>(BLK, N - base);
#if defined(__AVX2__)
          if (use_simd) {
            scan_simd(blk, lut_u8.data(), d, acc32);
            float thr = top.threshold();
            for (int t = 0; t < tmax; ++t) {
              int64_t n = base + t;
              float s = (qb_bias + vn[n] * (scale * (float)acc32[t] + bias)) * vr[n];
              if (s > thr) {
                top.push(s, n);
                thr = top.threshold();
              }
            }
            continue;
          }
#endif
          scan_ref(blk, lut_f.data(), d, S, accf);
          float thr = top.threshold();
          for (int t = 0; t < tmax; ++t) {
            int64_t n = base + t;
            float s = (qb_bias + vn[n] * accf[t]) * vr[n];
            if (s > thr) {
              top.push(s, n);
              thr = top.threshold();
            }
          }
        }
        top.emit(&oi[(size_t)qi * k], &os[(size_t)qi * k]);
      }
    }
  }
  return py::make_tuple(out_idx, out_sc);
}

PYBIND11_MODULE(adc_scan, m) {
  m.doc() = "tq-pro M1 CPU SIMD batched ADC fast-scan (v2: nibble-packed, no uint16 wrap, streaming top-k)";
  m.def("search", &search, py::arg("codes"), py::arg("queries"), py::arg("cent"),
        py::arg("vnorm"), py::arg("vrnorm"), py::arg("qbias"), py::arg("k") = 10,
        py::arg("use_simd") = true);
}
