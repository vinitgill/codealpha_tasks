"""Streamlit dashboard for real-time object detection and tracking.

Supports three input modes: live webcam, image upload, and video upload.
Reuses the ObjectDetector class for consistent detection/tracking logic
across all three modes.
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parent.parent))

from detection.detector import ObjectDetector


def draw_detections(frame, result, class_names: dict) -> None:
    """Draw bounding boxes, labels, confidence, and tracking IDs onto the frame."""
    if result.boxes is None:
        return
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


def summarize_classes(result, class_names: dict) -> str:
    """Build a human-readable summary of detected classes and their counts.

    Args:
        result: The Ultralytics Results object.
        class_names: Mapping of class ID to human-readable class name.

    Returns:
        A string like "person: 3, cell phone: 1, clock: 2".
    """
    if result.boxes is None or len(result.boxes) == 0:
        return "No objects detected."

    counts: dict[str, int] = {}
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = class_names[class_id]
        counts[class_name] = counts.get(class_name, 0) + 1

    return ", ".join(f"{name}: {count}" for name, count in sorted(counts.items()))


@st.cache_resource
def load_detector(confidence: float) -> ObjectDetector:
    """Load the detector once and cache it across Streamlit reruns."""
    return ObjectDetector(model_path="yolo11s.pt", confidence=confidence)


def run_webcam_mode(detector: ObjectDetector) -> None:
    st.warning("Check the box below to start. Uncheck it to stop.")
    run = st.checkbox("Start Webcam", key="webcam_running")
    frame_placeholder = st.empty()
    fps_placeholder = st.empty()

    if run:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open webcam. Close other apps using the camera and retry.")
            return

        objects_placeholder = st.empty()
        prev_time = time.time()
        while st.session_state.get("webcam_running", False):
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read frame from webcam.")
                break

            result = detector.track(frame)
            draw_detections(frame, result, detector.class_names)

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
            prev_time = curr_time

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB")
            fps_placeholder.metric("FPS", f"{fps:.1f}")
            objects_placeholder.info(f"Detected: {summarize_classes(result, detector.class_names)}")

        cap.release()


def run_image_mode(detector: ObjectDetector) -> None:
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        result = detector.track(frame, persist=False)
        draw_detections(frame, result, detector.class_names)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, channels="RGB", caption="Detection Result")
        st.success(f"Detected: {summarize_classes(result, detector.class_names)}")

def run_video_mode(detector: ObjectDetector) -> None:
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
    if uploaded_file is not None:
        temp_path = Path("outputs") / uploaded_file.name
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_bytes(uploaded_file.read())

        cap = cv2.VideoCapture(str(temp_path))
        frame_placeholder = st.empty()
        objects_placeholder = st.empty()
        status_placeholder = st.empty()
        stop_button = st.button("Stop Video")

        class_totals: dict[str, set] = {}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or stop_button:
                break

            result = detector.track(frame, persist=True)
            draw_detections(frame, result, detector.class_names)

            if result.boxes.id is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = detector.class_names[class_id]
                    track_id = int(box.id[0])
                    class_totals.setdefault(class_name, set()).add(track_id)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB")
            objects_placeholder.info(f"Currently visible: {summarize_classes(result, detector.class_names)}")

        cap.release()
        summary = ", ".join(f"{name}: {len(ids)}" for name, ids in sorted(class_totals.items())) or "No objects detected."
        status_placeholder.success(f"Done — unique objects seen: {summary}")

def main() -> None:
    st.set_page_config(page_title="Real-Time Object Detection & Tracking", layout="wide")
    st.title("🎯 Real-Time Object Detection & Multi-Object Tracking")
    st.markdown("Powered by **YOLO11** + **BoT-SORT** — built by Vinit Gill")

    st.sidebar.header("Settings")
    confidence = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
    mode = st.sidebar.radio("Input Source", ["Webcam", "Image Upload", "Video Upload"])

    detector = load_detector(confidence)
    detector.confidence = confidence  # allow live threshold updates

    if mode == "Webcam":
        run_webcam_mode(detector)
    elif mode == "Image Upload":
        run_image_mode(detector)
    else:
        run_video_mode(detector)


if __name__ == "__main__":
    main()