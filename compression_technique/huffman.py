import os
from PIL import Image
import heapq
from collections import Counter
import pickle # Used to estimate the size of the tree for statistics

# 1. HUFFMAN NODE CLASS
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # This makes the nodes comparable
    def __lt__(self, other):
        return self.freq < other.freq

# 2. HUFFMAN ENCODING

def huffman_encode(data):

    # 1. Calculate frequency of each pixel value
    freq = Counter(data)

    # 2. Build the priority queue (min-heap)
    heap = [HuffmanNode(k, v) for k, v in freq.items()]
    heapq.heapify(heap)

    # 3. Build the Huffman Tree
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)

    tree_root = heap[0]

    # 4. Generate the codebook ({255: '01', 100: '1'})
    def generate_codes_recursive(node, prefix="", codebook={}):
        if node is not None:
            if node.char is not None:
                codebook[node.char] = prefix
            generate_codes_recursive(node.left, prefix + "0", codebook)
            generate_codes_recursive(node.right, prefix + "1", codebook)
        return codebook

    codebook = generate_codes_recursive(tree_root)

    # 5. Encode the data into a bitstring
    encoded_bits = "".join(codebook[byte] for byte in data)

    return encoded_bits, tree_root

# 3. HUFFMAN DECODING
def huffman_decode(encoded_bits, tree_root):
    """
    Decompresses a bitstring using the Huffman tree.
    """
    decoded_data = []
    current_node = tree_root

    # Handle the special case of an image with only one color
    if not current_node.left and not current_node.right:
        # The frequency is the number of pixels
        return [current_node.char] * current_node.freq

    for bit in encoded_bits:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right

        # If we reach a leaf node, we have found a character
        if current_node.char is not None:
            decoded_data.append(current_node.char)
            current_node = tree_root # Reset to the root for the next character

    return decoded_data

# 4. MAIN FUNCTION

def process_image_with_huffman(input_file):
    try:
        # Load image and convert to grayscale ("L" mode)
        img = Image.open(input_file).convert("L")
        width, height = img.size
        original_data = list(img.getdata())

        print(f"Successfully opened '{input_file}'")
        print(f"Image size: {width}x{height} pixels")
        print(f"Original file size (bytes): {os.path.getsize(input_file)}")
        print("-" * 30)

        # Encoding the image data
        print("1. Compressing image data with Huffman coding...")
        encoded_bits, huffman_tree = huffman_encode(original_data)
        print("   Compression complete.")
        print(f"   Example of encoded data (first 70 bits): {encoded_bits[:70]}...")
        print("-" * 30)

        # Calculate and display compression statistics
        original_size_bytes = len(original_data)

        # Compressed size = size of bitstring + size of the tree/codebook needed for decoding
        compressed_bits_size_bytes = len(encoded_bits) / 8
        tree_size_bytes = len(pickle.dumps(huffman_tree)) # Estimate tree size by serializing it
        total_compressed_size_bytes = compressed_bits_size_bytes + tree_size_bytes

        compression_ratio = (total_compressed_size_bytes / original_size_bytes) * 100

        print("2. Calculating Compression Statistics...")
        print(f"   Original data size:    {original_size_bytes:,.0f} bytes")
        print(f"   Compressed size (est.): {total_compressed_size_bytes:,.0f} bytes (bits: {compressed_bits_size_bytes:,.0f} + tree: {tree_size_bytes:,.0f})")
        print(f"   Compression Ratio:     {compression_ratio:.2f}%")
        print("-" * 30)

        # Decoding the compressed data
        print("3. Decompressing the data...")
        decompressed_data = huffman_decode(encoded_bits, huffman_tree)
        print("   Decompression complete.")
        print("-" * 30)

        # Verify the decompression
        if original_data == decompressed_data:
            print("4. Verification successful: Decompressed data matches original data.")
        else:
            print("4. Verification failed: Data mismatch.")
        print("-" * 30)

        # Saving the decompressed image
        print("5. Saving the decompressed image...")
        output_file = "huffman_decompressed_output.bmp"

        output_img = Image.new("L", (width, height))
        output_img.putdata(decompressed_data)
        output_img.save(output_file)

        print(f"   Success! Decompressed image saved as '{output_file}'")
        print(f"   Output file size (bytes): {os.path.getsize(output_file)}")

    except FileNotFoundError:
        print(f"ERROR: The file '{input_file}' was not found.")
        print("Please make sure you have uploaded the file to your Colab session.")
    except Exception as e:
        print(f"An error occurred: {e}")


input_filename = "blackbuck.bmp"
process_image_with_huffman(input_filename)