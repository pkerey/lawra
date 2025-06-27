import os
import cv2
from mtcnn import MTCNN
from keras_facenet import FaceNet

# Ensure the directory for captured images exists
if not os.path.exists('Captured Img'):
    os.makedirs('Captured Img')

# Initialize MTCNN for face detection
mtcnn = MTCNN()

# Initialize FaceNet for face embeddings (optional, not used in this snippet but could be used later)
facenet = FaceNet()

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Set the counter for the image filename
img_counter = 0

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image from webcam.")
        break

    # Detect faces in the frame using MTCNN
    faces = mtcnn.detect_faces(frame)

    # Draw bounding boxes around the detected faces
    for face in faces:
        x, y, w, h = face['box']
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame with bounding boxes
    cv2.imshow('Webcam', frame)

    # Press 'c' to capture an image
    if cv2.waitKey(1) & 0xFF == ord('c'):
        # Check if at least one face is detected
        if len(faces) > 0:
            img_name = f"Captured Img/img_{img_counter}.jpg"
            cv2.imwrite(img_name, frame)
            print(f"Image {img_counter} saved as {img_name}")
            img_counter += 1

    # Press 'q' to quit
    elif cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
