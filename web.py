import cv2
import numpy as np
import serial
import serial.tools.list_ports
from ultralytics import YOLO
from flask import Flask, Response
import threading
import time
import os
import sys
import webbrowser

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

BAUD_RATE = 115200

model_path = resource_path('yolo26n.pt')
model = YOLO(model_path)

app = Flask(__name__)
latest_frame = None
frame_lock = threading.Lock()

def find_esp32_port():
    """ESP32-CAM 포트 자동 찾기"""
    print("🔍 Searching for ESP32-CAM...")
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # ESP32는 보통 "USB-SERIAL", "CP210", "CH340" 등으로 나타남
        if any(keyword in port.description.upper() for keyword in ['USB', 'SERIAL', 'CP210', 'CH340', 'UART']):
            print(f"✓ Found possible device: {port.device} ({port.description})")
            try:
                # 포트 테스트
                ser = serial.Serial(port.device, BAUD_RATE, timeout=1, dsrdtr=False, rtscts=False)
                ser.setDTR(False)
                ser.setRTS(False)
                time.sleep(0.5)
                
                # 데이터가 오는지 확인
                if ser.in_waiting > 0:
                    ser.close()
                    print(f"✅ ESP32-CAM detected on {port.device}")
                    return port.device
                ser.close()
            except:
                continue
    
    # 못 찾으면 사용 가능한 포트 출력
    print("\n❌ ESP32-CAM not found automatically.")
    print("Available ports:")
    for port in ports:
        print(f"  - {port.device}: {port.description}")
    
    # 첫 번째 포트 시도
    if ports:
        default_port = ports[0].device
        print(f"\n⚠️ Trying default: {default_port}")
        return default_port
    
    return None

def read_serial():
    global latest_frame
    
    # 자동으로 포트 찾기
    SERIAL_PORT = find_esp32_port()
    
    if not SERIAL_PORT:
        print("❌ No serial port found!")
        return
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1, dsrdtr=False, rtscts=False)
        ser.setDTR(False)
        ser.setRTS(False)
        print(f"✓ Connected to {SERIAL_PORT}")
    except Exception as e:
        print(f"❌ Serial Error: {e}")
        return
    
    while True:
        try:
            if ser.in_waiting > 0:
                char = ser.read(1)
                if char == b'S':
                    rest = ser.read(4)
                    if rest == b'TART':
                        size_data = ser.read(4)
                        if len(size_data) < 4: continue
                        size = int.from_bytes(size_data, byteorder='little')
                        
                        img_data = b''
                        start_time = time.time()
                        while len(img_data) < size and (time.time() - start_time) < 1.0:
                            chunk = ser.read(size - len(img_data))
                            if chunk:
                                img_data += chunk
                        
                        if len(img_data) == size:
                            nparr = np.frombuffer(img_data, np.uint8)
                            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            if frame is not None:
                                results = model(frame, verbose=False, imgsz=320)
                                annotated = results[0].plot()
                                with frame_lock:
                                    latest_frame = annotated
                                #print(f"✅ Frame: {size} bytes")
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(1)

def generate():
    while True:
        with frame_lock:
            if latest_frame is not None:
                ret, buffer = cv2.imencode('.jpg', latest_frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.04)

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>ESP32-CAM YOLO</title>
        <meta charset="utf-8">
    </head>
    <body style='background:#000;text-align:center;margin:0;padding:20px;'>
        <h1 style='color:#0f0;font-family:monospace;'>🎥 ESP32-CAM + YOLO</h1>
        <img src='/stream' style='width:80%;border:3px solid #0f0;'>
        <p style='color:#888;margin-top:20px;'>자동 포트 탐지 | 속도: 115200</p>
    </body>
    </html>
    """

@app.route('/stream')
def stream():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 ESP32-CAM YOLO Server")
    print("="*60 + "\n")
    
    threading.Thread(target=read_serial, daemon=True).start()
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
