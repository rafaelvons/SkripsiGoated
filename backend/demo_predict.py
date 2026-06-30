"""
Demo script: kirim file audio ke API /api/predict
Hasil langsung tampil di dashboard UI secara real-time.

Jalankan:
  py demo_predict.py                  -> pakai burping1.wav
  py demo_predict.py nama_file.wav    -> pakai file lain
"""
import sys
import os
import requests
import json

# ── Konfigurasi ──────────────────────────────────────────────────────────────
API_URL    = "http://localhost:8000/api/predict"
AUDIO_FILE = sys.argv[1] if len(sys.argv) > 1 else "burping1.wav"

# ── Cek file ada ─────────────────────────────────────────────────────────────
if not os.path.exists(AUDIO_FILE):
    print(f"[ERROR] File tidak ditemukan: {AUDIO_FILE}")
    sys.exit(1)

file_size_kb = os.path.getsize(AUDIO_FILE) / 1024
print(f"=" * 50)
print(f"  BabyVoice - Demo Predict via API")
print(f"=" * 50)
print(f"  File      : {AUDIO_FILE}")
print(f"  Ukuran    : {file_size_kb:.1f} KB")
print(f"  Endpoint  : {API_URL}")
print(f"-" * 50)
print(f"  Mengirim audio ke server...")

# ── Kirim ke API ──────────────────────────────────────────────────────────────
try:
    with open(AUDIO_FILE, "rb") as f:
        response = requests.post(
            API_URL,
            files={"audio": (AUDIO_FILE, f, "audio/wav")},
            timeout=30,
        )

    if response.status_code == 200:
        data = response.json()

        label      = data.get("prediction", "?")
        confidence = data.get("confidence", 0)
        probs      = data.get("probabilities", {})

        # Urutkan probabilitas
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)

        print(f"\n  [OK] Respons diterima dari server!\n")
        print(f"=== HASIL PREDIKSI ===")
        for lbl, prob in sorted_probs:
            bar  = "#" * int(prob / 3)
            mark = " <-- WINNER" if lbl == label else ""
            print(f"  {lbl:15s}: {prob:6.2f}% {bar}{mark}")

        print()
        print(f"  => Prediksi akhir  : {label.upper()}")
        print(f"  => Confidence      : {confidence:.2f}%")
        print(f"=" * 22)
        print()
        print(f"  [OK] Dashboard UI sudah update otomatis!")
        print(f"       Buka browser dan lihat hasilnya.")

    else:
        print(f"\n  [ERROR] Server mengembalikan status {response.status_code}")
        print(f"  Detail: {response.text}")

except requests.exceptions.ConnectionError:
    print(f"\n  [ERROR] Tidak bisa konek ke server!")
    print(f"  Pastikan backend sudah berjalan:")
    print(f"    cd backend")
    print(f"    py main.py")
except requests.exceptions.Timeout:
    print(f"\n  [ERROR] Server timeout (>30 detik).")
except Exception as e:
    print(f"\n  [ERROR] {e}")
