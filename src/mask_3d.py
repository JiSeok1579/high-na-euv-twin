"""Reduced Mask 3D effect stubs for Phase 4.

This module is a qualitative boundary-correction scaffold, not a rigorous
Maxwell or RCWA mask solver. It maps the six paper #12 Mask 3D effects into
stable, testable metrics so downstream Phase 6 SMO work can depend on a clear
interface before a higher-fidelity electromagnetic model is introduced.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np

from . import constants as C
from .aerial import WaferGrid, aerial_image
from .mask import MaskGrid, kirchhoff_mask
from .pupil import PupilSpec


@dataclass(frozen=True)
class AbsorberMaterial:
    """EUV absorber optical constants at 13.5 nm."""

    name: str
    n: float
    k: float
    thickness_m: float
    top_reflectivity: float = 0.015
    source: str = "qualitative-starter"
    reference: str = ""
    measured: bool = False


@dataclass(frozen=True)
class Mask3DEffectSummary:
    """Qualitative six-effect Mask 3D summary from paper #12."""

    material: AbsorberMaterial
    pitch_m: float
    chief_ray_angle_deg: float
    orientation: str
    shadowing_loss_fraction: float
    orientation_cd_bias_m: float
    telecentricity_error_mrad: float
    contrast_loss_fraction: float
    best_focus_shift_m: float
    secondary_image_fraction: float
    phase_error_waves: float

    def as_effect_vector(self) -> tuple[float, float, float, float, float, float]:
        """Return the six paper #12 effect metrics in checklist order."""
        return (
            self.shadowing_loss_fraction,
            self.orientation_cd_bias_m,
            self.telecentricity_error_mrad,
            self.contrast_loss_fraction,
            self.best_focus_shift_m,
            self.secondary_image_fraction,
        )


@dataclass(frozen=True)
class BoundaryCorrectionResult:
    """Field-level reduced Mask 3D boundary correction output."""

    baseline_field: np.ndarray
    corrected_field: np.ndarray
    shadow_map: np.ndarray
    phase_map_radians: np.ndarray
    secondary_field: np.ndarray
    summary: Mask3DEffectSummary
    ghost_shift_px: int


@dataclass(frozen=True)
class Mask3DLookupEntry:
    """One imported rigorous or measured Mask 3D effect-table row."""

    material_name: str
    pitch_m: float
    chief_ray_angle_deg: float
    orientation: str
    shadowing_loss_fraction: float
    orientation_cd_bias_m: float
    telecentricity_error_mrad: float
    contrast_loss_fraction: float
    best_focus_shift_m: float
    secondary_image_fraction: float
    phase_error_waves: float
    source: str = ""


@dataclass(frozen=True)
class Mask3DLookupTable:
    """Imported Mask 3D lookup table for replacing reduced proxies."""

    entries: tuple[Mask3DLookupEntry, ...]
    source: str = ""


@dataclass(frozen=True)
class AbsorberScreeningRow:
    """Ranked absorber candidate row for qualitative Mask 3D screening."""

    material: AbsorberMaterial
    summary: Mask3DEffectSummary
    score: float
    used_lookup: bool


@dataclass(frozen=True)
class Mask3DAerialRegressionResult:
    """Aerial-image comparison against imported rigorous or measured reference data."""

    predicted_intensity: np.ndarray
    reference_intensity: np.ndarray
    wafer_grid: WaferGrid | None
    rmse: float
    mean_abs_error: float
    max_abs_error: float
    rmse_tolerance: float
    max_abs_tolerance: float
    passed: bool


TABN_REFERENCE = AbsorberMaterial(
    name="TaBN reference",
    n=0.94,
    k=0.030,
    thickness_m=60.0e-9,
    top_reflectivity=0.018,
)

NI_HIGH_K = AbsorberMaterial(
    name="Ni high-k candidate",
    n=0.98,
    k=0.085,
    thickness_m=42.0e-9,
    top_reflectivity=0.010,
)

RUTA_LOW_N_PSM = AbsorberMaterial(
    name="RuTa low-n attenuated PSM candidate",
    n=0.92,
    k=0.055,
    thickness_m=45.0e-9,
    top_reflectivity=0.012,
)


