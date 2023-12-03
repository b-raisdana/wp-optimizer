import glob
import os
from datetime import datetime
from typing import Tuple, Union, List

import pandas as pd
from PIL import Image

from helper import log

temp_file_path = 'tmp'
total_number_of_files = 0
processed_files = 0


def tmp_file_path(file_name: str) -> str:
    file_name = file_name.replace('/', '_')
    file_name = file_name.replace('\\\\', '_')
    file_name = file_name.replace('\\', '_')
    return os.path.join(temp_file_path, f"{file_name}.{datetime.now().strftime('%y-%m-%d.%H-%M-%S.%f')}.tmp")


def compress_jpg_to_size(image: Image.Image, file_name: str, max_size_kb: float, size: float, quality: float = 85) \
        -> Image.Image:
    while size > max_size_kb and quality > 20:
        quality -= 5
        tmp_file_name = tmp_file_path(file_name)
        image.save(tmp_file_name, "JPEG", optimize=True, quality=quality)
        image.close()
        size = os.path.getsize(tmp_file_name) / 1024
        image = Image.open(tmp_file_name)
        # os.remove(tmp_file_name)
    return image


def optimize_image(image_path: str, original_size_kb: float, max_dim_px: int, max_size_kb: float) \
        -> Tuple[int, Union[Tuple[int, int], None]]:
    global processed_files, total_number_of_files
    try:
        with Image.open(image_path) as img:
            original_dim = img.size
            if img.size[0] > max_dim_px or img.size[1] > max_dim_px:
                img.thumbnail((max_dim_px, max_dim_px))
                new_aspect_ratio = img.size[1] / img.size[0]
                original_aspect_ratio = original_dim[1] / original_dim[0]
                assert abs(new_aspect_ratio - original_aspect_ratio) / original_aspect_ratio < 0.01
            if image_path.lower().endswith('.png') or image_path.lower().endswith('.gif'):
                try:
                    img.save(image_path, optimize=True, compression_level=9)
                except IOError as e:
                    log(f"Error in optimizing image:{image_path}")
                    raise e
            elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
                if original_size_kb > max_size_kb:
                    img = compress_jpg_to_size(img, image_path, max_size_kb, original_size_kb)
                    img.save(image_path)
            optimized_size = os.path.getsize(image_path) / 1024
            # assert optimized_size <= original_size_kb, f'optimized_size:{optimized_size}original_size_kb:{original_size_kb}>'
            log(f'{image_path}({int(original_size_kb)}KB[{original_dim[0]}x{original_dim[1]}]) >> '
                f'({int(optimized_size)}KB[{img.size[0]}x{img.size[1]}]) '
                f'({processed_files}/{total_number_of_files}={int(100 * processed_files / total_number_of_files)}% '
                f'in {int((datetime.now()-start_time).total_seconds())}s)',
                stack_trace=False)
            return int(optimized_size), img.size
    except Exception as e:
        log(f'Error in opening file{image_path}')
        raise e

def process_folder(folder_path, max_dim_px: int = 1800, max_size_kb: int = 800) -> List[list]:
    global total_number_of_files
    _log_entries = []
    t = glob.glob(f'{folder_path}/**/*', recursive=True)
    total_number_of_files = len(t)
    for image_path in glob.glob(f'{folder_path}/**/*', recursive=True):
        if image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            _log_entry = list(process_file(image_path, max_dim_px, max_size_kb))
            _log_entries.append(_log_entry)
    return _log_entries


def process_file(image_path, max_dim_px, max_size_kb):
    global processed_files
    original_size_kb = os.path.getsize(image_path) / 1024
    original_dimensions = Image.open(image_path).size
    processed_files += 1
    if original_size_kb > max_size_kb or max(original_dimensions) > max_dim_px:
        new_size, new_dimensions = optimize_image(image_path, original_size_kb, max_dim_px, max_size_kb)
        return (image_path, f'{original_dimensions[0]}x{original_dimensions[1]}',
                None, original_size_kb, new_size)
    else:
        log(f'{image_path}({int(original_size_kb)}KB) is small!', stack_trace=False)
        return (image_path, f'{original_dimensions[0]}x{original_dimensions[1]}',
                None, original_size_kb, None)


# Example usage
start_time = datetime.now()
_folder_path = 'uploads'  # Replace with your folder path
log_entries = process_folder(_folder_path)
log_df = pd.DataFrame(log_entries, columns=['Path', 'OriginalDim', 'OptimizedDim', 'OriginalSize', 'OptimizedSize'])
log_df.to_csv(f'log.{datetime.now().strftime("%y-%m-%d.%H-%M-%S.%f")}.log')
