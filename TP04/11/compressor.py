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
        
        return output_ints
    
    def decode_variable_byte(self, encoded_numbers):
        decoded = []
        for encoded in encoded_numbers:
            result = 0
            for byte in encoded:
                if byte < 128:
                    result += (byte * 128)
                else:
                    result += byte - 128
            decoded.append(result)
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
               
        total_length = binary_rep_len * 2 - 1
        padding_bits = 8 - (total_length % 8) if (total_length % 8) > 0 else 0              
        compressed_value_bits += bitarray(padding_bits * "0")
        
        compressed_values_int = []
        for i in range(0, len(compressed_value_bits), 8):
            compressed_values_int.append(self.bits_to_int(compressed_value_bits[i:i+8]))
        return compressed_values_int
        #return compressed_value_bits

    def bits_to_int(self, bits):
        result = 0
        for bit in bits:
            result = (result << 1) | bit
        return result

    def decode_elias_gamma(self, encoded_as_ints):
        decoded_values = []
        
        if len(encoded_as_ints) == 0:
            raise Exception("Codification should at least be '0'")

        encoded_bitarray = bitarray()
        for each_int in encoded_as_ints:
            binary_int = self.int_to_bits(each_int)
            padding_bits = 8 - (len(binary_int) % 8) if (len(binary_int) % 8) > 0 else 0            
            encoded_bitarray += bitarray("0" * padding_bits) + bitarray(binary_int)
            #encoded_bitarray += bitarray(binary_int)

        i = 0
        while i < len(encoded_bitarray) and encoded_bitarray[i]:
            unary = 0
            while encoded_bitarray[i]:
                unary += encoded_bitarray[i]
                i += 1        
            
            unary += 1
            binary = bitarray("1") + encoded_bitarray[i+1:i+unary]       
            i = i+unary
            decoded_values.append(self.bits_to_int(binary))
            #if i < len(encoded_bitarray) - 1:
            #    i +=1
        
        return decoded_values

    def compress(self, values, compression_method):
        if compression_method == 1:
            return self.encode_elias_gamma(values)
        else:
            return self.encode_variable_byte(values)

    def decompress(self, compressed_value, compression_method):
        if compression_method == 1:
            return self.decode_elias_gamma(compressed_value)
        else:
            return self.decode_variable_byte(compressed_value)

if __name__ == '__main__':
    compressor = Compressor()    
    numbers = [16, 33, 90, 1900]
    encoded = compressor.encode_elias_gamma(numbers)
    #print(encoded)
    decoded = compressor.decode_elias_gamma(encoded)    
    print(decoded)