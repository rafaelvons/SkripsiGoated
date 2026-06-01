#include <SPI.h>
#include <SD.h>
#include <driver/i2s.h>
#include <math.h>
#include <WiFi.h>

/* 
 * ==========================================
 * KONFIGURASI WIFI & SERVER
 * ==========================================
 */
const char* ssid = "NAMA_WIFI_KAMU";           // Ganti dengan SSID WiFi kamu
const char* password = "PASSWORD_WIFI_KAMU";   // Ganti dengan Password WiFi kamu
const char* serverHost = "192.168.1.xxx";      // Ganti dengan IP Address Laptop kamu (IPv4)
const int serverPort = 8000;                   // Port backend FastAPI

/* 
 * ==========================================
 * KONFIGURASI PIN & PARAMETER
 * ==========================================
 */
// Pin I2S (Microphone INMP441 / SPH0645)
#define I2S_WS      25
#define I2S_SCK     33
#define I2S_SD      32

// Pin SD Card (SPI)
#define SD_CS        5
#define SPI_MOSI    23
#define SPI_MISO    19
#define SPI_SCK     18

// Periferal Lainnya
#define LED_PIN      2
#define RADAR_RX    26
#define RADAR_TX    27

// Setting Audio
#define SAMPLE_RATE  16000
#define BIT_DEPTH    16
#define CHANNELS     1
#define RECORD_SEC   3
#define WAV_HDR_SIZE 44

/* 
 * ==========================================
 * VARIABEL & OBJEK GLOBAL
 * ==========================================
 */
HardwareSerial radarSerial(2);
const int waveDataSize = RECORD_SEC * SAMPLE_RATE * (BIT_DEPTH / 8) * CHANNELS;

struct AudioFeature {
  int32_t rms;
  float zcr;
};

// Data Radar Global
struct RadarData {
  uint16_t movingEnergy = 0;
  uint16_t stationaryEnergy = 0;
  uint16_t distance = 0;
} currentRadar;

/* 
 * ==========================================
 * FUNGSI HELPER: WAV HEADER
 * ==========================================
 */
void writeWavHeader(File &file, int dataSize) {
  byte header[WAV_HDR_SIZE];
  uint32_t sampleRate = SAMPLE_RATE;
  uint32_t byteRate = SAMPLE_RATE * CHANNELS * (BIT_DEPTH / 8);

  memcpy(header, "RIFF", 4);
  uint32_t fileSize = dataSize + WAV_HDR_SIZE - 8;
  header[4] = (fileSize & 0xFF); header[5] = ((fileSize >> 8) & 0xFF);
  header[6] = ((fileSize >> 16) & 0xFF); header[7] = ((fileSize >> 24) & 0xFF);
  
  memcpy(header + 8, "WAVEfmt ", 8);
  header[16] = 0x10; header[17] = 0; header[18] = 0; header[19] = 0; // Subchunk1Size
  header[20] = 0x01; header[21] = 0; // AudioFormat (PCM)
  header[22] = CHANNELS; header[23] = 0;
  
  header[24] = (sampleRate & 0xFF); header[25] = ((sampleRate >> 8) & 0xFF);
  header[26] = ((sampleRate >> 16) & 0xFF); header[27] = ((sampleRate >> 24) & 0xFF);
  
  header[28] = (byteRate & 0xFF); header[29] = ((byteRate >> 8) & 0xFF);
  header[30] = ((byteRate >> 16) & 0xFF); header[31] = ((byteRate >> 24) & 0xFF);
  
  header[32] = (CHANNELS * BIT_DEPTH / 8); header[33] = 0; // BlockAlign
  header[34] = BIT_DEPTH; header[35] = 0; // BitsPerSample
  
  memcpy(header + 36, "data", 4);
  header[40] = (dataSize & 0xFF); header[41] = ((dataSize >> 8) & 0xFF);
  header[42] = ((dataSize >> 16) & 0xFF); header[43] = ((dataSize >> 24) & 0xFF);

  file.write(header, WAV_HDR_SIZE);
}

