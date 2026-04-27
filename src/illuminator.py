"""Phase 2 illuminator and partial-coherence helpers.

This module keeps the Phase 2 model intentionally study-grade: a source is a
finite set of normalized pupil-plane points, and partial coherence is modeled
as an incoherent weighted sum of coherent aerial images from those points.

The source coordinates use normalized sigma units:

    sigma = sqrt(sigma_x^2 + sigma_y^2), with sigma <= 1

Each source point is passed to ``aerial_image`` as an off-axis illumination
tilt. This is sufficient for source-shape, contrast, and SMO/PMWO workflow
experiments without claiming rigorous Hopkins/TCC accuracy.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from . import constants as C
from .aerial import WaferGrid, aerial_image
from .mask import MaskGrid
from .pupil import PupilSpec


@dataclass(frozen=True)
class SourcePoint:
    """One weighted source sample in normalized pupil coordinates."""

    sigma_x: float
    sigma_y: float
    weight: float = 1.0

    def __post_init__(self) -> None:
        sigma_x = float(self.sigma_x)
        sigma_y = float(self.sigma_y)
        weight = float(self.weight)
        if not np.isfinite(sigma_x) or not np.isfinite(sigma_y):
            raise ValueError("source sigma coordinates must be finite")
        if np.hypot(sigma_x, sigma_y) > 1.0 + 1e-12:
            raise ValueError("source sigma radius must be <= 1")
        if not np.isfinite(weight) or weight <= 0.0:
            raise ValueError("source point weight must be positive and finite")
        object.__setattr__(self, "sigma_x", sigma_x)
        object.__setattr__(self, "sigma_y", sigma_y)
        object.__setattr__(self, "weight", weight)

    @property
    def radius(self) -> float:
        """Return radial sigma magnitude."""
        return float(np.hypot(self.sigma_x, self.sigma_y))


@dataclass(frozen=True)
class SourceShape:
    """Collection of weighted source samples."""

    points: tuple[SourcePoint, ...]
    name: str = "custom"

    def __post_init__(self) -> None:
        points = tuple(self.points)
        if not points:
            raise ValueError("source shape must contain at least one point")
        if any(not isinstance(point, SourcePoint) for point in points):
            raise TypeError("source shape points must be SourcePoint instances")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("source shape name must be a non-empty string")
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "name", self.name.strip())

    def normalized_weights(self) -> tuple[float, ...]:
        """Return weights normalized to sum to one."""
        weights = np.array([point.weight for point in self.points], dtype=np.float64)
        total = float(np.sum(weights))
        if total <= 0.0:
            raise ValueError("source shape weights must have positive total")
        return tuple(float(weight / total) for weight in weights)


@dataclass(frozen=True)
class PartialCoherenceResult:
    """Result bundle for partial-coherence aerial-image integration."""

    intensity: np.ndarray
    wafer_grid: WaferGrid
    source_shape: SourceShape
    normalized_weights: tuple[float, ...]
    point_images: tuple[np.ndarray, ...] = ()


def point_source(*, weight: float = 1.0, name: str = "point") -> SourceShape:
    """Return the on-axis coherent source used by Phase 1."""
    return SourceShape((SourcePoint(0.0, 0.0, weight),), name=name)


def freeform_source(
    points: Iterable[SourcePoint | Mapping[str, Any] | tuple[float, ...]],
    *,
    name: str = "freeform",
) -> SourceShape:
    """Create a source shape from explicit source points.

    Each point may be a ``SourcePoint``, a mapping with ``sigma_x`` and
    ``sigma_y`` keys, or a tuple ``(sigma_x, sigma_y[, weight])``.
    """
    return SourceShape(tuple(_coerce_source_point(point) for point in points), name=name)


def dipole_source(
    sigma_center: float = 0.6,
    *,
    orientation: str = "x",
    name: str | None = None,
) -> SourceShape:
    """Return a two-pole source along x or y."""
    sigma = _validate_sigma_center(sigma_center)
    if orientation == "x":
        points = (SourcePoint(-sigma, 0.0), SourcePoint(sigma, 0.0))
    elif orientation == "y":
        points = (SourcePoint(0.0, -sigma), SourcePoint(0.0, sigma))
    else:
        raise ValueError("orientation must be 'x' or 'y'")
    return SourceShape(points, name=name or f"dipole_{orientation}_{sigma:.2f}")


def quadrupole_source(
    sigma_center: float = 0.6,
    *,
    diagonal: bool = False,
    name: str | None = None,
) -> SourceShape:
    """Return a four-pole source on cardinal axes or diagonals."""
    sigma = _validate_sigma_center(sigma_center)
    if diagonal:
        component = sigma / np.sqrt(2.0)
        points = (
            SourcePoint(-component, -component),
            SourcePoint(component, -component),
            SourcePoint(-component, component),
            SourcePoint(component, component),
        )
        default_name = f"quadrupole_diagonal_{sigma:.2f}"
    else:
        points = (
            SourcePoint(-sigma, 0.0),
            SourcePoint(sigma, 0.0),
            SourcePoint(0.0, -sigma),
            SourcePoint(0.0, sigma),
        )
        default_name = f"quadrupole_cardinal_{sigma:.2f}"
    return SourceShape(points, name=name or default_name)


def annular_source(
    inner_sigma: float,
    outer_sigma: float,
    *,
    num_radial: int = 2,
    num_azimuthal: int = 16,
    name: str | None = None,
) -> SourceShape:
    """Sample an annular source with area-proportional radial weights."""
    inner = _validate_sigma_bound(inner_sigma, "inner_sigma")
    outer = _validate_sigma_bound(outer_sigma, "outer_sigma")
    if not inner < outer:
        raise ValueError("inner_sigma must be smaller than outer_sigma")
    if num_radial <= 0 or num_azimuthal <= 0:
        raise ValueError("num_radial and num_azimuthal must be positive")

    radial_edges = np.linspace(inner, outer, num_radial + 1)
    points: list[SourcePoint] = []
    for ring_index in range(num_radial):
        r_inner = float(radial_edges[ring_index])
        r_outer = float(radial_edges[ring_index + 1])
        radius = 0.5 * (r_inner + r_outer)
        ring_weight = (r_outer * r_outer - r_inner * r_inner) / num_azimuthal
        for az_index in range(num_azimuthal):
            theta = 2.0 * np.pi * az_index / num_azimuthal
            points.append(
                SourcePoint(
                    radius * float(np.cos(theta)),
                    radius * float(np.sin(theta)),
                    ring_weight,
                )
            )

    return SourceShape(
        tuple(points),
        name=name or f"annular_{inner:.2f}_{outer:.2f}_{num_radial}x{num_azimuthal}",
    )


def source_shape_from_json_dict(data: Mapping[str, Any]) -> SourceShape:
    """Parse one source shape from a JSON-like mapping."""
    if "points" not in data:
        raise ValueError("source shape JSON must contain a 'points' field")
    name = str(data.get("name", "json_source"))
    raw_points = data["points"]
    if (
        not isinstance(raw_points, Iterable)
        or isinstance(raw_points, Mapping)
        or isinstance(raw_points, str | bytes)
    ):
        raise TypeError("source shape 'points' must be iterable")
    return freeform_source(raw_points, name=name)


def load_source_shape_json(path: str | Path) -> SourceShape:
    """Load one source shape from JSON."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, Mapping):
        raise TypeError("source shape JSON root must be an object")
    return source_shape_from_json_dict(data)


