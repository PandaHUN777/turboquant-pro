"""Consumer-read truncation bases for retrieval (docs/PREREG_consumer_basis.md).

Which directions should a truncated embedding keep? Corpus PCA keeps what the documents
vary in (the reconstruction corner, P_C = I). Observation Theory says keep what the
consumer reads: for top-k inner-product retrieval, the query second moment P_C = E[q q^T].
This package measures the difference with exact search, no quantization.
"""
