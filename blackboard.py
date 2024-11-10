import numpy as np
import cv2
import mediapipe as mp
import time
from collections import deque

# Initialize webcam
cap = cv2.VideoCapture(0)
frameWidth, frameHeight = 640, 480
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(10, 150)

# Initialize MediaPipe and drawing tools
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Set up drawing variables
board = np.zeros((frameHeight, frameWidth, 3), dtype=np.uint8)
board_bg = np.zeros((frameHeight, frameWidth, 3), dtype=np.uint8)
prevx, prevy = 0, 0

# Buffer to smooth out the drawing
points_buffer = deque(maxlen=5)  # Store the last 5 points for averaging

# Function to calculate distance
def calculate_distance(x1, y1, x2, y2):
    return int(np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))

pTime = 0  # Initialize previous time for FPS calculation

while True:
    cx, cy = 0, 0
    ix, iy, jx, jy = 0, 0, 0, 0
    board_pointer = np.zeros((frameHeight, frameWidth, 3), dtype=np.uint8)
    
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    # Process hand landmarks
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                
                if id == 8:  # Index finger tip
                    ix, iy = cx, cy
                    cv2.circle(board_pointer, (ix, iy), 5, (0, 0, 255), cv2.FILLED)
                    points_buffer.append((ix, iy))  # Add point to buffer
                elif id == 4:  # Thumb tip
                    jx, jy = cx, cy
                    
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    
    # Calculate FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime - pTime != 0 else 0
    pTime = cTime  # Update previous time

    # Calculate distance for drawing
    dist = calculate_distance(ix, iy, jx, jy)

    # Only draw when fingers are close enough
    if len(points_buffer) > 0:
        avg_x = int(np.mean([p[0] for p in points_buffer]))
        avg_y = int(np.mean([p[1] for p in points_buffer]))
        
        if dist < 50:  # Adjust distance threshold if needed
            if prevx == 0 and prevy == 0:
                prevx, prevy = avg_x, avg_y
            cv2.line(board_bg, (prevx, prevy), (avg_x, avg_y), (0, 255, 0), 5)
            prevx, prevy = avg_x, avg_y
        else:
            prevx, prevy = 0, 0

    # Display FPS on screen
    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    board = cv2.add(board_bg, board_pointer)
    
    # Display images
    cv2.imshow("Image", img)
    cv2.imshow("Board", board)
    
    # Keypress actions
    key = cv2.waitKey(1) & 0xFF
    if key == ord('x'):  # Clear board
        board_bg = np.zeros((frameHeight, frameWidth, 3), dtype=np.uint8)
    elif key == 27:  # Exit on 'ESC' key
        break

cap.release()
cv2.destroyAllWindows()
