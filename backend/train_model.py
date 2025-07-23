import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
import numpy as np
import os

print("TensorFlow Version:", tf.__version__)

DATASET_DIR = '../Dataset/Train' 
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32


# Function to create and train the multi-task model
def create_and_train_model(dataset_path, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3), epochs=10):
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset directory '{dataset_path}' not found.")
        print("Creating a simple dummy model instead.")
        return None, None

    # Load dataset from directory
    images_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_path,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_path,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE
    )
    
   
    def generate_dummy_pH(images, labels):
        pH_labels = tf.random.uniform(shape=tf.shape(labels), minval=6.0, maxval=7.0)
        return images, {'soil_type_output': labels, 'pH_output': pH_labels}
    
    train_ds = images_ds.map(generate_dummy_pH)
    val_ds = val_ds.map(generate_dummy_pH)
  
    
    class_names = images_ds.class_names
    num_classes = len(class_names)
    
    normalization_layer = layers.Rescaling(1./255)
    normalized_train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    normalized_val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

    input_tensor = keras.Input(shape=input_shape)

    # Define the layers of the base model
    x = layers.Conv2D(32, (3, 3), activation='relu')(input_tensor)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation='relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation='relu')(x)

    # Output for soil type classification
    soil_type_output = layers.Dense(num_classes, activation='softmax', name='soil_type_output')(x)
    
    # Output for pH regression (a single value)
    pH_output = layers.Dense(1, activation='linear', name='pH_output')(x)
    
    # Combine the two outputs into a single model
    model = Model(inputs=input_tensor, outputs=[soil_type_output, pH_output])

    model.compile(optimizer='adam',
                  loss={'soil_type_output': tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                        'pH_output': tf.keras.losses.MeanSquaredError()},
                  metrics={'soil_type_output': ['accuracy'],
                           'pH_output': ['mse']})
  

    model.summary()
    print(f"Starting multi-task model training for {epochs} epochs...")
    history = model.fit(
        normalized_train_ds,
        validation_data=normalized_val_ds,
        epochs=epochs
    )
    print("\nMulti-task model training complete.")
    return model, class_names

# --- Main execution ---
if __name__ == "__main__":
    full_dataset_path = os.path.join(os.path.dirname(__file__), DATASET_DIR)
    trained_model, class_names_from_training = create_and_train_model(full_dataset_path, epochs=10)

    if trained_model:
        model_filename = 'multi_task_soil_model.h5'
        print(f"Saving multi-task model as {model_filename}...")
        trained_model.save(model_filename)
        print(f"Model '{model_filename}' saved successfully.")

        class_names_path = 'soil_classes.txt'
        with open(class_names_path, 'w') as f:
            for cls_name in class_names_from_training:
                f.write(f"{cls_name}\n")
        print(f"Class names saved to '{class_names_path}'.")
    else:
        print("Model was not trained. Please check dataset path.")