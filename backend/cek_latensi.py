import requests
import time
import numpy as np

FLASK_URL  = "http://localhost:8000/api/predict"
TEST_FILE  = "baby_0016_seg00.wav"  
N_TRIALS   = 10

latencies = []

for i in range(N_TRIALS):
    t_start = time.time()
    with open(TEST_FILE, 'rb') as f:
        response = requests.post(FLASK_URL, files={'audio': f})
    t_end = time.time()

    lat = (t_end - t_start) * 1000
    latencies.append(lat)
    print(f"Trial {i+1:2d}: {lat:.1f} ms → {response.json().get('prediction')}")

print(f"\nRata-rata : {np.mean(latencies):.1f} ms")
print(f"Min       : {np.min(latencies):.1f} ms")
print(f"Max       : {np.max(latencies):.1f} ms")
print(f"Std       : {np.std(latencies):.1f} ms")