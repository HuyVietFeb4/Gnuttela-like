import sys
sys.path.insert(0, '../../config')

import math
import hashlib
import bitarray
import random
# import peer_settings as config
# Standard Bloom filter

class BloomFilter:
    def __init__(self, capacity, error_rate=0.01):
        """
        :param capacity: Expected number of filenames (n)
        :param error_rate: Desired false positive probability (p)
        """
        self.capacity = capacity
        self.error_rate = error_rate

        # 1. Calculate optimal bit array size (m)
        self.size = self._get_size(capacity, error_rate)

        # 2. Calculate optimal number of hash functions (k)
        self.hash_count = self._get_hash_count(self.size, capacity)

        # 3. Initialize bit array (using a simple integer as a bitfield)
        self.bit_array = bitarray.bitarray(self.size)
        self.bit_array.setall(0)

    def _get_size(self, n, p):
        """Returns the size of bit array (m) using standard formula"""
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)

    def _get_hash_count(self, m, n):
        """Returns the number of hash functions (k) to be used"""
        k = (m / n) * math.log(2)
        return int(k)

    def _get_hashes(self, item):
        """
            Original Bloom filter hashing:
            Generate k independent hash values using different hash functions or seeds.
        """
        encoded = item.encode('utf-8')

        for i in range(self.hash_count):
            h = int(hashlib.sha256(encoded + str(i).encode('utf-8')).hexdigest(), 16)
            yield h % self.size


    def add(self, filename):
        """Adds a filename to the Bloom Filter"""
        for position in self._get_hashes(filename):
            # Set the bit at 'position' to 1 using bitwise OR
            self.bit_array[position] = 1

    def is_available(self, filename):
        """
        Checks if a filename is available.
        Returns True if DEFINITELY available.
        Returns False if PROBABLY taken.
        """
        for position in self._get_hashes(filename):
            # Check if the bit at 'position' is 0
            if not (self.bit_array[position]):
                return False  # If any bit is 0, it's definitely not in the set
        return True  # All bits were 1, so it's probably in the set
    
    def reset_bit_array(self):
        self.bit_array = bitarray.bitarray(self.size)
        self.bit_array.setall(0)

class KM_BloomFilter(BloomFilter):
    def _get_hashes(self, item):
        """
        Generates k hash values using Double Hashing (Kirsch-Mitzenmacher).
        We generate two large hashes and combine them to create k positions.
        """
        encoded = item.encode('utf-8')

        # Use MD5 and SHA1 to get two independent hash integers
        h1 = int(hashlib.md5(encoded).hexdigest(), 16)
        h2 = int(hashlib.sha1(encoded).hexdigest(), 16)

        for i in range(self.hash_count):
            # Calculate position: (h1 + i * h2) % size
            yield (h1 + i * h2) % self.size

class Compact_BloomFilter(BloomFilter):
    def to_compacted(self):
        """
        Convert standard bloom filter into CmBF array
        """
        block_size = self.size // self.hash_count
        cmBF = []
        for i in range(block_size):
            pattern = [self.bit_array[j*block_size + i] for j in range(self.hash_count)]
            ones = sum(pattern)

            if ones == 0:
                cmBF.append(0)
            elif ones == 1:
                cmBF.append(pattern.index(1))
            elif ones >= self.hash_count / 2:
                cmBF.append((1 << self.hash_count)-1)
            else:
                indices = [j for j, bit in enumerate(pattern) if bit == 1]
                cmBF.append(random.choice(indices))

        return cmBF
    
    def from_compacted(self, cmBF):
        """
        Reconstruct a Bloom filter bit array from a compacted Bloom filter (CmBF).
        """
        block_size = self.size // self.hash_count
        new_bits = bitarray.bitarray(self.size)
        new_bits.setall(0)

        for i, val in enumerate(cmBF):
            if val == 0:
                continue
            elif val == (1 << self.hash_count) - 1:
                for j in range(self.hash_count):
                    new_bits[j*block_size + i] = 1
            else:
                new_bits[val*block_size + i] = 1

        self.bit_array = new_bits

class Compact_Refined_BloomFilter(Compact_BloomFilter):
    def to_compacted(self):
        block_size = self.size // self.hash_count
        cmBF = []

        for i in range(block_size):
            # Collect the i-th bit across all blocks
            pattern = [self.bit_array[j*block_size + i] for j in range(self.hash_count)]
            val = int("".join(str(b) for b in pattern), 2)

            if val == (1 << self.hash_count) - 1:
                cmBF.append(val)  # special all-on
            else:
                cmBF.append(val)  # actual bit pattern value
        return cmBF

    def from_compacted(self, cmBF):
        block_size = self.size // self.hash_count
        new_bits = bitarray.bitarray(self.size)
        new_bits.setall(0)

        for i, val in enumerate(cmBF):
            bits = bin(val)[2:].zfill(self.hash_count)
            for j, bit in enumerate(bits):
                if bit == '1':
                    new_bits[j*block_size + i] = 1
        self.bit_array = new_bits

'''
In a P2P file sharing systems, the impact of false negative and false positive is as follow:
- False negative: meaning that the file exists in the system but is flagged as not exists. In this case the bandwidth is reserve
since there is no query to the peer that has the files.
- False positive: meaning that the file does not exists in the system but is flagged as exists. In this case reliability is provided
since it will guarantee to retrieve the file if it exists in the system. But the bandwidth will be wasted to the peer that flagged as
has the file but do not actually have it.

Categories that need to be considered to choose bloom filter:
- Memory: To send over the network and reserve the bandwidth
- False Positive and False Negative: FP < FN in term of bandwidth for the system and reverse for reliability
- Deletion: Need to have delete feature to delete elements. Could introduce false negative but can reduce false positive
- Frequency: There is no need to keep track of frequency of files in the system.
- Adaptability: Can grow or adapt dynamically ? Could need for the app
- Distance: How close is item to known set? (Cat is present, when query cot it will notify back that there are no cot but it close to some distance to cat) Interesting case to look into
- Function value: What value is associated with item? (Like dictionary in python) Maybe also needed
'''
'''
After implementing, the following categories will be used to choose the suitable bloom filter to the context:
- Memory
- Accuracy
- Time
- Context
'''