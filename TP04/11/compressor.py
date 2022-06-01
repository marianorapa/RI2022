from ast import unaryop
from math import log
from math import ceil
from bitarray import bitarray
 
class Compressor:

    def encode_variable_byte(self, numbers):
        output_ints = []
        for number in numbers:
            encoded = []
            while True:
                encoded = [number & 0b01111111] + encoded
                if number < 128:
                    break
                else:
                    number = int(number / 128)
            encoded[-1] += 128
            for enc in encoded:
                output_ints.append(enc)
        
        return output_ints, 0
 
    def decode_variable_byte(self, encoded_numbers, right_padding = 0):
        decoded = []
        result = 0
        for byte in encoded_numbers:
            if byte < 128:
                result += (byte * 128)
            else:
                result += byte - 128
                decoded.append(result)
                result = 0
        return decoded

    def __unary__(self, number):
        unary = ""
        for i in range(0, number - 1):
            unary += "1"
        unary += "0"
        return bitarray(unary)

    def int_to_bits(self, number):
        return bin(number)[2:]

    def encode_elias_gamma(self, numbers):
        
        compressed_value_bits = bitarray()

        for number in numbers:
            if number <= 0:
                raise Exception("Can't encode number <= 0")

            binary_rep_raw = self.int_to_bits(number)
            binary_rep = bitarray(binary_rep_raw)

            binary_rep_len = ceil(log(number + 1, 2))
            
            unary = self.__unary__(binary_rep_len)

            binary_rep.remove(1)
                  
            compressed_value_bits += unary + binary_rep
               
        bits_length = len(compressed_value_bits)
        padding_bits = 8 - (bits_length % 8) if (bits_length % 8) > 0 else 0              
        compressed_value_bits += bitarray(padding_bits * "0")
        
        compressed_values_int = []
        for i in range(0, len(compressed_value_bits), 8):
            compressed_values_int.append(self.bits_to_int(compressed_value_bits[i:i+8]))
        return compressed_values_int, padding_bits
        #return compressed_value_bits

    def bits_to_int(self, bits):
        result = 0
        for bit in bits:
            result = (result << 1) | bit
        return result

    def decode_elias_gamma(self, encoded_as_ints, right_padding):
        decoded_values = []
        if len(encoded_as_ints) == 0:
            raise Exception("Codification should at least be '0'")

        encoded_bitarray = bitarray()
        for each_int in encoded_as_ints:
            binary_int = self.int_to_bits(each_int)            
            padding_bits = 8 - (len(binary_int) % 8) if (len(binary_int) % 8) > 0 else 0                        
            encoded_bitarray += bitarray("0" * padding_bits) + bitarray(binary_int)

        i = 0
        
        while i < len(encoded_bitarray) - right_padding:# and encoded_bitarray[i]:
            unary = 0
            while encoded_bitarray[i]:
                unary += encoded_bitarray[i]
                i += 1
                if i >= len(encoded_bitarray) - right_padding:
                    break        
            
            unary += 1            
            binary = bitarray("1") + encoded_bitarray[i+1:i+unary]    
            i = i+unary
            decoded_values.append(self.bits_to_int(binary))
            #if i < len(encoded_bitarray) - 1:
            #    i +=1
            #if not encoded_bitarray[i]:
            #    break
        
        return decoded_values

    def compress(self, values, compression_method):
        if compression_method == 1:
            return self.encode_elias_gamma(values)
        else:
            return self.encode_variable_byte(values)

    def decompress(self, compressed_value, compression_method, right_padding):
        if compression_method == 1:
            return self.decode_elias_gamma(compressed_value, right_padding)
        else:
            return self.decode_variable_byte(compressed_value, right_padding)

if __name__ == '__main__':
    compressor = Compressor()    
    numbers = [1, 1, 5, 1, 100, 53, 88, 16, 32, 1, 10000, 2, 1]
    encoded, padding_bits = compressor.encode_elias_gamma(numbers)
    #print(encoded)
    decoded = compressor.decode_elias_gamma(encoded, padding_bits)    
    print(decoded)