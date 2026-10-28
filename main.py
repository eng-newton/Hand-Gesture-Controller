
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core import base_options as bo
import serial
import time

# ================= SERIAL SETUP =================
ARDUINO_PORT = "COM5"
BAUD_RATE = 9600

arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
arduino.reset_input_buffer()

# ================= MEDIAPIPE SETUP =================
BaseOptions = bo.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)


# ================= GESTURE CLASSIFICATION =================
def classify_gesture(lm):
    # Finger tip and lower joint landmarks
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    # Detect extended fingers using vertical position
    fingers = [
        lm[tip].y < lm[pip].y
        for tip, pip in zip(tips, pips)
    ]

    index, middle, ring, pinky = fingers

    # Approximate thumb extension for a mirrored webcam.
    # This works best when the palm faces the camera.
    thumb_extended = lm[4].x < lm[3].x

    # Thumbs up: thumb raised and all four fingers folded
    thumb_raised = (
        lm[4].y < lm[3].y
        and lm[4].y < lm[2].y
    )

    if thumb_raised and not any(fingers):
        return "THUMBS_UP"

    # Pinky only
    if pinky and not index and not middle and not ring:
        return "PINKY"

    # Fist: all four fingers folded
    if not any(fingers):
        return "FIST"

    # Four fingers extended, thumb folded
    if all(fingers) and not thumb_extended:
        return "FOUR_FINGERS"

    # Open hand: all four fingers and thumb extended
    if all(fingers) and thumb_extended:
        return "OPEN_HAND"

    # Three fingers
    if index and middle and ring and not pinky:
        return "THREE_FINGERS"

    # Two fingers
    if index and middle and not ring and not pinky:
        return "TWO_FINGERS"

    # Index finger only
    if index and not middle and not ring and not pinky:
        return "ONE_FINGER"

    return "UNKNOWN"


# ================= COMMAND MAPPING =================
gesture_map = {
    "ONE_FINGER": "LEDS_1",
    "TWO_FINGERS": "LEDS_2",
    "THREE_FINGERS": "LEDS_3",
    "FOUR_FINGERS": "LEDS_4",
    "OPEN_HAND": "LEDS_5",
    "THUMBS_UP": "RELAY_BLINK",
    "FIST": "ALL_OFF",
    "PINKY": "ALL_OFF",
}


# ================= WEBCAM =================
cap = cv2.VideoCapture(0)

last_command = None

try:
    with HandLandmarker.create_from_options(options) as landmarker:

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Could not read webcam.")
                break

            # Mirror the image
            frame = cv2.flip(frame, 1)

            h, w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            result = landmarker.detect(mp_image)

            gesture = None

            if result.hand_landmarks:
                lm = result.hand_landmarks[0]
                gesture = classify_gesture(lm)

                # Draw landmarks
                for point in lm:
                    x = int(point.x * w)
                    y = int(point.y * h)

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 255, 0),
                        -1
                    )

                command = gesture_map.get(gesture)

                # Send commands only when the gesture changes
                if command and command != last_command:
                    arduino.write(
                        (command + "\n").encode("utf-8")
                    )

                    print(
                        f"Gesture: {gesture} -> Command: {command}"
                    )

                    last_command = command

            else:
                # Allow the same gesture to trigger again
                # after the hand leaves the camera view.
                last_command = None

            # ================= DISPLAY =================
            instructions = [
                "1 finger: LED pin 6",
                "2 fingers: pins 6, 7",
                "3 fingers: pins 6, 7, 8",
                "4 fingers: pins 6, 7, 8, 9",
                "Open hand: all 5 LEDs",
                "Thumbs up: blink bulb",
                "Fist / pinky: all OFF",
                "Press ESC to exit"
            ]

            for i, line in enumerate(instructions):
                cv2.putText(
                    frame,
                    line,
                    (10, 25 + i * 24),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.52,
                    (255, 255, 255),
                    1
                )

            if gesture and gesture != "UNKNOWN":
                cv2.putText(
                    frame,
                    "GESTURE: " + gesture,
                    (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

            cv2.imshow("Hand Gesture LED and Bulb Control", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

finally:
    # Switch everything off when Python exits
    try:
        arduino.write(b"ALL_OFF\n")
        time.sleep(0.2)
    except (serial.SerialException, OSError):
        pass

    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
