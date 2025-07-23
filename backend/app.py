import os
from flask import Flask, request, jsonify
from flask_cors import CORS 
from tensorflow import keras 
import numpy as np 
from PIL import Image 
import io 
import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64

# Initialize Flask app
app = Flask(__name__)
CORS(app) 

MODEL_PATH = 'multi_task_soil_model.h5' 
CLASS_NAMES_PATH = 'soil_classes.txt' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'} 
MODEL_INPUT_SHAPE = (224, 224, 3) 
UPLOAD_FOLDER = 'uploads' 
# --- END CONFIGURATION ---

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
        print(f"WARNING: Class names file '{CLASS_NAMES_PATH}' not found. Using a default class list.")
        SOIL_CLASSES = ['Alluvial soil', 'Black Soil', 'Clay soil', 'Red soil'] 
except Exception as e:
    print(f"ERROR: Failed to load AI model or class names: {e}")
    print("Please check if 'multi_task_soil_model.h5' and 'soil_classes.txt' exist in the 'backend' folder.")
    SOIL_CLASSES = ['Unknown'] 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_chart_image(confidence_scores_dict, soil_classes_order, save_path=None):
    labels = soil_classes_order
    scores = [confidence_scores_dict.get(label, 0) for label in labels]
    
    plt.figure(figsize=(6, 4))
    bars = plt.bar(labels, scores, color=['#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'])
    plt.title('Prediction Confidence')
    plt.ylabel('Confidence (%)')
    plt.ylim(0, 100)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}%', ha='center', va='bottom')
            
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        try:
            plt.savefig(save_path, format='png')
            print(f"Chart image saved to: {save_path}")
        except Exception as e:
            print(f"ERROR: Failed to save chart image to file: {e}")

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str

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
            img_array = np.array(img).astype('float32')

            if img_array.ndim == 2:
                img_array = np.stack([img_array, img_array, img_array], axis=-1)
            elif img_array.shape[-1] == 4:
                img_array = img_array[..., :3]

            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0

            soil_type_predictions, pH_predictions = model.predict(img_array)

            predicted_class_idx = np.argmax(soil_type_predictions, axis=1)[0]
            confidence = float(soil_type_predictions[0][predicted_class_idx])
            predicted_soil_type = SOIL_CLASSES[predicted_class_idx]

            predicted_pH = float(pH_predictions[0][0])

            confidence_scores_dict = {
                soil_class: float(score) * 100
                for soil_class, score in zip(SOIL_CLASSES, soil_type_predictions[0])
            }

            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            chart_filename = f"chart_{timestamp}.png"
            chart_save_path = os.path.join(UPLOAD_FOLDER, chart_filename)

            chart_image_base64 = generate_chart_image(
                confidence_scores_dict,
                SOIL_CLASSES,
                save_path=chart_save_path
            )
            soil_quality = "Unknown"
            
            # Check if pH is within the ideal range (6.0-6.8)
            is_pH_good = 6.0 <= predicted_pH <= 6.8
            
            if predicted_soil_type == 'Alluvial soil' and is_pH_good:
                soil_quality = "Excellent"
            elif predicted_soil_type == 'Alluvial soil':
                soil_quality = "Good" # Alluvial is good, but pH is off
            elif predicted_soil_type == 'Black Soil' and is_pH_good:
                soil_quality = "Good" # pH helps make it good
            elif predicted_soil_type == 'Black Soil':
                soil_quality = "Okay"
            elif predicted_soil_type == 'Clay soil' and is_pH_good:
                soil_quality = "Okay" # pH is good, but drainage is still a challenge
            elif predicted_soil_type == 'Clay soil':
                soil_quality = "Challenging"
            elif predicted_soil_type == 'Red soil' and is_pH_good:
                soil_quality = "Okay"
            elif predicted_soil_type == 'Red soil':
                soil_quality = "Challenging"
            else:
                soil_quality = "Unknown"
      
            recommendations = ""
            if predicted_soil_type == 'Alluvial soil':
                recommendations = "Alluvial soil is typically fertile and good for tomatoes. Ensure consistent moisture and balanced nutrients. Good drainage is key."
                if not is_pH_good:
                    recommendations += f" However, the pH level of {round(predicted_pH, 2)} is outside the ideal range (6.0-6.8). You may need to adjust it."
            elif predicted_soil_type == 'Black Soil':
                recommendations = "Black soil is rich in clay and organic matter, holding water well. Ensure good aeration to prevent waterlogging. Calcium supplementation can be beneficial for tomato quality."
                if not is_pH_good:
                    recommendations += f" The pH level of {round(predicted_pH, 2)} is outside the ideal range (6.0-6.8), which may require adjustment."
            elif predicted_soil_type == 'Clay soil':
                recommendations = "Clay soil can become compacted and has poor drainage. Amend with plenty of organic matter (compost) and consider gypsum to improve structure and drainage. Focus on consistent watering to avoid cracking."
                if not is_pH_good:
                    recommendations += f" The pH level of {round(predicted_pH, 2)} is outside the ideal range (6.0-6.8), which may require adjustment."
            elif predicted_soil_type == 'Red soil':
                recommendations = "Red soil can be acidic and often lacks organic matter. Add lime to raise pH if needed (target 6.0-6.8). Incorporate organic compost to improve fertility and water retention. Monitor phosphorus and iron levels."
                if not is_pH_good:
                    recommendations += f" The pH level of {round(predicted_pH, 2)} is outside the ideal range (6.0-6.8), which may require adjustment."
            else:
                recommendations = "Soil characteristics can vary. General recommendations for tomatoes: Maintain soil pH between 6.0 and 6.8. Provide balanced nutrition, especially nitrogen for leaves and potassium for fruit development. Ensure consistent watering."
            
            return jsonify({
                "predicted_soil_type": predicted_soil_type,
                "confidence": round(confidence * 100, 2),
                "predicted_pH": round(predicted_pH, 2),
                "soil_quality": soil_quality,
                "recommendations": recommendations,
                "timestamp": np.datetime_as_string(np.datetime64('now')),
                "chart_image": chart_image_base64
            })
        except Exception as e:
            print(f"ERROR during image processing or prediction: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Server error processing image: {e}"}), 500
    else:
        return jsonify({"error": "Invalid file type. Please upload a PNG, JPG, JPEG, or GIF image."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)