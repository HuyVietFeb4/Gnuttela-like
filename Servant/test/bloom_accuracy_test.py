import sys
sys.path.append("../")
from src.application.bloom import BloomFilter, KM_BloomFilter
import bloom_test_util

bloom_test_util.test_accuracy_bloom_filters('dict.csv', BloomFilter, 10000)
bloom_test_util.test_accuracy_bloom_filters('dict.csv', KM_BloomFilter, 10000)