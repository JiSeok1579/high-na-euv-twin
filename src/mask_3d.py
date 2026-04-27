"""Reduced Mask 3D effect stubs for Phase 4.

This module is a qualitative boundary-correction scaffold, not a rigorous
Maxwell or RCWA mask solver. It maps the six paper #12 Mask 3D effects into
stable, testable metrics so downstream Phase 6 SMO work can depend on a clear
interface before a higher-fidelity electromagnetic model is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from . import constants as C


@dataclass(frozen=True)
class AbsorberMaterial:
    """EUV absorber optical constants at 13.5 nm."""

    name: str
    n: float
    k: float
    thickness_m: float
    top_reflectivity: float = 0.015


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


def _validate_positive(value: float, name: str) -> None:
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")
