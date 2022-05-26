
from ast import unaryop
from math import log
from math import ceil
from bitarray import bitarray
 
 
class Compressor:

    def encode_variable_byte(self, number):
        encoded = []
        while True:
            encoded = [number & 0b01111111] + encoded
            if number < 128:
                break
            else:
                number = int(number / 128)
        encoded[-1] += 128
        return encoded
    
    def decode_variable_byte(self, encoded):
        result = 0
        for byte in encoded:
            if byte < 128:
                result += (byte * 128)
            else:
                result += byte - 128
        return result


    def __unary__(self, number):
        unary = ""
        for i in range(0, number - 1):
            unary += "1"
        unary += "0"
        return bitarray(unary)

    def __int_to_bits__(self, number):
        return bin(number)[2:]

    def encode_elias_gamma(self, number):
        
        if number <= 0:
            raise Exception("Can't encode number <= 0")

        binary_rep_raw = self.__int_to_bits__(number)
        binary_rep = bitarray(binary_rep_raw)

        binary_rep_len = ceil(log(number + 1, 2))
        
        unary = self.__unary__(binary_rep_len)

        binary_rep.remove(1)

        total_length = binary_rep_len * 2 - 1
        
        padding_bits = 8 - (total_length % 8) if (total_length % 8) > 0 else 0         
        compressed_value_bits = unary + binary_rep + bitarray(padding_bits * "0")
        compressed_values_int = []
        for i in range(0, len(compressed_value_bits), 8):
            compressed_values_int.append(self.__bits_to_int__(compressed_value_bits[i:i+8]))
        return compressed_values_int

    def __bits_to_int__(self, bits):
        result = 0
        for bit in bits:
            result = (result << 1) | bit
        return result

    def decode_elias_gamma(self, encoded_as_ints):
        if len(encoded) == 0:
            raise Exception("Codification should at least be '0'")
                
        encoded_bitarray = bitarray()
        for each_int in encoded_as_ints:
            binary_int = self.__int_to_bits__(each_int)
            padding_bits = 8 - (len(binary_int) % 8) if (len(binary_int) % 8) > 0 else 0            
            encoded_bitarray += bitarray("0" * padding_bits) + bitarray(binary_int)
                
        i = 0
        unary = 0
        while encoded_bitarray[i]:
            unary += encoded_bitarray[i]
            i += 1        
        
        unary += 1

        binary = bitarray("1") + encoded_bitarray[i+1:i+unary]        
        result = self.__bits_to_int__(binary)
        return result

    def compress(self, value, compression_method):
        if compression_method == 1:
            return self.encode_elias_gamma(value)
        else:
            return self.encode_variable_byte(value)

    def decompress(self, compressed_value, compression_method):
        if compression_method == 1:
            return self.decode_elias_gamma(compressed_value)
        else:
            return self.decode_variable_byte(compressed_value)

if __name__ == '__main__':
    compressor = Compressor()    
    number = 10
    encoded = compressor.encode_elias_gamma(number)
    print(encoded)
    decoded = compressor.decode_elias_gamma(encoded)    
    print(decoded)