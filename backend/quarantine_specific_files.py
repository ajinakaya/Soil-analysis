import os
import shutil

def quarantine_files_from_list(file_paths_to_quarantine, quarantine_dir_name="quarantine_invalid_files"):
    """
    Moves a list of specified file paths to a quarantine directory.
    """
    if not file_paths_to_quarantine:
        print("No file paths provided to quarantine. Exiting.")
        return

    dataset_base_path = os.path.abspath('../Dataset') 
    full_quarantine_path = os.path.join(dataset_base_path, quarantine_dir_name)

    if not os.path.exists(full_quarantine_path):
        os.makedirs(full_quarantine_path)
        print(f"Created quarantine directory: {full_quarantine_path}")

    print(f"\n--- Starting to quarantine specified files ---")
    files_moved = 0

    for file_path in file_paths_to_quarantine:
    
        file_path = file_path.strip()
        if not file_path: continue 

        if not os.path.exists(file_path):
            print(f"  Warning: File not found, skipping: {file_path}")
            continue
        try:
           
            relative_to_dataset_train = os.path.relpath(file_path, os.path.join(dataset_base_path, 'Train'))
            destination_path = os.path.join(full_quarantine_path, 'Train', relative_to_dataset_train) 

            os.makedirs(os.path.dirname(destination_path), exist_ok=True) 
            shutil.move(file_path, destination_path)
            files_moved += 1
            print(f"  Moved: {file_path} to {destination_path}")
        except Exception as e:
            print(f"  ERROR moving {file_path}: {e}")

    print(f"\n--- Quarantine complete. {files_moved} files moved to {full_quarantine_path} ---")
    if files_moved > 0:
        print("Please review the files in the quarantine directory. You can safely delete that folder when confirmed.")
    else:
        print("No files were moved.")

if __name__ == "__main__":
   
    problematic_files = [
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_10.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_13.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_14.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_15.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_16 - Copy.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_16.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_17.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_18 - Copy.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_18.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_19.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_2.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_21.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_22.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_24.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_26.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_27.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_30.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_31.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_33.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_34 - Copy.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_34.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_37.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_43.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_44.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_45.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_46.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_47.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_48.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_50.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Alluvial soil\Alluvial_8.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Clay soil\91714675-background-of-red-clay-the-real-desert-soil.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Clay soil\94530057-red-clay-soil-on-nature-as-a-background-.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Clay soil\Copy of 91714675-background-of-red-clay-the-real-desert-soil.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Clay soil\Copy of 94530057-red-clay-soil-on-nature-as-a-background-.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Red soil\61050549-red-soil-texture-background.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Red soil\Copy of 61050549-red-soil-texture-background.jpg",
        r"D:\soil-analyzer-project\Dataset\Train\Red soil\Copy of red-soil-1.gif",
        r"D:\soil-analyzer-project\Dataset\Train\Red soil\red-soil-1.gif"
    ]


    quarantine_files_from_list(problematic_files)

    print("\nPart 2 (Specific File Quarantine) is complete.")
    print("Now proceed to Part 3: Rerun the debugger, and then train your model!")