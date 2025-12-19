import json
import zlib
import bitarray
class data_processing_util:
    @staticmethod
    def read_file(path: str):
        with open(path, 'rb') as f:
            return f.read()
    @staticmethod
    def json_serializer(json_data) -> bytes:
        json_str = json.dumps(json_data) # From json to str
        json_bytes = json_str.encode("utf-8") # From str to bytes
        return json_bytes
    
    @staticmethod
    def bloom_serializer(bloom_filter) -> bytes:
        '''
        Serialize bloom filter
        input: bloom_filter object
        return: abitrary bytes
        '''
        bloom_state = {
            'capacity': bloom_filter.capacity,
            'error_rate': bloom_filter.error_rate,
            'bit_array': bloom_filter.bit_array.to01()
        }
        return json.dumps(bloom_state).encode('utf-8')
    @staticmethod
    def bloom_deserializer(bloom_payload):
        '''
            Deserialize the to return bloom filter state
            Return: 
                bloom_state = {
                    'capacity': bloom_filter.capacity,
                    'error_rate': bloom_filter.error_rate,
                    'bit_array': bloom_filter.bit_array
                }
        '''
        bloom_state = json.loads(bloom_payload.decode('utf-8'))
        bloom_state['bit_array'] = bitarray(bloom_state['bit_array'])
        return bloom_state
    
    @staticmethod
    def compact_bloom_serializer(cmBF) -> bytes:
        '''
        Serialize compact bloom filter
        input: Compact_BloomFilter object
        return: abitrary bytes
        '''
        compact_bloom_state = {
            'capacity': cmBF.capacity,
            'error_rate': cmBF.error_rate,
            'cmBF': cmBF.to_compacted()
        }
        return json.dumps(compact_bloom_state).encode('utf-8')
    @staticmethod
    def compact_bloom_deserializer(cmBF_payload):
        '''
        Deserialize compact bloom filter
        input: bytes
        Return: 
            compact_bloom_state = {
                'capacity': cmBF.capacity,
                'error_rate': cmBF.error_rate,
                'cmBF': list of cmBF
            }
        '''
        compact_bloom_state = json.loads(cmBF_payload.decode('utf-8'))
        return compact_bloom_state
    
    @staticmethod
    def yesno_bloom_serializer(ynBF) -> bytes:
        '''
        Serialize yes no bloom filter
        input: Yes_No_BloomFilter object
        return: abitrary bytes
        '''
        yesno_bloom_state = {
            'capacity': ynBF.capacity,
            'error_rate': ynBF.error_rate,
            'no_capacity': ynBF.no_capacity,
            'no_error_rate': ynBF.no_error_rate,
            'yesFilter': ynBF.bit_array.to01(),
            'noFilter': ynBF.no_filter.to01()
        }
        return json.dumps(yesno_bloom_state).encode('utf-8')
    @staticmethod
    def yesno_bloom_deserializer(ynBF_payload):
        '''
        Deserialize bloomfilter
        input: bytes
            Return: 
                yesno_bloom_state = {
                'capacity': ynBF.capacity,
                'error_rate': ynBF.error_rate,
                'no_capacity': ynBF.no_capacity,
                'no_error_rate': ynBF.no_error_rate,
                'yesFilter': ynBF.bit_array.to01(),
                'noFilter': ynBF.no_filter.to01()
            }
        '''
        yesno_bloom_state = json.loads(ynBF_payload.decode('utf-8'))
        yesno_bloom_state['bit_array'] = bitarray(yesno_bloom_state['bit_array'])
        yesno_bloom_state['no_filter'] = bitarray(yesno_bloom_state['no_filter'])
        return yesno_bloom_state

    @staticmethod
    def json_deserializer(json_bytes: bytes):
        json_str = json_bytes.decode() # From bytes to str
        json_data = json.loads(json_str) # From str to json
        return json_data

    @staticmethod
    def compressor(byte_stream: bytes) -> bytes:
        return zlib.compress(byte_stream)
    @staticmethod
    def decompressor(byte_stream):
        return zlib.decompress(byte_stream)
    
    
    
