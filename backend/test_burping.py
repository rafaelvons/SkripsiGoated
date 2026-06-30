"""
Script pengujian langsung model SVM untuk diagnosa deteksi burping.
Jalankan: py test_burping.py <path_file_audio.wav>
Atau tanpa argumen untuk tes dengan file sample yang ada.
"""
import sys
import io
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import joblib
import librosa

MODEL_PATH = "model_svm_v3.pkl"

# ── Load model ─────────────────────────────────────────────────────────────
print(f"Loading model dari {MODEL_PATH}...")
bundle        = joblib.load(MODEL_PATH)
svm_pipeline  = bundle["pipeline"]
label_encoder = bundle["label_encoder"]
SAMPLE_RATE   = bundle["sample_rate"]
N_MFCC        = bundle["n_mfcc"]
HOP_LENGTH    = bundle["hop_length"]
N_FFT         = bundle["n_fft"]
DURATION      = bundle["duration"]
MAX_SAMPLES   = SAMPLE_RATE * DURATION

print(f"Label yang didukung: {bundle['label_names']}")
print(f"Akurasi training   : {bundle['accuracy']*100:.2f}%")
print(f"Sample rate        : {SAMPLE_RATE} Hz | Durasi maks: {DURATION}s")
print()

# ── Fungsi ekstraksi fitur ─────────────────────────────────────────────────
def extract_features(audio_path: str) -> np.ndarray:
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
    print(f"  Durasi audio asli  : {len(y)/sr:.2f}s ({len(y)} samples)")

    if len(y) < MAX_SAMPLES:
        y = np.pad(y, (0, MAX_SAMPLES - len(y)))
    y = y[:MAX_SAMPLES]

    mfcc   = librosa.feature.mfcc(y=y, sr=SAMPLE_RATE, n_mfcc=N_MFCC, hop_length=HOP_LENGTH, n_fft=N_FFT)
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

# ── Uji file audio ─────────────────────────────────────────────────────────
audio_file = sys.argv[1] if len(sys.argv) > 1 else "burping1.wav"
print(f"Menguji file: {audio_file}")
print("-" * 50)

features = extract_features(audio_file).reshape(1, -1)
print(f"  Fitur diekstrak    : {features.shape[1]} dimensi")

pred_encoded    = svm_pipeline.predict(features)
predicted_label = str(label_encoder.inverse_transform(pred_encoded)[0])
pred_proba      = svm_pipeline.predict_proba(features)[0]
prob_dict       = {label_encoder.classes_[i]: float(p) * 100
                   for i, p in enumerate(pred_proba)}

sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)

print()
print("=== HASIL PREDIKSI ===")
for lbl, prob in sorted_probs:
    bar  = "#" * int(prob / 3)
    mark = " <-- WINNER" if lbl == predicted_label else ""
    print(f"  {lbl:15s}: {prob:6.2f}% {bar}{mark}")

print()
print(f"  => Prediksi akhir  : {predicted_label.upper()}")
print(f"  => Confidence      : {max(prob_dict.values()):.2f}%")
print("=" * 22)

if predicted_label != "burping":
    burping_prob = prob_dict.get("burping", 0)
    print()
    print(f"[!] Burping TIDAK terdeteksi. Probabilitas burping: {burping_prob:.2f}%")
    print(f"   Kemungkinan penyebab:")
    print(f"   1. Audio terlalu singkat / kualitas rendah")
    print(f"   2. Noise background tinggi")
    print(f"   3. Suara burping tidak mirip data training")
else:
    print()
    print("[OK] Burping berhasil terdeteksi!")
