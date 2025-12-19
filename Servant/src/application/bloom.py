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

    def _get_hashes(self, filename):
        """
            Original Bloom filter hashing:
            Generate k independent hash values using different hash functions or seeds.
        """
        encoded = filename.encode('utf-8')

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
    def _get_hashes(self, filename):
        """
        Generates k hash values using Double Hashing (Kirsch-Mitzenmacher).
        We generate two large hashes and combine them to create k positions.
        """
        encoded = filename.encode('utf-8')

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

class Yes_No_BloomFilter(BloomFilter):
    def __init__(self, capacity, error_rate=0.01, no_capacity=None, no_error_rate=0.01):
        """
        :param capacity: Expected number of filenames for yes-filter
        :param error_rate: Desired false positive probability for yes-filter
        :param no_capacity: Expected number of false positives to store in no-filter
        :param no_error_rate: Desired false positive probability for no-filter
        """
        super().__init__(capacity, error_rate)
        # Initialize the no-filter (smaller, separate Bloom filter)
        if no_capacity is None:
            no_capacity = int(capacity * 0.1)  # heuristic: 10% of yes capacity
        self.no_capacity = no_capacity
        self.no_error_rate = no_error_rate
        self.no_size = self._get_size(no_capacity, self.no_error_rate)
        self.no_hash_count = self._get_hash_count(self.no_size, self.no_capacity)
        self.no_filter = bitarray.bitarray(self.no_size)
        self.no_filter.setall(0)

    def _get_no_hashes(self, filename):
        """
            No filter hashing:
            Generate k independent hash values using different hash functions or seeds.
        """
        encoded = filename.encode('utf-8')

        for i in range(self.no_hash_count):
            h = int(hashlib.sha256(encoded + str(i).encode('utf-8')).hexdigest(), 16)
            yield h % self.no_size

    def add_false_positive(self, filename):
        """
        Add a known false positive to the no-filter.
        This prevents it from being incorrectly reported as present.
        """
        for position in self._get_no_hashes(filename):
            # Set the bit at 'position' to 1 using bitwise OR
            self.no_filter[position] = 1
    
    def is_no_available(self, filename):
        """
        Checks if a filename is recorded in the no-filter (i.e., known false positive).
        Returns True if the filename is PROBABLY recorded in the no-filter (all its hash bits set).
        Returns False if the filename is DEFINITELY not recorded in the no-filter (at least one hash bit is 0).
        """
        for position in self._get_no_hashes(filename):
            # Check if the bit at 'position' is 0
            if not (self.no_filter[position]):
                return False  
        return True  

    def is_available(self, filename):
        """
        Query the Yes-No Bloom Filter.
        Returns:
          - False if definitely not present
          - False if present in yes-filter but also flagged in no-filter (false positive)
          - True if probably present (yes-filter positive, no-filter negative)
        """
        # Step 1: check yes-filter
        if not super().is_available(filename):
            return False  # definitely not present

        # Step 2: check no-filter
        if self.is_no_available(filename):
            return False  # known false positive

        return True  # probably present