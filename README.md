# 🎯 ESP32-CAM × YOLO26 — Real-Time Object Detection over Serial

<p align="center">
  <img src="https://img.shields.io/badge/ESP32--CAM-Serial%20Stream-blue?style=for-the-badge&logo=espressif&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLO26-Ultralytics-purple?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Web%20UI-green?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

<p align="center">
  <b>No Wi-Fi. No HTTP. Just raw bytes through a wire — and a neural network on the other end.</b>
</p>

---

## 💡 What Is This?

Most ESP32-CAM projects stream video over Wi-Fi. **This one doesn't.**

Instead, it pushes raw JPEG frames through the **USB serial port** at 115200 baud, where a host PC picks them up, runs **YOLOv8 inference in real time**, and serves the annotated stream via a local web interface.

**Why serial?** Because sometimes Wi-Fi isn't an option — embedded environments, RF-restricted zones, or when you just want a dead-simple wired connection with zero network config.

```
┌─────────────┐    Serial (USB)    ┌──────────────────┐    HTTP    ┌─────────┐
│  ESP32-CAM   │ ──── 115200 ────▶ │  Python + YOLO26  │ ────────▶ │ Browser │
│  JPEG frames │    binary proto   │  Flask server     │  :5000   │  Viewer │
└─────────────┘                    └──────────────────┘           └─────────┘
```

## ✨ Features

- **Plug & Play** — Auto-detects ESP32-CAM serial port (CP210x, CH340, FTDI)
- **Custom Binary Protocol** — `START` header + 4-byte little-endian size + JPEG payload
- **Real-Time YOLO Inference** — Runs YOLOv8n at 320×240 for low-latency detection
- **Web Dashboard** — Live MJPEG stream served on `localhost:5000`
- **Standalone Packaging** — PyInstaller-ready with `resource_path()` support

## 🚀 Quick Start

### 1. Flash the ESP32-CAM

Open `esp32cam_serial.ino` in Arduino IDE:

- **Board:** `AI Thinker ESP32-CAM`
- **Upload Speed:** `115200`
- **Partition Scheme:** `Huge APP (3MB No OTA)`

Upload, then disconnect GPIO0 from GND and reset.

### 2. Run the Python Server

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/esp32cam-yolo-serial.git
cd esp32cam-yolo-serial

# Install dependencies
pip install ultralytics flask pyserial opencv-python numpy

# Run
python main.py
```

The browser opens automatically at **http://localhost:5000** 🎉

## 📡 Serial Protocol

The ESP32-CAM sends each frame using a minimal binary protocol:

| Field | Size | Description |
|-------|------|-------------|
| `START` | 5 bytes | ASCII header (`0x53 0x54 0x41 0x52 0x54`) |
| `size` | 4 bytes | JPEG payload length (little-endian uint32) |
| `payload` | *size* bytes | Raw JPEG data |

The Python receiver implements a simple state machine: sync on `S` → verify `TART` → read size → read payload → decode → infer.

## 📂 Project Structure

```
.
├── main.py                  # Python server (serial reader + YOLO + Flask)
├── esp32cam_serial/
│   └── esp32cam_serial.ino  # Arduino firmware for ESP32-CAM
├── yolo26n.pt               # YOLOv8 custom model weights
├── requirements.txt
└── README.md
```

## ⚙️ Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `BAUD_RATE` | `115200` | Serial communication speed |
| `imgsz` | `320` | YOLO inference resolution |
| `jpeg_quality` | `12` | ESP32 JPEG compression (1–63, lower = better) |
| `FRAMESIZE` | `QVGA` | Camera resolution (320×240) |
| `delay()` | `100ms` | Frame interval (~10 FPS target) |

## 🛠️ Troubleshooting

| Symptom | Fix |
|---------|-----|
| `No serial port found` | Check USB cable (must be data-capable, not charge-only) |
| Garbled frames | Ensure baud rate matches on both sides (115200) |
| Low FPS | Reduce `jpeg_quality` value or increase `delay()` |
| Port busy | Close Arduino Serial Monitor before running |
| YOLO model not found | Place `yolo26n.pt` in the same directory as `main.py` |

## 📊 Performance

> Tested on a laptop with Intel i7 + integrated GPU

| Metric | Value |
|--------|-------|
| Serial throughput | ~8–12 FPS @ QVGA |
| YOLO inference | ~30–50ms per frame |
| End-to-end latency | ~150–200ms |
| JPEG size per frame | ~5–15 KB |

## 🔮 Roadmap

- [ ] Higher baud rate support (230400 / 460800)
- [ ] Detection result feedback to ESP32 (e.g., trigger GPIO on detection)
- [ ] Multi-camera support
- [ ] ONNX / TensorRT acceleration
- [ ] Electron desktop app packaging

## 📜 License

MIT License — do whatever you want with it.

---

<p align="center">
  Built with ☕ and too many USB cables.<br/>
  If this helped you, drop a ⭐
</p>