def default_absorber_materials() -> tuple[AbsorberMaterial, ...]:
    """Return the Phase 4 starter absorber library."""
    return (TABN_REFERENCE, NI_HIGH_K, RUTA_LOW_N_PSM)


def load_absorber_materials_json(path: str | Path) -> tuple[AbsorberMaterial, ...]:
    """Load absorber materials from a JSON material library.

    Rows may specify either `thickness_m` or `thickness_nm`. The loader is
    intentionally small so measured n,k rows can replace the starter qualitative
    values without changing the Phase 4 code interface.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("materials")
    if not isinstance(rows, list) or not rows:
        raise ValueError("materials JSON must contain a non-empty materials list")

    materials: list[AbsorberMaterial] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each material row must be a JSON object")
        if "thickness_m" in row:
            thickness_m = float(row["thickness_m"])
        elif "thickness_nm" in row:
            thickness_m = float(row["thickness_nm"]) * 1.0e-9
        else:
            raise ValueError("material row must include thickness_m or thickness_nm")

        material = AbsorberMaterial(
            name=str(row.get("name", "")),
            n=float(row["n"]),
            k=float(row["k"]),
            thickness_m=thickness_m,
            top_reflectivity=float(row.get("top_reflectivity", 0.015)),
            source=str(row.get("source", data.get("source", "json"))),
            reference=str(row.get("reference", "")),
            measured=bool(row.get("measured", False)),
        )
        _validate_material(material)
        materials.append(material)
    return tuple(materials)


def load_mask3d_lookup_json(path: str | Path) -> Mask3DLookupTable:
    """Load imported Mask 3D effect rows from JSON.

    The table is designed for future rigorous EM, DDM, or measured calibration
    outputs. Rows may specify `pitch_m` or `pitch_nm`; effect metrics use the
    same units as `Mask3DEffectSummary`.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("entries")
    if not isinstance(rows, list) or not rows:
        raise ValueError("lookup JSON must contain a non-empty entries list")

    entries: list[Mask3DLookupEntry] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each lookup row must be a JSON object")
        entries.append(_lookup_entry_from_row(row, source=str(data.get("source", ""))))
    return Mask3DLookupTable(entries=tuple(entries), source=str(data.get("source", "")))


def load_mask3d_lookup_csv(
    path: str | Path,
    *,
    source: str | None = None,
) -> Mask3DLookupTable:
    """Load imported rigorous Mask 3D rows from a CSV table.

    The CSV schema mirrors `Mask3DLookupEntry`. Length-valued columns may use
    either meter or nanometer suffixes:

    - `pitch_m` or `pitch_nm`
    - `orientation_cd_bias_m` or `orientation_cd_bias_nm`
    - `best_focus_shift_m` or `best_focus_shift_nm`

    This keeps RCWA/DDM export ingestion explicit while avoiding hard-coded
    assumptions about a particular vendor or solver output.
    """
    csv_path = Path(path)
    table_source = source or csv_path.name
    entries: list[Mask3DLookupEntry] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("lookup CSV must include a header row")
        for row in reader:
            if not any(_csv_cell_has_value(value) for value in row.values()):
                continue
            entries.append(_lookup_entry_from_row(row, source=table_source))
    if not entries:
        raise ValueError("lookup CSV must contain at least one data row")
    return Mask3DLookupTable(entries=tuple(entries), source=table_source)


