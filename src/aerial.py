"""Aerial-image solver (scalar Fourier optics, coherent source point).

Implements the canonical Hopkins coherent imaging step:

    I(x_w, y_w) = | IFFT( FFT(M) · P(f_x, f_y) ) |^2

where M is the complex mask field at the wafer plane (after the
anamorphic 4×/8× demagnification) and P is the pupil function. Phase 2 adds
off-axis source-point tilts here; `illuminator.py` builds partial coherence by
incoherently summing multiple coherent source-point images.

Coordinate convention
---------------------
- Mask plane uses (x_m, y_m); after the projection optics the wafer plane
  uses (x_w, y_w) = (x_m / 4, y_m / 8). The 4× factor is along the scan
  direction, 8× cross-scan (paper #19 Migura 2015).
- The aerial image grid pixel size is pixel_size_mask / mag_axis.
- The pupil sampling is set so that the highest spatial frequency on the
  aerial-plane grid is 1 / (2 · pixel_size_wafer); we map normalized pupil
  rho = 1 to the system NA.
- Constant defocus follows `wafer_topo.py`: positive defocus means wafer
  above best focus and adds +π·z·NA²/λ·rho² to the pupil phase.

References
----------
- physics_considerations.md Part E (Fourier optics), Part F (NA)
- 진행계획서.md §4.1 WP1.4
- Paper #19 (anamorphic), #15 (annular pupil), #11 (target imaging)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import constants as C
from .mask import MaskGrid
from .optics import wavefront
from .pupil import PupilSpec
from .wafer_topo import (
    DefocusApproximation,
    defocus_pupil_phase,
    validate_defocus_sampling,
)


@dataclass(frozen=True)
class WaferGrid:
    """Pixel grid of the wafer (aerial-image) plane."""

    nx: int
    ny: int
    pixel_x_m: float
    pixel_y_m: float

    def shape(self) -> tuple[int, int]:
        return (self.ny, self.nx)


def wafer_grid_from_mask(
    mask_grid: MaskGrid,
    mag_x: float = C.ANAMORPHIC_MAG_X,
    mag_y: float = C.ANAMORPHIC_MAG_Y,
    anamorphic: bool = True,
) -> WaferGrid:
    """Project a mask grid through the anamorphic optics to the wafer plane."""
    if not anamorphic:
        mag_x = mag_y = 1.0
    return WaferGrid(
        nx=mask_grid.nx,
        ny=mask_grid.ny,
        pixel_x_m=mask_grid.pixel_size / mag_x,
        pixel_y_m=mask_grid.pixel_size / mag_y,
    )


def _build_aerial_pupil(
    wafer: WaferGrid,
    na: float,
    obscuration_ratio: float,
    wavelength: float,
    zernike: dict | None,
    defocus_m: float,
    defocus_approximation: DefocusApproximation,
) -> np.ndarray:
    """Sample the pupil so that pupil radius rho = 1 maps to the system NA.

    The FFT frequency cell is df_x = 1 / (nx · dx_w). The Nyquist frequency
    1 / (2 · dx_w) must be at least NA / lambda for the pupil to fit in
    the FFT grid. For square FFT grids we resample the pupil to the
    spatial-frequency support of the wafer grid.
    """
    nx, ny = wafer.nx, wafer.ny
    fx_axis = np.fft.fftshift(np.fft.fftfreq(nx, d=wafer.pixel_x_m))
    fy_axis = np.fft.fftshift(np.fft.fftfreq(ny, d=wafer.pixel_y_m))
    fx, fy = np.meshgrid(fx_axis, fy_axis, indexing="xy")

    cutoff = na / wavelength
    rho = np.sqrt(fx**2 + fy**2) / cutoff
    theta = np.arctan2(fy, fx)

    inside = rho <= 1.0
    outside_obs = rho >= obscuration_ratio
    amplitude = (inside & outside_obs).astype(np.float64)

    if defocus_m != 0.0:
        validate_defocus_sampling(
            min(nx, ny),
            defocus_m,
            na=na,
            wavelength=wavelength,
            approximation=defocus_approximation,
        )

    phase = np.ones_like(amplitude, dtype=np.complex128)
    if zernike:
        w_waves = wavefront(rho, theta, zernike)
        phase *= np.exp(1j * 2.0 * np.pi * w_waves)
    if defocus_m != 0.0:
        phase *= defocus_pupil_phase(
            rho,
            defocus_m,
            na=na,
            wavelength=wavelength,
            approximation=defocus_approximation,
        )
    return (amplitude * phase).astype(np.complex128)


def _validate_source_sigma(source_sigma_x: float, source_sigma_y: float) -> None:
    if not np.isfinite(source_sigma_x) or not np.isfinite(source_sigma_y):
        raise ValueError("source sigma coordinates must be finite")
    if np.hypot(source_sigma_x, source_sigma_y) > 1.0 + 1e-12:
        raise ValueError("source sigma radius must be <= 1")


def _apply_source_tilt(
    mask_field: np.ndarray,
    wafer: WaferGrid,
    *,
    source_sigma_x: float,
    source_sigma_y: float,
    na: float,
    wavelength: float,
) -> np.ndarray:
    """Apply a Phase 2 off-axis illumination tilt before coherent imaging."""
    if source_sigma_x == 0.0 and source_sigma_y == 0.0:
        return np.asarray(mask_field, dtype=np.complex128)

    fx_source = source_sigma_x * na / wavelength
    fy_source = source_sigma_y * na / wavelength
    x = (np.arange(wafer.nx) - wafer.nx // 2) * wafer.pixel_x_m
    y = (np.arange(wafer.ny) - wafer.ny // 2) * wafer.pixel_y_m
    phase = np.exp(
        1j
        * 2.0
        * np.pi
        * (fy_source * y[:, np.newaxis] + fx_source * x[np.newaxis, :])
    )
    return np.asarray(mask_field, dtype=np.complex128) * phase


def aerial_image(
    mask_field: np.ndarray,
    mask_grid: MaskGrid,
    pupil_spec: PupilSpec | None = None,
    *,
    anamorphic: bool = True,
    mag_x: float = C.ANAMORPHIC_MAG_X,
    mag_y: float = C.ANAMORPHIC_MAG_Y,
    source_sigma_x: float = 0.0,
    source_sigma_y: float = 0.0,
    normalize: bool = True,
) -> tuple[np.ndarray, WaferGrid]:
    """Compute the coherent aerial image at the wafer plane.

    Parameters
    ----------
    mask_field : complex ndarray (ny, nx)
        Output of `kirchhoff_mask` (or any mask model).
    mask_grid : MaskGrid
        Sampling of the mask plane.
    pupil_spec : PupilSpec, optional
        If None, defaults to NA=0.55, ε=0.20, lambda=13.5 nm, no aberration.
    anamorphic : bool
        If False, mag_x and mag_y are forced to 1 (1× imaging for tests).
    source_sigma_x, source_sigma_y : float
        Off-axis source point in normalized pupil coordinates for Phase 2
        partial-coherence integration. `(0, 0)` is the original on-axis source.
    normalize : bool
        If True, scale the output peak to 1. Partial-coherence integration can
        set this False per source point and normalize after incoherent summation.

    Returns
    -------
    intensity : float ndarray (ny, nx)
        Aerial image intensity |E|^2 at the wafer plane.
    wafer : WaferGrid
        Pixel sampling of the returned image.
    """
    if mask_field.shape != mask_grid.shape():
        raise ValueError(
            f"mask_field shape {mask_field.shape} does not match grid {mask_grid.shape()}"
        )
    if pupil_spec is None:
        pupil_spec = PupilSpec(grid_size=max(mask_grid.nx, mask_grid.ny))
    _validate_source_sigma(source_sigma_x, source_sigma_y)

    wafer = wafer_grid_from_mask(mask_grid, mag_x, mag_y, anamorphic)

    # Sanity: aerial-plane Nyquist must support the pupil cutoff NA/λ.
    nyquist_x = 0.5 / wafer.pixel_x_m
    nyquist_y = 0.5 / wafer.pixel_y_m
    cutoff = pupil_spec.na / pupil_spec.wavelength
    if min(nyquist_x, nyquist_y) < cutoff:
        raise ValueError(
            f"pupil cutoff {cutoff:.3e} 1/m exceeds aerial Nyquist "
            f"{min(nyquist_x, nyquist_y):.3e}. Increase mask grid resolution."
        )

    pupil = _build_aerial_pupil(
        wafer,
        na=pupil_spec.na,
        obscuration_ratio=pupil_spec.obscuration_ratio,
        wavelength=pupil_spec.wavelength,
        zernike=dict(pupil_spec.zernike) if pupil_spec.zernike else None,
        defocus_m=pupil_spec.defocus_m,
        defocus_approximation=pupil_spec.defocus_approximation,
    )

    tilted_field = _apply_source_tilt(
        mask_field,
        wafer,
        source_sigma_x=source_sigma_x,
        source_sigma_y=source_sigma_y,
        na=pupil_spec.na,
        wavelength=pupil_spec.wavelength,
    )
    spectrum = np.fft.fftshift(np.fft.fft2(tilted_field))
    filtered = spectrum * pupil
    field = np.fft.ifft2(np.fft.ifftshift(filtered))
    intensity = np.abs(field) ** 2

    # Reference scale: intensity that a perfectly clear mask (M = 1) would
    # produce after the same pupil. This blocks the divide-by-noise case
    # when nothing physically passes through the pupil (e.g. sub-resolution
    # pattern + central obscuration that kills DC). Floor to zero in that case.
    n_pixels = float(mask_field.size)
    bright_field_amp = float(np.sum(np.abs(pupil)) / n_pixels)
    bright_field_intensity = bright_field_amp * bright_field_amp
    noise_floor = max(bright_field_intensity, 1.0) * 1e-12

    peak = float(np.max(intensity))
    if normalize and peak > noise_floor:
        intensity = intensity / peak
    elif peak <= noise_floor:
        intensity = np.zeros_like(intensity)
    return intensity.astype(np.float64), wafer


def contrast(intensity: np.ndarray) -> float:
    """Michelson contrast (I_max - I_min) / (I_max + I_min)."""
    i_max = float(np.max(intensity))
    i_min = float(np.min(intensity))
    if i_max + i_min <= 0.0:
        return 0.0
    return (i_max - i_min) / (i_max + i_min)


def nils(
    intensity_line: np.ndarray,
    pixel_size_m: float,
    cd_target_m: float,
    threshold: float = 0.3,
) -> float:
    """Normalized Image Log Slope along a 1-D intensity profile.

    NILS = CD · |∂ln I / ∂x| evaluated at the threshold crossing nearest
    the pattern edge.
    """
    if intensity_line.ndim != 1:
        raise ValueError("intensity_line must be 1-D")
    if intensity_line.size < 3:
        raise ValueError("intensity_line too short")
    log_i = np.log(np.maximum(intensity_line, 1e-12))
    dlog = np.gradient(log_i, pixel_size_m)
    edge = np.argmin(np.abs(intensity_line - threshold))
    return float(cd_target_m * abs(dlog[edge]))


def cd_from_threshold(
    intensity_line: np.ndarray,
    pixel_size_m: float,
    threshold: float = 0.3,
) -> float:
    """First-pass CD measurement: width above the threshold in a 1-D slice."""
    if intensity_line.ndim != 1:
        raise ValueError("intensity_line must be 1-D")
    above = intensity_line > threshold
    n_above = int(np.count_nonzero(above))
    return n_above * pixel_size_m
