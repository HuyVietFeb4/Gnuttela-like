import sys
sys.path.append("../")
from src.application.bloom import BloomFilter, KM_BloomFilter, Compact_BloomFilter, Compact_Refined_BloomFilter, Yes_No_BloomFilter
import bloom_test_util


standard_bf = BloomFilter(10000, 0.01)
km_bf = KM_BloomFilter(10000, 0.01)
cm_bf = Compact_BloomFilter(10000, 0.01)
cm_bf_refined = Compact_Refined_BloomFilter(10000, 0.01)
yn_bf = Yes_No_BloomFilter(10000, 0.01)

bloom_test_util.test_accuracy_bloom_filters('dict.csv', BloomFilter, standard_bf)
bloom_test_util.test_accuracy_bloom_filters('dict.csv', KM_BloomFilter, km_bf)
bloom_test_util.test_accuracy_bloom_filters('dict.csv', Compact_BloomFilter, cm_bf)
bloom_test_util.test_accuracy_bloom_filters('dict.csv', Compact_Refined_BloomFilter, cm_bf_refined)
bloom_test_util.test_accuracy_bloom_filters('dict.csv', Yes_No_BloomFilter, yn_bf)