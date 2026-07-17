"""Verifies environment: device detection (MPS/CUDA/CPU), and YOLO11 load."""
import logging
import torch
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def check_device() -> str:
    """Return the best available device: 'mps' (Apple Silicon), 'cuda' (NVIDIA), or 'cpu'."""
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    logger.info("Detected device: %s", device)
    return device


def check_yolo_load() -> None:
    """Download (if needed) and load YOLO11 nano, confirming Ultralytics works."""
    model = YOLO("yolo11n.pt")  # auto-downloads on first run
    logger.info("YOLO11n loaded successfully. Classes: %d", len(model.names))


if __name__ == "__main__":
    check_device()
    check_yolo_load()
    logger.info("Environment setup verified.")