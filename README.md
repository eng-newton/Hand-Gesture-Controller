## Note this project is still on development sometimes its glitching the machine learning part
# Hand Gesture Controlled Arduino System

This project demonstrates a **hand gesture controlled system** using **Python**, **MediaPipe**, **OpenCV**, and **Arduino**. The system reads gestures from a webcam, classifies them as **OPEN_HAND** or **FIST**, and sends corresponding commands to an Arduino to control connected devices.

---

## **Features**

- Real-time hand gesture recognition using MediaPipe.
- Gesture classification (OPEN_HAND / FIST).
- Sends serial commands to Arduino.
- Works with actuators, LEDs, or motors.
- Easy to extend for robotics or home automation projects.

---

## **Requirements**

### Python
- Python 3.9+
- OpenCV (`pip install opencv-python`)
- MediaPipe (`pip install mediapipe`)
- PySerial (`pip install pyserial`)

### Arduino
- Arduino Uno or compatible
- LED, motor, or other output device
- USB connection to computer

---

## **Python Usage**

1. Connect the Arduino to your computer.
2. Install required Python packages.
3. Update the Arduino port in the Python script if necessary:
   ```python
   arduino_port = "COM4"
