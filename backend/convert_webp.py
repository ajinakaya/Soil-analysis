from PIL import Image
import os
import glob 

def convert_webp_to_jpg_in_dataset(dataset_root_dir, delete_original=True):
    """
    Scans through the dataset directory, converts all .webp files found
    to .jpg format, and optionally deletes the original .webp files.
    """
    print(f"\n--- Starting WEBP to JPG conversion in: {dataset_root_dir} ---")
    files_converted = 0

    absolute_dataset_path = os.path.abspath(dataset_root_dir)

    if not os.path.exists(absolute_dataset_path):
        print(f"Error: Dataset directory '{absolute_dataset_path}' not found. Please check your DATASET_DIR path.")
        return

    for root, _, files in os.walk(absolute_dataset_path):
        for filename in files:
            # Check if the file is a .webp file (case-insensitive)
            if filename.lower().endswith('.webp'):
                webp_path = os.path.join(root, filename)
                # Create the new filename with .jpg extension
                jpg_filename = os.path.splitext(filename)[0] + '.jpg'
                jpg_path = os.path.join(root, jpg_filename)

                print(f"  Converting {webp_path} to {jpg_path}...")
                try:
                    with Image.open(webp_path) as img:
                       
                        img.convert('RGB').save(jpg_path, "jpeg") 
                    files_converted += 1
                    if delete_original:
                        os.remove(webp_path) # Delete the original .webp file
                        print(f"  Deleted original .webp file: {webp_path}")
                except Exception as e:
                    print(f"    ERROR converting {webp_path}: {e}")

    print(f"\n--- Conversion complete. {files_converted} .webp files converted to .jpg ---")
    if files_converted == 0:
        print("No .webp files were found for conversion.")
    else:
        print("Original .webp files have been deleted. You now have .jpg versions.")


if __name__ == "__main__":
   
    DATASET_PATH_FOR_SCRIPT = '../Dataset/Train' 

    convert_webp_to_jpg_in_dataset(DATASET_PATH_FOR_SCRIPT, delete_original=True)

    print("\nPart 1 (WEBP Conversion) is complete.")
    print("Now proceed to Part 2 to address other problematic files, then rerun the debugger.")