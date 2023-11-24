from typing import List

class CompressedFile:
    def __init__(self, data: bytes, extra_bits: int, queue: List['Node']):
        self.data = data
        self.extra_bits = extra_bits
        self.queue = queue
        self.name = ""

    def bits_trimmed(self) -> List[bool]:
        byte_as_bits = self._bytes_to_bits(self.data)
        return byte_as_bits[:len(byte_as_bits) - self.extra_bits]

    @staticmethod
    def _bytes_to_bits(data: bytes) -> List[bool]:
        return [bool((data_byte >> bit) & 1) for data_byte in data for bit in range(8)]

