"""Bounding-box span resolver for layout-shift adversarial checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class SpanResolveError(Exception):
    """Raised when a span cannot be grounded to evidence geometry."""


@dataclass(frozen=True, slots=True)
class BoundingBox:
    page: int
    x0: float
    y0: float
    x1: float
    y1: float

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "BoundingBox":
        return cls(
            page=int(data.get("page", 0)),
            x0=float(data["x0"]),
            y0=float(data["y0"]),
            x1=float(data["x1"]),
            y1=float(data["y1"]),
        )

    def overlaps(self, other: "BoundingBox", *, iou_threshold: float = 0.5) -> bool:
        if self.page != other.page:
            return False
        return self.iou(other) >= iou_threshold

    def iou(self, other: "BoundingBox") -> float:
        ix0 = max(self.x0, other.x0)
        iy0 = max(self.y0, other.y0)
        ix1 = min(self.x1, other.x1)
        iy1 = min(self.y1, other.y1)
        iw = max(0.0, ix1 - ix0)
        ih = max(0.0, iy1 - iy0)
        inter = iw * ih
        if inter <= 0:
            return 0.0
        area_a = max(0.0, self.x1 - self.x0) * max(0.0, self.y1 - self.y0)
        area_b = max(0.0, other.x1 - other.x0) * max(0.0, other.y1 - other.y0)
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    def center(self) -> tuple[float, float]:
        return ((self.x0 + self.x1) / 2.0, (self.y0 + self.y1) / 2.0)


@dataclass(frozen=True, slots=True)
class ResolvedSpan:
    field_name: str
    text: str
    bbox: BoundingBox
    confidence: float = 1.0


class BoundingBoxSpanResolver:
    """
    Resolve field extractions against expected bounding boxes.

    Detects line-item / layout shifts when the extracted value's geometry
    no longer overlaps the ground-truth span for that field.
    """

    def resolve(
        self,
        field_name: str,
        proposed_bbox: Mapping[str, Any] | BoundingBox,
        expected_bbox: Mapping[str, Any] | BoundingBox,
        *,
        text: str = "",
        iou_threshold: float = 0.5,
    ) -> ResolvedSpan:
        proposed = (
            proposed_bbox
            if isinstance(proposed_bbox, BoundingBox)
            else BoundingBox.from_mapping(proposed_bbox)
        )
        expected = (
            expected_bbox
            if isinstance(expected_bbox, BoundingBox)
            else BoundingBox.from_mapping(expected_bbox)
        )
        if not proposed.overlaps(expected, iou_threshold=iou_threshold):
            raise SpanResolveError(
                f"layout shift for '{field_name}': proposed bbox does not overlap expected "
                f"(iou={proposed.iou(expected):.3f} < {iou_threshold})"
            )
        return ResolvedSpan(field_name=field_name, text=text, bbox=proposed)

    def detect_layout_shifts(
        self,
        proposed_spans: Mapping[str, Mapping[str, Any]],
        expected_spans: Mapping[str, Mapping[str, Any]],
        *,
        iou_threshold: float = 0.5,
    ) -> list[str]:
        """Return human-readable reasons for each shifted field."""
        reasons: list[str] = []
        for name, expected in expected_spans.items():
            if name not in proposed_spans:
                reasons.append(f"missing span for '{name}' under layout shift check")
                continue
            try:
                self.resolve(
                    name,
                    proposed_spans[name],
                    expected,
                    iou_threshold=iou_threshold,
                )
            except SpanResolveError as exc:
                reasons.append(str(exc))
        return reasons

    def nearest_span(
        self,
        query: BoundingBox | Mapping[str, Any],
        candidates: Sequence[tuple[str, Mapping[str, Any] | BoundingBox]],
    ) -> tuple[str, float] | None:
        """Return (field_name, iou) for the highest-overlap candidate."""
        q = query if isinstance(query, BoundingBox) else BoundingBox.from_mapping(query)
        best: tuple[str, float] | None = None
        for name, cand in candidates:
            box = cand if isinstance(cand, BoundingBox) else BoundingBox.from_mapping(cand)
            score = q.iou(box)
            if best is None or score > best[1]:
                best = (name, score)
        return best
