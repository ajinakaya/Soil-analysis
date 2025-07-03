import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os # Added for dataset loading

print("TensorFlow Version:", tf.__version__)


DATASET_DIR = '../Dataset/Train' 


IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32

# Function to create and train the model
def create_and_train_model(dataset_path, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3), epochs=10):
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset directory '{dataset_path}' not found.")
        print("Please ensure your 'Dataset' folder is in the 'soil-analyzer-project' root,")
        print("and it contains 'Train' with your soil type folders.")
        print("Skipping real model training. Creating a dummy model instead.")
     
        model = keras.Sequential([
            layers.Input(shape=input_shape),
            layers.Conv2D(32, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(4, activation='softmax') 
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model, ['Class_0', 'Class_1', 'Class_2', 'Class_3'] 

    # Load dataset from directory
    print(f"Loading dataset from: {dataset_path}")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_path,
        validation_split=0.2, # Use 20% of data for validation
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

    class_names = train_ds.class_names
    print(f"Detected classes from dataset: {class_names}")
    num_classes = len(class_names)

    # Normalize pixel values (0-255 to 0-1)
    normalization_layer = layers.Rescaling(1./255)
    normalized_train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    normalized_val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

    # Optimize dataset loading for performance
    AUTOTUNE = tf.data.AUTOTUNE
    normalized_train_ds = normalized_train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    normalized_val_ds = normalized_val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    model = keras.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes, activation='softmax') # Output layer for classification
    ])

    # Compile the model
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False), 
                  metrics=['accuracy'])

    model.summary()

    print(f"Starting model training for {epochs} epochs...")
    history = model.fit(
        normalized_train_ds,
        validation_data=normalized_val_ds,
        epochs=epochs
    )

    print("\nModel training complete.")
    return model, class_names

model_filename = 'soil_model.h5'
class_names_path = 'soil_classes.txt'

trained_model, class_names_from_training = create_and_train_model(DATASET_DIR, epochs=10)

# Save the model
print(f"Saving model as {model_filename}...")
trained_model.save(model_filename)
print(f"Model '{model_filename}' saved successfully.")

if class_names_from_training:
    with open(class_names_path, 'w') as f:
        for cls_name in class_names_from_training:
            f.write(f"{cls_name}\n")
    print(f"Class names saved to '{class_names_path}'.")
else:
    print("No class names from training (dummy model used). Flask app will use default classes.")

try:
    loaded_model = keras.models.load_model(model_filename)
    print(f"Model '{model_filename}' loaded successfully for verification.")
except Exception as e:
    print(f"Error loading saved model for verification: {e}")