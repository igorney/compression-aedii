import base64
import datetime
import heapq
from RunLengthEncodingCompressor import RunLengthEncodingCompressor

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None


def calculate_probabilities(data):
    frequency = {}
    for symbol in data:
        if symbol not in frequency:
            frequency[symbol] = 0
        frequency[symbol] += 1
    return frequency


def build_huffman_tree(frequency):
    heap = [[weight, [symbol, ""]] for symbol, weight in frequency.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[-1]), p))


def huffman_coding(data):
    start = datetime.datetime.now().microsecond

    frequency = calculate_probabilities(data)
    huffman_tree = build_huffman_tree(frequency)
    huffman_dict = {symbol: code for symbol, code in huffman_tree}
    print(huffman_dict)
    end = datetime.datetime.now().microsecond
    print(f"Time to compression with Huffman Encoding: {abs(end - start)} ms")
    return ''.join(huffman_dict[symbol] for symbol in data), huffman_dict


# TODO: Ajustar a função de decodificação para que ela funcione com o dicionário de Huffman
def huffman_decoding(encoded_data, huffman_table):
    start = datetime.datetime.now().microsecond
    decoded_data = ''
    temp = ''
    for bit in encoded_data:
        temp += bit
        print(temp)
        if temp in huffman_table:
            decoded_data += huffman_table[temp]
            print(decoded_data)
            temp = ''
    end = datetime.datetime.now().microsecond
    print(f"Time to decompression with Huffman Decoding: {abs(end - start)} ms")
    return decoded_data


def rle_encode(input_string):
    """
    Run-length encoding of a string.
    """
    start = datetime.datetime.now().microsecond
    count = 1
    prev = ""
    encoded_string = ""

    for character in input_string:
        if character != prev:
            if prev:
                encoded_string += str(count) + str(prev)  # Convert prev to string
            count = 1
            prev = character
        else:
            count += 1
    else:
        encoded_string += str(count) + str(prev)  # Convert prev to string

    end = datetime.datetime.now().microsecond
    print(f"Time to compression with Run-Length Encoding (RLE): {abs(end - start)} ms")

    return encoded_string


def rle_decode(input_string):
    """
    Run-length decoding of a string.
    """
    start = datetime.datetime.now().microsecond
    decoded_string = ""
    count = ""

    for character in input_string:
        if character.isdigit():
            count += character
        else:
            decoded_string += character * int(count)
            count = ""
    end = datetime.datetime.now().microsecond
    print(f"Time to decompression with Run-Length Decocoding (RLE): {abs(end - start)} ms")
    return decoded_string


if __name__ == '__main__':
    videoFile = open('./Peer1/video.mp4', 'rb')
    data = videoFile.read()
    rle = RunLengthEncodingCompressor()
    enconded_data = rle.compress(data)
    print(len(enconded_data))
    print(len(data))
    decoded_data = (rle.decompress(enconded_data))
    file = open("videoEnviado.mp4", "wb")
    file.write(decoded_data)
    print(len(decoded_data))
    print("SUCESSO = ", data == decoded_data)
    #enconded_data, huffman_dict = huffman_coding(data)
    # decoded_data = huffman_decoding(enconded_data, huffman_dict)