import os
from flask import Flask, request, jsonify
from flask_cors import CORS 
from tensorflow import keras 
import numpy as np 
from PIL import Image 
import io 
# Initialize Flask app
app = Flask(__name__)

CORS(app) 


MODEL_PATH = 'soil_model.h5' 
CLASS_NAMES_PATH = 'soil_classes.txt' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'} 
MODEL_INPUT_SHAPE = (224, 224, 3) # Model expects 224x224 pixel RGB images

model = None
SOIL_CLASSES = [] 

try:
    model = keras.models.load_model(MODEL_PATH)
    print(f"AI Model '{MODEL_PATH}' loaded successfully.")

    if os.path.exists(CLASS_NAMES_PATH):
        with open(CLASS_NAMES_PATH, 'r') as f:
            SOIL_CLASSES = [line.strip() for line in f if line.strip()]
        print(f"Loaded soil classes for prediction: {SOIL_CLASSES}")
    else:
        print(f"WARNING: Class names file '{CLASS_NAMES_PATH}' not found.")
        print("Please ensure you ran train_model.py successfully. Using a default class list.")
        SOIL_CLASSES = ['Alluvial soil', 'Black Soil', 'Clay soil', 'Red soil'] 


except Exception as e:
    print(f"ERROR: Failed to load AI model or class names: {e}")
    print("Please check if 'soil_model.h5' and 'soil_classes.txt' exist in the 'backend' folder.")
    # If model loading fails, ensure SOIL_CLASSES has some values to prevent index errors
    SOIL_CLASSES = ['Unknown'] 

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API Routes ---
@app.route('/')
def home():
    return "Soil Quality Monitoring Backend is running! Send a POST request to /predict with an image."

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"error": "AI model not loaded on server. Server setup issue."}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image file provided in the request. Please select a file."}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file. Please choose an image."}), 400

    if file and allowed_file(file.filename):
        try:
   
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))

            img = img.resize((MODEL_INPUT_SHAPE[0], MODEL_INPUT_SHAPE[1]))
            # Convert image to a NumPy array and ensure correct data type
            img_array = np.array(img).astype('float32')

            if img_array.ndim == 2: 
                img_array = np.stack([img_array, img_array, img_array], axis=-1)
            elif img_array.shape[-1] == 4: # RGBA image 
                img_array = img_array[..., :3] 

            img_array = np.expand_dims(img_array, axis=0) 
            # Normalize pixel values from 0-255 to 0-1 
            img_array /= 255.0 

            predictions = model.predict(img_array)
            predicted_class_idx = np.argmax(predictions, axis=1)[0]
            confidence = float(predictions[0][predicted_class_idx])
            predicted_soil_type = SOIL_CLASSES[predicted_class_idx]

           
            recommendations = ""
            if predicted_soil_type == 'Alluvial soil':
                recommendations = "Alluvial soil is typically fertile and good for tomatoes. Ensure consistent moisture and balanced nutrients. Good drainage is key."
            elif predicted_soil_type == 'Black Soil':
                recommendations = "Black soil is rich in clay and organic matter, holding water well. Ensure good aeration to prevent waterlogging. Calcium supplementation can be beneficial for tomato quality."
            elif predicted_soil_type == 'Clay soil':
                recommendations = "Clay soil can become compacted and has poor drainage. Amend with plenty of organic matter (compost) and consider gypsum to improve structure and drainage. Focus on consistent watering to avoid cracking."
            elif predicted_soil_type == 'Red soil':
                recommendations = "Red soil can be acidic and often lacks organic matter. Add lime to raise pH if needed (target 6.0-6.8). Incorporate organic compost to improve fertility and water retention. Monitor phosphorus and iron levels."
            else: 
                recommendations = "Soil characteristics can vary. General recommendations for tomatoes: Maintain soil pH between 6.0 and 6.8. Provide balanced nutrition, especially nitrogen for leaves and potassium for fruit development. Ensure consistent watering."
          
            return jsonify({
                "predicted_soil_type": predicted_soil_type,
                "confidence": round(confidence * 100, 2), # Convert to percentage
                "recommendations": recommendations,
                "timestamp": np.datetime_as_string(np.datetime64('now')) # Current time
            })

        except Exception as e:
          
            print(f"ERROR during image processing or prediction: {e}")
            import traceback
            traceback.print_exc() 
            return jsonify({"error": f"Server error processing image: {e}"}), 500
    else:
        return jsonify({"error": "Invalid file type. Please upload a PNG, JPG, JPEG, or GIF image."}), 400

# --- Run the Flask Application ---
if __name__ == '__main__':
 
    app.run(debug=True, port=5000)