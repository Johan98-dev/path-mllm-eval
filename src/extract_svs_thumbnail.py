# -*- coding: utf-8 -*-
"""
Extrae la miniatura (thumbnail) embebida en un archivo Aperio SVS de TCGA en el GDC
usando HTTP Range requests sin descargar toda la lámina gigapíxel.
"""

import io
import struct
import urllib.request
from PIL import Image

class HTTPRangeReader:
    def __init__(self, url):
        self.url = url
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-10"})
        with urllib.request.urlopen(req) as resp:
            content_range = resp.headers.get("Content-Range", "")
            if "/" in content_range:
                self.size = int(content_range.split("/")[1])
            else:
                self.size = int(resp.headers.get("Content-Length", 0))
        self.pos = 0

    def read_at(self, offset, length):
        if length <= 0 or offset >= self.size:
            return b""
        end = min(self.size - 1, offset + length - 1)
        req = urllib.request.Request(
            self.url,
            headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={offset}-{end}"}
        )
        with urllib.request.urlopen(req) as resp:
            return resp.read()

def extract_thumbnail_from_gdc(file_id: str):
    url = f"https://api.gdc.cancer.gov/data/{file_id}"
    reader = HTTPRangeReader(url)
    print(f"Lámina SVS en GDC ({file_id}): Tamaño total = {reader.size / (1024**2):.1f} MB")

    # 1. Leer header de TIFF (8 bytes)
    header = reader.read_at(0, 8)
    byte_order = "<" if header[:2] == b"II" else ">"
    magic = struct.unpack(f"{byte_order}H", header[2:4])[0]
    if magic != 42:
        print(f"Formato no es TIFF estándar (magic={magic})")
        return None

    first_ifd_offset = struct.unpack(f"{byte_order}I", header[4:8])[0]

    # 2. Recorrer IFDs buscando el thumbnail o macro
    current_ifd_offset = first_ifd_offset
    ifd_index = 0

    while current_ifd_offset != 0 and ifd_index < 6:
        ifd_data = reader.read_at(current_ifd_offset, 2)
        num_entries = struct.unpack(f"{byte_order}H", ifd_data[:2])[0]
        
        entries_data = reader.read_at(current_ifd_offset + 2, num_entries * 12 + 4)
        tags = {}
        for i in range(num_entries):
            entry = entries_data[i*12 : (i+1)*12]
            tag_id, tag_type, count, val_or_offset = struct.unpack(f"{byte_order}HHI I", entry)
            tags[tag_id] = (tag_type, count, val_or_offset)

        next_ifd_offset = struct.unpack(f"{byte_order}I", entries_data[num_entries*12 : num_entries*12 + 4])[0]
        
        width = tags.get(256, (None, None, 0))[2]
        height = tags.get(257, (None, None, 0))[2]
        compression = tags.get(259, (None, None, 0))[2]
        
        desc = ""
        if 270 in tags:
            d_type, d_count, d_offset = tags[270]
            if d_count > 4:
                desc_bytes = reader.read_at(d_offset, min(d_count, 200))
            else:
                desc_bytes = struct.pack(f"{byte_order}I", d_offset)[:d_count]
            desc = desc_bytes.decode("ascii", errors="ignore").splitlines()[0] if desc_bytes else ""

        print(f"IFD #{ifd_index}: {width}x{height} px, Compresión={compression}, Desc='{desc[:50]}'")

        # En Aperio SVS, IFD1 suele ser el thumbnail (dimensiones reducidas)
        # Si tiene StripOffsets (273) y StripByteCounts (279) o JPEGTables (347)
        if 0 < width <= 2500 and 0 < height <= 2500 and 273 in tags and 279 in tags:
            _, s_count, s_offset = tags[273]
            _, b_count, b_offset = tags[279]
            
            # Leer lista completa de offsets y byte counts
            if s_count == 1:
                offsets = [s_offset]
            else:
                raw_offs = reader.read_at(s_offset, s_count * 4)
                offsets = list(struct.unpack(f"{byte_order}{s_count}I", raw_offs))
                
            if b_count == 1:
                byte_counts = [b_offset]
            else:
                raw_counts = reader.read_at(b_offset, b_count * 4)
                byte_counts = list(struct.unpack(f"{byte_order}{b_count}I", raw_counts))
                
            print(f"-> IFD #{ifd_index} tiene {s_count} tiras/strips. Bytes totales = {sum(byte_counts)}")
            
            # Si es un solo strip o si las tiras son contiguas
            min_off = min(offsets)
            max_off = max([o + bc for o, bc in zip(offsets, byte_counts)])
            total_bytes = reader.read_at(min_off, max_off - min_off)
            
            try:
                # Aperio guarda un JPEG completo en el thumbnail
                pil_img = Image.open(io.BytesIO(total_bytes))
                pil_img.load()
                print(f"[OK] Miniatura decodificada exitosamente: {pil_img.size}, {pil_img.format}")
                return pil_img
            except Exception as e:
                print(f"Error decodificando imagen contigua: {e}")
                # Intentar concatenar tiras individuales
                strip_data = b"".join([reader.read_at(o, bc) for o, bc in zip(offsets, byte_counts)])
                try:
                    pil_img = Image.open(io.BytesIO(strip_data))
                    pil_img.load()
                    print(f"[OK] Miniatura decodificada uniendo tiras: {pil_img.size}, {pil_img.format}")
                    return pil_img
                except Exception as e2:
                    print(f"Error decodificando tiras concatenadas: {e2}")

        current_ifd_offset = next_ifd_offset
        ifd_index += 1

    return None

if __name__ == "__main__":
    test_file_id = "5f7da64f-aaaf-4a31-b144-83bd6656bd3f"
    img = extract_thumbnail_from_gdc(test_file_id)
    if img:
        img.save("test_thumbnail.jpg")
        print("[EXITO] Guardado en test_thumbnail.jpg")
