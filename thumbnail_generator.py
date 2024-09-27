from concurrent import futures
import argparse
import logging
import os
import sys
from PIL import Image, ImageOps, ImageEnhance
from tqdm import tqdm

def process_options():
    """The function sets up a basic logging configuration using the logging.basicConfig() function.
    It then creates an ArgumentParser object with a description and fromfile_prefix_chars.
    The parser adds two optional arguments: --debug and --verbose, which enable debug and verbose modes respectively.
    The parsed arguments are returned.
    If the --debug argument is provided, the logging level is set to DEBUG.
    If the --verbose argument is provided, the logging level is set to INFO."""
    
    logging.basicConfig(format='[%(levelname)s] %(message)s')

    parser = argparse.ArgumentParser(
        description="Thumbnail generator",
        fromfile_prefix_chars="@"
    )

    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('--v', '--verbose', action='store_true', help="Enable verbose mode")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.v:
        logging.getLogger().setLevel(logging.INFO)

    return args

def process_file(root, basename):
    """
    Process a single image file to create a thumbnail with a border.
    """
    try:
        image_path = os.path.join(root, basename)
        logging.debug(f"Processing file: {image_path}")
        
        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)  # Handle orientation based on EXIF data
            img.thumbnail((1024, 1024), Image.LANCZOS)  # Create a thumbnail with LANCZOS filter
            
            # Convert to RGB if not already in that mode
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Enhance image (optional)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)

            # Add a border
            border_size = 10
            img = ImageOps.expand(img, border=border_size, fill='black')
            
            thumbnail_path = os.path.join('thumbnails', basename)
            img.save(thumbnail_path, "JPEG", quality=95)  # Save thumbnail with high quality
            logging.info(f"Saved thumbnail: {thumbnail_path}")
    except Exception as e:
        logging.error(f"Error processing {basename}: {e}")

def progress_bar(files):
    """
    Creates a progress bar for the list of files being processed.
    """
    return tqdm(files, desc="Processing", total=len(files), dynamic_ncols=True)

def main():
    args = process_options()

    if not os.path.exists('thumbnails'):
        os.mkdir('thumbnails')

    executor = futures.ProcessPoolExecutor()

    for root, _, files in os.walk('images'):
        for basename in progress_bar(files):
            if not basename.endswith('.jpg'):
                continue
            executor.submit(process_file, root, basename)

    logging.info('Waiting for all threads to finish.')
    executor.shutdown(wait=True)
    logging.info('All threads finished.')

    return 0

if __name__ == "__main__":
    sys.exit(main())