def mask3d_six_effects(
    pitch_m: float,
    *,
    material: AbsorberMaterial = TABN_REFERENCE,
    chief_ray_angle_deg: float = 6.0,
    orientation: str = "vertical",
    absorber_fraction: float = 0.5,
) -> Mask3DEffectSummary:
    """Return a reduced six-effect Mask 3D checklist for one pitch/material.

    The model intentionally scales every 3D correction by chief-ray angle. A
    zero-CRA in-line projector therefore collapses to the thin-mask baseline,
    matching the paper #12 mitigation logic used by the Phase 4 gate.
    """
    _validate_material(material)
    _validate_positive(pitch_m, "pitch_m")
    if not np.isfinite(chief_ray_angle_deg):
        raise ValueError("chief_ray_angle_deg must be finite")
    if orientation not in {"vertical", "horizontal"}:
        raise ValueError("orientation must be 'vertical' or 'horizontal'")
    if not np.isfinite(absorber_fraction) or not 0.0 < absorber_fraction < 1.0:
        raise ValueError("absorber_fraction must be in (0, 1)")

    angle_scale = abs(math.sin(math.radians(chief_ray_angle_deg)))
    height_ratio = material.thickness_m / pitch_m
    phase_strength = abs(1.0 - material.n)
    attenuation_leak = 1.0 / (1.0 + 20.0 * material.k)
    m3d_strength = phase_strength + 0.10 * attenuation_leak
    pitch_scale = math.sqrt(32.0e-9 / pitch_m)

    shadowing = min(
        0.80,
        angle_scale * height_ratio * absorber_fraction * (0.7 + attenuation_leak),
    )
    orientation_sign = 1.0 if orientation == "vertical" else -1.0
    orientation_bias = orientation_sign * 0.12 * shadowing * pitch_m
    telecentricity = 1.0e3 * angle_scale * m3d_strength * pitch_scale
    contrast_loss = min(0.80, 0.45 * angle_scale * height_ratio * m3d_strength)
    best_focus_shift = 120.0e-9 * angle_scale * height_ratio * m3d_strength * pitch_scale
    secondary = min(
        0.50,
        0.5 * angle_scale * height_ratio * material.top_reflectivity,
    )
    phase_error_waves = angle_scale * phase_strength * material.thickness_m / C.LAMBDA_EUV

    return Mask3DEffectSummary(
        material=material,
        pitch_m=float(pitch_m),
        chief_ray_angle_deg=float(chief_ray_angle_deg),
        orientation=orientation,
        shadowing_loss_fraction=float(shadowing),
        orientation_cd_bias_m=float(orientation_bias),
        telecentricity_error_mrad=float(telecentricity),
        contrast_loss_fraction=float(contrast_loss),
        best_focus_shift_m=float(best_focus_shift),
        secondary_image_fraction=float(secondary),
        phase_error_waves=float(phase_error_waves),
    )


def lookup_mask3d_six_effects(
    pitch_m: float,
    table: Mask3DLookupTable,
    *,
    material: AbsorberMaterial = TABN_REFERENCE,
    chief_ray_angle_deg: float = 6.0,
    orientation: str = "vertical",
    absorber_fraction: float = 0.5,
    fallback_to_reduced: bool = True,
) -> Mask3DEffectSummary:
    """Return lookup-refined Mask 3D effects with reduced-model fallback."""
    _validate_positive(pitch_m, "pitch_m")
    _validate_material(material)
    matches = _matching_lookup_entries(
        table,
        material_name=material.name,
        chief_ray_angle_deg=chief_ray_angle_deg,
        orientation=orientation,
    )
    if not matches:
        if fallback_to_reduced:
            return mask3d_six_effects(
                pitch_m,
                material=material,
                chief_ray_angle_deg=chief_ray_angle_deg,
                orientation=orientation,
                absorber_fraction=absorber_fraction,
            )
        raise ValueError("lookup table has no matching material/CRA/orientation rows")

    entry = _interpolate_lookup_entries(pitch_m, matches)
    return Mask3DEffectSummary(
        material=material,
        pitch_m=float(pitch_m),
        chief_ray_angle_deg=float(chief_ray_angle_deg),
        orientation=orientation,
        shadowing_loss_fraction=entry.shadowing_loss_fraction,
        orientation_cd_bias_m=entry.orientation_cd_bias_m,
        telecentricity_error_mrad=entry.telecentricity_error_mrad,
        contrast_loss_fraction=entry.contrast_loss_fraction,
        best_focus_shift_m=entry.best_focus_shift_m,
        secondary_image_fraction=entry.secondary_image_fraction,
        phase_error_waves=entry.phase_error_waves,
    )


