import heapq
from collections import Counter
from typing import List, Tuple


class Node:
    def __init__(self, value=None, priority=0, left=None, right=None):
        self.value = value
        self.priority = priority
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.priority < other.priority


def bytes_to_bits(bytes):
    bits = []
    for byte in bytes:
        bits.extend([(byte >> i) & 1 for i in range(8)])
    return bits


def bits_to_bytes(bits):
    List_bytes = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        List_bytes.append(sum([byte[i] * 2 ** (7 - i) for i in range(8)]))
    return bytearray(List_bytes)


def pad_bits(bits):
    while len(bits) % 8 != 0:
        bits.append(0)
    return bits


def build_huffman_tree(priority_queue):
    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        node = Node(None, left.priority + right.priority, left, right)
        heapq.heappush(priority_queue, node)
    return priority_queue[0]


class HuffmanCoding:
    def __init__(self):
        self.position = 0
        self.file_length = 0
        self.huffman_tree = None

    @property
    def percentage(self):
        return (self.position / self.file_length * 100) if self.file_length > 0 else 0

    def compress(self, file: bytes) -> Tuple[bytes, int, List[Node]]:
        self.position = 0
        frequency = Counter(file)
        priority_queue = [Node(value, priority) for value, priority in frequency.items()]
        heapq.heapify(priority_queue)

        huffman_tree = build_huffman_tree(priority_queue)
        self.huffman_tree = huffman_tree
        coding_dict = self.build_coding_dictionary(huffman_tree)

        bits = []
        for byte in file:
            bits.extend(coding_dict[byte])

        total_length = len(bits)
        padded_bits = pad_bits(bits)
        compressed_bytes = bits_to_bytes(padded_bits)
        extra_bits = len(padded_bits) - total_length

        return compressed_bytes, extra_bits, huffman_tree

    def decompress(self, compressed_file: Tuple[bytes, int, List[Node]]) -> bytes:
        compressed_bytes, extra_bits, huffman_tree = compressed_file
        bits = bytes_to_bits(compressed_bytes)[:-extra_bits]

        encoding_dict = self.build_encoding_dictionary(huffman_tree)

        decoded_bytes = []
        current_bits = []
        for bit in bits:
            current_bits.append(bit)
            if tuple(current_bits) in encoding_dict:
                decoded_bytes.append(encoding_dict[tuple(current_bits)])
                current_bits = []

        return bytes(decoded_bytes)

    def build_coding_dictionary(self, huffman_tree):
        coding_dict = {}
        self.build_coding_dict_helper(huffman_tree, coding_dict, [])
        return coding_dict

    def build_coding_dict_helper(self, node, coding_dict, current_code):
        if node is None:
            return
        if node.value is not None:
            coding_dict[node.value] = current_code
        self.build_coding_dict_helper(node.left, coding_dict, current_code + [0])
        self.build_coding_dict_helper(node.right, coding_dict, current_code + [1])

    def build_encoding_dictionary(self, huffman_tree):
        encoding_dict = {}
        self.build_encoding_dict_helper(huffman_tree, encoding_dict, [])
        return encoding_dict

    def build_encoding_dict_helper(self, node, encoding_dict, current_code):
        if node is None:
            return
        if node.value is not None:
            encoding_dict[tuple(current_code)] = node.value
        self.build_encoding_dict_helper(node.left, encoding_dict, current_code + [0])
        self.build_encoding_dict_helper(node.right, encoding_dict, current_code + [1])
