import os
from PIL import Image


# 1. RUN-LENGTH ENCODING

def rle_encode(data):
    if not data:
        return []

    encoded = []
    prev_item = data[0]
    count = 1
    for item in data[1:]:
        if item == prev_item:
            count += 1
        else:
            encoded.append((prev_item, count))
            prev_item = item
            count = 1
    # Append the last run
    encoded.append((prev_item, count))
    return encoded


# 2. RUN-LENGTH DECODING

def rle_decode(encoded_data):
    decoded = []
    for value, count in encoded_data:
        # Extend the list by adding the 'value' 'count' times
        decoded.extend([value] * count)
    return decoded


# MAIN FUNCTION

def process_image_with_rle(input_file):
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
        print("1. Compressing image data with RLE...")
        compressed_data = rle_encode(original_data)
        print("   Compression complete.")
        # printing the first 5 compressed runs to see the result
        print(f"   Example of compressed data: {compressed_data[:5]}")
        print("-" * 30)

        #Decoding the compressed data
        print("2. Decompressing the data...")
        decompressed_data = rle_decode(compressed_data)
        print("   Decompression complete.")
        print("-" * 30)

        #Verify the decompression
        if original_data == decompressed_data:
            print("Verification successful: Decompressed data matches original data.")
        else:
            print("Verification failed: Data mismatch.")
        print("-" * 30)

        #Saving the decompressed image
        print("3. Saving the decompressed image...")
        output_file = "rle_decompressed_output.bmp"

        #Creating a new image from the decompressed data
        output_img = Image.new("L", (width, height))
        output_img.putdata(decompressed_data)

        #Saving the new image
        output_img.save(output_file)

        print(f"Success! Decompressed image saved as '{output_file}'")
        print(f"Output file size (bytes): {os.path.getsize(output_file)}")


        # This is the size of the raw data in memory
        original_size_bytes = len(original_data)
        # This is the estimated size of YOUR compressed data in memory
        compressed_size_bytes = len(compressed_data) * 2
        # This ratio accurately reflects how well YOUR RLE algorithm performed
        compression_ratio = (compressed_size_bytes / original_size_bytes) * 100
        print(f"Compression ratio: {compression_ratio:.2f} %")

    except FileNotFoundError:
        print(f"ERROR: The file '{input_file}' was not found.")
        print("Please make sure you have uploaded the file to your Colab session.")
    except Exception as e:
        print(f"An error occurred: {e}")


input_filename = "forest_3.bmp"
process_image_with_rle(input_filename)