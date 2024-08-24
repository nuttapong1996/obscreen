import struct
import imghdr
import os


def get_png_size(file):
    file.seek(16)
    width, height = struct.unpack('>ii', file.read(8))
    return width, height


def get_jpeg_size(file):
    file.seek(0)
    size = 2
    ftype = 0
    while not 0xC0 <= ftype <= 0xCF:
        file.seek(size, 1)
        byte = file.read(1)
        while ord(byte) == 0xFF:
            byte = file.read(1)
        ftype = ord(byte)
        size = struct.unpack('>H', file.read(2))[0] - 2
    file.seek(1, 1)
    height, width = struct.unpack('>HH', file.read(4))
    return width, height


def get_gif_size(file):
    file.seek(6)
    width, height = struct.unpack('<HH', file.read(4))
    return width, height


def get_webp_size(file):
    file.seek(12)
    chunk_header = file.read(8)
    while chunk_header:
        chunk_size = struct.unpack('<I', chunk_header[4:])[0]
        if chunk_header[0:4] == b'VP8 ':
            vp8_header = file.read(10)
            width, height = struct.unpack('<HH', vp8_header[6:10])
            return width, height
        elif chunk_header[0:4] == b'VP8L':
            vp8l_header = file.read(5)
            b1, b2, b3, b4 = struct.unpack('<BBBB', vp8l_header[1:])
            width = (b1 | ((b2 & 0x3F) << 8)) + 1
            height = ((b2 >> 6) | (b3 << 2) | ((b4 & 0x0F) << 10)) + 1
            return width, height
        elif chunk_header[0:4] == b'VP8X':
            vp8x_header = file.read(10)
            width, height = struct.unpack('<HH', vp8x_header[4:8])
            width = (width + 1) & 0xFFFFFF
            height = (height + 1) & 0xFFFFFF
            return width, height
        else:
            file.seek(chunk_size, 1)
        chunk_header = file.read(8)
    raise ValueError("Not a valid WebP file")


def get_bmp_size(file):
    file.seek(18)
    width, height = struct.unpack('<ii', file.read(8))
    return width, height


def get_tiff_size(file):
    file.seek(0)
    byte_order = file.read(2)
    if byte_order == b'II':
        endian = '<'
    elif byte_order == b'MM':
        endian = '>'
    else:
        raise ValueError("Not a valid TIFF file")

    file.seek(4)
    offset = struct.unpack(endian + 'I', file.read(4))[0]
    file.seek(offset)

    while True:
        num_tags = struct.unpack(endian + 'H', file.read(2))[0]
        for _ in range(num_tags):
            tag = file.read(12)
            if struct.unpack(endian + 'H', tag[:2])[0] == 256:
                width = struct.unpack(endian + 'I', tag[8:])[0]
            elif struct.unpack(endian + 'H', tag[:2])[0] == 257:
                height = struct.unpack(endian + 'I', tag[8:])[0]
        next_ifd_offset = struct.unpack(endian + 'I', file.read(4))[0]
        if next_ifd_offset == 0:
            break
        file.seek(next_ifd_offset)
    return width, height


def get_ico_size(file):
    file.seek(6)
    num_images = struct.unpack('<H', file.read(2))[0]
    largest_size = (0, 0)
    for _ in range(num_images):
        width, height = struct.unpack('<BB', file.read(2))
        width = width if width != 0 else 256
        height = height if height != 0 else 256
        if width * height > largest_size[0] * largest_size[1]:
            largest_size = (width, height)
        file.seek(14, 1)  # Skip over the rest of the directory entry
    return largest_size


def get_picture_metadata(image_path):
    # Determine the image type using imghdr and file extension as a fallback
    img_type = imghdr.what(image_path)
    if not img_type:
        _, ext = os.path.splitext(image_path)
        img_type = ext.lower().replace('.', '')

    with open(image_path, 'rb') as file:
        if img_type == 'png':
            return get_png_size(file)
        elif img_type == 'jpeg' or img_type == 'jpg':
            return get_jpeg_size(file)
        elif img_type == 'gif':
            return get_gif_size(file)
        elif img_type == 'webp':
            return get_webp_size(file)
        elif img_type == 'bmp':
            return get_bmp_size(file)
        elif img_type == 'tiff' or img_type == 'tif':
            return get_tiff_size(file)
        elif img_type == 'ico':
            return get_ico_size(file)
        else:
            raise ValueError("Unsupported image format or corrupted file")