def load_source_shape_library_json(path: str | Path) -> tuple[SourceShape, ...]:
    """Load a library JSON containing ``source_shapes`` rows."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, Mapping):
        raise TypeError("source shape library JSON root must be an object")
    raw_shapes = data.get("source_shapes")
    if (
        not isinstance(raw_shapes, Iterable)
        or isinstance(raw_shapes, Mapping)
        or isinstance(raw_shapes, str | bytes)
    ):
        raise ValueError("source shape library must contain 'source_shapes'")
    shape_rows = tuple(raw_shapes)
    if not all(isinstance(shape, Mapping) for shape in shape_rows):
        raise TypeError("each source shape library row must be an object")
    shapes = tuple(source_shape_from_json_dict(shape) for shape in shape_rows)
    if not shapes:
        raise ValueError("source shape library must contain at least one shape")
    return shapes


def partial_coherent_aerial_image(
    mask_field: np.ndarray,
    mask_grid: MaskGrid,
    source_shape: SourceShape,
    pupil_spec: PupilSpec | None = None,
    *,
    anamorphic: bool = True,
    mag_x: float = C.ANAMORPHIC_MAG_X,
    mag_y: float = C.ANAMORPHIC_MAG_Y,
    normalize: bool = True,
    return_point_images: bool = False,
) -> PartialCoherenceResult:
    """Compute a partial-coherence aerial image by incoherent source summation."""
    weights = source_shape.normalized_weights()
    accumulated: np.ndarray | None = None
    wafer_grid: WaferGrid | None = None
    point_images: list[np.ndarray] = []

    for point, weight in zip(source_shape.points, weights, strict=True):
        image, wafer = aerial_image(
            mask_field,
            mask_grid,
            pupil_spec=pupil_spec,
            anamorphic=anamorphic,
            mag_x=mag_x,
            mag_y=mag_y,
            source_sigma_x=point.sigma_x,
            source_sigma_y=point.sigma_y,
            normalize=False,
        )
        if accumulated is None:
            accumulated = np.zeros_like(image, dtype=np.float64)
            wafer_grid = wafer
        accumulated += weight * image
        if return_point_images:
            point_images.append(image)

    if accumulated is None or wafer_grid is None:
        raise ValueError("source shape did not produce any source points")

    if normalize:
        peak = float(np.max(accumulated))
        if peak > 0.0:
            accumulated = accumulated / peak

    return PartialCoherenceResult(
        intensity=accumulated.astype(np.float64),
        wafer_grid=wafer_grid,
        source_shape=source_shape,
        normalized_weights=weights,
        point_images=tuple(point_images),
    )


def _coerce_source_point(
    point: SourcePoint | Mapping[str, Any] | tuple[float, ...],
) -> SourcePoint:
    if isinstance(point, SourcePoint):
        return point
    if isinstance(point, Mapping):
        weight = float(point.get("weight", 1.0))
        if "sigma_x" in point and "sigma_y" in point:
            return SourcePoint(float(point["sigma_x"]), float(point["sigma_y"]), weight)
        if "sigma" in point and "angle_deg" in point:
            sigma = float(point["sigma"])
            theta = np.deg2rad(float(point["angle_deg"]))
            return SourcePoint(
                sigma * float(np.cos(theta)),
                sigma * float(np.sin(theta)),
                weight,
            )
        raise ValueError(
            "source point mapping must contain sigma_x/sigma_y or sigma/angle_deg"
        )
    if isinstance(point, tuple):
        if len(point) == 2:
            return SourcePoint(float(point[0]), float(point[1]))
        if len(point) == 3:
            return SourcePoint(float(point[0]), float(point[1]), float(point[2]))
    raise TypeError("source point must be SourcePoint, mapping, or tuple")


def _validate_sigma_center(value: float) -> float:
    sigma = float(value)
    if not np.isfinite(sigma) or not 0.0 < sigma <= 1.0:
        raise ValueError("sigma_center must be in (0, 1]")
    return sigma


def _validate_sigma_bound(value: float, name: str) -> float:
    sigma = float(value)
    if not np.isfinite(sigma) or not 0.0 <= sigma <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return sigma
