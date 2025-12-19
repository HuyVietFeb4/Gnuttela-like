import sys
sys.path.append("../")
from src.data_processing.data_processing import data_processing_util 
from src.application.bloom import BloomFilter, KM_BloomFilter, Compact_BloomFilter, Compact_Refined_BloomFilter
import bloom_test_util

standard_bf = BloomFilter(10000, 0.01)
km_bf = KM_BloomFilter(10000, 0.01)
cm_bf = Compact_BloomFilter(10000, 0.01)
cm_bf_refined = Compact_Refined_BloomFilter(10000, 0.01)

bloom_test_util.test_memory_bloom_filters(BloomFilter, standard_bf, data_processing_util.bloom_serializer)
bloom_test_util.test_memory_bloom_filters(KM_BloomFilter, km_bf, data_processing_util.bloom_serializer)
bloom_test_util.test_memory_bloom_filters(Compact_BloomFilter, cm_bf, data_processing_util.compact_bloom_serializer)
bloom_test_util.test_memory_bloom_filters(Compact_Refined_BloomFilter, cm_bf_refined, data_processing_util.compact_bloom_serializer)