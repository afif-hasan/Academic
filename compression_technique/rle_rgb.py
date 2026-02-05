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

def process_color_image_with_rle(input_file):
    try:
        # 1. Load image and convert to RGB
        img = Image.open(input_file).convert("RGB")
        width, height = img.size
        print(f"Opened '{input_file}' in RGB mode. Size: {width}x{height}")


        format=input_file.split(".")

        # 2. Split the image into Red, Green, and Blue channels
        r_band, g_band, b_band = img.split()
        


        # Get data for each channel
        r_data = list(r_band.get_flattened_data())
        g_data = list(g_band.get_flattened_data())
        b_data = list(b_band.get_flattened_data())

        
        # 3. Encode each channel separately
        print("Compressing R, G, B channels...")
        r_enc = rle_encode(r_data)
        g_enc = rle_encode(g_data)
        b_enc = rle_encode(b_data)
        
        # 4. Decode each channel separately
        print("Decompressing channels...")
        r_dec = rle_decode(r_enc)
        g_dec = rle_decode(g_enc)
        b_dec = rle_decode(b_enc)

        # 5. Reconstruct the image
        # Create 3 new grayscale images from the decompressed data
        r_out = Image.new("L", (width, height))
        r_out.putdata(r_dec)

        g_out = Image.new("L", (width, height))
        g_out.putdata(g_dec)

        b_out = Image.new("L", (width, height))
        b_out.putdata(b_dec)

        # Merge them back into one RGB image
        final_img = Image.merge("RGB", (r_out, g_out, b_out))

        output_file = "rle_color_output."+format[1]
        final_img.save(output_file)
        print(f"Success! Color image saved as '{output_file}'")

        
        
        # Calculate Ratios
        original_size = len(r_data) + len(g_data) + len(b_data)
        compressed_size = (len(r_enc) + len(g_enc) + len(b_enc)) * 2
        print(f"Original size: {original_size} bytes")
        print(f"Compressed Image: {compressed_size} bytes")
        print(f"Compression Ratio: {(compressed_size/original_size)*100:.2f}%")

    except Exception as e:
        print(f"Error: {e}")


input_filename = "blackbuck.bmp"
process_color_image_with_rle(input_filename)