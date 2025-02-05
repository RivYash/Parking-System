from flask import Flask, jsonify
from flask_cors import CORS  # To handle CORS for requests from different origins
import cv2
import pickle
import numpy as np
from pymongo import MongoClient
import threading  # For running the real-time update in the background

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection
client = MongoClient("mongodb+srv://mongo:GqJDx8ymHaFGUcOM@cluster0.4icd0.mongodb.net/?retryWrites=true&w=majority")
db = client["parking_system"]
collection = db["parking_data"]

# Load parking space positions for both cameras
with open('CarParkPos_Camera1', 'rb') as f:
    posList1 = pickle.load(f)

with open('CarParkPos_Camera2', 'rb') as f:
    posList2 = pickle.load(f)

# Open video files for both cameras
cap1 = cv2.VideoCapture('carPark1.mp4')
cap2 = cv2.VideoCapture('carPark2.mp4')

# Dimensions of parking space
width, height = 103, 43

# Camera locations (latitude and longitude)
camera_locations = {
    "camera1": {"latitude": 15.518882, "longitude": 73.835982},
    "camera2": {"latitude": 15.526793, "longitude": 73.829386},
}

# Function to check parking spaces
def checkSpaces(cap, posList, width, height, v_theshold):
    success, img = cap.read()
    if not success or cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, img = cap.read()

    # Convert image to grayscale and apply filters
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 25, 16)
    imgThres = cv2.medianBlur(imgThres, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgThres = cv2.dilate(imgThres, kernel, iterations=1)

    spaces = 0
    for pos in posList:
        x, y = pos
        w, h = width, height
        imgCrop = imgThres[y:y + h, x:x + w]
        count = cv2.countNonZero(imgCrop)
        if count < v_theshold:  # If parking space is empty
            spaces += 1

    totalSpaces = len(posList)
    return spaces, totalSpaces

# Function to continuously update data in MongoDB
def update_parking_data():
    while True:
        # Get parking data for both cameras
        spaces1, totalSpaces1 = checkSpaces(cap1, posList1, 103, 43, 900)
        spaces2, totalSpaces2 = checkSpaces(cap2, posList2, 103, 43, 900)

        # Prepare data for MongoDB update
        camera1_data = {
            "camera_id": "camera1",
            "free_spaces": spaces1,
            "total_spaces": totalSpaces1,
            "latitude": camera_locations["camera1"]["latitude"],
            "longitude": camera_locations["camera1"]["longitude"]
        }
        camera2_data = {
            "camera_id": "camera2",
            "free_spaces": spaces2,
            "total_spaces": totalSpaces2,
            "latitude": camera_locations["camera2"]["latitude"],
            "longitude": camera_locations["camera2"]["longitude"]
        }

        # Update MongoDB
        collection.update_one(
            {"camera_id": "camera1"},
            {"$set": camera1_data},
            upsert=True
        )
        collection.update_one(
            {"camera_id": "camera2"},
            {"$set": camera2_data},
            upsert=True
        )

# Start the real-time update in a separate thread
thread = threading.Thread(target=update_parking_data, daemon=True)
thread.start()

# Define route to check if the server is running
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running and updating data in real-time."})

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
