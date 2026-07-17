# Real-Time Object Detection and Multi-Object Tracking using YOLO

A production-style computer vision application for real-time object detection and multi-object tracking, built with YOLO11 and BoT-SORT. Supports live webcam, image upload, and video upload — all through an interactive Streamlit dashboard.

## Features

- **Real-time detection** via YOLO11, with bounding boxes, class labels, and confidence scores
- **Multi-object tracking** via BoT-SORT, assigning persistent IDs to objects across frames
- **Three input modes**: live webcam, image upload, video upload
- **Adjustable confidence threshold** via UI slider
- **Per-class detection summaries** showing what was detected and how many
- **Auto GPU/MPS/CPU detection** — runs accelerated on Apple Silicon (MPS) or NVIDIA GPUs (CUDA), falls back to CPU
- **Reusable, OOP-structured codebase** with logging, type hints, and docstrings throughout

## Tech Stack & Model Choices

| Component | Choice | Why |
|---|---|---|
| Detection model | YOLO11 (small variant) | Best balance of accuracy and real-time speed for this use case; mature Ultralytics tooling and deployment support. Compared against YOLOv12 and RT-DETR — both offer marginal accuracy gains but with less mature tooling for this project's timeline. |
| Tracker | BoT-SORT | Ships natively with Ultralytics; combines Kalman-filter motion prediction with the Hungarian algorithm for frame-to-frame matching, plus camera motion compensation. Compared against ByteTrack (lighter, no camera compensation) and DeepSORT (heavier, not natively integrated). |
| UI | Streamlit | Fast to build a functional interactive dashboard without frontend code |
| Core libraries | OpenCV, PyTorch, Ultralytics, NumPy, Pillow | Industry-standard computer vision and ML stack |

## Project Structure
```text
ObjectDetectionAI/
├── app/                # Standalone demo scripts (webcam CLI demo)
├── analytics/          # Unique object counting logic
├── detection/          # ObjectDetector class — YOLO11 wrapper
├── ui/                 # Streamlit dashboard
├── tests/              # Environment/setup verification scripts
├── models/             # Downloaded model weights (gitignored)
├── outputs/             # Runtime outputs, uploaded videos (gitignored)
├── requirements.txt
├── README.md
└── main.py
```

## Setup Instructions

1. **Clone the repository**
```bash
   git clone <your-repo-url>
   cd ObjectDetectionAI
```

2. **Create and activate a virtual environment** (Python 3.12 recommended)
```bash
   python3.12 -m venv venv
   source venv/bin/activate      # macOS/Linux
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Run the dashboard**
```bash
   streamlit run ui/dashboard.py
```
   This opens the app in your browser at `http://localhost:8501`.

5. **Or run the standalone webcam CLI demo**
```bash
   python app/webcam_demo.py
```
   Press `q` to quit.

## Usage

- Select an input mode (Webcam / Image Upload / Video Upload) from the sidebar
- Adjust the confidence threshold slider to control detection sensitivity
- For webcam/video, tracking IDs persist across frames — the same object retains the same ID as long as it stays in view

## Known Limitations

- **Closed vocabulary**: YOLO11 is trained on the 80-class COCO dataset. Objects outside this taxonomy (e.g. smartwatches, chargers) are misclassified to the nearest visually similar known class. This is a standard limitation of pre-trained, closed-vocabulary detectors — addressable via custom fine-tuning as a future enhancement.
- **ID reassignment on occlusion**: BoT-SORT's default configuration tracks by motion prediction, not visual appearance. Objects that leave the frame or are occluded for an extended period are assigned a new ID upon reappearing, rather than resuming their original ID. This could be improved with appearance-based re-identification (Re-ID), which BoT-SORT supports as an optional extension.
- **Accuracy vs. speed tradeoff**: Using the "small" YOLO11 variant for real-time performance; larger variants (medium/large) would improve accuracy on difficult angles/lighting at the cost of inference speed.

## Future Improvements

- Line-crossing and region-based counting
- Heatmap generation and trajectory visualization
- CSV/JSON export of detection logs
- Docker containerization and cloud deployment (Render / HuggingFace Spaces)
- Appearance-based re-identification for occlusion handling
- Custom fine-tuning for domain-specific object classes

## Author

Vinit Gill
