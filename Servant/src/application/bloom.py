import sys
sys.path.insert(0, '../../config')

import math
import hashlib

# import peer_settings as config

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
        self.bit_array = 0

        print(f"Bloom Filter Initialized: Size={self.size} bits, Hashes={self.hash_count}")

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

    def add(self, filename):
        """Adds a filename to the Bloom Filter"""
        for position in self._get_hashes(filename):
            # Set the bit at 'position' to 1 using bitwise OR
            self.bit_array |= (1 << position)

    def is_available(self, filename):
        """
        Checks if a filename is available.
        Returns True if DEFINITELY available.
        Returns False if PROBABLY taken.
        """
        for position in self._get_hashes(filename):
            # Check if the bit at 'position' is 0
            if not (self.bit_array & (1 << position)):
                return True  # If any bit is 0, it's definitely not in the set
        return False  # All bits were 1, so it's probably taken