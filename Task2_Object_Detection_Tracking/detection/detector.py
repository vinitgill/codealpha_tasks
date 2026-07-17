"""YOLO11-based object detection wrapper.

Provides a reusable ObjectDetector class that loads a YOLO model once
and runs inference on frames, images, or video — used consistently
across webcam, upload, and dashboard entry points.
"""
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class ObjectDetector:
    """Wraps a YOLO11 model for consistent, reusable inference.

    Attributes:
        model_path: Path to the .pt weights file (auto-downloads if missing).
        confidence: Minimum confidence score to keep a detection (0.0-1.0).
        iou: IoU threshold used for Non-Max Suppression (0.0-1.0).
        device: Compute device ('mps', 'cuda', or 'cpu'), auto-detected if not given.
    """

    def __init__(
        self,
        model_path: str = "yolo11s.pt",
        confidence: float = 0.5,
        iou: float = 0.45,
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.confidence = confidence
        self.iou = iou
        self.device = device or self._detect_device()

        logger.info("Loading model '%s' on device '%s'", self.model_path, self.device)
        self.model = YOLO(self.model_path)
        self.class_names: dict[int, str] = self.model.names
        logger.info("Model loaded. %d classes available.", len(self.class_names))

    @staticmethod
    def _detect_device() -> str:
        """Auto-select the best available compute device."""
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def detect(self, frame: np.ndarray):
        """Run detection on a single frame (image array).

        Args:
            frame: A BGR image as a NumPy array (OpenCV format).

        Returns:
            The raw Ultralytics Results object for this frame, containing
            boxes, confidence scores, and class IDs.
        """
        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            iou=self.iou,
            device=self.device,
            verbose=False,
        )
        return results[0]  # predict() always returns a list; we passed 1 frame

    def track(self, frame: np.ndarray, persist: bool = True):
        """Run detection + tracking on a single frame, assigning persistent IDs.

        Args:
            frame: A BGR image as a NumPy array (OpenCV format).
            persist: If True, remembers tracker state across calls (for video/
                webcam streams). If False, resets tracker state each call —
                required for single, unrelated images to avoid frame-size
                mismatches in the tracker's motion compensation.

        Returns:
            The raw Ultralytics Results object, with .boxes.id populated
            containing the persistent tracking ID for each detected object.
        """
        results = self.model.track(
            source=frame,
            conf=self.confidence,
            iou=self.iou,
            device=self.device,
            tracker="botsort.yaml",
            persist=persist,
            verbose=False,
        )
        return results[0]

if __name__ == "__main__":
    # Quick manual test: run detection on a sample image bundled with Ultralytics
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    detector = ObjectDetector(confidence=0.5)
    sample_url = "https://ultralytics.com/images/bus.jpg"
    result = detector.detect(sample_url)

    logger.info("Detections found: %d", len(result.boxes))
    for box in result.boxes:
        class_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = detector.class_names[class_id]
        logger.info("  %s — confidence: %.2f", class_name, conf)