/* 
 * ==========================================
 * FUNGSI INTI: AUDIO & RADAR
 * ==========================================
 */
AudioFeature getAudioFeature() {
  const int chunk = 256;
  int32_t buffer[chunk];
  size_t bytesRead;
  
  i2s_read(I2S_NUM_0, buffer, sizeof(buffer), &bytesRead, 10);
  int samples = bytesRead / sizeof(int32_t);
  
  int64_t sqSum = 0;
  int zeroCross = 0;
  int16_t prevSample = 0;

  for (int i = 0; i < samples; i++) {
    int16_t s = (int16_t)(buffer[i] >> 14); // Bit-shift adjustment untuk I2S Mic
    sqSum += (int64_t)s * s;
    if (i > 0 && ((s ^ prevSample) < 0)) zeroCross++;
    prevSample = s;
  }

  AudioFeature f;
  f.rms = (samples > 0) ? (int32_t)sqrt(sqSum / samples) : 0;
  f.zcr = (samples > 0) ? (float)zeroCross / samples : 0;
  return f;
}

void updateRadar() {
  if (radarSerial.available()) {
    uint8_t buf[32];
    int len = radarSerial.readBytes(buf, sizeof(buf));
    for (int i = 0; i <= len - 10; i++) {
      if (buf[i] == 0xF4 && buf[i+1] == 0xF3 && buf[i+2] == 0xF2 && buf[i+3] == 0xF1) {
        currentRadar.movingEnergy = buf[i+11];
        currentRadar.stationaryEnergy = buf[i+14];
        currentRadar.distance = buf[i+15] | (buf[i+16] << 8);
        break;
      }
    }
  }
}

// ==========================================
// FUNGSI KIRIM KE LAPTOP VIA WIFI
// ==========================================
void sendDataViaWiFi(const char* filepath) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] Tidak terhubung ke WiFi!");
    return;
  }

  File file = SD.open(filepath, FILE_READ);
  if (!file) {
    Serial.println("[SD] Gagal membuka file untuk dikirim via WiFi.");
    return;
  }

  uint32_t fsize = file.size();
  String boundary = "----ESP32Boundary";
  
  String bodyStart = "";
  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"moving_energy\"\r\n\r\n";
  bodyStart += String(currentRadar.movingEnergy) + "\r\n";
  
  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"distance\"\r\n\r\n";
  bodyStart += String(currentRadar.distance) + "\r\n";

  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"static_energy\"\r\n\r\n";
  bodyStart += String(currentRadar.stationaryEnergy) + "\r\n";
  
  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"audio\"; filename=\"audio.wav\"\r\n";
  bodyStart += "Content-Type: audio/wav\r\n\r\n";

  String bodyEnd = "\r\n--" + boundary + "--\r\n";

  uint32_t totalLen = bodyStart.length() + fsize + bodyEnd.length();

  WiFiClient client;
  Serial.printf("[WIFI] Connecting to %s:%d...\n", serverHost, serverPort);
  if (client.connect(serverHost, serverPort)) {
    Serial.println("[WIFI] Connected! Mengirim data...");
    
    // HTTP Headers
    client.println("POST /api/predict HTTP/1.1");
    client.print("Host: "); client.println(serverHost);
    client.print("Content-Length: "); client.println(totalLen);
    client.print("Content-Type: multipart/form-data; boundary="); client.println(boundary);
    client.println("Connection: close");
    client.println();
    
    // Body Start (Form fields + File Header)
    client.print(bodyStart);
    
    // File Data
    uint8_t buf[512];
    while (file.available()) {
      int bytesRead = file.read(buf, sizeof(buf));
      client.write(buf, bytesRead);
    }
    file.close();
    
    // Body End
    client.print(bodyEnd);
    
    // Read Response
    Serial.println("[WIFI] Data terkirim. Menunggu respon...");
    while (client.connected() || client.available()) {
      if (client.available()) {
        String line = client.readStringUntil('\n');
        Serial.println(line);
      }
    }
    client.stop();
    Serial.println("[WIFI] Selesai.");
  } else {
    Serial.println("[WIFI] Gagal koneksi ke server!");
    file.close();
  }
}

