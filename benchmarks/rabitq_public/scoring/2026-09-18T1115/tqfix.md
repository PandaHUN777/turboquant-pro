## Claim verdicts (primary endpoint: +rerank x5 recall@10)

- **C1_beats_rabitq**: MIXED ({'TIES': 54, 'BEATS': 15, 'LOSES': 3}, n=72, no-config=47)
- **C2_ties_opq**: HOLDS ({'TIES': 14, 'BEATS': 6, 'LOSES': 2}, n=22, no-config=19)

## Matched-byte comparisons

| dataset | tq-pro config | B | family | matched baseline | B | endpoint | tq | baseline | diff [95% CI] | verdict |
|---|---|---:|---|---|---:|---|---:|---:|---|---|
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b1 | 200 | rr5 | 0.9990 | 0.9990 | -0.0001 [-0.0009, +0.0008] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b1 | 200 | single | 0.8421 | 0.8228 | +0.0192 [+0.0128, +0.0259] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b1 | 200 | rr2 | 0.9811 | 0.9742 | +0.0069 [+0.0031, +0.0107] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b2 | 404 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b2 | 404 | single | 0.9328 | 0.9035 | +0.0293 [+0.0248, +0.0341] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b2 | 404 | rr2 | 0.9995 | 0.9985 | +0.0010 [+0.0002, +0.0018] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b3 | 596 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b3 | 596 | single | 0.9426 | 0.9439 | -0.0014 [-0.0050, +0.0023] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b3 | 596 | rr2 | 0.9999 | 1.0000 | -0.0001 [-0.0002, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b4 | 788 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b4 | 788 | single | 0.9710 | 0.9665 | +0.0045 [+0.0016, +0.0074] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitq_flat-b4 | 788 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_flat-b5 (baseline anchor) | 980 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b1-n4096 | 200 | rr5 | 0.9990 | 0.9995 | -0.0006 [-0.0012, -0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b1-n4096 | 200 | single | 0.8421 | 0.8515 | -0.0094 [-0.0154, -0.0036] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b1-n4096 | 200 | rr2 | 0.9811 | 0.9845 | -0.0034 [-0.0063, -0.0005] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096 | 404 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096 | 404 | single | 0.9328 | 0.9208 | +0.0120 [+0.0084, +0.0158] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096 | 404 | rr2 | 0.9995 | 0.9991 | +0.0004 [-0.0000, +0.0009] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b3-n4096 | 596 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b3-n4096 | 596 | single | 0.9426 | 0.9553 | -0.0127 [-0.0153, -0.0101] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b3-n4096 | 596 | rr2 | 0.9999 | 1.0000 | -0.0001 [-0.0002, +0.0001] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b4-n4096 | 788 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b4-n4096 | 788 | single | 0.9710 | 0.9728 | -0.0018 [-0.0039, +0.0003] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b4-n4096 | 788 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_ivf-b5-n4096 (baseline anchor) | 980 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b1-n4096 | 221.24 | rr5 | 0.9990 | 0.9997 | -0.0007 [-0.0013, -0.0002] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b1-n4096 | 221.24 | single | 0.8421 | 0.8545 | -0.0125 [-0.0182, -0.0069] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b1-n4096 | 221.24 | rr2 | 0.9811 | 0.9872 | -0.0061 [-0.0087, -0.0036] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b2-n4096 | 421.24 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b2-n4096 | 421.24 | single | 0.9328 | 0.9264 | +0.0064 [+0.0029, +0.0099] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b2-n4096 | 421.24 | rr2 | 0.9995 | 0.9996 | -0.0001 [-0.0005, +0.0003] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b3-n4096 | 613.24 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b3-n4096 | 613.24 | single | 0.9426 | 0.9581 | -0.0155 [-0.0182, -0.0128] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b3-n4096 | 613.24 | rr2 | 0.9999 | 1.0000 | -0.0001 [-0.0002, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b4-n4096 | 805.24 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b4-n4096 | 805.24 | single | 0.9710 | 0.9761 | -0.0051 [-0.0071, -0.0030] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-3large-1536-1m-rabitqlib_ivf-b4-n4096 | 805.24 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitqlib_ivf-b5-n4096 (baseline anchor) | 997.24 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096 | 404 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096 | 404 | single | 0.9075 | 0.9208 | -0.0133 [-0.0165, -0.0100] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | RABITQ | dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096 | 404 | rr2 | 0.9981 | 0.9991 | -0.0010 [-0.0016, -0.0004] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b3 (tq anchor) | 148 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b3 (tq anchor) | 292 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b1-n4096 (baseline anchor) | 56 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b2-n4096 (baseline anchor) | 116 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b3 | 148 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b3-n4096 | 164 | rr5 | 0.9973 | 0.9964 | +0.0009 [+0.0003, +0.0015] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b3 | 148 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b3-n4096 | 164 | single | 0.8012 | 0.8049 | -0.0037 [-0.0074, +0.0001] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b3 | 148 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b3-n4096 | 164 | rr2 | 0.9654 | 0.9649 | +0.0005 [-0.0016, +0.0026] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b1-n4096 (baseline anchor) | 104 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b2-n4096 | 212 | rr5 | 0.9980 | 0.9954 | +0.0026 [+0.0009, +0.0042] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b2-n4096 | 212 | single | 0.8302 | 0.7908 | +0.0394 [+0.0328, +0.0461] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b2-n4096 | 212 | rr2 | 0.9782 | 0.9535 | +0.0248 [+0.0203, +0.0292] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b3 | 292 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b3-n4096 | 308 | rr5 | 1.0000 | 0.9987 | +0.0013 [+0.0009, +0.0018] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b3 | 292 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b3-n4096 | 308 | single | 0.8931 | 0.8681 | +0.0250 [+0.0210, +0.0288] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b3 | 292 | RABITQ | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b3-n4096 | 308 | rr2 | 0.9979 | 0.9903 | +0.0076 [+0.0062, +0.0091] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b1 | 200 | rr5 | 0.9980 | 0.9982 | -0.0002 [-0.0016, +0.0011] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b1 | 200 | single | 0.8302 | 0.7942 | +0.0360 [+0.0289, +0.0429] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b1 | 200 | rr2 | 0.9782 | 0.9641 | +0.0141 [+0.0096, +0.0186] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b2 | 404 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b2 | 404 | single | 0.9306 | 0.8938 | +0.0368 [+0.0319, +0.0416] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b2 | 404 | rr2 | 0.9999 | 0.9971 | +0.0028 [+0.0018, +0.0039] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b3 | 596 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b3 | 596 | single | 0.9282 | 0.9356 | -0.0074 [-0.0110, -0.0035] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b3 | 596 | rr2 | 0.9996 | 1.0000 | -0.0004 [-0.0007, -0.0002] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b4 | 788 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b4 | 788 | single | 0.9575 | 0.9636 | -0.0060 [-0.0091, -0.0030] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b4 | 788 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_flat-b5 (baseline anchor) | 980 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b1-n4096 | 200 | rr5 | 0.9980 | 0.9994 | -0.0014 [-0.0027, -0.0003] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b1-n4096 | 200 | single | 0.8302 | 0.8379 | -0.0077 [-0.0136, -0.0020] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b1-n4096 | 200 | rr2 | 0.9782 | 0.9827 | -0.0044 [-0.0076, -0.0013] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b2-n4096 | 404 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b2-n4096 | 404 | single | 0.9306 | 0.9127 | +0.0179 [+0.0144, +0.0214] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b2-n4096 | 404 | rr2 | 0.9999 | 0.9989 | +0.0010 [+0.0006, +0.0015] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b3-n4096 | 596 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b3-n4096 | 596 | single | 0.9282 | 0.9503 | -0.0221 [-0.0249, -0.0193] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b3-n4096 | 596 | rr2 | 0.9996 | 1.0000 | -0.0004 [-0.0007, -0.0002] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b4-n4096 | 788 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b4-n4096 | 788 | single | 0.9575 | 0.9717 | -0.0142 [-0.0166, -0.0117] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitq_ivf-b4-n4096 | 788 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0001] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_ivf-b5-n4096 (baseline anchor) | 980 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b1-n4096 | 221.36 | rr5 | 0.9980 | 0.9997 | -0.0018 [-0.0031, -0.0007] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b1-n4096 | 221.36 | single | 0.8302 | 0.8365 | -0.0063 [-0.0117, -0.0009] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b1-n4096 | 221.36 | rr2 | 0.9782 | 0.9817 | -0.0034 [-0.0066, -0.0004] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b2-n4096 | 421.36 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0001] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b2-n4096 | 421.36 | single | 0.9306 | 0.9169 | +0.0136 [+0.0102, +0.0171] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b2-n4096 | 421.36 | rr2 | 0.9999 | 0.9989 | +0.0010 [+0.0006, +0.0015] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b3-n4096 | 613.36 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b3-n4096 | 613.36 | single | 0.9282 | 0.9529 | -0.0247 [-0.0275, -0.0218] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | 580 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b3-n4096 | 613.36 | rr2 | 0.9996 | 1.0000 | -0.0004 [-0.0007, -0.0002] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b4-n4096 | 805.36 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b4-n4096 | 805.36 | single | 0.9575 | 0.9733 | -0.0157 [-0.0180, -0.0134] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | RABITQ | dbpedia-ada002-1m-rabitqlib_ivf-b4-n4096 | 805.36 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitqlib_ivf-b5-n4096 (baseline anchor) | 997.36 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b2 | 404 | rr5 | 1.0000 | 1.0000 | -0.0000 [-0.0001, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b2 | 404 | single | 0.8856 | 0.8938 | -0.0082 [-0.0130, -0.0034] | LOSES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | RABITQ | dbpedia-ada002-1m-rabitq_flat-b2 | 404 | rr2 | 0.9959 | 0.9971 | -0.0012 [-0.0024, -0.0001] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b3 (tq anchor) | 148 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b3 (tq anchor) | 292 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b1 (baseline anchor) | 20 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitq_flat-b2 | 44 | rr5 | 0.9823 | 0.8614 | +0.1208 [+0.1150, +0.1267] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitq_flat-b2 | 44 | single | 0.6850 | 0.4807 | +0.2043 [+0.1984, +0.2104] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitq_flat-b2 | 44 | rr2 | 0.8839 | 0.6675 | +0.2164 [+0.2098, +0.2232] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_flat-b3 | 56 | rr5 | 0.9991 | 0.9845 | +0.0146 [+0.0126, +0.0168] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_flat-b3 | 56 | single | 0.8262 | 0.6957 | +0.1305 [+0.1255, +0.1354] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_flat-b3 | 56 | rr2 | 0.9793 | 0.8929 | +0.0864 [+0.0820, +0.0911] | BEATS |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b4 (baseline anchor) | 68 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b5 (baseline anchor) | 80 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b1-n16384 (baseline anchor) | 20 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitq_ivf-b2-n16384 | 44 | rr5 | 0.9823 | 0.9785 | +0.0038 [+0.0016, +0.0060] | TIES |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitq_ivf-b2-n16384 | 44 | single | 0.6850 | 0.6708 | +0.0143 [+0.0091, +0.0195] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitq_ivf-b2-n16384 | 44 | rr2 | 0.8839 | 0.8708 | +0.0131 [+0.0084, +0.0178] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_ivf-b3-n16384 | 56 | rr5 | 0.9991 | 0.9995 | -0.0004 [-0.0010, +0.0000] | TIES |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_ivf-b3-n16384 | 56 | single | 0.8262 | 0.8251 | +0.0010 [-0.0027, +0.0047] | TIES |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_ivf-b3-n16384 | 56 | rr2 | 0.9793 | 0.9806 | -0.0013 [-0.0035, +0.0009] | TIES |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b4-n16384 (baseline anchor) | 68 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b5-n16384 (baseline anchor) | 80 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b1-n16384 | 32.94 | rr5 | 0.8634 | 0.8489 | +0.0144 [+0.0086, +0.0202] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b1-n16384 | 32.94 | single | 0.4933 | 0.4724 | +0.0209 [+0.0148, +0.0268] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b1-n16384 | 32.94 | rr2 | 0.6781 | 0.6553 | +0.0228 [+0.0163, +0.0294] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b2-n16384 | 56.94 | rr5 | 0.9991 | 0.9919 | +0.0072 [+0.0062, +0.0082] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b2-n16384 | 56.94 | single | 0.8262 | 0.7219 | +0.1042 [+0.0998, +0.1085] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b2-n16384 | 56.94 | rr2 | 0.9793 | 0.9167 | +0.0626 [+0.0592, +0.0661] | BEATS |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b3-n16384 (baseline anchor) | 72.94 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b4-n16384 (baseline anchor) | 88.94 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b5-n16384 (baseline anchor) | 104.94 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 (tq anchor) | 28 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b1-n16384 | 32.94 | rr5 | 0.9823 | 0.8489 | +0.1334 [+0.1282, +0.1386] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b1-n16384 | 32.94 | single | 0.6850 | 0.4724 | +0.2127 [+0.2070, +0.2184] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | RABITQ | deep-image-96-angular-rabitqlib_ivf-b1-n16384 | 32.94 | rr2 | 0.8839 | 0.6553 | +0.2285 [+0.2222, +0.2349] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_ivf-b2-n16384 | 44 | rr5 | 0.9991 | 0.9785 | +0.0206 [+0.0188, +0.0223] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_ivf-b2-n16384 | 44 | single | 0.8262 | 0.6708 | +0.1554 [+0.1505, +0.1603] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | RABITQ | deep-image-96-angular-rabitq_ivf-b2-n16384 | 44 | rr2 | 0.9793 | 0.8708 | +0.1086 [+0.1041, +0.1131] | BEATS |
| glove-100-angular | glove-100-angular-rabitq_flat-b1 (baseline anchor) | 21 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitq_flat-b2 | 46 | rr5 | 0.9877 | 0.8939 | +0.0939 [+0.0887, +0.0990] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitq_flat-b2 | 46 | single | 0.7353 | 0.5575 | +0.1778 [+0.1717, +0.1840] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitq_flat-b2 | 46 | rr2 | 0.9139 | 0.7350 | +0.1789 [+0.1724, +0.1855] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_flat-b3 | 58 | rr5 | 1.0000 | 0.9939 | +0.0061 [+0.0050, +0.0072] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_flat-b3 | 58 | single | 0.8599 | 0.7555 | +0.1043 [+0.0997, +0.1089] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_flat-b3 | 58 | rr2 | 0.9896 | 0.9338 | +0.0558 [+0.0522, +0.0595] | BEATS |
| glove-100-angular | glove-100-angular-rabitq_flat-b4 (baseline anchor) | 71 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-rabitq_flat-b5 (baseline anchor) | 83 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-rabitq_ivf-b1-n4096 (baseline anchor) | 21 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitq_ivf-b2-n4096 | 46 | rr5 | 0.9877 | 0.9379 | +0.0499 [+0.0466, +0.0532] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitq_ivf-b2-n4096 | 46 | single | 0.7353 | 0.6318 | +0.1035 [+0.0987, +0.1082] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitq_ivf-b2-n4096 | 46 | rr2 | 0.9139 | 0.8147 | +0.0992 [+0.0943, +0.1039] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_ivf-b3-n4096 | 58 | rr5 | 1.0000 | 0.9968 | +0.0031 [+0.0026, +0.0037] | TIES |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_ivf-b3-n4096 | 58 | single | 0.8599 | 0.8004 | +0.0595 [+0.0561, +0.0628] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_ivf-b3-n4096 | 58 | rr2 | 0.9896 | 0.9594 | +0.0302 [+0.0280, +0.0326] | BEATS |
| glove-100-angular | glove-100-angular-rabitq_ivf-b4-n4096 (baseline anchor) | 71 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-rabitq_ivf-b5-n4096 (baseline anchor) | 83 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | RABITQ | glove-100-angular-rabitqlib_ivf-b1-n4096 | 33.99 | rr5 | 0.9058 | 0.7298 | +0.1760 [+0.1694, +0.1827] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | RABITQ | glove-100-angular-rabitqlib_ivf-b1-n4096 | 33.99 | single | 0.5765 | 0.4193 | +0.1573 [+0.1519, +0.1626] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | RABITQ | glove-100-angular-rabitqlib_ivf-b1-n4096 | 33.99 | rr2 | 0.7554 | 0.5665 | +0.1889 [+0.1828, +0.1951] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitqlib_ivf-b2-n4096 | 57.99 | rr5 | 1.0000 | 0.9659 | +0.0340 [+0.0316, +0.0365] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitqlib_ivf-b2-n4096 | 57.99 | single | 0.8599 | 0.6827 | +0.1772 [+0.1725, +0.1818] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitqlib_ivf-b2-n4096 | 57.99 | rr2 | 0.9896 | 0.8657 | +0.1239 [+0.1189, +0.1289] | BEATS |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b3-n4096 (baseline anchor) | 73.99 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b4-n4096 (baseline anchor) | 89.99 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b5-n4096 (baseline anchor) | 105.99 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b2 (tq anchor) | 29 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitqlib_ivf-b1-n4096 | 33.99 | rr5 | 0.9877 | 0.7298 | +0.2580 [+0.2492, +0.2666] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitqlib_ivf-b1-n4096 | 33.99 | single | 0.7353 | 0.4193 | +0.3160 [+0.3100, +0.3221] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | RABITQ | glove-100-angular-rabitqlib_ivf-b1-n4096 | 33.99 | rr2 | 0.9139 | 0.5665 | +0.3474 [+0.3393, +0.3553] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_ivf-b2-n4096 | 46 | rr5 | 1.0000 | 0.9379 | +0.0621 [+0.0584, +0.0659] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_ivf-b2-n4096 | 46 | single | 0.8599 | 0.6318 | +0.2281 [+0.2225, +0.2335] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | RABITQ | glove-100-angular-rabitq_ivf-b2-n4096 | 46 | rr2 | 0.9896 | 0.8147 | +0.1749 [+0.1686, +0.1811] | BEATS |
| nytimes-256-angular | nytimes-256-angular-rabitq_flat-b1 (baseline anchor) | 40 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | RABITQ | nytimes-256-angular-rabitq_flat-b2 | 84 | rr5 | 0.9618 | 0.9603 | +0.0014 [-0.0013, +0.0042] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | RABITQ | nytimes-256-angular-rabitq_flat-b2 | 84 | single | 0.7682 | 0.7633 | +0.0049 [-0.0001, +0.0099] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | RABITQ | nytimes-256-angular-rabitq_flat-b2 | 84 | rr2 | 0.9071 | 0.9022 | +0.0049 [+0.0007, +0.0090] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitq_flat-b3 | 116 | rr5 | 0.9819 | 0.9831 | -0.0012 [-0.0023, -0.0000] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitq_flat-b3 | 116 | single | 0.8489 | 0.8608 | -0.0119 [-0.0158, -0.0081] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitq_flat-b3 | 116 | rr2 | 0.9605 | 0.9661 | -0.0056 [-0.0078, -0.0032] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitq_flat-b4 | 148 | rr5 | 0.9846 | 0.9845 | +0.0001 [-0.0009, +0.0011] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitq_flat-b4 | 148 | single | 0.9146 | 0.9087 | +0.0060 [+0.0027, +0.0092] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitq_flat-b4 | 148 | rr2 | 0.9820 | 0.9805 | +0.0014 [+0.0001, +0.0028] | TIES |
| nytimes-256-angular | nytimes-256-angular-rabitq_flat-b5 (baseline anchor) | 180 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-rabitq_ivf-b1-n2048 (baseline anchor) | 40 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | RABITQ | nytimes-256-angular-rabitq_ivf-b2-n2048 | 84 | rr5 | 0.9618 | 0.9656 | -0.0038 [-0.0059, -0.0018] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | RABITQ | nytimes-256-angular-rabitq_ivf-b2-n2048 | 84 | single | 0.7682 | 0.7890 | -0.0208 [-0.0249, -0.0168] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | RABITQ | nytimes-256-angular-rabitq_ivf-b2-n2048 | 84 | rr2 | 0.9071 | 0.9183 | -0.0112 [-0.0144, -0.0080] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitq_ivf-b3-n2048 | 116 | rr5 | 0.9819 | 0.9832 | -0.0013 [-0.0025, -0.0001] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitq_ivf-b3-n2048 | 116 | single | 0.8489 | 0.8771 | -0.0282 [-0.0314, -0.0251] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitq_ivf-b3-n2048 | 116 | rr2 | 0.9605 | 0.9708 | -0.0103 [-0.0123, -0.0084] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitq_ivf-b4-n2048 | 148 | rr5 | 0.9846 | 0.9844 | +0.0002 [-0.0008, +0.0013] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitq_ivf-b4-n2048 | 148 | single | 0.9146 | 0.9211 | -0.0065 [-0.0089, -0.0040] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitq_ivf-b4-n2048 | 148 | rr2 | 0.9820 | 0.9818 | +0.0002 [-0.0010, +0.0013] | TIES |
| nytimes-256-angular | nytimes-256-angular-rabitq_ivf-b5-n2048 (baseline anchor) | 180 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b1-n2048 (baseline anchor) | 52.9 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b2-n2048 (baseline anchor) | 92.9 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b3-n2048 | 124.9 | rr5 | 0.9819 | 0.9835 | -0.0015 [-0.0027, -0.0004] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b3-n2048 | 124.9 | single | 0.8489 | 0.8765 | -0.0276 [-0.0307, -0.0247] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b3-n2048 | 124.9 | rr2 | 0.9605 | 0.9707 | -0.0102 [-0.0121, -0.0083] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b4-n2048 | 156.9 | rr5 | 0.9846 | 0.9844 | +0.0002 [-0.0008, +0.0012] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b4-n2048 | 156.9 | single | 0.9146 | 0.9233 | -0.0087 [-0.0110, -0.0064] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b4-n2048 | 156.9 | rr2 | 0.9820 | 0.9822 | -0.0002 [-0.0014, +0.0010] | TIES |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b5-n2048 (baseline anchor) | 188.9 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 (tq anchor) | 68 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b2-n2048 | 92.9 | rr5 | 0.9819 | 0.9677 | +0.0142 [+0.0123, +0.0162] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b2-n2048 | 92.9 | single | 0.8489 | 0.7926 | +0.0563 [+0.0525, +0.0601] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | 100 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b2-n2048 | 92.9 | rr2 | 0.9605 | 0.9219 | +0.0386 [+0.0352, +0.0420] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b3-n2048 | 124.9 | rr5 | 0.9846 | 0.9835 | +0.0011 [+0.0001, +0.0022] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b3-n2048 | 124.9 | single | 0.9146 | 0.8765 | +0.0381 [+0.0352, +0.0410] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | RABITQ | nytimes-256-angular-rabitqlib_ivf-b3-n2048 | 124.9 | rr2 | 0.9820 | 0.9707 | +0.0113 [+0.0096, +0.0131] | BEATS |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d256-b1-n16384 (baseline anchor) | 40 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d256-b2-n16384 (baseline anchor) | 84 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 | 100 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d256-b3-n16384 | 116 | rr5 | 0.9793 | 0.9790 | +0.0003 [-0.0015, +0.0021] | TIES |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 | 100 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d256-b3-n16384 | 116 | single | 0.7617 | 0.7601 | +0.0017 [-0.0023, +0.0054] | TIES |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 | 100 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d256-b3-n16384 | 116 | rr2 | 0.9163 | 0.9177 | -0.0014 [-0.0043, +0.0016] | TIES |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d512-b1-n16384 (baseline anchor) | 72 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b2-n16384 | 148 | rr5 | 0.9851 | 0.9974 | -0.0123 [-0.0152, -0.0097] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b2-n16384 | 148 | single | 0.7869 | 0.8381 | -0.0512 [-0.0584, -0.0440] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b2-n16384 | 148 | rr2 | 0.9378 | 0.9722 | -0.0344 [-0.0400, -0.0292] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b3 | 196 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | rr5 | 1.0000 | 0.9995 | +0.0004 [+0.0002, +0.0007] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b3 | 196 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | single | 0.9001 | 0.9008 | -0.0007 [-0.0041, +0.0028] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b3 | 196 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | rr2 | 0.9957 | 0.9949 | +0.0008 [-0.0003, +0.0020] | TIES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitq_flat-b1 | 136 | rr5 | 0.9851 | 0.9869 | -0.0018 [-0.0052, +0.0014] | TIES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitq_flat-b1 | 136 | single | 0.7869 | 0.7706 | +0.0163 [+0.0079, +0.0249] | BEATS |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitq_flat-b1 | 136 | rr2 | 0.9378 | 0.9266 | +0.0112 [+0.0047, +0.0176] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitq_flat-b2 | 276 | rr5 | 1.0000 | 0.9998 | +0.0002 [+0.0000, +0.0005] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitq_flat-b2 | 276 | single | 0.9382 | 0.8706 | +0.0676 [+0.0622, +0.0730] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitq_flat-b2 | 276 | rr2 | 0.9999 | 0.9886 | +0.0113 [+0.0092, +0.0136] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitq_flat-b3 | 404 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitq_flat-b3 | 404 | single | 0.9304 | 0.9292 | +0.0012 [-0.0027, +0.0051] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitq_flat-b3 | 404 | rr2 | 0.9993 | 0.9995 | -0.0002 [-0.0007, +0.0004] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | RABITQ | wiki1024-10m-rabitq_flat-b4 | 532 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | RABITQ | wiki1024-10m-rabitq_flat-b4 | 532 | single | 0.9622 | 0.9547 | +0.0076 [+0.0044, +0.0107] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | RABITQ | wiki1024-10m-rabitq_flat-b4 | 532 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-rabitq_flat-b5 (baseline anchor) | 660 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitq_ivf-b1-n16384 | 136 | rr5 | 0.9851 | 0.9952 | -0.0101 [-0.0130, -0.0074] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitq_ivf-b1-n16384 | 136 | single | 0.7869 | 0.8132 | -0.0263 [-0.0333, -0.0193] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitq_ivf-b1-n16384 | 136 | rr2 | 0.9378 | 0.9596 | -0.0218 [-0.0273, -0.0165] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitq_ivf-b2-n16384 | 276 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitq_ivf-b2-n16384 | 276 | single | 0.9382 | 0.8988 | +0.0395 [+0.0356, +0.0433] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitq_ivf-b2-n16384 | 276 | rr2 | 0.9999 | 0.9947 | +0.0052 [+0.0041, +0.0063] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitq_ivf-b3-n16384 | 404 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitq_ivf-b3-n16384 | 404 | single | 0.9304 | 0.9417 | -0.0113 [-0.0144, -0.0084] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitq_ivf-b3-n16384 | 404 | rr2 | 0.9993 | 0.9997 | -0.0004 [-0.0009, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | RABITQ | wiki1024-10m-rabitq_ivf-b4-n16384 | 532 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | RABITQ | wiki1024-10m-rabitq_ivf-b4-n16384 | 532 | single | 0.9622 | 0.9642 | -0.0019 [-0.0043, +0.0005] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | RABITQ | wiki1024-10m-rabitq_ivf-b4-n16384 | 532 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-rabitq_ivf-b5-n16384 (baseline anchor) | 660 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitqlib_ivf-b1-n16384 | 147.57 | rr5 | 0.9851 | 0.9975 | -0.0124 [-0.0152, -0.0097] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitqlib_ivf-b1-n16384 | 147.57 | single | 0.7869 | 0.8265 | -0.0396 [-0.0461, -0.0335] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | RABITQ | wiki1024-10m-rabitqlib_ivf-b1-n16384 | 147.57 | rr2 | 0.9378 | 0.9692 | -0.0314 [-0.0367, -0.0263] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitqlib_ivf-b2-n16384 | 283.57 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitqlib_ivf-b2-n16384 | 283.57 | single | 0.9382 | 0.9113 | +0.0269 [+0.0236, +0.0303] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-rabitqlib_ivf-b2-n16384 | 283.57 | rr2 | 0.9999 | 0.9976 | +0.0023 [+0.0017, +0.0029] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitqlib_ivf-b3-n16384 | 411.57 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitqlib_ivf-b3-n16384 | 411.57 | single | 0.9304 | 0.9510 | -0.0206 [-0.0235, -0.0178] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | 388 | RABITQ | wiki1024-10m-rabitqlib_ivf-b3-n16384 | 411.57 | rr2 | 0.9993 | 0.9999 | -0.0006 [-0.0010, -0.0002] | TIES |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 | 100 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d256-b2-n16384 | 84 | rr5 | 0.9793 | 0.9663 | +0.0130 [+0.0104, +0.0156] | BEATS |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 | 100 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d256-b2-n16384 | 84 | single | 0.7617 | 0.7242 | +0.0375 [+0.0330, +0.0421] | BEATS |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 | 100 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d256-b2-n16384 | 84 | rr2 | 0.9163 | 0.8885 | +0.0278 [+0.0239, +0.0319] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | rr5 | 0.9999 | 0.9995 | +0.0004 [+0.0001, +0.0007] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | single | 0.8863 | 0.9008 | -0.0145 [-0.0183, -0.0107] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | rr2 | 0.9928 | 0.9949 | -0.0022 [-0.0036, -0.0008] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b3 (tq anchor) | 196 | RABITQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | rr5 | 1.0000 | 0.9995 | +0.0005 [+0.0002, +0.0008] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | single | 0.9382 | 0.9008 | +0.0374 [+0.0341, +0.0407] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | RABITQ | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | 212 | rr2 | 0.9999 | 0.9949 | +0.0049 [+0.0039, +0.0060] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | OPQ | dbpedia-3large-1536-1m-opq-m192 | 192 | rr5 | 0.9990 | 0.9999 | -0.0009 [-0.0015, -0.0004] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | OPQ | dbpedia-3large-1536-1m-opq-m192 | 192 | single | 0.8421 | 0.8565 | -0.0144 [-0.0191, -0.0097] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | OPQ | dbpedia-3large-1536-1m-opq-m192 | 192 | rr2 | 0.9811 | 0.9888 | -0.0077 [-0.0100, -0.0054] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | OPQ | dbpedia-3large-1536-1m-opq-m384 | 384 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | OPQ | dbpedia-3large-1536-1m-opq-m384 | 384 | single | 0.9328 | 0.9167 | +0.0161 [+0.0128, +0.0196] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | OPQ | dbpedia-3large-1536-1m-opq-m384 | 384 | rr2 | 0.9995 | 0.9993 | +0.0002 [-0.0002, +0.0006] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | OPQ | dbpedia-3large-1536-1m-opq-m768 | 768 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | OPQ | dbpedia-3large-1536-1m-opq-m768 | 768 | single | 0.9710 | 0.9643 | +0.0067 [+0.0043, +0.0090] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | OPQ | dbpedia-3large-1536-1m-opq-m768 | 768 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-opq-m96 (baseline anchor) | 96 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | OPQ | dbpedia-3large-1536-1m-opq-m384 | 384 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | OPQ | dbpedia-3large-1536-1m-opq-m384 | 384 | single | 0.9075 | 0.9167 | -0.0092 [-0.0124, -0.0060] | LOSES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | OPQ | dbpedia-3large-1536-1m-opq-m384 | 384 | rr2 | 0.9981 | 0.9993 | -0.0012 [-0.0018, -0.0006] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 (tq anchor) | 580 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b3 (tq anchor) | 148 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b3 (tq anchor) | 292 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | OPQ | dbpedia-ada002-1m-opq-m192 | 192 | rr5 | 0.9980 | 0.9984 | -0.0004 [-0.0017, +0.0007] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | OPQ | dbpedia-ada002-1m-opq-m192 | 192 | single | 0.8302 | 0.8091 | +0.0211 [+0.0154, +0.0270] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | OPQ | dbpedia-ada002-1m-opq-m192 | 192 | rr2 | 0.9782 | 0.9703 | +0.0079 [+0.0047, +0.0112] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | OPQ | dbpedia-ada002-1m-opq-m384 | 384 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | OPQ | dbpedia-ada002-1m-opq-m384 | 384 | single | 0.9306 | 0.8743 | +0.0563 [+0.0523, +0.0602] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | OPQ | dbpedia-ada002-1m-opq-m384 | 384 | rr2 | 0.9999 | 0.9950 | +0.0049 [+0.0040, +0.0058] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | OPQ | dbpedia-ada002-1m-opq-m768 | 768 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | OPQ | dbpedia-ada002-1m-opq-m768 | 768 | single | 0.9575 | 0.9368 | +0.0208 [+0.0181, +0.0235] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | OPQ | dbpedia-ada002-1m-opq-m768 | 768 | rr2 | 1.0000 | 0.9999 | +0.0001 [+0.0000, +0.0002] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-opq-m96 (baseline anchor) | 96 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | OPQ | dbpedia-ada002-1m-opq-m384 | 384 | rr5 | 1.0000 | 1.0000 | -0.0000 [-0.0001, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | OPQ | dbpedia-ada002-1m-opq-m384 | 384 | single | 0.8856 | 0.8743 | +0.0113 [+0.0076, +0.0151] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | OPQ | dbpedia-ada002-1m-opq-m384 | 384 | rr2 | 0.9959 | 0.9950 | +0.0008 [-0.0001, +0.0018] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 (tq anchor) | 580 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b3 (tq anchor) | 148 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b3 (tq anchor) | 292 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-opq-m24 (baseline anchor) | 24 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | OPQ | deep-image-96-angular-opq-m32 | 32 | rr5 | 0.8634 | 0.8342 | +0.0292 [+0.0235, +0.0352] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | OPQ | deep-image-96-angular-opq-m32 | 32 | single | 0.4933 | 0.4742 | +0.0191 [+0.0134, +0.0248] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | OPQ | deep-image-96-angular-opq-m32 | 32 | rr2 | 0.6781 | 0.6515 | +0.0266 [+0.0203, +0.0330] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | OPQ | deep-image-96-angular-opq-m48 | 48 | rr5 | 0.9823 | 0.9646 | +0.0177 [+0.0139, +0.0216] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | OPQ | deep-image-96-angular-opq-m48 | 48 | single | 0.6850 | 0.6837 | +0.0014 [-0.0039, +0.0069] | TIES |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | OPQ | deep-image-96-angular-opq-m48 | 48 | rr2 | 0.8839 | 0.8722 | +0.0116 [+0.0064, +0.0171] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | OPQ | deep-image-96-angular-opq-m24 | 24 | rr5 | 0.8634 | 0.6878 | +0.1756 [+0.1691, +0.1822] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | OPQ | deep-image-96-angular-opq-m24 | 24 | single | 0.4933 | 0.3460 | +0.1473 [+0.1418, +0.1529] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | OPQ | deep-image-96-angular-opq-m24 | 24 | rr2 | 0.6781 | 0.4930 | +0.1851 [+0.1788, +0.1916] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | OPQ | deep-image-96-angular-opq-m32 | 32 | rr5 | 0.9823 | 0.8342 | +0.1481 [+0.1415, +0.1551] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | OPQ | deep-image-96-angular-opq-m32 | 32 | single | 0.6850 | 0.4742 | +0.2108 [+0.2054, +0.2165] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | OPQ | deep-image-96-angular-opq-m32 | 32 | rr2 | 0.8839 | 0.6515 | +0.2324 [+0.2259, +0.2390] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | OPQ | deep-image-96-angular-opq-m48 | 48 | rr5 | 0.9991 | 0.9646 | +0.0345 [+0.0302, +0.0391] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | OPQ | deep-image-96-angular-opq-m48 | 48 | single | 0.8262 | 0.6837 | +0.1425 [+0.1373, +0.1478] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | OPQ | deep-image-96-angular-opq-m48 | 48 | rr2 | 0.9793 | 0.8722 | +0.1071 [+0.1015, +0.1129] | BEATS |
| glove-100-angular | glove-100-angular-opq-m20 (baseline anchor) | 20 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-opq-m25 (baseline anchor) | 25 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | OPQ | glove-100-angular-opq-m50 | 50 | rr5 | 0.9877 | 0.9992 | -0.0115 [-0.0127, -0.0104] | LOSES |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | OPQ | glove-100-angular-opq-m50 | 50 | single | 0.7353 | 0.8278 | -0.0925 [-0.0966, -0.0886] | LOSES |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | OPQ | glove-100-angular-opq-m50 | 50 | rr2 | 0.9139 | 0.9774 | -0.0635 [-0.0668, -0.0604] | LOSES |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | OPQ | glove-100-angular-opq-m25 | 25 | rr5 | 0.9058 | 0.8654 | +0.0403 [+0.0367, +0.0441] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | OPQ | glove-100-angular-opq-m25 | 25 | single | 0.5765 | 0.5181 | +0.0584 [+0.0539, +0.0630] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | OPQ | glove-100-angular-opq-m25 | 25 | rr2 | 0.7554 | 0.6946 | +0.0609 [+0.0563, +0.0656] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 (tq anchor) | 42 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | OPQ | glove-100-angular-opq-m50 | 50 | rr5 | 1.0000 | 0.9992 | +0.0007 [+0.0004, +0.0010] | TIES |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | OPQ | glove-100-angular-opq-m50 | 50 | single | 0.8599 | 0.8278 | +0.0321 [+0.0291, +0.0350] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | OPQ | glove-100-angular-opq-m50 | 50 | rr2 | 0.9896 | 0.9774 | +0.0122 [+0.0106, +0.0138] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | OPQ | nytimes-256-angular-opq-m128 | 128 | rr5 | 0.9846 | 0.9846 | -0.0001 [-0.0010, +0.0009] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | OPQ | nytimes-256-angular-opq-m128 | 128 | single | 0.9146 | 0.9086 | +0.0060 [+0.0036, +0.0085] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | OPQ | nytimes-256-angular-opq-m128 | 128 | rr2 | 0.9820 | 0.9821 | -0.0002 [-0.0013, +0.0010] | TIES |
| nytimes-256-angular | nytimes-256-angular-opq-m32 (baseline anchor) | 32 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-opq-m64 (baseline anchor) | 64 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | OPQ | nytimes-256-angular-opq-m64 | 64 | rr5 | 0.9618 | 0.9667 | -0.0049 [-0.0069, -0.0029] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | OPQ | nytimes-256-angular-opq-m64 | 64 | single | 0.7682 | 0.7639 | +0.0043 [+0.0005, +0.0082] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | OPQ | nytimes-256-angular-opq-m64 | 64 | rr2 | 0.9071 | 0.9091 | -0.0020 [-0.0052, +0.0011] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 (tq anchor) | 100 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | OPQ | wiki1024-10m-opq-m128 | 128 | rr5 | 0.9851 | 0.9974 | -0.0123 [-0.0150, -0.0097] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | OPQ | wiki1024-10m-opq-m128 | 128 | single | 0.7869 | 0.8197 | -0.0328 [-0.0393, -0.0261] | LOSES |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | 132 | OPQ | wiki1024-10m-opq-m128 | 128 | rr2 | 0.9378 | 0.9648 | -0.0270 [-0.0322, -0.0221] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | OPQ | wiki1024-10m-opq-m256 | 256 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | OPQ | wiki1024-10m-opq-m256 | 256 | single | 0.9382 | 0.8993 | +0.0389 [+0.0353, +0.0424] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | OPQ | wiki1024-10m-opq-m256 | 256 | rr2 | 0.9999 | 0.9967 | +0.0031 [+0.0024, +0.0040] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | OPQ | wiki1024-10m-opq-m512 | 512 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | OPQ | wiki1024-10m-opq-m512 | 512 | single | 0.9622 | 0.9485 | +0.0137 [+0.0111, +0.0164] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | OPQ | wiki1024-10m-opq-m512 | 512 | rr2 | 1.0000 | 0.9999 | +0.0001 [+0.0000, +0.0002] | TIES |
| wiki1024-10m | wiki1024-10m-opq-m64 (baseline anchor) | 64 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 (tq anchor) | 100 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | OPQ | wiki1024-10m-opq-m256 | 256 | rr5 | 0.9999 | 1.0000 | -0.0001 [-0.0002, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | OPQ | wiki1024-10m-opq-m256 | 256 | single | 0.8863 | 0.8993 | -0.0130 [-0.0166, -0.0095] | LOSES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | OPQ | wiki1024-10m-opq-m256 | 256 | rr2 | 0.9928 | 0.9967 | -0.0040 [-0.0052, -0.0028] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 (tq anchor) | 388 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b3 (tq anchor) | 196 | OPQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | PQ | dbpedia-3large-1536-1m-pq-m192 | 192 | rr5 | 0.9990 | 0.9983 | +0.0006 [-0.0001, +0.0014] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | PQ | dbpedia-3large-1536-1m-pq-m192 | 192 | single | 0.8421 | 0.8069 | +0.0352 [+0.0295, +0.0409] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | 196 | PQ | dbpedia-3large-1536-1m-pq-m192 | 192 | rr2 | 0.9811 | 0.9645 | +0.0167 [+0.0133, +0.0200] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | PQ | dbpedia-3large-1536-1m-pq-m384 | 384 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | PQ | dbpedia-3large-1536-1m-pq-m384 | 384 | single | 0.9328 | 0.8962 | +0.0366 [+0.0329, +0.0405] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | 388 | PQ | dbpedia-3large-1536-1m-pq-m384 | 384 | rr2 | 0.9995 | 0.9971 | +0.0025 [+0.0017, +0.0032] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | PQ | dbpedia-3large-1536-1m-pq-m768 | 768 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | PQ | dbpedia-3large-1536-1m-pq-m768 | 768 | single | 0.9710 | 0.9628 | +0.0082 [+0.0058, +0.0105] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | 772 | PQ | dbpedia-3large-1536-1m-pq-m768 | 768 | rr2 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-pq-m96 (baseline anchor) | 96 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | PQ | dbpedia-3large-1536-1m-pq-m384 | 384 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | PQ | dbpedia-3large-1536-1m-pq-m384 | 384 | single | 0.9075 | 0.8962 | +0.0113 [+0.0079, +0.0146] | BEATS |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | 388 | PQ | dbpedia-3large-1536-1m-pq-m384 | 384 | rr2 | 0.9981 | 0.9971 | +0.0011 [+0.0003, +0.0018] | TIES |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 (tq anchor) | 580 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b3 (tq anchor) | 148 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b3 (tq anchor) | 292 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | PQ | dbpedia-ada002-1m-pq-m192 | 192 | rr5 | 0.9980 | 0.9680 | +0.0300 [+0.0267, +0.0335] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | PQ | dbpedia-ada002-1m-pq-m192 | 192 | single | 0.8302 | 0.6686 | +0.1616 [+0.1542, +0.1689] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | 196 | PQ | dbpedia-ada002-1m-pq-m192 | 192 | rr2 | 0.9782 | 0.8571 | +0.1211 [+0.1144, +0.1278] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | PQ | dbpedia-ada002-1m-pq-m384 | 384 | rr5 | 1.0000 | 0.9994 | +0.0006 [+0.0003, +0.0010] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | PQ | dbpedia-ada002-1m-pq-m384 | 384 | single | 0.9306 | 0.8190 | +0.1115 [+0.1068, +0.1163] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | 388 | PQ | dbpedia-ada002-1m-pq-m384 | 384 | rr2 | 0.9999 | 0.9756 | +0.0243 [+0.0218, +0.0268] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | PQ | dbpedia-ada002-1m-pq-m768 | 768 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | PQ | dbpedia-ada002-1m-pq-m768 | 768 | single | 0.9575 | 0.9395 | +0.0181 [+0.0153, +0.0209] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | 772 | PQ | dbpedia-ada002-1m-pq-m768 | 768 | rr2 | 1.0000 | 0.9999 | +0.0001 [+0.0000, +0.0003] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pq-m96 (baseline anchor) | 96 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | PQ | dbpedia-ada002-1m-pq-m384 | 384 | rr5 | 1.0000 | 0.9994 | +0.0006 [+0.0003, +0.0009] | TIES |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | PQ | dbpedia-ada002-1m-pq-m384 | 384 | single | 0.8856 | 0.8190 | +0.0666 [+0.0625, +0.0708] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | 388 | PQ | dbpedia-ada002-1m-pq-m384 | 384 | rr2 | 0.9959 | 0.9756 | +0.0203 [+0.0181, +0.0225] | BEATS |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 (tq anchor) | 580 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b3 (tq anchor) | 148 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b3 (tq anchor) | 292 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-pq-m24 (baseline anchor) | 24 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | PQ | deep-image-96-angular-pq-m32 | 32 | rr5 | 0.8634 | 0.8252 | +0.0382 [+0.0323, +0.0442] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | PQ | deep-image-96-angular-pq-m32 | 32 | single | 0.4933 | 0.4662 | +0.0271 [+0.0213, +0.0331] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | PQ | deep-image-96-angular-pq-m32 | 32 | rr2 | 0.6781 | 0.6387 | +0.0394 [+0.0328, +0.0464] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | PQ | deep-image-96-angular-pq-m48 | 48 | rr5 | 0.9823 | 0.9650 | +0.0173 [+0.0137, +0.0212] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | PQ | deep-image-96-angular-pq-m48 | 48 | single | 0.6850 | 0.6826 | +0.0025 [-0.0028, +0.0079] | TIES |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | PQ | deep-image-96-angular-pq-m48 | 48 | rr2 | 0.8839 | 0.8715 | +0.0123 [+0.0071, +0.0178] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | PQ | deep-image-96-angular-pq-m24 | 24 | rr5 | 0.8634 | 0.6545 | +0.2088 [+0.2020, +0.2158] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | PQ | deep-image-96-angular-pq-m24 | 24 | single | 0.4933 | 0.3268 | +0.1665 [+0.1609, +0.1722] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | 28 | PQ | deep-image-96-angular-pq-m24 | 24 | rr2 | 0.6781 | 0.4652 | +0.2129 [+0.2065, +0.2193] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | PQ | deep-image-96-angular-pq-m32 | 32 | rr5 | 0.9823 | 0.8252 | +0.1571 [+0.1502, +0.1644] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | PQ | deep-image-96-angular-pq-m32 | 32 | single | 0.6850 | 0.4662 | +0.2188 [+0.2131, +0.2248] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | 40 | PQ | deep-image-96-angular-pq-m32 | 32 | rr2 | 0.8839 | 0.6387 | +0.2452 [+0.2382, +0.2523] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | PQ | deep-image-96-angular-pq-m48 | 48 | rr5 | 0.9991 | 0.9650 | +0.0341 [+0.0300, +0.0386] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | PQ | deep-image-96-angular-pq-m48 | 48 | single | 0.8262 | 0.6826 | +0.1436 [+0.1385, +0.1487] | BEATS |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | 52 | PQ | deep-image-96-angular-pq-m48 | 48 | rr2 | 0.9793 | 0.8715 | +0.1078 [+0.1023, +0.1136] | BEATS |
| glove-100-angular | glove-100-angular-pq-m20 (baseline anchor) | 20 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-pq-m25 (baseline anchor) | 25 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | PQ | glove-100-angular-pq-m50 | 50 | rr5 | 0.9877 | 0.9990 | -0.0112 [-0.0125, -0.0100] | LOSES |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | PQ | glove-100-angular-pq-m50 | 50 | single | 0.7353 | 0.8256 | -0.0903 [-0.0945, -0.0862] | LOSES |
| glove-100-angular | glove-100-angular-tq-d100-b3 | 42 | PQ | glove-100-angular-pq-m50 | 50 | rr2 | 0.9139 | 0.9748 | -0.0609 [-0.0644, -0.0574] | LOSES |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | PQ | glove-100-angular-pq-m25 | 25 | rr5 | 0.9058 | 0.8627 | +0.0430 [+0.0392, +0.0469] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | PQ | glove-100-angular-pq-m25 | 25 | single | 0.5765 | 0.5176 | +0.0589 [+0.0543, +0.0636] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b2 | 29 | PQ | glove-100-angular-pq-m25 | 25 | rr2 | 0.7554 | 0.6929 | +0.0625 [+0.0577, +0.0672] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b3 (tq anchor) | 42 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | PQ | glove-100-angular-pq-m50 | 50 | rr5 | 1.0000 | 0.9990 | +0.0010 [+0.0006, +0.0014] | TIES |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | PQ | glove-100-angular-pq-m50 | 50 | single | 0.8599 | 0.8256 | +0.0343 [+0.0312, +0.0373] | BEATS |
| glove-100-angular | glove-100-angular-tq-d100-b4 | 54 | PQ | glove-100-angular-pq-m50 | 50 | rr2 | 0.9896 | 0.9748 | +0.0148 [+0.0130, +0.0167] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | PQ | nytimes-256-angular-pq-m128 | 128 | rr5 | 0.9846 | 0.9846 | -0.0001 [-0.0010, +0.0009] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | PQ | nytimes-256-angular-pq-m128 | 128 | single | 0.9146 | 0.9089 | +0.0057 [+0.0033, +0.0082] | BEATS |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | 132 | PQ | nytimes-256-angular-pq-m128 | 128 | rr2 | 0.9820 | 0.9819 | +0.0001 [-0.0010, +0.0013] | TIES |
| nytimes-256-angular | nytimes-256-angular-pq-m32 (baseline anchor) | 32 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-pq-m64 (baseline anchor) | 64 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | PQ | nytimes-256-angular-pq-m64 | 64 | rr5 | 0.9618 | 0.9669 | -0.0051 [-0.0072, -0.0031] | LOSES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | PQ | nytimes-256-angular-pq-m64 | 64 | single | 0.7682 | 0.7662 | +0.0020 [-0.0019, +0.0059] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | 68 | PQ | nytimes-256-angular-pq-m64 | 64 | rr2 | 0.9071 | 0.9110 | -0.0039 [-0.0071, -0.0009] | TIES |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 (tq anchor) | 100 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | PQ | wiki1024-10m-pq-m256 | 256 | rr5 | 1.0000 | 0.9998 | +0.0002 [+0.0000, +0.0004] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | PQ | wiki1024-10m-pq-m256 | 256 | single | 0.9382 | 0.8827 | +0.0555 [+0.0514, +0.0596] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | 260 | PQ | wiki1024-10m-pq-m256 | 256 | rr2 | 0.9999 | 0.9920 | +0.0078 [+0.0065, +0.0092] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | PQ | wiki1024-10m-pq-m512 | 512 | rr5 | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | PQ | wiki1024-10m-pq-m512 | 512 | single | 0.9622 | 0.9491 | +0.0131 [+0.0106, +0.0158] | BEATS |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | 516 | PQ | wiki1024-10m-pq-m512 | 512 | rr2 | 1.0000 | 0.9999 | +0.0001 [+0.0000, +0.0002] | TIES |
| wiki1024-10m | wiki1024-10m-pq-m64 (baseline anchor) | 64 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 (tq anchor) | 100 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 (tq anchor) | 132 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | PQ | wiki1024-10m-pq-m256 | 256 | rr5 | 0.9999 | 0.9998 | +0.0001 [-0.0001, +0.0004] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | PQ | wiki1024-10m-pq-m256 | 256 | single | 0.8863 | 0.8827 | +0.0036 [-0.0004, +0.0075] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | 260 | PQ | wiki1024-10m-pq-m256 | 256 | rr2 | 0.9928 | 0.9920 | +0.0007 [-0.0007, +0.0021] | TIES |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 (tq anchor) | 388 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b3 (tq anchor) | 196 | PQ | nothing in [0.80, 1.05] x B | - | - | - | - | - | NO-CONFIG |

## Every scored config (mean over 3 seeds; seed spread in brackets)

| dataset | config | family | B/vec | single | rr2 | rr5 | build s | search s |
|---|---|---|---:|---|---|---|---:|---:|
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-opq-m96 | OPQ | 96 | 0.7602 [0.7560, 0.7628] | 0.9345 [0.9303, 0.9385] | 0.9930 [0.9925, 0.9937] | 993.6 | 16.69 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-opq-m192 | OPQ | 192 | 0.8565 [0.8555, 0.8576] | 0.9888 [0.9875, 0.9904] | 0.9999 [0.9998, 0.9999] | 1587.8 | 33.30 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-opq-m384 | OPQ | 384 | 0.9167 [0.9134, 0.9195] | 0.9993 [0.9990, 0.9995] | 1.0000 [1.0000, 1.0000] | 1245.2 | 79.72 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-opq-m768 | OPQ | 768 | 0.9643 [0.9642, 0.9646] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 2117.9 | 189.51 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-pq-m96 | PQ | 96 | 0.6794 [0.6774, 0.6828] | 0.8618 [0.8595, 0.8637] | 0.9629 [0.9618, 0.9641] | 136.4 | 16.72 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-pq-m192 | PQ | 192 | 0.8069 [0.8058, 0.8085] | 0.9645 [0.9621, 0.9663] | 0.9983 [0.9979, 0.9988] | 178.1 | 33.59 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-pq-m384 | PQ | 384 | 0.8962 [0.8953, 0.8973] | 0.9971 [0.9962, 0.9984] | 1.0000 [1.0000, 1.0000] | 311.8 | 77.37 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-pq-m768 | PQ | 768 | 0.9628 [0.9622, 0.9632] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 649.5 | 193.99 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_ivf-b1-n4096 | RABITQ | 200 | 0.8515 [0.8493, 0.8547] | 0.9845 [0.9844, 0.9847] | 0.9995 [0.9995, 0.9996] | 154.9 | 2543.72 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_flat-b1 | RABITQ | 200 | 0.8228 [0.8218, 0.8241] | 0.9742 [0.9741, 0.9744] | 0.9990 [0.9990, 0.9991] | 45.8 | 2535.09 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitqlib_ivf-b1-n4096 | RABITQ | 221.24 | 0.8545 [0.8522, 0.8564] | 0.9872 [0.9861, 0.9886] | 0.9997 [0.9996, 0.9997] | 223.5 | 8.27 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096 | RABITQ | 404 | 0.9208 [0.9181, 0.9234] | 0.9991 [0.9989, 0.9993] | 1.0000 [1.0000, 1.0000] | 172.4 | 2520.35 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_flat-b2 | RABITQ | 404 | 0.9035 [0.9032, 0.9038] | 0.9985 [0.9984, 0.9986] | 1.0000 [1.0000, 1.0000] | 72.4 | 2576.31 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitqlib_ivf-b2-n4096 | RABITQ | 421.24 | 0.9264 [0.9254, 0.9273] | 0.9996 [0.9995, 0.9997] | 1.0000 [1.0000, 1.0000] | 230.3 | 7.47 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_ivf-b3-n4096 | RABITQ | 596 | 0.9553 [0.9543, 0.9563] | 1.0000 [0.9999, 1.0000] | 1.0000 [1.0000, 1.0000] | 214.8 | 2554.80 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_flat-b3 | RABITQ | 596 | 0.9439 [0.9436, 0.9443] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 89.0 | 2599.64 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitqlib_ivf-b3-n4096 | RABITQ | 613.24 | 0.9581 [0.9569, 0.9593] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 230.5 | 7.37 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_ivf-b4-n4096 | RABITQ | 788 | 0.9728 [0.9712, 0.9746] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 203.2 | 2544.74 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_flat-b4 | RABITQ | 788 | 0.9665 [0.9658, 0.9673] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 88.9 | 2573.92 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitqlib_ivf-b4-n4096 | RABITQ | 805.24 | 0.9761 [0.9748, 0.9782] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 234.3 | 7.30 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_ivf-b5-n4096 | RABITQ | 980 | 0.9853 [0.9842, 0.9863] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 265.5 | 2574.00 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitq_flat-b5 | RABITQ | 980 | 0.9814 [0.9808, 0.9820] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 108.4 | 2605.06 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-rabitqlib_ivf-b5-n4096 | RABITQ | 997.24 | 0.9867 [0.9855, 0.9880] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 237.8 | 8.09 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b3 | TQFIX | 148 | 0.8221 [0.8188, 0.8242] | 0.9734 [0.9726, 0.9741] | 0.9985 [0.9980, 0.9988] | 36.7 | 8.04 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d384-b4 | TQFIX | 196 | 0.8421 [0.8399, 0.8435] | 0.9811 [0.9805, 0.9817] | 0.9990 [0.9987, 0.9991] | 41.2 | 8.14 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b3 | TQFIX | 292 | 0.9076 [0.9066, 0.9084] | 0.9983 [0.9978, 0.9986] | 0.9999 [0.9999, 1.0000] | 64.0 | 16.22 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d768-b4 | TQFIX | 388 | 0.9328 [0.9316, 0.9344] | 0.9995 [0.9995, 0.9996] | 1.0000 [1.0000, 1.0000] | 66.8 | 15.93 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b2 | TQFIX | 388 | 0.9075 [0.9069, 0.9082] | 0.9981 [0.9977, 0.9984] | 1.0000 [1.0000, 1.0000] | 94.4 | 41.20 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b3 | TQFIX | 580 | 0.9426 [0.9421, 0.9434] | 0.9999 [0.9998, 1.0000] | 1.0000 [1.0000, 1.0000] | 96.8 | 31.15 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tqfix-d1536-b4 | TQFIX | 772 | 0.9710 [0.9697, 0.9720] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 112.9 | 31.73 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tq_ivf-d384-b3-n4096 | TQIVF | 148 | 0.8216 [0.8202, 0.8241] | 0.9687 [0.9680, 0.9695] | 0.9976 [0.9974, 0.9979] | 127.2 | 9.87 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tq_ivf-d384-b4-n4096 | TQIVF | 196 | 0.8433 [0.8424, 0.8443] | 0.9815 [0.9813, 0.9818] | 0.9990 [0.9989, 0.9991] | 127.1 | 9.73 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tq_ivf-d768-b3-n4096 | TQIVF | 292 | 0.9032 [0.9015, 0.9052] | 0.9968 [0.9961, 0.9975] | 0.9999 [0.9999, 1.0000] | 201.0 | 18.21 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tq_ivf-d1536-b2-n4096 | TQIVF | 388 | 0.9001 [0.8982, 0.9030] | 0.9954 [0.9950, 0.9959] | 1.0000 [0.9999, 1.0000] | 370.4 | 31.62 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tq_ivf-d768-b4-n4096 | TQIVF | 388 | 0.9342 [0.9332, 0.9350] | 0.9995 [0.9993, 0.9997] | 1.0000 [1.0000, 1.0000] | 210.2 | 17.17 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tq_ivf-d1536-b3-n4096 | TQIVF | 580 | 0.9347 [0.9345, 0.9350] | 0.9995 [0.9994, 0.9995] | 1.0000 [1.0000, 1.0000] | 393.1 | 30.95 |
| dbpedia-3large-1536-1m | dbpedia-3large-1536-1m-tq_ivf-d1536-b4-n4096 | TQIVF | 772 | 0.9712 [0.9698, 0.9723] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 380.3 | 31.70 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-opq-m96 | OPQ | 96 | 0.7091 [0.7068, 0.7115] | 0.8980 [0.8959, 0.8998] | 0.9826 [0.9811, 0.9838] | 1080.2 | 16.75 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-opq-m192 | OPQ | 192 | 0.8091 [0.8067, 0.8120] | 0.9703 [0.9694, 0.9721] | 0.9984 [0.9978, 0.9988] | 1611.1 | 33.68 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-opq-m384 | OPQ | 384 | 0.8743 [0.8720, 0.8772] | 0.9950 [0.9936, 0.9963] | 1.0000 [1.0000, 1.0000] | 1181.0 | 80.21 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-opq-m768 | OPQ | 768 | 0.9368 [0.9345, 0.9406] | 0.9999 [0.9999, 0.9999] | 1.0000 [1.0000, 1.0000] | 1810.0 | 190.17 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pq-m96 | PQ | 96 | 0.5041 [0.5007, 0.5068] | 0.6770 [0.6715, 0.6802] | 0.8387 [0.8336, 0.8427] | 153.9 | 16.82 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pq-m192 | PQ | 192 | 0.6686 [0.6664, 0.6725] | 0.8571 [0.8551, 0.8602] | 0.9680 [0.9664, 0.9700] | 177.5 | 33.53 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pq-m384 | PQ | 384 | 0.8190 [0.8167, 0.8210] | 0.9756 [0.9746, 0.9767] | 0.9994 [0.9991, 0.9997] | 331.0 | 78.42 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pq-m768 | PQ | 768 | 0.9395 [0.9385, 0.9405] | 0.9999 [0.9998, 0.9999] | 1.0000 [1.0000, 1.0000] | 602.7 | 193.90 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b1-n4096 | RABITQ | 56 | 0.6377 [0.6356, 0.6419] | 0.8206 [0.8176, 0.8230] | 0.9451 [0.9420, 0.9475] | 93.0 | 638.28 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b1-n4096 | RABITQ | 104 | 0.6648 [0.6626, 0.6676] | 0.8479 [0.8453, 0.8516] | 0.9553 [0.9545, 0.9562] | 108.1 | 1270.79 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b2-n4096 | RABITQ | 116 | 0.7542 [0.7513, 0.7561] | 0.9317 [0.9308, 0.9323] | 0.9900 [0.9899, 0.9901] | 92.3 | 629.70 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d384-b3-n4096 | RABITQ | 164 | 0.8049 [0.8015, 0.8075] | 0.9649 [0.9641, 0.9664] | 0.9964 [0.9960, 0.9968] | 92.0 | 633.01 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_ivf-b1-n4096 | RABITQ | 200 | 0.8379 [0.8374, 0.8386] | 0.9827 [0.9815, 0.9838] | 0.9994 [0.9991, 0.9995] | 163.3 | 2534.30 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_flat-b1 | RABITQ | 200 | 0.7942 [0.7933, 0.7949] | 0.9641 [0.9637, 0.9645] | 0.9982 [0.9982, 0.9982] | 39.2 | 2540.22 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b2-n4096 | RABITQ | 212 | 0.7908 [0.7887, 0.7918] | 0.9535 [0.9527, 0.9547] | 0.9954 [0.9951, 0.9959] | 122.6 | 1262.47 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitqlib_ivf-b1-n4096 | RABITQ | 221.36 | 0.8365 [0.8341, 0.8385] | 0.9817 [0.9808, 0.9825] | 0.9997 [0.9997, 0.9998] | 218.2 | 7.23 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-pca_rabitq_ivf-d768-b3-n4096 | RABITQ | 308 | 0.8681 [0.8659, 0.8711] | 0.9903 [0.9898, 0.9908] | 0.9987 [0.9985, 0.9988] | 126.3 | 1275.75 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_flat-b2 | RABITQ | 404 | 0.8938 [0.8928, 0.8946] | 0.9971 [0.9971, 0.9971] | 1.0000 [1.0000, 1.0000] | 71.5 | 2566.62 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_ivf-b2-n4096 | RABITQ | 404 | 0.9127 [0.9118, 0.9141] | 0.9989 [0.9987, 0.9992] | 1.0000 [1.0000, 1.0000] | 194.1 | 2516.07 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitqlib_ivf-b2-n4096 | RABITQ | 421.36 | 0.9169 [0.9158, 0.9188] | 0.9989 [0.9986, 0.9992] | 1.0000 [0.9999, 1.0000] | 220.0 | 7.35 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_flat-b3 | RABITQ | 596 | 0.9356 [0.9353, 0.9357] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 103.5 | 2595.55 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_ivf-b3-n4096 | RABITQ | 596 | 0.9503 [0.9484, 0.9514] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 226.3 | 2546.19 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitqlib_ivf-b3-n4096 | RABITQ | 613.36 | 0.9529 [0.9506, 0.9547] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 252.7 | 7.71 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_flat-b4 | RABITQ | 788 | 0.9636 [0.9633, 0.9638] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 105.7 | 2593.44 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_ivf-b4-n4096 | RABITQ | 788 | 0.9717 [0.9712, 0.9725] | 1.0000 [0.9999, 1.0000] | 1.0000 [1.0000, 1.0000] | 330.3 | 2979.86 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitqlib_ivf-b4-n4096 | RABITQ | 805.36 | 0.9733 [0.9714, 0.9751] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 261.6 | 7.10 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_flat-b5 | RABITQ | 980 | 0.9800 [0.9789, 0.9812] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 136.9 | 2603.45 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitq_ivf-b5-n4096 | RABITQ | 980 | 0.9853 [0.9848, 0.9856] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 383.7 | 3054.60 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-rabitqlib_ivf-b5-n4096 | RABITQ | 997.36 | 0.9862 [0.9857, 0.9868] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 240.5 | 7.32 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b3 | TQFIX | 148 | 0.8012 [0.8008, 0.8015] | 0.9654 [0.9642, 0.9662] | 0.9973 [0.9970, 0.9975] | 54.2 | 11.93 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d384-b4 | TQFIX | 196 | 0.8302 [0.8294, 0.8310] | 0.9782 [0.9778, 0.9790] | 0.9980 [0.9977, 0.9982] | 53.3 | 10.25 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b3 | TQFIX | 292 | 0.8931 [0.8904, 0.8965] | 0.9979 [0.9977, 0.9981] | 1.0000 [1.0000, 1.0000] | 59.2 | 20.80 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d768-b4 | TQFIX | 388 | 0.9306 [0.9289, 0.9326] | 0.9999 [0.9999, 0.9999] | 1.0000 [1.0000, 1.0000] | 73.6 | 22.69 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b2 | TQFIX | 388 | 0.8856 [0.8838, 0.8870] | 0.9959 [0.9957, 0.9960] | 1.0000 [0.9999, 1.0000] | 109.9 | 52.67 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b3 | TQFIX | 580 | 0.9282 [0.9259, 0.9300] | 0.9996 [0.9994, 0.9997] | 1.0000 [1.0000, 1.0000] | 122.2 | 44.34 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tqfix-d1536-b4 | TQFIX | 772 | 0.9575 [0.9560, 0.9591] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 125.7 | 40.83 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tq_ivf-d384-b3-n4096 | TQIVF | 148 | 0.8060 [0.8035, 0.8075] | 0.9665 [0.9653, 0.9678] | 0.9963 [0.9959, 0.9966] | 139.9 | 14.15 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tq_ivf-d384-b4-n4096 | TQIVF | 196 | 0.8328 [0.8314, 0.8339] | 0.9799 [0.9794, 0.9802] | 0.9978 [0.9977, 0.9978] | 141.4 | 12.97 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tq_ivf-d768-b3-n4096 | TQIVF | 292 | 0.8954 [0.8942, 0.8965] | 0.9965 [0.9953, 0.9971] | 1.0000 [0.9999, 1.0000] | 224.3 | 23.59 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tq_ivf-d768-b4-n4096 | TQIVF | 388 | 0.9348 [0.9331, 0.9357] | 0.9998 [0.9997, 1.0000] | 1.0000 [1.0000, 1.0000] | 228.5 | 22.59 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tq_ivf-d1536-b2-n4096 | TQIVF | 388 | 0.8871 [0.8848, 0.8887] | 0.9942 [0.9931, 0.9951] | 1.0000 [0.9999, 1.0000] | 441.3 | 48.28 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tq_ivf-d1536-b3-n4096 | TQIVF | 580 | 0.9238 [0.9200, 0.9262] | 0.9993 [0.9990, 0.9996] | 1.0000 [1.0000, 1.0000] | 434.8 | 45.25 |
| dbpedia-ada002-1m | dbpedia-ada002-1m-tq_ivf-d1536-b4-n4096 | TQIVF | 772 | 0.9617 [0.9604, 0.9640] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 432.1 | 45.04 |
| deep-image-96-angular | deep-image-96-angular-opq-m24 | OPQ | 24 | 0.3460 [0.3443, 0.3472] | 0.4930 [0.4904, 0.4952] | 0.6878 [0.6849, 0.6908] | 90.3 | 138.47 |
| deep-image-96-angular | deep-image-96-angular-opq-m32 | OPQ | 32 | 0.4742 [0.4722, 0.4755] | 0.6515 [0.6486, 0.6564] | 0.8342 [0.8322, 0.8364] | 230.3 | 118.47 |
| deep-image-96-angular | deep-image-96-angular-opq-m48 | OPQ | 48 | 0.6837 [0.6825, 0.6853] | 0.8722 [0.8707, 0.8739] | 0.9646 [0.9645, 0.9648] | 156.7 | 296.72 |
| deep-image-96-angular | deep-image-96-angular-pq-m24 | PQ | 24 | 0.3268 [0.3257, 0.3280] | 0.4652 [0.4645, 0.4658] | 0.6545 [0.6537, 0.6552] | 36.8 | 154.88 |
| deep-image-96-angular | deep-image-96-angular-pq-m32 | PQ | 32 | 0.4662 [0.4638, 0.4678] | 0.6387 [0.6377, 0.6399] | 0.8252 [0.8242, 0.8264] | 153.5 | 118.16 |
| deep-image-96-angular | deep-image-96-angular-pq-m48 | PQ | 48 | 0.6825 [0.6806, 0.6842] | 0.8715 [0.8703, 0.8722] | 0.9649 [0.9642, 0.9656] | 84.3 | 254.90 |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b1-n16384 | RABITQ | 20 | 0.4113 [0.4086, 0.4146] | 0.5791 [0.5768, 0.5811] | 0.7805 [0.7801, 0.7812] | 483.6 | 3383.73 |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b1 | RABITQ | 20 | 0.1781 [0.1777, 0.1786] | 0.2720 [0.2707, 0.2727] | 0.4333 [0.4331, 0.4335] | 3.5 | 4362.36 |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b1-n16384 | RABITQ | 32.94 | 0.4724 [0.4718, 0.4728] | 0.6553 [0.6527, 0.6584] | 0.8489 [0.8471, 0.8504] | 740.3 | 51.71 |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b2 | RABITQ | 44 | 0.4807 [0.4803, 0.4812] | 0.6675 [0.6673, 0.6676] | 0.8614 [0.8610, 0.8623] | 24.4 | 4312.85 |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b2-n16384 | RABITQ | 44 | 0.6708 [0.6700, 0.6723] | 0.8708 [0.8675, 0.8732] | 0.9785 [0.9772, 0.9794] | 393.9 | 3278.98 |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b3 | RABITQ | 56 | 0.6957 [0.6949, 0.6971] | 0.8929 [0.8925, 0.8931] | 0.9845 [0.9844, 0.9845] | 33.9 | 3317.70 |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b3-n16384 | RABITQ | 56 | 0.8251 [0.8230, 0.8264] | 0.9806 [0.9795, 0.9815] | 0.9996 [0.9995, 0.9997] | 500.3 | 3400.34 |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b2-n16384 | RABITQ | 56.94 | 0.7219 [0.7177, 0.7274] | 0.9167 [0.9156, 0.9187] | 0.9919 [0.9914, 0.9922] | 728.6 | 41.65 |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b4 | RABITQ | 68 | 0.8162 [0.8158, 0.8166] | 0.9772 [0.9761, 0.9781] | 0.9988 [0.9988, 0.9989] | 44.0 | 4218.94 |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b4-n16384 | RABITQ | 68 | 0.8908 [0.8901, 0.8915] | 0.9969 [0.9966, 0.9975] | 1.0000 [0.9999, 1.0000] | 412.4 | 3383.22 |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b3-n16384 | RABITQ | 72.94 | 0.8427 [0.8419, 0.8435] | 0.9870 [0.9861, 0.9879] | 0.9999 [0.9998, 1.0000] | 846.2 | 52.99 |
| deep-image-96-angular | deep-image-96-angular-rabitq_flat-b5 | RABITQ | 80 | 0.9053 [0.9039, 0.9065] | 0.9982 [0.9980, 0.9983] | 0.9999 [0.9999, 0.9999] | 62.3 | 4218.58 |
| deep-image-96-angular | deep-image-96-angular-rabitq_ivf-b5-n16384 | RABITQ | 80 | 0.9471 [0.9460, 0.9484] | 0.9999 [0.9999, 0.9999] | 1.0000 [0.9999, 1.0000] | 424.8 | 3395.42 |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b4-n16384 | RABITQ | 88.94 | 0.9122 [0.9105, 0.9133] | 0.9989 [0.9984, 0.9992] | 1.0000 [0.9999, 1.0000] | 934.0 | 28.11 |
| deep-image-96-angular | deep-image-96-angular-rabitqlib_ivf-b5-n16384 | RABITQ | 104.94 | 0.9523 [0.9517, 0.9526] | 0.9999 [0.9999, 1.0000] | 1.0000 [0.9999, 1.0000] | 773.6 | 46.08 |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b2 | TQFIX | 28 | 0.4932 [0.4921, 0.4940] | 0.6781 [0.6762, 0.6797] | 0.8634 [0.8626, 0.8639] | 24.3 | 95.14 |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b3 | TQFIX | 40 | 0.6850 [0.6819, 0.6875] | 0.8839 [0.8831, 0.8852] | 0.9823 [0.9819, 0.9830] | 38.0 | 124.00 |
| deep-image-96-angular | deep-image-96-angular-tq-d96-b4 | TQFIX | 52 | 0.8262 [0.8255, 0.8267] | 0.9793 [0.9783, 0.9801] | 0.9991 [0.9988, 0.9993] | 47.8 | 124.13 |
| deep-image-96-angular | deep-image-96-angular-tq_ivf-d96-b2-n16384 | TQIVF | 28 | 0.6805 [0.6780, 0.6836] | 0.8784 [0.8762, 0.8805] | 0.9798 [0.9791, 0.9805] | 706.8 | 60.74 |
| deep-image-96-angular | deep-image-96-angular-tq_ivf-d96-b3-n16384 | TQIVF | 40 | 0.7945 [0.7926, 0.7971] | 0.9661 [0.9656, 0.9672] | 0.9991 [0.9991, 0.9991] | 693.6 | 61.22 |
| deep-image-96-angular | deep-image-96-angular-tq_ivf-d96-b4-n16384 | TQIVF | 52 | 0.8925 [0.8909, 0.8941] | 0.9975 [0.9971, 0.9977] | 1.0000 [0.9999, 1.0000] | 696.3 | 60.46 |
| glove-100-angular | glove-100-angular-opq-m20 | OPQ | 20 | 0.4220 [0.4197, 0.4258] | 0.5724 [0.5698, 0.5752] | 0.7505 [0.7482, 0.7520] | 251.7 | 42.41 |
| glove-100-angular | glove-100-angular-opq-m25 | OPQ | 25 | 0.5181 [0.5155, 0.5208] | 0.6946 [0.6927, 0.6964] | 0.8654 [0.8618, 0.8677] | 131.8 | 52.77 |
| glove-100-angular | glove-100-angular-opq-m50 | OPQ | 50 | 0.8278 [0.8264, 0.8290] | 0.9774 [0.9768, 0.9787] | 0.9992 [0.9991, 0.9994] | 181.2 | 77.06 |
| glove-100-angular | glove-100-angular-pq-m20 | PQ | 20 | 0.4204 [0.4180, 0.4218] | 0.5732 [0.5716, 0.5741] | 0.7517 [0.7497, 0.7533] | 94.9 | 42.34 |
| glove-100-angular | glove-100-angular-pq-m25 | PQ | 25 | 0.5176 [0.5159, 0.5195] | 0.6929 [0.6920, 0.6935] | 0.8627 [0.8610, 0.8642] | 72.7 | 53.35 |
| glove-100-angular | glove-100-angular-pq-m50 | PQ | 50 | 0.8256 [0.8251, 0.8261] | 0.9748 [0.9736, 0.9755] | 0.9990 [0.9989, 0.9991] | 112.2 | 78.29 |
| glove-100-angular | glove-100-angular-rabitq_flat-b1 | RABITQ | 21 | 0.2751 [0.2742, 0.2759] | 0.3846 [0.3838, 0.3854] | 0.5366 [0.5364, 0.5370] | 1.2 | 1412.96 |
| glove-100-angular | glove-100-angular-rabitq_ivf-b1-n4096 | RABITQ | 21 | 0.3595 [0.3579, 0.3613] | 0.4921 [0.4904, 0.4941] | 0.6521 [0.6506, 0.6531] | 34.3 | 1415.64 |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b1-n4096 | RABITQ | 33.99 | 0.4193 [0.4170, 0.4221] | 0.5665 [0.5655, 0.5679] | 0.7298 [0.7285, 0.7314] | 73.8 | 17.18 |
| glove-100-angular | glove-100-angular-rabitq_ivf-b2-n4096 | RABITQ | 46 | 0.6318 [0.6297, 0.6344] | 0.8147 [0.8106, 0.8177] | 0.9378 [0.9370, 0.9393] | 40.8 | 1397.09 |
| glove-100-angular | glove-100-angular-rabitq_flat-b2 | RABITQ | 46 | 0.5575 [0.5572, 0.5578] | 0.7350 [0.7344, 0.7354] | 0.8939 [0.8929, 0.8947] | 8.0 | 1427.48 |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b2-n4096 | RABITQ | 57.99 | 0.6827 [0.6799, 0.6855] | 0.8657 [0.8640, 0.8672] | 0.9659 [0.9655, 0.9663] | 60.8 | 13.88 |
| glove-100-angular | glove-100-angular-rabitq_flat-b3 | RABITQ | 58 | 0.7555 [0.7553, 0.7558] | 0.9338 [0.9329, 0.9345] | 0.9939 [0.9936, 0.9940] | 14.0 | 1432.80 |
| glove-100-angular | glove-100-angular-rabitq_ivf-b3-n4096 | RABITQ | 58 | 0.8004 [0.7986, 0.8021] | 0.9594 [0.9589, 0.9602] | 0.9968 [0.9963, 0.9973] | 47.8 | 1406.46 |
| glove-100-angular | glove-100-angular-rabitq_ivf-b4-n4096 | RABITQ | 71 | 0.8756 [0.8743, 0.8766] | 0.9918 [0.9915, 0.9924] | 0.9996 [0.9995, 0.9998] | 65.5 | 1717.32 |
| glove-100-angular | glove-100-angular-rabitq_flat-b4 | RABITQ | 71 | 0.8461 [0.8458, 0.8464] | 0.9855 [0.9852, 0.9857] | 0.9994 [0.9994, 0.9995] | 14.6 | 1433.30 |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b3-n4096 | RABITQ | 73.99 | 0.8231 [0.8214, 0.8248] | 0.9724 [0.9712, 0.9731] | 0.9987 [0.9984, 0.9993] | 61.8 | 14.46 |
| glove-100-angular | glove-100-angular-rabitq_ivf-b5-n4096 | RABITQ | 83 | 0.9396 [0.9386, 0.9414] | 0.9995 [0.9993, 0.9997] | 0.9997 [0.9995, 0.9999] | 72.2 | 1736.12 |
| glove-100-angular | glove-100-angular-rabitq_flat-b5 | RABITQ | 83 | 0.9240 [0.9239, 0.9243] | 0.9992 [0.9992, 0.9992] | 0.9995 [0.9995, 0.9995] | 24.9 | 1769.17 |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b4-n4096 | RABITQ | 89.99 | 0.8987 [0.8974, 0.9004] | 0.9965 [0.9961, 0.9967] | 0.9998 [0.9997, 0.9999] | 59.6 | 14.71 |
| glove-100-angular | glove-100-angular-rabitqlib_ivf-b5-n4096 | RABITQ | 105.99 | 0.9450 [0.9445, 0.9453] | 0.9997 [0.9995, 0.9999] | 0.9998 [0.9997, 0.9999] | 60.5 | 13.55 |
| glove-100-angular | glove-100-angular-tq-d100-b2 | TQFIX | 29 | 0.5765 [0.5721, 0.5793] | 0.7554 [0.7537, 0.7568] | 0.9058 [0.9043, 0.9075] | 3.1 | 21.62 |
| glove-100-angular | glove-100-angular-tq-d100-b3 | TQFIX | 42 | 0.7353 [0.7331, 0.7368] | 0.9139 [0.9117, 0.9157] | 0.9877 [0.9873, 0.9883] | 4.0 | 21.79 |
| glove-100-angular | glove-100-angular-tq-d100-b4 | TQFIX | 54 | 0.8599 [0.8575, 0.8613] | 0.9896 [0.9890, 0.9905] | 0.9999 [0.9999, 0.9999] | 5.0 | 21.61 |
| glove-100-angular | glove-100-angular-tq_ivf-d100-b2-n4096 | TQIVF | 29 | 0.6520 [0.6518, 0.6523] | 0.8355 [0.8334, 0.8370] | 0.9523 [0.9515, 0.9533] | 55.4 | 29.43 |
| glove-100-angular | glove-100-angular-tq_ivf-d100-b3-n4096 | TQIVF | 42 | 0.7767 [0.7757, 0.7778] | 0.9476 [0.9468, 0.9487] | 0.9956 [0.9950, 0.9963] | 63.6 | 31.44 |
| glove-100-angular | glove-100-angular-tq_ivf-d100-b4-n4096 | TQIVF | 54 | 0.8839 [0.8834, 0.8850] | 0.9947 [0.9941, 0.9950] | 1.0000 [0.9999, 1.0000] | 62.0 | 30.07 |
| nytimes-256-angular | nytimes-256-angular-opq-m32 | OPQ | 32 | 0.6022 [0.5988, 0.6039] | 0.7479 [0.7449, 0.7513] | 0.8544 [0.8520, 0.8576] | 225.2 | 14.09 |
| nytimes-256-angular | nytimes-256-angular-opq-m64 | OPQ | 64 | 0.7639 [0.7627, 0.7665] | 0.9091 [0.9073, 0.9103] | 0.9667 [0.9659, 0.9677] | 344.7 | 28.75 |
| nytimes-256-angular | nytimes-256-angular-opq-m128 | OPQ | 128 | 0.9086 [0.9075, 0.9092] | 0.9821 [0.9816, 0.9826] | 0.9846 [0.9846, 0.9847] | 600.5 | 57.76 |
| nytimes-256-angular | nytimes-256-angular-pq-m32 | PQ | 32 | 0.6014 [0.5999, 0.6029] | 0.7462 [0.7448, 0.7487] | 0.8519 [0.8508, 0.8533] | 73.7 | 12.31 |
| nytimes-256-angular | nytimes-256-angular-pq-m64 | PQ | 64 | 0.7662 [0.7649, 0.7671] | 0.9110 [0.9094, 0.9123] | 0.9669 [0.9653, 0.9680] | 177.6 | 28.69 |
| nytimes-256-angular | nytimes-256-angular-pq-m128 | PQ | 128 | 0.9089 [0.9075, 0.9100] | 0.9819 [0.9818, 0.9819] | 0.9846 [0.9846, 0.9847] | 279.9 | 46.77 |
| nytimes-256-angular | nytimes-256-angular-rabitq_ivf-b1-n2048 | RABITQ | 40 | 0.6048 [0.5597, 0.6276] | 0.7323 [0.6630, 0.7671] | 0.8047 [0.7068, 0.8551] | 14.7 | 863.39 |
| nytimes-256-angular | nytimes-256-angular-rabitq_flat-b1 | RABITQ | 40 | 0.5837 [0.5832, 0.5843] | 0.7234 [0.7232, 0.7236] | 0.8284 [0.8284, 0.8285] | 0.9 | 1072.70 |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b1-n2048 | RABITQ | 52.9 | 0.6239 [0.6221, 0.6272] | 0.7635 [0.7622, 0.7641] | 0.8521 [0.8510, 0.8543] | 24.4 | 4.34 |
| nytimes-256-angular | nytimes-256-angular-rabitq_flat-b2 | RABITQ | 84 | 0.7633 [0.7629, 0.7636] | 0.9022 [0.9018, 0.9027] | 0.9603 [0.9601, 0.9605] | 5.6 | 885.46 |
| nytimes-256-angular | nytimes-256-angular-rabitq_ivf-b2-n2048 | RABITQ | 84 | 0.7890 [0.7884, 0.7901] | 0.9183 [0.9160, 0.9204] | 0.9656 [0.9652, 0.9658] | 26.4 | 1045.83 |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b2-n2048 | RABITQ | 92.9 | 0.7926 [0.7915, 0.7945] | 0.9219 [0.9217, 0.9220] | 0.9677 [0.9671, 0.9680] | 27.4 | 5.60 |
| nytimes-256-angular | nytimes-256-angular-rabitq_flat-b3 | RABITQ | 116 | 0.8608 [0.8602, 0.8618] | 0.9661 [0.9658, 0.9662] | 0.9831 [0.9831, 0.9831] | 10.0 | 893.06 |
| nytimes-256-angular | nytimes-256-angular-rabitq_ivf-b3-n2048 | RABITQ | 116 | 0.8771 [0.8764, 0.8775] | 0.9708 [0.9703, 0.9713] | 0.9832 [0.9830, 0.9835] | 24.4 | 860.75 |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b3-n2048 | RABITQ | 124.9 | 0.8765 [0.8750, 0.8778] | 0.9707 [0.9704, 0.9709] | 0.9835 [0.9834, 0.9835] | 28.6 | 5.58 |
| nytimes-256-angular | nytimes-256-angular-rabitq_flat-b4 | RABITQ | 148 | 0.9087 [0.9082, 0.9094] | 0.9805 [0.9803, 0.9809] | 0.9845 [0.9845, 0.9845] | 10.4 | 893.62 |
| nytimes-256-angular | nytimes-256-angular-rabitq_ivf-b4-n2048 | RABITQ | 148 | 0.9211 [0.9197, 0.9220] | 0.9818 [0.9813, 0.9820] | 0.9844 [0.9842, 0.9845] | 31.1 | 1057.75 |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b4-n2048 | RABITQ | 156.9 | 0.9233 [0.9219, 0.9246] | 0.9822 [0.9819, 0.9826] | 0.9844 [0.9843, 0.9845] | 35.1 | 8.25 |
| nytimes-256-angular | nytimes-256-angular-rabitq_ivf-b5-n2048 | RABITQ | 180 | 0.9507 [0.9500, 0.9514] | 0.9842 [0.9841, 0.9843] | 0.9844 [0.9843, 0.9845] | 36.0 | 1066.69 |
| nytimes-256-angular | nytimes-256-angular-rabitq_flat-b5 | RABITQ | 180 | 0.9451 [0.9449, 0.9453] | 0.9843 [0.9841, 0.9844] | 0.9845 [0.9845, 0.9845] | 17.4 | 1122.51 |
| nytimes-256-angular | nytimes-256-angular-rabitqlib_ivf-b5-n2048 | RABITQ | 188.9 | 0.9496 [0.9487, 0.9511] | 0.9841 [0.9839, 0.9843] | 0.9844 [0.9843, 0.9844] | 28.1 | 6.04 |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b2 | TQFIX | 68 | 0.7682 [0.7660, 0.7698] | 0.9071 [0.9049, 0.9107] | 0.9618 [0.9601, 0.9629] | 2.9 | 14.40 |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b3 | TQFIX | 100 | 0.8489 [0.8465, 0.8505] | 0.9605 [0.9591, 0.9613] | 0.9819 [0.9815, 0.9822] | 3.9 | 16.59 |
| nytimes-256-angular | nytimes-256-angular-tq-d256-b4 | TQFIX | 132 | 0.9146 [0.9137, 0.9159] | 0.9819 [0.9811, 0.9824] | 0.9846 [0.9840, 0.9849] | 4.2 | 14.67 |
| nytimes-256-angular | nytimes-256-angular-tq_ivf-d256-b2-n2048 | TQIVF | 68 | 0.7926 [0.7918, 0.7943] | 0.9247 [0.9240, 0.9257] | 0.9692 [0.9689, 0.9698] | 25.6 | 15.56 |
| nytimes-256-angular | nytimes-256-angular-tq_ivf-d256-b3-n2048 | TQIVF | 100 | 0.8657 [0.8640, 0.8683] | 0.9684 [0.9669, 0.9697] | 0.9833 [0.9831, 0.9834] | 26.2 | 15.21 |
| nytimes-256-angular | nytimes-256-angular-tq_ivf-d256-b4-n2048 | TQIVF | 132 | 0.9216 [0.9198, 0.9242] | 0.9825 [0.9820, 0.9829] | 0.9847 [0.9844, 0.9851] | 27.0 | 15.41 |
| wiki1024-10m | wiki1024-10m-opq-m64 | OPQ | 64 | 0.6739 [0.6701, 0.6762] | 0.8442 [0.8402, 0.8473] | 0.9476 [0.9464, 0.9483] | 1286.7 | 194.44 |
| wiki1024-10m | wiki1024-10m-opq-m128 | OPQ | 128 | 0.8197 [0.8190, 0.8210] | 0.9648 [0.9631, 0.9662] | 0.9974 [0.9968, 0.9979] | 1425.0 | 225.88 |
| wiki1024-10m | wiki1024-10m-opq-m256 | OPQ | 256 | 0.8993 [0.8980, 0.9011] | 0.9967 [0.9964, 0.9970] | 1.0000 [1.0000, 1.0000] | 1945.7 | 468.57 |
| wiki1024-10m | wiki1024-10m-opq-m512 | OPQ | 512 | 0.9485 [0.9467, 0.9500] | 0.9999 [0.9999, 1.0000] | 1.0000 [1.0000, 1.0000] | 2029.4 | 1191.97 |
| wiki1024-10m | wiki1024-10m-pq-m64 | PQ | 64 | 0.6526 [0.6499, 0.6545] | 0.8225 [0.8213, 0.8248] | 0.9347 [0.9335, 0.9363] | 783.9 | 234.80 |
| wiki1024-10m | wiki1024-10m-pq-m256 | PQ | 256 | 0.8827 [0.8815, 0.8838] | 0.9920 [0.9917, 0.9925] | 0.9998 [0.9997, 0.9999] | 467.0 | 472.41 |
| wiki1024-10m | wiki1024-10m-pq-m512 | PQ | 512 | 0.9491 [0.9478, 0.9506] | 0.9999 [0.9999, 1.0000] | 1.0000 [1.0000, 1.0000] | 675.6 | 1198.09 |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d256-b1-n16384 | RABITQ | 40 | 0.6189 [0.6181, 0.6196] | 0.7832 [0.7827, 0.7842] | 0.8985 [0.8975, 0.8998] | 1064.9 | 4268.59 |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d512-b1-n16384 | RABITQ | 72 | 0.7294 [0.7273, 0.7311] | 0.8872 [0.8854, 0.8889] | 0.9663 [0.9656, 0.9677] | 2669.3 | 11595.60 |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d256-b2-n16384 | RABITQ | 84 | 0.7242 [0.7225, 0.7257] | 0.8885 [0.8853, 0.8908] | 0.9663 [0.9658, 0.9671] | 1445.3 | 5054.11 |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d256-b3-n16384 | RABITQ | 116 | 0.7601 [0.7583, 0.7623] | 0.9177 [0.9162, 0.9185] | 0.9790 [0.9780, 0.9795] | 1345.6 | 4974.35 |
| wiki1024-10m | wiki1024-10m-rabitq_ivf-b1-n16384 | RABITQ | 136 | 0.8132 [0.8115, 0.8159] | 0.9596 [0.9594, 0.9598] | 0.9952 [0.9952, 0.9953] | 2455.4 | 17303.18 |
| wiki1024-10m | wiki1024-10m-rabitq_flat-b1 | RABITQ | 136 | 0.7706 [0.7701, 0.7712] | 0.9266 [0.9261, 0.9273] | 0.9869 [0.9867, 0.9871] | 1505.1 | 17272.34 |
| wiki1024-10m | wiki1024-10m-rabitqlib_ivf-b1-n16384 | RABITQ | 147.57 | 0.8265 [0.8232, 0.8284] | 0.9692 [0.9682, 0.9699] | 0.9975 [0.9974, 0.9976] | 4232.6 | 62.52 |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d512-b2-n16384 | RABITQ | 148 | 0.8381 [0.8366, 0.8393] | 0.9722 [0.9709, 0.9738] | 0.9974 [0.9973, 0.9976] | 1417.8 | 8745.04 |
| wiki1024-10m | wiki1024-10m-pca_rabitq_ivf-d512-b3-n16384 | RABITQ | 212 | 0.9008 [0.8982, 0.9022] | 0.9949 [0.9945, 0.9952] | 0.9995 [0.9993, 0.9997] | 1687.8 | 8520.07 |
| wiki1024-10m | wiki1024-10m-rabitq_flat-b2 | RABITQ | 276 | 0.8706 [0.8703, 0.8711] | 0.9886 [0.9883, 0.9890] | 0.9998 [0.9997, 0.9998] | 1842.7 | 17271.10 |
| wiki1024-10m | wiki1024-10m-rabitq_ivf-b2-n16384 | RABITQ | 276 | 0.8988 [0.8970, 0.8999] | 0.9947 [0.9945, 0.9949] | 1.0000 [1.0000, 1.0000] | 2522.5 | 17155.29 |
| wiki1024-10m | wiki1024-10m-rabitqlib_ivf-b2-n16384 | RABITQ | 283.57 | 0.9113 [0.9102, 0.9121] | 0.9976 [0.9972, 0.9978] | 1.0000 [1.0000, 1.0000] | 3142.9 | 52.11 |
| wiki1024-10m | wiki1024-10m-rabitq_flat-b3 | RABITQ | 404 | 0.9292 [0.9284, 0.9302] | 0.9995 [0.9994, 0.9995] | 1.0000 [1.0000, 1.0000] | 567.8 | 17204.74 |
| wiki1024-10m | wiki1024-10m-rabitq_ivf-b3-n16384 | RABITQ | 404 | 0.9417 [0.9406, 0.9426] | 0.9997 [0.9996, 0.9998] | 1.0000 [1.0000, 1.0000] | 2633.2 | 16965.16 |
| wiki1024-10m | wiki1024-10m-rabitqlib_ivf-b3-n16384 | RABITQ | 411.57 | 0.9510 [0.9505, 0.9518] | 0.9999 [0.9999, 0.9999] | 1.0000 [1.0000, 1.0000] | 3256.8 | 44.84 |
| wiki1024-10m | wiki1024-10m-rabitq_ivf-b4-n16384 | RABITQ | 532 | 0.9642 [0.9636, 0.9650] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 2795.4 | 17311.00 |
| wiki1024-10m | wiki1024-10m-rabitq_flat-b4 | RABITQ | 532 | 0.9547 [0.9534, 0.9561] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 571.2 | 17423.59 |
| wiki1024-10m | wiki1024-10m-rabitq_flat-b5 | RABITQ | 660 | 0.9733 [0.9729, 0.9738] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 897.7 | 17715.96 |
| wiki1024-10m | wiki1024-10m-rabitq_ivf-b5-n16384 | RABITQ | 660 | 0.9798 [0.9795, 0.9801] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 3027.6 | 17402.09 |
| wiki1024-10m | wiki1024-10m-tq-d256-b3 | TQFIX | 100 | 0.7617 [0.7579, 0.7648] | 0.9163 [0.9143, 0.9192] | 0.9793 [0.9785, 0.9797] | 304.4 | 121.27 |
| wiki1024-10m | wiki1024-10m-tq-d256-b4 | TQFIX | 132 | 0.7869 [0.7857, 0.7877] | 0.9378 [0.9367, 0.9389] | 0.9851 [0.9845, 0.9856] | 340.3 | 127.68 |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b3 | TQFIX | 196 | 0.9001 [0.8967, 0.9042] | 0.9957 [0.9955, 0.9959] | 1.0000 [0.9999, 1.0000] | 260.6 | 119.85 |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b2 | TQFIX | 260 | 0.8863 [0.8838, 0.8877] | 0.9928 [0.9920, 0.9936] | 0.9999 [0.9998, 1.0000] | 1460.2 | 212.28 |
| wiki1024-10m | wiki1024-10m-tqfix-d512-b4 | TQFIX | 260 | 0.9382 [0.9372, 0.9388] | 0.9999 [0.9998, 1.0000] | 1.0000 [1.0000, 1.0000] | 441.9 | 115.20 |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b3 | TQFIX | 388 | 0.9304 [0.9298, 0.9314] | 0.9993 [0.9992, 0.9995] | 1.0000 [1.0000, 1.0000] | 909.3 | 222.96 |
| wiki1024-10m | wiki1024-10m-tqfix-d1024-b4 | TQFIX | 516 | 0.9622 [0.9610, 0.9631] | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 728.9 | 226.31 |
| wiki1024-10m | wiki1024-10m-tq_ivf-d256-b3-n16384 | TQIVF | 100 | 0.7642 [0.7624, 0.7657] | 0.9175 [0.9165, 0.9181] | 0.9771 [0.9760, 0.9778] | 1470.5 | 62.39 |
| wiki1024-10m | wiki1024-10m-tq_ivf-d256-b4-n16384 | TQIVF | 132 | 0.7874 [0.7871, 0.7878] | 0.9366 [0.9362, 0.9370] | 0.9850 [0.9843, 0.9855] | 1475.0 | 59.14 |
| wiki1024-10m | wiki1024-10m-tq_ivf-d512-b3-n16384 | TQIVF | 196 | 0.9063 [0.9055, 0.9078] | 0.9953 [0.9952, 0.9954] | 0.9999 [0.9998, 1.0000] | 2023.3 | 107.89 |
| wiki1024-10m | wiki1024-10m-tq_ivf-d1024-b2-n16384 | TQIVF | 260 | 0.8893 [0.8874, 0.8921] | 0.9915 [0.9911, 0.9920] | 0.9997 [0.9995, 0.9999] | 3431.2 | 208.03 |
| wiki1024-10m | wiki1024-10m-tq_ivf-d512-b4-n16384 | TQIVF | 260 | 0.9429 [0.9427, 0.9432] | 0.9999 [0.9998, 0.9999] | 1.0000 [1.0000, 1.0000] | 2071.4 | 114.81 |
| wiki1024-10m | wiki1024-10m-tq_ivf-d1024-b3-n16384 | TQIVF | 388 | 0.9282 [0.9270, 0.9300] | 0.9986 [0.9984, 0.9988] | 1.0000 [1.0000, 1.0000] | 3472.5 | 235.72 |
| wiki1024-10m | wiki1024-10m-tq_ivf-d1024-b4-n16384 | TQIVF | 516 | 0.9663 [0.9649, 0.9688] | 1.0000 [0.9999, 1.0000] | 1.0000 [1.0000, 1.0000] | 3585.6 | 229.24 |

## Incomplete configs (excluded)

- dbpedia-3large-1536-1m dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b1-n4096: seeds [0]
- dbpedia-3large-1536-1m dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b3-n4096: seeds [0]
- wiki1024-10m wiki1024-10m-pq-m128: seeds [0, 2]
- wiki1024-10m wiki1024-10m-rabitqlib_ivf-b4-n16384: seeds [0]
- wiki1024-10m wiki1024-10m-rabitqlib_ivf-b5-n16384: seeds [0]
