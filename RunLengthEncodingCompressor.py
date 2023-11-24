# A classe CompressedFile deve ser definida separadamente.

# Nessa tradução, a classe RunLengthEncodingCompressor herda a interface ICompressor e implementa os métodos compress e decompress. 
# Os métodos e propriedades são adaptados para a sintaxe Python, e as listas são usadas no lugar das List<byte> do CSharp. 
# A classe CompressedFile mencionada deve ser definida separadamente, 
# conforme sua implementação específica no contexto de compressão de dados.

class RunLengthEncodingCompressor:
    MAX_PACKAGE_SIZE = 255

    def __init__(self):
        self.position = 0
        self.file_length = 0

    @property
    def percentage(self):
        return (self.position / self.file_length * 100) if self.file_length > 0 else 0

    def compress(self, file):
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
        return compressed_file

    def decompress(self, compressed_file_data):
        NEXT_COUNT_OFFSET = 2
        RUN_VALUE_OFFSET = 1
        compressed_file_data = bytes(compressed_file_data)
        file = []

        for position in range(0, len(compressed_file_data), NEXT_COUNT_OFFSET):
            run_count = compressed_file_data[position]
            run_value = compressed_file_data[position + RUN_VALUE_OFFSET]

            file.extend([run_value] * run_count)

        return bytes(file)


