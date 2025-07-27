import os
from PIL import Image

def check_images_for_corruption(directory):
    """
    Checks all image files in a given directory and its subdirectories for corruption.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory not found at {directory}")
        return

    print(f"--- Checking for corrupted images in {directory} ---")
    corrupted_count = 0
    total_count = 0

    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Check for common image extensions
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                continue

            total_count += 1
            try:
                # Attempt to open and verify the image
                with Image.open(file_path) as img:
                    img.verify()
            except Exception as e:
                print(f"Found corrupted file: {file_path}")
                corrupted_count += 1

    print(f"\n--- Check complete: {corrupted_count} corrupted files found out of {total_count} ---")
    if corrupted_count > 0:
        print("Please remove the corrupted images before training.")
    else:
        print("All images checked are valid.")

if __name__ == "__main__":
    # --- PATH TO YOUR NOT SOIL FOLDERS ---
    # Path to your Train/Not Soil folder
    check_images_for_corruption('../Dataset/Train/Not Soil')
    # Path to your Test/Not Soil folder
    check_images_for_corruption('../Dataset/test/Not Soil')