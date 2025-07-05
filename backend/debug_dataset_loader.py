import tensorflow as tf
import os
DATASET_DIR = '../Dataset/Train' 
IMG_HEIGHT = 224 
IMG_WIDTH = 224  


def debug_dataset_loading(dataset_path_relative_to_script):
    print(f"--- Starting deep debug of dataset loading from: {dataset_path_relative_to_script} ---")

    absolute_dataset_path = os.path.abspath(dataset_path_relative_to_script)

    if not os.path.exists(absolute_dataset_path):
        print(f"Error: Dataset directory '{absolute_dataset_path}' not found.")
        print("Please check the 'DATASET_DIR' path in this script and your project structure.")
        return

    problem_files = []
    total_files_checked = 0

    for class_name in os.listdir(absolute_dataset_path):
        class_path = os.path.join(absolute_dataset_path, class_name)

        if os.path.isdir(class_path): 
            print(f"  Checking folder: {class_name}/")
        
            for filename in os.listdir(class_path):
                file_path = os.path.join(class_path, filename)

                if os.path.isfile(file_path): 
                    total_files_checked += 1
                    try:
                      
                        img_bytes = tf.io.read_file(file_path)
                        img_tensor = tf.image.decode_image(img_bytes, channels=3)
                    except tf.errors.InvalidArgumentError as e:
                 
                        print(f"ERROR: TensorFlow decode failed for file: {file_path}")
                        print(f"Reason: {e.message}")
                        problem_files.append(file_path)
                    except Exception as e:
                    
                        print(f"OTHER ERROR: Failed to process file: {file_path}")
                        print(f"Reason: {e}")
                        problem_files.append(file_path)

    print(f"\n--- Debugging complete. Checked {total_files_checked} files ---")
    if problem_files:
        print("\nFound the following problematic files that TensorFlow could not decode:")
        for p_file in problem_files:
            print(f"- {p_file}")
        print("\nACTION REQUIRED: Please remove or replace these specific files from your dataset.")
        print("Once done, run 'python train_model.py' again.")
    else:
        print("\nNo problematic files found by this TensorFlow-specific decoding script.")
        print("Your dataset should now be fully compatible with TensorFlow's image loading.")
        print("You can now safely run 'python train_model.py' again.")

if __name__ == "__main__":
  
    debug_dataset_loading(DATASET_DIR)