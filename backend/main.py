import os
import io
import librosa
import numpy as np
import joblib
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, db as rtdb
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = FastAPI(title="Backend Klasifikasi Tangisan Bayi")

FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS_PATH", "skripsigoat-firebase-adminsdk-fbsvc-76d7f1db11.json")
RTDB_URL             = os.getenv("FIREBASE_DATABASE_URL", "https://skripsigoat-default-rtdb.asia-southeast1.firebasedatabase.app")
MODEL_PATH           = "model_svm_v3.pkl"

try:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred, {"databaseURL": RTDB_URL})
    db = rtdb.reference("/")
    print(f"Firebase RTDB berhasil diinisialisasi: {RTDB_URL}")
except Exception as e:
    print(f"Gagal inisialisasi Firebase: {e}")
    db = None

try:
    bundle        = joblib.load(MODEL_PATH)
    svm_pipeline  = bundle["pipeline"]
    label_encoder = bundle["label_encoder"]
    SAMPLE_RATE   = bundle["sample_rate"]
    N_MFCC        = bundle["n_mfcc"]
    HOP_LENGTH    = bundle["hop_length"]
    N_FFT         = bundle["n_fft"]
    DURATION      = bundle["duration"]
    MAX_SAMPLES   = SAMPLE_RATE * DURATION
    print(f"Model berhasil dimuat dari {MODEL_PATH}")
    print(f"  Akurasi : {bundle['accuracy']*100:.2f}%")
    print(f"  Label   : {bundle['label_names']}")
    print(f"  Fitur   : {bundle['feature_dim']} dimensi")
except Exception as e:
    print(f"Gagal load model: {e}")
    svm_pipeline = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_features(audio_bytes: bytes) -> np.ndarray:
    y, _ = librosa.load(io.BytesIO(audio_bytes), sr=SAMPLE_RATE, mono=True)
    if len(y) < MAX_SAMPLES:
        y = np.pad(y, (0, MAX_SAMPLES - len(y)))
    y = y[:MAX_SAMPLES]

    mfcc   = librosa.feature.mfcc(y=y, sr=SAMPLE_RATE, n_mfcc=N_MFCC,
                                   hop_length=HOP_LENGTH, n_fft=N_FFT)
    delta  = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    zcr    = librosa.feature.zero_crossing_rate(y, hop_length=HOP_LENGTH)
    rms    = librosa.feature.rms(y=y, hop_length=HOP_LENGTH)

    return np.concatenate([
        np.mean(mfcc, axis=1),   np.std(mfcc, axis=1),
        np.mean(delta, axis=1),  np.std(delta, axis=1),
        np.mean(delta2, axis=1), np.std(delta2, axis=1),
        [np.mean(zcr), np.std(zcr)],
        [np.mean(rms), np.std(rms)],
    ])

@app.post("/api/predict")
async def predict(audio: UploadFile = File(...)):
    print(f"[DEBUG] Received file: {audio.filename}, content_type: {audio.content_type}")
    
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase belum terhubung.")
    if svm_pipeline is None:
        raise HTTPException(status_code=500, detail="Model SVM belum dimuat.")

    audio_bytes = await audio.read()
    print(f"[DEBUG] Audio bytes received: {len(audio_bytes)}")
    
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="File audio kosong.")

    try:
        features = extract_features(audio_bytes).reshape(1, -1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ekstraksi fitur gagal: {e}")

    try:
        pred_encoded    = svm_pipeline.predict(features)
        predicted_label = str(label_encoder.inverse_transform(pred_encoded)[0])
        pred_proba      = svm_pipeline.predict_proba(features)[0]
        confidence      = float(np.max(pred_proba) * 100)
        prob_dict       = {label_encoder.classes_[i]: round(float(p) * 100, 2)
                           for i, p in enumerate(pred_proba)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediksi gagal: {e}")

    result = {
        "label"         : predicted_label,
        "confidence"    : round(confidence, 2),
        "probabilities" : prob_dict,
        "timestamp"     : int(time.time() * 1000)
    }

    try:
        db.child("deteksi_bayi/latest_result").set(result)
        db.child("deteksi_bayi/history").push(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal simpan ke Firebase: {e}")

    print(f"Prediksi: {predicted_label} ({confidence:.2f}%)")
    print(f"  [PROB] {prob_dict}")
    return {"status": "success", "prediction": predicted_label, "confidence": confidence, "probabilities": prob_dict}

@app.post("/api/debug_predict")
async def debug_predict(audio: UploadFile = File(...)):
    """Endpoint debug: tampilkan semua probabilitas per label (tanpa simpan ke Firebase)."""
    if svm_pipeline is None:
        raise HTTPException(status_code=500, detail="Model SVM belum dimuat.")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="File audio kosong.")

    try:
        features = extract_features(audio_bytes).reshape(1, -1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ekstraksi fitur gagal: {e}")

    pred_encoded    = svm_pipeline.predict(features)
    predicted_label = str(label_encoder.inverse_transform(pred_encoded)[0])
    pred_proba      = svm_pipeline.predict_proba(features)[0]
    prob_dict       = {label_encoder.classes_[i]: round(float(p) * 100, 2)
                       for i, p in enumerate(pred_proba)}

    # Urutkan dari probabilitas tertinggi ke terendah
    sorted_probs = dict(sorted(prob_dict.items(), key=lambda x: x[1], reverse=True))

    print(f"\n=== DEBUG PREDICT ===")
    for lbl, prob in sorted_probs.items():
        bar = "█" * int(prob / 5)
        print(f"  {lbl:15s}: {prob:6.2f}% {bar}")
    print(f"  => Hasil: {predicted_label}")
    print(f"===================")

    return {
        "predicted_label"  : predicted_label,
        "all_probabilities": sorted_probs,
        "note"             : "Gunakan endpoint ini untuk melihat distribusi probabilitas saat pengujian"
    }

@app.get("/")
def read_root():
    return {"message": "API Klasifikasi Tangisan Bayi — POST audio ke /api/predict | Debug ke /api/debug_predict"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)