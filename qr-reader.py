import os
import time
import webbrowser

import cv2

from dotenv import load_dotenv


def scan_qr_with_scanner():
    """Uses a scanner to scan a QR code"""
    pass


def scan_qr_with_camera():
    """Uses a camera to scan a QR code"""
    # TODO: Search for camera if one does exist with the default ID
    # TODO: Allow user to set camera ID in env file
    camera_id = 0
    delay = 1
    window_name = 'OpenCV QR Code'

    qcd = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(camera_id)

    while True:
        ret, frame = cap.read()

        if ret:
            ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
            if ret_qr:
                for s, p in zip(decoded_info, points):
                    if s:
                        print('QR Data:')
                        print(s + '\n')
                        webbrowser.open(s)
                        time.sleep(3)
                        break
                    else:
                        color = (0, 0, 255)
                    frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
            cv2.imshow(window_name, frame)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break
        # TODO: Add the option to toggle cameras if multiple are detected

    cv2.destroyWindow(window_name)


def start_program():
    # Load environment variables from .env file
    load_dotenv()

    # Get the env variable for determining which device to scan QR with: Scanner or Camera
    env_var_name = 'INPUT_TYPE'
    input_type = os.getenv(env_var_name)

    if input_type == 'Scanner':
        scan_qr_with_scanner()
    elif input_type == 'Camera':
        scan_qr_with_camera()
    else:
        print(f"Invalid input type. Check the '{env_var_name}' variable in the .env file.")


if __name__ == '__main__':
    start_program()