void recordToSD() {
  if (!SD.exists("/rekaman")) SD.mkdir("/rekaman");

  char filename[32];
  int n = 1;
  while (true) {
    snprintf(filename, sizeof(filename), "/rekaman/baby_%04d.wav", n++);
    if (!SD.exists(filename)) break;
  }

  Serial.printf("\n[REC] Recording to %s...\n", filename);
  digitalWrite(LED_PIN, HIGH);

  File file = SD.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println("[ERROR] Failed to open file for writing");
    return;
  }

  writeWavHeader(file, waveDataSize);

  int32_t i2s_sample;
  size_t read_len;
  uint32_t totalSamples = SAMPLE_RATE * RECORD_SEC;

  for (uint32_t i = 0; i < totalSamples; i++) {
    i2s_read(I2S_NUM_0, &i2s_sample, sizeof(i2s_sample), &read_len, portMAX_DELAY);
    int16_t pcm16 = (int16_t)(i2s_sample >> 14);
    file.write((const uint8_t*)&pcm16, sizeof(pcm16));
  }

  file.close();
  digitalWrite(LED_PIN, LOW);
  Serial.printf("[DONE] Saved. Radar: %dcm\n", currentRadar.distance);
  
  // Mengirim file yang baru saja direkam ke Python via WiFi
  sendDataViaWiFi(filename);
}

/* 
 * ==========================================
 * SETUP & LOOP
 * ==========================================
 */
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  
  // WiFi Connection
  Serial.printf("\nMenghubungkan ke WiFi %s", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[WIFI] Terhubung!");
  Serial.print("[WIFI] IP Address: ");
  Serial.println(WiFi.localIP());

  // SPI & SD Card
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, SD_CS);
  if (!SD.begin(SD_CS)) {
    Serial.println("SD Card Error!");
    while(1); 
  }

  // I2S Configuration
  i2s_config_t i2s_cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 1024,
    .use_apll = false
  };
  i2s_pin_config_t pins = {
    .bck_io_num = I2S_SCK, .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE, .data_in_num = I2S_SD
  };
  i2s_driver_install(I2S_NUM_0, &i2s_cfg, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pins);

  // Radar
  radarSerial.begin(256000, SERIAL_8N1, RADAR_RX, RADAR_TX);

  Serial.println("\n>>> SISTEM MONITORING SIAP <<<");
}

void loop() {
  static uint32_t tStatus = 0, tRadar = 0, tCooldown = 0;
  static int cryCounter = 0;

  if (millis() < tCooldown) return;

  // Update sensor data
  if (millis() - tRadar > 100) { updateRadar(); tRadar = millis(); }

  AudioFeature audio = getAudioFeature();

  // Print Monitoring (5 detik sekali)
  if (millis() - tStatus > 5000) {
    Serial.printf("[MON] RMS: %d | ZCR: %.3f | Dist: %dcm\n", audio.rms, audio.zcr, currentRadar.distance);
    tStatus = millis();
  }

  // Logika Trigger: RMS > 800 & ZCR di range tangisan (0.01 - 0.5)
  if (audio.rms > 800 && audio.zcr > 0.01 && audio.zcr < 0.50) {
    cryCounter++;
    Serial.printf("Checking... (%d/3)\n", cryCounter);
    if (cryCounter >= 3) {
      recordToSD();
      cryCounter = 0;
      tCooldown = millis() + 3000; // Delay antar rekaman
    }
  } else {
    if (cryCounter > 0) cryCounter--;
  }
  
  delay(10); 
}