def boundary_corrected_mask(
    pattern: np.ndarray,
    grid: MaskGrid,
    pitch_m: float,
    *,
    material: AbsorberMaterial = TABN_REFERENCE,
    chief_ray_angle_deg: float = 6.0,
    orientation: str = "vertical",
    absorber_fraction: float | None = None,
    ghost_shift_px: int = 1,
) -> BoundaryCorrectionResult:
    """Apply reduced field-level Mask 3D boundary correction to a binary mask.

    The baseline is the Phase 1 Kirchhoff field. Corrections are localized to
    clear pixels adjacent to absorber boundaries: shadowing attenuates the
    incident-side boundary, absorber phase perturbs the edge field, and the
    secondary-image term adds a shifted weak ghost field. This is still a
    qualitative scaffold, but it returns the same complex field type expected by
    `aerial_image`.
    """
    absorber = _as_absorber_mask(pattern, expected_shape=grid.shape())
    if absorber_fraction is None:
        absorber_fraction = float(np.mean(absorber))
    if not 0.0 < absorber_fraction < 1.0:
        raise ValueError("absorber_fraction must be in (0, 1)")

    summary = mask3d_six_effects(
        pitch_m,
        material=material,
        chief_ray_angle_deg=chief_ray_angle_deg,
        orientation=orientation,
        absorber_fraction=absorber_fraction,
    )

    return _boundary_corrected_mask_from_summary(
        pattern,
        grid,
        summary,
        absorber=absorber,
        ghost_shift_px=ghost_shift_px,
    )


def lookup_boundary_corrected_mask(
    pattern: np.ndarray,
    grid: MaskGrid,
    pitch_m: float,
    table: Mask3DLookupTable,
    *,
    material: AbsorberMaterial = TABN_REFERENCE,
    chief_ray_angle_deg: float = 6.0,
    orientation: str = "vertical",
    absorber_fraction: float | None = None,
    ghost_shift_px: int = 1,
    fallback_to_reduced: bool = True,
) -> BoundaryCorrectionResult:
    """Apply boundary correction using imported lookup rows when available."""
    absorber = _as_absorber_mask(pattern, expected_shape=grid.shape())
    if absorber_fraction is None:
        absorber_fraction = float(np.mean(absorber))
    if not 0.0 < absorber_fraction < 1.0:
        raise ValueError("absorber_fraction must be in (0, 1)")

    summary = lookup_mask3d_six_effects(
        pitch_m,
        table,
        material=material,
        chief_ray_angle_deg=chief_ray_angle_deg,
        orientation=orientation,
        absorber_fraction=absorber_fraction,
        fallback_to_reduced=fallback_to_reduced,
    )
    return _boundary_corrected_mask_from_summary(
        pattern,
        grid,
        summary,
        absorber=absorber,
        ghost_shift_px=ghost_shift_px,
    )


def compare_mask3d_aerial_images(
    predicted_intensity: np.ndarray,
    reference_intensity: np.ndarray,
    *,
    wafer_grid: WaferGrid | None = None,
    rmse_tolerance: float = 0.02,
    max_abs_tolerance: float = 0.08,
    normalize: bool = True,
) -> Mask3DAerialRegressionResult:
    """Compare predicted aerial intensity against rigorous reference data."""
    _validate_positive(rmse_tolerance, "rmse_tolerance")
    _validate_positive(max_abs_tolerance, "max_abs_tolerance")
    predicted = _as_aerial_reference(predicted_intensity, "predicted_intensity")
    reference = _as_aerial_reference(reference_intensity, "reference_intensity")
    if predicted.shape != reference.shape:
        raise ValueError("predicted_intensity and reference_intensity shapes must match")
    if wafer_grid is not None and predicted.shape != wafer_grid.shape():
        raise ValueError("wafer_grid shape must match aerial image shape")

    if normalize:
        predicted = _normalize_aerial(predicted)
        reference = _normalize_aerial(reference)

    error = predicted - reference
    rmse = float(np.sqrt(np.mean(error * error)))
    mean_abs = float(np.mean(np.abs(error)))
    max_abs = float(np.max(np.abs(error)))
    passed = rmse <= rmse_tolerance and max_abs <= max_abs_tolerance
    return Mask3DAerialRegressionResult(
        predicted_intensity=predicted,
        reference_intensity=reference,
        wafer_grid=wafer_grid,
        rmse=rmse,
        mean_abs_error=mean_abs,
        max_abs_error=max_abs,
        rmse_tolerance=float(rmse_tolerance),
        max_abs_tolerance=float(max_abs_tolerance),
        passed=bool(passed),
    )


