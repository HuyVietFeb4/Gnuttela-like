import sys
sys.path.append("../")
from Servant.src.data_processing.data_processing import data_processing_util 
from Servant.src.application.bloom import BloomFilter, KM_BloomFilter, Compact_BloomFilter, Compact_Refined_BloomFilter, Yes_No_BloomFilter
import re
import csv
import random
def create_keyword_list(filename: str):
    filename = filename.lower()
    filename = re.sub(r'[ .\-_]', ' ', filename)
    pattern = r'[a-z0-9._\-()&\[\]+=,]+'
    return re.findall(pattern, filename)

def init_bf(files, bloom_filter):
    '''
        Breaks down a filename into keywords and adds them to the Bloom filter.
    '''
    for file in files:
        keyword_list = create_keyword_list(file)
        for keyword in keyword_list:
            bloom_filter.add(keyword)

def convert_bytes(size_in_bytes):
    kb = size_in_bytes / 1024
    mb = size_in_bytes / (1024 ** 2)
    gb = size_in_bytes / (1024 ** 3)
    return {
        "B": size_in_bytes,
        "KB": kb,
        "MB": mb,
        "GB": gb
    } 

import csv, random

def init_train_and_test_words(file_name, train_percent=0.8):
    words = []
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            if row:
                words.append(row[0])

    random.shuffle(words)

    split_index = int(len(words) * train_percent)
    train_words = words[:split_index]
    not_in_train = words[split_index:]

    # all of the not_in_train
    test_from_not_train = not_in_train

    # 20% of train
    test_from_train = random.sample(train_words, int(len(words) * (1 - train_percent)))

    # Combine
    test_words = test_from_not_train + test_from_train
    random.shuffle(test_words)
    random.shuffle(train_words)

    return train_words, test_words

import random

def test_accuracy_bloom_filters(file_name, bloom_filter_class, bf_object, train_percent=0.8):
    train_words, test_words = init_train_and_test_words(file_name, train_percent)

    # Initialize a fresh Bloom filter each iteration

    for word in train_words:
        bf_object.add(word)

    if('Compact' in bloom_filter_class.__name__):
        cm_bf_payload = data_processing_util.compact_bloom_serializer(bf_object)
        bf_object.from_compacted((data_processing_util.compact_bloom_deserializer(cm_bf_payload))['cmBF'])

    train_set = set(train_words)  # faster membership check

    correct_answer = 0
    false_positives = 0
    false_negatives = 0

    for word in test_words:
        isAppear = word in train_set
        bloom_answer = bf_object.is_available(word)

        if bloom_answer == isAppear:
            correct_answer += 1
        else:
            if bloom_answer and not isAppear:
                false_positives += 1
                if(isinstance(bf_object, Yes_No_BloomFilter)):
                    bf_object.add_false_positive(word)
            elif not bloom_answer and isAppear:
                false_negatives += 1

    print(f"{bloom_filter_class.__name__} accuracy: {correct_answer/len(test_words):.4f}")
    print(f"False positives: {false_positives}, rate={false_positives/len(test_words):.4f}")
    print(f"False negatives: {false_negatives}, rate={false_negatives/len(test_words):.4f}")

    if(isinstance(bf_object, Yes_No_BloomFilter)):
        correct_answer = 0
        false_positives = 0
        false_negatives = 0
        for word in test_words:
            isAppear = word in train_set
            bloom_answer = bf_object.is_available(word)

            if bloom_answer == isAppear:
                correct_answer += 1
            else:
                if bloom_answer and not isAppear:
                    false_positives += 1
                elif not bloom_answer and isAppear:
                    false_negatives += 1

        print(f"{bloom_filter_class.__name__} re-test accuracy: {correct_answer/len(test_words):.4f}")
        print(f"False positives: {false_positives}, rate={false_positives/len(test_words):.4f}")
        print(f"False negatives: {false_negatives}, rate={false_negatives/len(test_words):.4f}")
        return correct_answer/len(test_words), false_positives/len(test_words), false_negatives/len(test_words)
    print("--------------------------------------------------------")
    return correct_answer/len(test_words), false_positives/len(test_words), false_negatives/len(test_words)

import time

def test_time_init_bloom_filters(file_name, bloom_filter_class, bf_object, train_percent=1):
    train_words, test_words = init_train_and_test_words(file_name, train_percent)

    # Measure initialization time
    start_time = time.perf_counter()
    for word in train_words:
        bf_object.add(word)
    end_time = time.perf_counter()

    init_duration = end_time - start_time
    print(f"{bloom_filter_class.__name__} init time: {init_duration:.6f} seconds")


def test_memory_bloom_filters(bloom_filter_class, bf_object, bloom_serializer):
    bf_transmit = bloom_serializer(bf_object)
    print(f"{bloom_filter_class.__name__} memory usage: {convert_bytes(len(bf_transmit))}")