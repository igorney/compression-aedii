import unittest

import bitarray

from compression.HuffmanCodingCompressor import HuffmanCoding


class HuffmanTests(unittest.TestCase):

    def test_compression(self):
        content = "dabdccadadad"
        file = content.encode('utf-8')

        huffman = HuffmanCoding()

        compressed_bytes, extra_bits, priority_queue = huffman.compress(file)
        bits = bitarray.bitarray()
        bits.frombytes(bytes(compressed_bytes))
        trimmed_bits = bits[:-extra_bits]

        self.assertEqual(trimmed_bits.to01(), "0111000101101110110110")


    def test_decompression(self):
        content = "The quick Brown Fox jumps over the Lazy Dog"
        file = content.encode('utf-8')

        huffman = HuffmanCoding()

        compressed = huffman.compress(file)
        decompressed = huffman.decompress(compressed)

        decompressed_content = decompressed.decode('utf-8')

        self.assertFalse(content == decompressed_content)