def lookup_mask3d_aerial_regression(
    pattern: np.ndarray,
    grid: MaskGrid,
    pitch_m: float,
    reference_intensity: np.ndarray,
    table: Mask3DLookupTable,
    *,
    material: AbsorberMaterial = TABN_REFERENCE,
    chief_ray_angle_deg: float = 6.0,
    orientation: str = "vertical",
    absorber_fraction: float | None = None,
    ghost_shift_px: int = 1,
    pupil_spec: PupilSpec | None = None,
    anamorphic: bool = True,
    rmse_tolerance: float = 0.02,
    max_abs_tolerance: float = 0.08,
    fallback_to_reduced: bool = True,
) -> Mask3DAerialRegressionResult:
    """Run lookup-driven Mask 3D correction and compare its aerial image."""
    boundary = lookup_boundary_corrected_mask(
        pattern,
        grid,
        pitch_m,
        table,
        material=material,
        chief_ray_angle_deg=chief_ray_angle_deg,
        orientation=orientation,
        absorber_fraction=absorber_fraction,
        ghost_shift_px=ghost_shift_px,
        fallback_to_reduced=fallback_to_reduced,
    )
    predicted, wafer = aerial_image(
        boundary.corrected_field,
        grid,
        pupil_spec=pupil_spec,
        anamorphic=anamorphic,
    )
    return compare_mask3d_aerial_images(
        predicted,
        reference_intensity,
        wafer_grid=wafer,
        rmse_tolerance=rmse_tolerance,
        max_abs_tolerance=max_abs_tolerance,
    )


def _boundary_corrected_mask_from_summary(
    pattern: np.ndarray,
    grid: MaskGrid,
    summary: Mask3DEffectSummary,
    *,
    absorber: np.ndarray | None = None,
    ghost_shift_px: int = 1,
) -> BoundaryCorrectionResult:
    baseline = kirchhoff_mask(pattern)
    if absorber is None:
        absorber = _as_absorber_mask(pattern, expected_shape=grid.shape())
    if ghost_shift_px < 0:
        raise ValueError("ghost_shift_px must be non-negative")

    clear = ~absorber
    axis = 1 if summary.orientation == "vertical" else 0
    incidence_shift = 1 if summary.chief_ray_angle_deg >= 0.0 else -1
    incident_absorber = _shift_bool(absorber, incidence_shift, axis=axis)
    boundary_clear = clear & _edge_neighbor_mask(absorber)
    shadow_region = clear & incident_absorber

    shadow_map = np.zeros(grid.shape(), dtype=np.float64)
    shadow_map[shadow_region] = summary.shadowing_loss_fraction

    signed_phase = math.copysign(
        2.0 * math.pi * summary.phase_error_waves,
        summary.chief_ray_angle_deg if summary.chief_ray_angle_deg != 0.0 else 1.0,
    )
    phase_map = np.zeros(grid.shape(), dtype=np.float64)
    phase_map[boundary_clear] = signed_phase

    amplitude = np.abs(baseline)
    amplitude *= 1.0 - shadow_map
    amplitude[boundary_clear] *= 1.0 - 0.5 * summary.contrast_loss_fraction
    corrected = amplitude * np.exp(1j * phase_map)

    if ghost_shift_px == 0 or summary.secondary_image_fraction == 0.0:
        secondary = np.zeros_like(baseline)
    else:
        secondary = (
            summary.secondary_image_fraction
            * _shift_complex(
                baseline,
                incidence_shift * ghost_shift_px,
                axis=axis,
            )
            * np.exp(1j * signed_phase)
        )
    corrected = (corrected + secondary).astype(np.complex128)

    return BoundaryCorrectionResult(
        baseline_field=baseline,
        corrected_field=corrected,
        shadow_map=shadow_map,
        phase_map_radians=phase_map,
        secondary_field=secondary.astype(np.complex128),
        summary=summary,
        ghost_shift_px=int(ghost_shift_px),
    )


