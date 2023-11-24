import unittest

from compression.RunLengthEncodingCompressor import RunLengthEncodingCompressor


class RLETests(unittest.TestCase):

    def test_compression(self):
        content = "dabdccadadad"
        file = content.encode('utf-8')

        rle = RunLengthEncodingCompressor()

        compressed_file = rle.compress(file)

        self.assertTrue(file > compressed_file)

    def test_decompression(self):
        content = "The quick Brown Fox jumps over the Lazy Dog"
        file = content.encode('utf-8')

        rle = RunLengthEncodingCompressor()

        compressed = rle.compress(file)
        decoded_data = (rle.decompress(compressed))

        decompressed_content = decoded_data.decode('utf-8')

        self.assertEqual(content, decompressed_content)
