"""Unique object counting based on persistent tracking IDs.

Maintains a running record of every unique tracking ID seen per class,
enabling accurate "total unique objects seen" analytics — as opposed to
raw per-frame detection counts, which would overcount repeated sightings
of the same object across frames.
"""
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ObjectCounter:
    """Tracks unique object counts per class using persistent tracking IDs.

    Attributes:
        seen_ids: Maps class name -> set of tracking IDs seen for that class.
    """

    def __init__(self) -> None:
        self.seen_ids: dict[str, set[int]] = defaultdict(set)

    def update(self, result, class_names: dict) -> None:
        """Register all tracking IDs present in this frame's result.

        Args:
            result: The Ultralytics Results object from detector.track().
            class_names: Mapping of class ID to human-readable class name.
        """
        if result.boxes.id is None:
            return  # No tracked objects this frame (e.g. empty frame)

        for box in result.boxes:
            track_id = int(box.id[0]) if box.id is not None else None
            if track_id is None:
                continue
            class_id = int(box.cls[0])
            class_name = class_names[class_id]
            self.seen_ids[class_name].add(track_id)

    def get_counts(self) -> dict[str, int]:
        """Return the current unique count per class.

        Returns:
            A dict mapping class name to the number of unique tracking IDs
            seen for that class so far.
        """
        return {class_name: len(ids) for class_name, ids in self.seen_ids.items()}

    def get_total(self) -> int:
        """Return the total unique object count across all classes."""
        return sum(len(ids) for ids in self.seen_ids.values())