def screen_absorber_materials(
    pitch_m: float,
    materials: Iterable[AbsorberMaterial],
    *,
    chief_ray_angle_deg: float = 6.0,
    orientation: str = "vertical",
    lookup_table: Mask3DLookupTable | None = None,
) -> tuple[AbsorberScreeningRow, ...]:
    """Rank absorber candidates by a reduced Mask 3D penalty score."""
    library = tuple(materials)
    if not library:
        raise ValueError("materials must contain at least one AbsorberMaterial")

    rows: list[AbsorberScreeningRow] = []
    for material in library:
        used_lookup = (
            lookup_table is not None
            and bool(
                _matching_lookup_entries(
                    lookup_table,
                    material_name=material.name,
                    chief_ray_angle_deg=chief_ray_angle_deg,
                    orientation=orientation,
                )
            )
        )
        if lookup_table is None:
            summary = mask3d_six_effects(
                pitch_m,
                material=material,
                chief_ray_angle_deg=chief_ray_angle_deg,
                orientation=orientation,
            )
        else:
            summary = lookup_mask3d_six_effects(
                pitch_m,
                lookup_table,
                material=material,
                chief_ray_angle_deg=chief_ray_angle_deg,
                orientation=orientation,
            )
        rows.append(
            AbsorberScreeningRow(
                material=material,
                summary=summary,
                score=_mask3d_penalty_score(summary),
                used_lookup=used_lookup,
            )
        )
    return tuple(sorted(rows, key=lambda row: row.score))


def compare_absorber_materials(
    pitch_m: float,
    materials: Iterable[AbsorberMaterial] | None = None,
    *,
    chief_ray_angle_deg: float = 6.0,
    orientation: str = "vertical",
) -> tuple[Mask3DEffectSummary, ...]:
    """Evaluate the same reduced Mask 3D checklist across absorber materials."""
    library = default_absorber_materials() if materials is None else tuple(materials)
    if not library:
        raise ValueError("materials must contain at least one AbsorberMaterial")
    return tuple(
        mask3d_six_effects(
            pitch_m,
            material=material,
            chief_ray_angle_deg=chief_ray_angle_deg,
            orientation=orientation,
        )
        for material in library
    )


def _validate_material(material: AbsorberMaterial) -> None:
    if not material.name:
        raise ValueError("material.name must be non-empty")
    _validate_positive(material.n, "material.n")
    if not np.isfinite(material.k) or material.k < 0.0:
        raise ValueError("material.k must be non-negative and finite")
    _validate_positive(material.thickness_m, "material.thickness_m")
    if (
        not np.isfinite(material.top_reflectivity)
        or not 0.0 <= material.top_reflectivity < 1.0
    ):
        raise ValueError("material.top_reflectivity must be in [0, 1)")
    if not isinstance(material.source, str):
        raise ValueError("material.source must be a string")
    if not isinstance(material.reference, str):
        raise ValueError("material.reference must be a string")


def _validate_positive(value: float, name: str) -> None:
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")


def _lookup_entry_from_row(row: dict[str, object], *, source: str) -> Mask3DLookupEntry:
    if _row_has_value(row, "pitch_m"):
        pitch_m = _required_float(row, "pitch_m")
    elif _row_has_value(row, "pitch_nm"):
        pitch_m = _required_float(row, "pitch_nm") * 1.0e-9
    else:
        raise ValueError("lookup row must include pitch_m or pitch_nm")
    _validate_positive(pitch_m, "pitch_m")

    orientation = str(row["orientation"])
    if orientation not in {"vertical", "horizontal"}:
        raise ValueError("lookup orientation must be 'vertical' or 'horizontal'")

    entry = Mask3DLookupEntry(
        material_name=str(row["material_name"]),
        pitch_m=pitch_m,
        chief_ray_angle_deg=_required_float(row, "chief_ray_angle_deg"),
        orientation=orientation,
        shadowing_loss_fraction=_required_float(row, "shadowing_loss_fraction"),
        orientation_cd_bias_m=_required_length_m(row, "orientation_cd_bias"),
        telecentricity_error_mrad=_required_float(row, "telecentricity_error_mrad"),
        contrast_loss_fraction=_required_float(row, "contrast_loss_fraction"),
        best_focus_shift_m=_required_length_m(row, "best_focus_shift"),
        secondary_image_fraction=_required_float(row, "secondary_image_fraction"),
        phase_error_waves=_required_float(row, "phase_error_waves"),
        source=_optional_string(row, "source", fallback=source),
    )
    _validate_lookup_entry(entry)
    return entry


