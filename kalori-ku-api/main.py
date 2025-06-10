import os
import numpy as np
from PIL import Image
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- Konfigurasi Awal ---
MODEL_PATH = "models/model.tflite" 
LABELS_PATH = "models/labels.txt"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Muat model TFLite HANYA SEKALI
try:
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("Model TFLite berhasil dimuat.")
except Exception as e:
    print(f"Error memuat model TFLite: {e}")
    interpreter = None

with open(LABELS_PATH, "r") as f:
    labels = [line.strip() for line in f.readlines()]
print(f"Labels berhasil dimuat: {labels}")

# --- Fungsi Helper ---
def preprocess_image_tflite(image_path, target_size=(224, 224), input_details=input_details):
    """
    Fungsi untuk memproses gambar untuk model TFLite.
    Sesuaikan target_size dengan ukuran input model Anda!
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize(target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Cek jika model TFLite butuh normalisasi atau tipe data integer
    if input_details[0]['dtype'] == np.float32:
        img_array = (img_array / 255.0).astype(np.float32)
        
    return img_array

def get_calories_from_db(food_name):
    # ... (fungsi ini sama seperti di Opsi A)
    calories_db = {"Nasi Goreng": 485, "Sate Ayam": 350, "Gado-gado": 250, "Bakso": 320, "Rendang": 550}
    return calories_db.get(food_name, "Kalori tidak ditemukan")

# --- Inisialisasi FastAPI ---
app = FastAPI(title="KaloriKu API")
origins = ["null"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Endpoint API ---
@app.get("/")
def read_root():
    return {"message": "Selamat datang di API KaloriKu! Model TFLite sudah siap."}

@app.post("/detect_food")
async def detect_food(image: UploadFile = File(...)):
    if not interpreter:
        return {"error": "Model tidak berhasil dimuat, cek log server."}

    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())
        
    try:
        # 1. Preprocess gambar
        processed_image = preprocess_image_tflite(file_path)

        # 2. Lakukan prediksi dengan TFLite Interpreter
        interpreter.set_tensor(input_details[0]['index'], processed_image)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])
        
        # 3. Dapatkan hasil prediksi
        predicted_class_index = np.argmax(predictions[0])
        predicted_class_name = labels[predicted_class_index]
        confidence = float(np.max(predictions[0]) * 100)

        # 4. Ambil data kalori
        calories = get_calories_from_db(predicted_class_name)

        return {
            "detected_food": predicted_class_name,
            "confidence_percent": f"{confidence:.2f}%",
            "estimated_calories_kcal": calories,
        }
    except Exception as e:
        return {"error": f"Terjadi kesalahan saat prediksi: {e}"}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)