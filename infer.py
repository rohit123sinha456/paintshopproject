import cv2

from ultralytics import solutions

cap = cv2.VideoCapture("street.mp4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Define region points
region_points = [(20, 400), (1080, 400)]  # For line counting
# region_points = [(20, 400), (1080, 400), (1080, 360), (20, 360)]  # For rectangle region counting
# region_points = [(20, 400), (1080, 400), (1080, 360), (20, 360), (20, 400)]  # For polygon region counting

# Video writer
video_writer = cv2.VideoWriter("object_counting_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# Init Object Counter
counter = solutions.ObjectCounter(
    show=True,  # Display the output
    region=region_points,  # Pass region points
    model="yolo11n.pt",  # model="yolo11n-obb.pt" for object counting using YOLO11 OBB model.
    # classes=[0, 2],  # If you want to count specific classes i.e person and car with COCO pretrained model.
    show_in=True,  # Display in counts
    show_out=True,  # Display out counts
    verbose=False
    # line_width=2,  # Adjust the line width for bounding boxes and text display
)

# Process video
frame_count = 0
seconds_interval = 10 

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    im0 = counter.count(im0)
    video_writer.write(im0)
    frame_count += 1

    # Check if it's time to print the counts
    if frame_count % (fps * seconds_interval) == 0:
        print(f"Time: {frame_count // fps} seconds")
        print(f"In counts: {counter.in_count}")  # Accessing current counts
        print(f"Out counts: {counter.out_count}")  # Accessing current counts

cap.release()
video_writer.release()
cv2.destroyAllWindows()