def _validate_lookup_entry(entry: Mask3DLookupEntry) -> None:
    if not entry.material_name:
        raise ValueError("lookup material_name must be non-empty")
    _validate_positive(entry.pitch_m, "lookup pitch_m")
    if not np.isfinite(entry.chief_ray_angle_deg):
        raise ValueError("lookup chief_ray_angle_deg must be finite")
    if entry.orientation not in {"vertical", "horizontal"}:
        raise ValueError("lookup orientation must be 'vertical' or 'horizontal'")
    _validate_fraction(entry.shadowing_loss_fraction, "shadowing_loss_fraction")
    _validate_fraction(entry.contrast_loss_fraction, "contrast_loss_fraction")
    _validate_fraction(entry.secondary_image_fraction, "secondary_image_fraction")
    if not np.isfinite(entry.orientation_cd_bias_m):
        raise ValueError("orientation_cd_bias_m must be finite")
    if not np.isfinite(entry.telecentricity_error_mrad):
        raise ValueError("telecentricity_error_mrad must be finite")
    if not np.isfinite(entry.best_focus_shift_m):
        raise ValueError("best_focus_shift_m must be finite")
    if not np.isfinite(entry.phase_error_waves):
        raise ValueError("phase_error_waves must be finite")


def _validate_fraction(value: float, name: str) -> None:
    if not np.isfinite(value) or not 0.0 <= value < 1.0:
        raise ValueError(f"{name} must be finite and in [0, 1)")


def _required_float(row: dict[str, object], name: str) -> float:
    value = row.get(name)
    if not isinstance(value, str | int | float):
        raise ValueError(f"{name} must be a numeric value")
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a numeric value") from exc


def _required_length_m(row: dict[str, object], base_name: str) -> float:
    meters_name = f"{base_name}_m"
    nanometers_name = f"{base_name}_nm"
    if _row_has_value(row, meters_name):
        return _required_float(row, meters_name)
    if _row_has_value(row, nanometers_name):
        return _required_float(row, nanometers_name) * 1.0e-9
    raise ValueError(f"{base_name} must include _m or _nm units")


def _row_has_value(row: dict[str, object], name: str) -> bool:
    return name in row and _csv_cell_has_value(row.get(name))


