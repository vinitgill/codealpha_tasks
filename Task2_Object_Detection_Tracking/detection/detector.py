import logging
from typing import Optional

import numpy as np
import torch
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class ObjectDetector:
    def __init__(self, model_path="yolo11s.pt", confidence=0.5, iou=0.45, device=None):
        self.model_path = model_path
        self.confidence = confidence
        self.iou = iou
        self.device = device or self._detect_device()
        logger.info("Loading models '%s' on device '%s'", self.model_path, self.device)
        self.model = YOLO(self.model_path)
        self.detect_model = YOLO(self.model_path)
        self.class_names = self.model.names
        logger.info("Models loaded. %d classes available.", len(self.class_names))

    @staticmethod
    def _detect_device():
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def reset_tracker(self):
        self.model.predictor = None

    def detect(self, frame):
        results = self.detect_model.predict(
            source=frame, conf=self.confidence, iou=self.iou,
            device=self.device, verbose=False,
        )
        return results[0]

    def detect_adaptive(self, frame, min_boxes=1, floor=0.25):
        original_confidence = self.confidence
        try:
            threshold = original_confidence
            result = self.detect(frame)
            while len(result.boxes) < min_boxes and threshold > floor:
                threshold = max(threshold - 0.1, floor)
                self.confidence = threshold
                result = self.detect(frame)
            return result
        finally:
            self.confidence = original_confidence

    def track(self, frame, persist=True):
        results = self.model.track(
            source=frame, conf=self.confidence, iou=self.iou,
            device=self.device, tracker="botsort.yaml",
            persist=persist, verbose=False,
        )
        return results[0]
