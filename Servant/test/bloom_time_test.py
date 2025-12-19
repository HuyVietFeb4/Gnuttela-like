import sys
sys.path.append("../")
from src.data_processing.data_processing import data_processing_util 
from src.application.bloom import BloomFilter, KM_BloomFilter
import bloom_test_util


bloom_test_util.test_time_init_bloom_filters('dict.csv', BloomFilter, 10000)
bloom_test_util.test_time_init_bloom_filters('dict.csv', KM_BloomFilter, 10000)