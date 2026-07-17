"""Live webcam object detection demo.

Captures frames from the default webcam, runs YOLO11 detection on each
frame via the ObjectDetector class, and displays bounding boxes with
labels and confidence scores in a live OpenCV window.

Press 'q' to quit.
"""
import logging
import sys
from pathlib import Path

import cv2

# Allow imports from the project root when running this file directly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from detection.detector import ObjectDetector
from analytics.counter import ObjectCounter
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def draw_detections(frame, result, class_names: dict) -> None:
    """Draw bounding boxes, labels, and confidence scores directly onto the frame.

    Args:
        frame: The image (NumPy array) to draw on, modified in place.
        result: The Ultralytics Results object from detector.detect().
        class_names: Mapping of class ID to human-readable class name.
    """
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        track_id = int(box.id[0]) if box.id is not None else -1
        label = f"ID:{track_id} {class_names[class_id]} {confidence:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame, label, (x1, max(y1 - 10, 10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
        )


def draw_counts(frame, counts: dict) -> None:
    """Draw a running tally of unique objects seen, top-left corner.

    Args:
        frame: The image to draw on, modified in place.
        counts: Dict mapping class name to unique count, from ObjectCounter.
    """
    y_offset = 30
    cv2.putText(
        frame, "Unique objects seen:", (10, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
    )
    for i, (class_name, count) in enumerate(counts.items(), start=1):
        text = f"{class_name}: {count}"
        cv2.putText(
            frame, text, (10, y_offset + (i * 25)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2,
        )


def run_webcam_demo() -> None:
    """Open the default webcam and run live detection until 'q' is pressed."""
    detector = ObjectDetector(confidence=0.65)
    counter = ObjectCounter()

    cap = cv2.VideoCapture(0)  # 0 = default webcam
    if not cap.isOpened():
        logger.error("Could not open webcam. Check camera permissions for Terminal/VS Code.")
        return

    logger.info("Webcam opened. Press 'q' in the video window to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to read frame from webcam.")
            break

        result = detector.track(frame)
        draw_detections(frame, result, detector.class_names)
        counter.update(result, detector.class_names)
        draw_counts(frame, counter.get_counts())

        cv2.imshow("Real-Time Object Detection - Press 'q' to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            logger.info("Quit key pressed. Closing webcam.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_webcam_demo()