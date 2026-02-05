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
    heap = []
    for k, v in freq.items():  # k = symbol, v = frequency
        node = HuffmanNode(k, v)  # Create a node for this symbol
        heap.append(node)

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


def process_color_image_with_huffman(input_file):
    try:
        # 1. Load image
        img = Image.open(input_file).convert("RGB")
        width, height = img.size
        print(f"Successfully opened '{input_file}'")
        print(f"Image Dimensions: {width}x{height}")
        print("-" * 40)

        format=input_file.split(".")

        # 2. Split Channels
        r_band, g_band, b_band = img.split()
        r_data = list(r_band.getdata())
        g_data = list(g_band.getdata())
        b_data = list(b_band.getdata())

        # 3. Compress Channels
        print("Compressing R, G, B channels with Huffman...")
        r_bits, r_tree = huffman_encode(r_data)
        g_bits, g_tree = huffman_encode(g_data)
        b_bits, b_tree = huffman_encode(b_data)
        print("Compression complete.")
        print("-" * 40)

        # --- SIZE CALCULATIONS ---
        # Original size: Total pixels
        original_size_bytes = len(r_data) + len(g_data) + len(b_data)

        # Compressed size: Total bits / 8
        total_bits = len(r_bits) + len(g_bits) + len(b_bits)
        data_size_bytes = total_bits / 8
        
        # Tree Overhead: We must store the 3 trees to decode later
        tree_overhead = len(pickle.dumps(r_tree)) + len(pickle.dumps(g_tree)) + len(pickle.dumps(b_tree))
        
        total_compressed_bytes = data_size_bytes + tree_overhead
        
        ratio = (total_compressed_bytes / original_size_bytes) * 100
        # -------------------------

        print("COMPRESSION STATISTICS (HUFFMAN):")
        print(f"Original Size:     {original_size_bytes:,} bytes")
        print(f"Compressed Data:   {data_size_bytes:,.0f} bytes")
        print(f"Tree Overhead:     {tree_overhead:,.0f} bytes")
        print(f"Total Compressed:  {total_compressed_bytes:,.0f} bytes")
        print(f"Compression Ratio: {ratio:.2f} %")
        print("-" * 40)

        # 4. Decompress and Save
        print("Decompressing and saving...")
        r_dec = huffman_decode(r_bits, r_tree)
        g_dec = huffman_decode(g_bits, g_tree)
        b_dec = huffman_decode(b_bits, b_tree)

        r_out = Image.new("L", (width, height))
        r_out.putdata(r_dec)
        
        g_out = Image.new("L", (width, height))
        g_out.putdata(g_dec)
        
        b_out = Image.new("L", (width, height))
        b_out.putdata(b_dec)

        final_img = Image.merge("RGB", (r_out, g_out, b_out))
        output_file = "huffman_color_output."+format[1]
        final_img.save(output_file)
        print(f"Saved reconstructed image as '{output_file}'")

    except Exception as e:
        print(f"Error: {e}")


input_filename = "lion.jpg"
process_color_image_with_huffman(input_filename)