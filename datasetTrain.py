import os
import glob
import pickle
import cv2
from mtcnn import MTCNN
from keras_facenet import FaceNet

# Initialize MTCNN for face detection
mtcnn = MTCNN()

# Initialize the FaceNet model for face embeddings
facenet = FaceNet()

# Create a dictionary to store the face embeddings
face_embeddings_dict = {}

# Directory containing images for each class (person)
image_directory = "images"  # Ensure this path is correct
if not os.path.exists(image_directory):
    print(f"Directory {image_directory} does not exist.")
else:
    for class_dir in glob.glob(os.path.join(image_directory, "*")):
        class_label = os.path.basename(class_dir)
        face_embeddings_dict[class_label] = []

        # Iterate through the face images in the class directory
        for img_path in glob.glob(os.path.join(class_dir, "*.jpg")):
            # Load the face image
            img = cv2.imread(img_path)
            if img is None:
                print(f"Could not load image: {img_path}")
                continue  # Skip if image can't be loaded

            # Detect faces in the image using MTCNN
            faces = mtcnn.detect_faces(img)
            if len(faces) == 0:
                print(f"No face detected in image: {img_path}")
                continue  # Skip if no face is detected

            # Process each detected face (though usually there is one per image)
            for i, face in enumerate(faces):
                confidence = face['confidence']
                x, y, w, h = face['box']
                keypoints = face['keypoints']

                print(f"Image: {img_path} | Confidence: {confidence:.2f} | Box: {x, y, w, h}")

                # Ensure coordinates are within the image bounds
                x, y = max(0, x), max(0, y)
                w, h = min(img.shape[1] - x, w), min(img.shape[0] - y, h)

                face_img = img[y:y+h, x:x+w]

                # Resize the face image to a uniform size (160x160 for FaceNet)
                face_img = cv2.resize(face_img, (160, 160))

                # Extract the face embedding
                face_embedding = facenet.extract(face_img)

                # Store the face embedding in the dictionary
                face_embeddings_dict[class_label].append(face_embedding)

                # Draw the bounding box and confidence on the image
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(img, f"Conf: {confidence:.2f}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Draw keypoints (eyes, nose, mouth) on the image
                for key, point in keypoints.items():
                    cv2.circle(img, point, 2, (0, 0, 255), 2)

            # Display the image with bounding boxes, confidence, and keypoints
            cv2.imshow("Face Detection", img)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break

    # Save the face embeddings dictionary to a file (e.g., pickle)
    with open("face_embeddings_dict.pkl", "wb") as f:
        pickle.dump(face_embeddings_dict, f)

    # Close all OpenCV windows after processing
    cv2.destroyAllWindows()

    print("Face embeddings successfully saved.")