def _csv_cell_has_value(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def _optional_string(row: dict[str, object], name: str, *, fallback: str) -> str:
    value = row.get(name)
    if not _csv_cell_has_value(value):
        return fallback
    return str(value)


def _as_aerial_reference(values: np.ndarray, name: str) -> np.ndarray:
    image = np.asarray(values, dtype=np.float64)
    if image.ndim != 2:
        raise ValueError(f"{name} must be a 2-D aerial image")
    if image.size == 0:
        raise ValueError(f"{name} must contain at least one pixel")
    if not np.all(np.isfinite(image)):
        raise ValueError(f"{name} must contain finite values")
    if np.any(image < 0.0):
        raise ValueError(f"{name} intensity must be non-negative")
    return image.copy()


def _normalize_aerial(image: np.ndarray) -> np.ndarray:
    peak = float(np.max(image))
    if peak == 0.0:
        return image.copy()
    return image / peak


def _matching_lookup_entries(
    table: Mask3DLookupTable,
    *,
    material_name: str,
    chief_ray_angle_deg: float,
    orientation: str,
) -> tuple[Mask3DLookupEntry, ...]:
    if not table.entries:
        raise ValueError("lookup table must contain at least one entry")
    requested_angle = abs(float(chief_ray_angle_deg))
    matches = [
        entry
        for entry in table.entries
        if entry.material_name == material_name
        and entry.orientation == orientation
        and math.isclose(abs(entry.chief_ray_angle_deg), requested_angle, abs_tol=1.0e-9)
    ]
    return tuple(sorted(matches, key=lambda entry: entry.pitch_m))


def _interpolate_lookup_entries(
    pitch_m: float,
    entries: tuple[Mask3DLookupEntry, ...],
) -> Mask3DLookupEntry:
    if len(entries) == 1 or pitch_m <= entries[0].pitch_m:
        return entries[0]
    if pitch_m >= entries[-1].pitch_m:
        return entries[-1]

    for lower, upper in zip(entries, entries[1:], strict=True):
        if lower.pitch_m <= pitch_m <= upper.pitch_m:
            if math.isclose(lower.pitch_m, upper.pitch_m):
                return lower
            weight = (pitch_m - lower.pitch_m) / (upper.pitch_m - lower.pitch_m)
            return Mask3DLookupEntry(
                material_name=lower.material_name,
                pitch_m=float(pitch_m),
                chief_ray_angle_deg=lower.chief_ray_angle_deg,
                orientation=lower.orientation,
                shadowing_loss_fraction=_lerp(
                    lower.shadowing_loss_fraction,
                    upper.shadowing_loss_fraction,
                    weight,
                ),
                orientation_cd_bias_m=_lerp(
                    lower.orientation_cd_bias_m,
                    upper.orientation_cd_bias_m,
                    weight,
                ),
                telecentricity_error_mrad=_lerp(
                    lower.telecentricity_error_mrad,
                    upper.telecentricity_error_mrad,
                    weight,
                ),
                contrast_loss_fraction=_lerp(
                    lower.contrast_loss_fraction,
                    upper.contrast_loss_fraction,
                    weight,
                ),
                best_focus_shift_m=_lerp(
                    lower.best_focus_shift_m,
                    upper.best_focus_shift_m,
                    weight,
                ),
                secondary_image_fraction=_lerp(
                    lower.secondary_image_fraction,
                    upper.secondary_image_fraction,
                    weight,
                ),
                phase_error_waves=_lerp(
                    lower.phase_error_waves,
                    upper.phase_error_waves,
                    weight,
                ),
                source=lower.source or upper.source,
            )
    return entries[-1]


def _lerp(lower: float, upper: float, weight: float) -> float:
    return float((1.0 - weight) * lower + weight * upper)


def _mask3d_penalty_score(summary: Mask3DEffectSummary) -> float:
    return float(
        summary.shadowing_loss_fraction
        + summary.contrast_loss_fraction
        + summary.secondary_image_fraction
        + abs(summary.telecentricity_error_mrad) / 100.0
        + abs(summary.best_focus_shift_m) / 50.0e-9
        + abs(summary.orientation_cd_bias_m) / max(summary.pitch_m, np.finfo(float).eps)
    )


def _as_absorber_mask(pattern: np.ndarray, expected_shape: tuple[int, int]) -> np.ndarray:
    arr = np.asarray(pattern)
    if arr.shape != expected_shape:
        raise ValueError("pattern shape must match MaskGrid.shape()")
    if not np.all((arr == 0) | (arr == 1)):
        raise ValueError("pattern must contain only 0 or 1")
    mask = arr.astype(bool)
    if np.all(mask) or not np.any(mask):
        raise ValueError("pattern must contain both absorber and clear regions")
    return mask


def _edge_neighbor_mask(absorber: np.ndarray) -> np.ndarray:
    neighbors = np.zeros_like(absorber, dtype=bool)
    for axis in (0, 1):
        neighbors |= _shift_bool(absorber, 1, axis=axis)
        neighbors |= _shift_bool(absorber, -1, axis=axis)
    return neighbors


def _shift_bool(values: np.ndarray, shift: int, *, axis: int) -> np.ndarray:
    return _shift_array(values, shift, axis=axis, fill_value=False).astype(bool)


def _shift_complex(values: np.ndarray, shift: int, *, axis: int) -> np.ndarray:
    return _shift_array(values, shift, axis=axis, fill_value=0.0 + 0.0j).astype(
        np.complex128
    )


def _shift_array(
    values: np.ndarray,
    shift: int,
    *,
    axis: int,
    fill_value: object,
) -> np.ndarray:
    if shift == 0:
        return values.copy()
    result = np.full(values.shape, fill_value, dtype=values.dtype)
    source = [slice(None)] * values.ndim
    destination = [slice(None)] * values.ndim
    if shift > 0:
        source[axis] = slice(0, -shift)
        destination[axis] = slice(shift, None)
    else:
        source[axis] = slice(-shift, None)
        destination[axis] = slice(0, shift)
    result[tuple(destination)] = values[tuple(source)]
    return result
