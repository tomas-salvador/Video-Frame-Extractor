# Contact: tomas-salvador (https://github.com/tomas-salvador)

import cv2
import os

# Path to the video file
video_path = '/path/to/video.mp4'  # Replace with the path to your video file
# Path where the frames will be saved
output_folder = 'frames'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Capture the video
cap = cv2.VideoCapture(video_path)

frame_count = 0

while cap.isOpened():
    # Read a frame
    ret, frame = cap.read()
    if not ret:
        break  # If no more frames, exit the loop

    # Save the frame as a JPG image
    frame_filename = os.path.join(output_folder, f'{frame_count:04d}.jpg')
    cv2.imwrite(frame_filename, frame)

    frame_count += 1

# Release the capture
cap.release()

print(f"Extracted {frame_count} frames and saved them in the '{output_folder}' folder.")
