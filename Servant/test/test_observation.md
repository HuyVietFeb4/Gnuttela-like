# Sample test output
```bash
(env) PS D:\HCMUT\HK 251\Distributed Systems\Gnuttela-like\Servant\test> python .\bloom_accuracy_test.py
BloomFilter accuracy: 0.7834
False positives: 1822, rate=0.2166
False negatives: 0, rate=0.0000
--------------------------------------------------------
KM_BloomFilter accuracy: 0.7716
False positives: 1921, rate=0.2284
False negatives: 0, rate=0.0000
--------------------------------------------------------
Compact_BloomFilter accuracy: 0.5194
False positives: 4024, rate=0.4785
False negatives: 18, rate=0.0021
--------------------------------------------------------
Compact_Refined_BloomFilter accuracy: 0.7817
False positives: 1836, rate=0.2183
False negatives: 0, rate=0.0000
--------------------------------------------------------
Yes_No_BloomFilter accuracy: 0.7780
False positives: 1772, rate=0.2107
False negatives: 95, rate=0.0113
Yes_No_BloomFilter re-test accuracy: 0.9478
False positives: 0, rate=0.0000
False negatives: 439, rate=0.0522
--------------------------------------------------------
(env) PS D:\HCMUT\HK 251\Distributed Systems\Gnuttela-like\Servant\test> python .\bloom_memory_test.py
BloomFilter memory usage: {'B': 95906, 'KB': 93.658203125, 'MB': 0.09146308898925781, 'GB': 8.931942284107208e-05}
KM_BloomFilter memory usage: {'B': 95906, 'KB': 93.658203125, 'MB': 0.09146308898925781, 'GB': 8.931942284107208e-05}      
Compact_BloomFilter memory usage: {'B': 47974, 'KB': 46.849609375, 'MB': 0.04575157165527344, 'GB': 4.4679269194602966e-05}
Compact_Refined_BloomFilter memory usage: {'B': 47974, 'KB': 46.849609375, 'MB': 0.04575157165527344, 'GB': 4.4679269194602966e-05}
Yes_No_BloomFilter memory usage: {'B': 105551, 'KB': 103.0771484375, 'MB': 0.1006612777709961, 'GB': 9.830202907323837e-05}
(env) PS D:\HCMUT\HK 251\Distributed Systems\Gnuttela-like\Servant\test>
```
# General Observations

The evaluation was carried out on two main metrics: **memory usage** and **accuracy** (false positives and false negatives).

## Memory Usage
- **Compact_BloomFilter** and **Compact_Refined_BloomFilter** significantly reduce memory requirements, achieving about a **50% reduction** compared to the standard **BloomFilter** and **KM_BloomFilter**.
- **Yes_No_BloomFilter** consumes the most memory among all variants, though the increase is moderate and not excessively large.

## Accuracy
- **Yes_No_BloomFilter** delivers the highest accuracy by greatly reducing false positives, but it introduces some false negatives as a trade-off.
- **Compact_BloomFilter** performs the worst in terms of accuracy, showing higher error rates.
- **BloomFilter**, **KM_BloomFilter**, and **Compact_Refined_BloomFilter** achieve **moderate accuracy**, sitting between the extremes of Yes-No and Compact Bloom filters.