# KaloriKu - API Deteksi Makanan
Versi: 1.0.0
Tim: Machine Learning

## Deskripsi Singkat
API ini berfungsi untuk menerima file gambar makanan, melakukan prediksi nama makanan menggunakan model Machine Learning, dan mengembalikan nama makanan beserta estimasi kalorinya.

API ini dibangun menggunakan **Python 3.11** dengan framework **FastAPI**.

---

## Untuk Tim Backend: Setup & Deployment

Berikut adalah panduan untuk menjalankan server API ini di lingkungan development dan production.

### 1. Prasyarat
- **Python 3.11 (64-bit)**. Pastikan versi Python yang digunakan sesuai.

### 2. Instruksi Setup
1.  **Clone repositori ini atau ekstrak file ZIP.**
2.  **Buat Virtual Environment:**
    ```bash
    python -m venv venv
    ```
3.  **Aktifkan Virtual Environment:**
    - Windows: `.\venv\Scripts\activate`
    - MacOS/Linux: `source venv/bin/activate`
4.  **Install semua dependency yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Menjalankan Server
- **Untuk Development (Lokal):**
  Gunakan perintah ini untuk menjalankan server dengan auto-reload.
  ```bash
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- **Untuk Production:**
  Disarankan menggunakan Gunicorn sebagai process manager.
  ```bash
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8000
  ```
  `-w 4` berarti menjalankan 4 proses worker. Sesuaikan jumlahnya dengan spesifikasi server.

### 4. Konfigurasi
- **Model & Label:** Path ke model (`.tflite` atau `.h5`) dan file `labels.txt` sudah di-hardcode di `main.py`. Jika Anda ingin memindahkannya, silakan ubah variabel `MODEL_PATH` dan `LABELS_PATH`.
- **Database Kalori:** Saat ini, data kalori masih bersifat *dummy* (hardcoded) di dalam fungsi `get_calories_from_db` di `main.py`. Mohon ganti fungsi ini untuk melakukan query ke database production Anda.

---

## Untuk Tim Frontend: Panduan Konsumsi API

Berikut adalah cara menggunakan (consume) API ini dari aplikasi web Anda.

### 1. Alamat Dasar (Base URL)
- **Lokal:** `http://127.0.0.1:8000`
- **Production:** `https://api.domain-anda.com` (Akan disediakan oleh tim Backend setelah deployment)

### 2. Dokumentasi Interaktif
Dokumentasi API lengkap, termasuk contoh, tersedia secara otomatis. Cukup jalankan server dan buka alamat berikut di browser:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### 3. Endpoint Utama: Deteksi Makanan

#### `POST /detect_food`
Endpoint ini digunakan untuk mengunggah gambar dan mendapatkan hasil prediksi.

- **Method:** `POST`
- **URL:** `/detect_food`
- **Request Body:** `multipart/form-data`
  - Anda harus mengirimkan sebuah form data dengan `key` sebagai berikut:
    - **key:** `image`
    - **value:** File gambar (`.jpg`, `.png`, dll.)

- **Contoh Respons Sukses (200 OK):**
  Anda akan menerima respons dalam format JSON seperti ini.
  ```json
  {
    "detected_food": "Nasi Goreng",
    "confidence_percent": "98.75%",
    "estimated_calories_kcal": 485
  }
  ```

- **Contoh Respons Gagal (Error):**
  ```json
  {
    "error": "Pesan error spesifik akan muncul di sini."
  }
  ```

### 4. Aturan CORS
Server API sudah dikonfigurasi untuk menerima permintaan dari `origin` tertentu. Jika frontend production berjalan di domain `https://app.kaloriku.com`, tim Backend perlu menambahkan domain tersebut ke dalam list `origins` di `main.py` agar tidak diblokir oleh browser.
