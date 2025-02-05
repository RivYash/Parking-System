import cv2
import pickle
import cvzone
import numpy as np

cap = cv2.VideoCapture('carPark.mp4')
width, height = 103, 43

# Load parking space positions
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except FileNotFoundError:
    print("Error: 'CarParkPos' file not found.")
    exit()

# Create trackbars for threshold adjustments
def empty(a):
    pass

cv2.namedWindow("Threshold Controls")
cv2.resizeWindow("Threshold Controls", 640, 240)
cv2.createTrackbar("Block Size", "Threshold Controls", 25, 50, empty)
cv2.createTrackbar("C Value", "Threshold Controls", 16, 50, empty)
cv2.createTrackbar("Blur Kernel", "Threshold Controls", 5, 50, empty)

def checkSpaces():
    spaces = 0
    for pos in posList:
        x, y = pos
        w, h = width, height
        imgCrop = imgThres[y:y + h, x:x + w]
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            color = (0, 200, 0)
            thic = 5
            spaces += 1
        else:
            color = (0, 0, 200)
            thic = 2

        cv2.rectangle(img, (x, y), (x + w, y + h), color, thic)
        cv2.putText(img, str(count), (x, y + h - 6), cv2.FONT_HERSHEY_PLAIN, 1, color, 2)

    cvzone.putTextRect(img, f'Free: {spaces}/{len(posList)}', (50, 60), thickness=3, offset=20,
                       colorR=(0, 200, 0))

while True:
    success, img = cap.read()
    if not success or cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    # Retrieve trackbar values
    blockSize = cv2.getTrackbarPos("Block Size", "Threshold Controls")
    cValue = cv2.getTrackbarPos("C Value", "Threshold Controls")
    blurKernel = cv2.getTrackbarPos("Blur Kernel", "Threshold Controls")
    
    if blockSize % 2 == 0: blockSize += 1
    if blurKernel % 2 == 0: blurKernel += 1

    # Adaptive thresholding
    imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, blockSize, cValue)
    imgThres = cv2.medianBlur(imgThres, blurKernel)
    kernel = np.ones((3, 3), np.uint8)
    imgThres = cv2.dilate(imgThres, kernel, iterations=1)

    # Check parking spaces
    checkSpaces()

    # Display the processed frame
    cv2.imshow("Parking Lot", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
