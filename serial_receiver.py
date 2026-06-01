import serial
import time
import requests
import io
import argparse

# Konfigurasi
SERIAL_PORT = 'COM6'  # Sesuaikan dengan port ESP32 di laptop (misal: COM3, /dev/ttyUSB0)
BAUD_RATE = 115200
API_URL = 'http://localhost:8000/api/predict'

def main():
    parser = argparse.ArgumentParser(description='ESP32 Serial Receiver for VoxMotion')
    parser.add_argument('--port', type=str, default=SERIAL_PORT, help='Serial port ESP32 (e.g., COM3)')
    parser.add_argument('--baud', type=int, default=BAUD_RATE, help='Baud rate (default: 115200)')
    parser.add_argument('--api', type=str, default=API_URL, help='FastAPI predict URL')
    args = parser.parse_args()

    print(f"Menghubungkan ke {args.port} dengan baud rate {args.baud}...")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
        ser.setDTR(False)
        ser.setRTS(False)
        print("Berhasil terhubung. Menunggu data dari ESP32...")
    except Exception as e:
        print(f"Gagal membuka port serial {args.port}: {e}")
        return

    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
                
            if line == "---START_PAYLOAD---":
                print("\n[+] Mendapatkan payload baru...")
                
                # Baca RADAR
                radar_line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not radar_line.startswith("RADAR:"):
                    print("[-] Format RADAR salah:", radar_line)
                    continue
                
                # Format: RADAR:moving,stationary,distance
                radar_data = radar_line.replace("RADAR:", "").split(",")
                if len(radar_data) != 3:
                    print("[-] Data RADAR tidak lengkap:", radar_data)
                    continue
                    
                moving_energy = int(radar_data[0])
                stationary_energy = int(radar_data[1])
                distance = int(radar_data[2])
                print(f"    Radar -> Moving: {moving_energy}, Static: {stationary_energy}, Distance: {distance}")

                # Baca SIZE
                size_line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not size_line.startswith("SIZE:"):
                    print("[-] Format SIZE salah:", size_line)
                    continue
                
                fsize = int(size_line.replace("SIZE:", ""))
                print(f"    Ukuran Audio: {fsize} bytes")

                # Baca ---AUDIO_BEGIN---
                audio_begin = ser.readline().decode('utf-8', errors='ignore').strip()
                if audio_begin != "---AUDIO_BEGIN---":
                    print("[-] Menunggu AUDIO_BEGIN gagal:", audio_begin)
                    continue

                # Baca Audio Bytes
                print("    Menerima data audio...")
                audio_bytes = b''
                bytes_read = 0
                while bytes_read < fsize:
                    # Baca chunk yang tersedia, atau sisa byte yang diperlukan
                    to_read = min(fsize - bytes_read, ser.in_waiting or 1) 
                    chunk = ser.read(to_read)
                    audio_bytes += chunk
                    bytes_read += len(chunk)

                print("    Audio selesai diterima.")

                # Baca sisa serial untuk membuang ---AUDIO_END---
                time.sleep(0.1)
                while ser.in_waiting:
                    end_marker = ser.readline().decode('utf-8', errors='ignore').strip()
                    if end_marker == "---AUDIO_END---":
                        break
                
                # Kirim ke API FastAPI
                print(f"[+] Mengirim ke API: {args.api}")
                
                data = {
                    'moving_energy': moving_energy,
                    'distance': distance,
                    'static_energy': stationary_energy
                }
                
                files = {
                    'audio': ('rekaman.wav', io.BytesIO(audio_bytes), 'audio/wav')
                }
                
                try:
                    response = requests.post(args.api, data=data, files=files)
                    print("    --- RESPONSE DARI SERVER ---")
                    print("    Status Code:", response.status_code)
                    try:
                        print("    Response JSON:", response.json())
                    except:
                        print("    Response Text:", response.text)
                except Exception as e:
                    print(f"    Gagal menghubungi server: {e}")
                
                print("\nMenunggu data selanjutnya...")
            else:
                # Print log biasa dari ESP32
                print(f"[ESP32] {line}")

        except KeyboardInterrupt:
            print("\nBerhenti.")
            break
        except Exception as e:
            print(f"Error membaca serial: {e}")
            time.sleep(1)

    ser.close()

if __name__ == '__main__':
    main()
