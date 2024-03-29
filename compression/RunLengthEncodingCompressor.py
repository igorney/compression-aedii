import datetime


class RunLengthEncodingCompressor:
    MAX_PACKAGE_SIZE = 255

    def __init__(self):
        self.position = 0
        self.file_length = 0

    @property
    def percentage(self):
        return (self.position / self.file_length * 100) if self.file_length > 0 else 0

    def compress(self, file):
        start = datetime.datetime.now().microsecond
        self.file_length = len(file)
        new_file = []

        run_value = file[0]
        run_count = 1

        for self.position in range(1, len(file)):
            current_byte = file[self.position]
            if run_value == current_byte:
                if run_count != self.MAX_PACKAGE_SIZE:
                    run_count += 1
                else:
                    new_file.extend([run_count, run_value])
                    run_count = 1
            else:
                new_file.extend([run_count, run_value])
                run_value = current_byte
                run_count = 1

        new_file.extend([run_count, run_value])
        
        compressed_file = bytes(new_file)
        end = datetime.datetime.now().microsecond
        print(f"Time and size to compression with Run-Length Encoding (RLE): {abs(end - start)} ms")
        print(f"Size of file compressed: {len(compressed_file)} bytes, Size of file original: {len(file)} bytes")
        return compressed_file

    def decompress(self, compressed_file_data):
        start = datetime.datetime.now().microsecond
        NEXT_COUNT_OFFSET = 2
        RUN_VALUE_OFFSET = 1
        compressed_file_data = bytes(compressed_file_data)
        file = []

        for position in range(0, len(compressed_file_data), NEXT_COUNT_OFFSET):
            run_count = compressed_file_data[position]
            run_value = compressed_file_data[position + RUN_VALUE_OFFSET]

            file.extend([run_value] * run_count)
        end = datetime.datetime.now().microsecond
        print(f"Time to decompression with Run-Length Encoding (RLE): {abs(end - start)} ms")
        print(f"Size of file compressed: {len(compressed_file_data)} bytes, Size of file decompressed: {len(file)} bytes")
        return bytes(file)
