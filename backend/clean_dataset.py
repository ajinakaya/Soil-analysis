import os
from PIL import Image 
import shutil 

def clean_dataset(dataset_root_dir, quarantine_dir_name="quarantine_invalid_files"):
    """
    Scans through the dataset directory, identifies non-image or corrupted files,
    and moves them to a quarantine directory.

    Args:
        dataset_root_dir (str): The path to the root of your dataset 
                                (e.g., '../Dataset/Train' from the 'backend' folder).
        quarantine_dir_name (str): The name of the directory where invalid files will be moved.
    """

    # List of allowed image file extensions
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'} 

    full_quarantine_path = os.path.join(os.path.dirname(os.path.abspath(dataset_root_dir)), quarantine_dir_name)

    if not os.path.exists(full_quarantine_path):
        os.makedirs(full_quarantine_path)
        print(f"Created quarantine directory: {full_quarantine_path}")

    print(f"\n--- Starting dataset cleanup in: {dataset_root_dir} ---")
    files_moved = 0

    for root, _, files in os.walk(dataset_root_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_extension = os.path.splitext(filename)[1].lower() 

            is_valid_image = True
            reason = ""


            if file_extension not in allowed_extensions:
                is_valid_image = False
                reason = "Invalid extension"
            else:
                try:

                    with Image.open(file_path) as img:
                        img.verify() 

                    img = Image.open(file_path)
                    img.load()
                except Exception as e:

                    is_valid_image = False
                    reason = f"Corrupted or unreadable image file ({e})"

            if not is_valid_image:
                print(f"  Moving invalid file: {file_path} (Reason: {reason})")

                relative_path_from_dataset_root = os.path.relpath(file_path, dataset_root_dir)
                destination_path = os.path.join(full_quarantine_path, relative_path_from_dataset_root)

                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                try:
                    shutil.move(file_path, destination_path) # Move the file
                    files_moved += 1
                except Exception as e:
                    print(f"    ERROR moving {file_path}: {e}") # Log if move fails

    print(f"\n--- Cleanup complete. {files_moved} invalid files moved to {full_quarantine_path} ---")
    if files_moved > 0:
        print("Please review the files in the quarantine directory if needed.")
        print("After confirming they are indeed invalid, you can safely delete the entire 'quarantine_invalid_files' folder.")
    else:
        print("No invalid files found. Your dataset appears clean!")


if __name__ == "__main__":

    dataset_to_clean = '../Dataset/Train' 

    # Run the cleaning function
    clean_dataset(dataset_to_clean)

    print("\nNow, your dataset should be clean. Please try running 'python train_model.py' again.")