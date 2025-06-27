import cv2
import numpy as np
import face_recognition as face_rec
import os
import pyttsx3 as text_speech
from mtcnn import MTCNN
import serial as ser
import pandas as pd
from datetime import datetime

# Initialize text-to-speech engine
engine = text_speech.init()

# Initialize serial communication with Arduino
ser = ser.Serial('COM4', 9600, timeout=1)

# Helper function to resize image
def resize(img, size):
    width = int(img.shape[1] * size)
    height = int(img.shape[0] * size)
    dimension = (width, height)
    return cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)

# Path to user images for encoding comparison
path = "user_images"
user_images = []
user_names = []

# Load all user images and names
myList = os.listdir(path)
for user in myList:
    curr_image = cv2.imread(f'{path}/{user}')
    user_images.append(curr_image)
    user_names.append(os.path.splitext(user)[0])

# Helper function to find encodings for the loaded images
def find_encodings(images):
    encoding_list = []
    for img in images:
        img_resized = resize(img, 0.50)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        encode_img = face_rec.face_encodings(img_rgb)
        if encode_img:
            encoding_list.append(encode_img[0])
    return encoding_list

# Get the face encodings for all stored images
encode_list = find_encodings(user_images)

# Initialize MTCNN for face detection
detector = MTCNN()

# Start video capture from the webcam
capture = cv2.VideoCapture(0)

# Initialize DataFrames
attendance_df = pd.DataFrame(columns=["Name", "Date", "Day", "Time"])
attendance_log_df = pd.DataFrame(columns=["Name", "Date", "Day", "Time"])

while True:
    success, frame = capture.read()
    if not success:
        print("Failed to capture frame from camera")
        continue

    # Resize frame for faster processing
    smaller_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = cv2.cvtColor(smaller_frame, cv2.COLOR_BGR2RGB)

    # Detect faces using MTCNN
    faces = detector.detect_faces(rgb_small_frame)

    for face in faces:
        x, y, width, height = face['box']
        face_location = (y, x + width, y + height, x)

        # Extract face encoding using face_recognition
        face_encoding = face_rec.face_encodings(rgb_small_frame, [face_location])

        if face_encoding:
            face_encoding = face_encoding[0]
            # Compare the encoding with known encodings
            face_distances = face_rec.face_distance(encode_list, face_encoding)
            best_match_index = np.argmin(face_distances)
            if face_distances[best_match_index] < 0.7:  # Stricter threshold
                name = user_names[best_match_index].upper()

                # Get current time and date
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                day_str = now.strftime("%A")
                time_str = now.strftime("%H:%M:%S")

                # Log attendance if not already recorded today
                if not ((attendance_df['Name'] == name) & (attendance_df['Date'] == date_str)).any():
                    new_row = pd.DataFrame([{"Name": name, "Date": date_str, "Day": day_str, "Time": time_str}])
                    attendance_df = pd.concat([attendance_df, new_row], ignore_index=True)

                # Always log the pass-through instance
                new_log_row = pd.DataFrame([{"Name": name, "Date": date_str, "Day": day_str, "Time": time_str}])
                attendance_log_df = pd.concat([attendance_log_df, new_log_row], ignore_index=True)

                # Save DataFrames to Excel files
                attendance_df.to_excel("attendance.xlsx", index=False)
                attendance_log_df.to_excel("attendance_log.xlsx", index=False)

                # Send the open door signal to Arduino when a match is found
                ser.write(b'open_door\n')

            else:
                name = "Unknown"

            # Scale back the face location to full size
            top, right, bottom, left = [v * 2 for v in face_location]

            # Draw a rectangle around the face
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            # Text-to-speech
            statement = f"The detected face is {name}" if name != "Unknown" else "No match found"
            engine.say(statement)
            engine.runAndWait()

    # Display the video feed with annotations
    cv2.imshow("Webcam Face Recognition", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
capture.release()
cv2.destroyAllWindows()
ser.close()
