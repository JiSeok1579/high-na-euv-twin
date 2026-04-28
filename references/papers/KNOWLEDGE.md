# Integrated Reference Knowledge

This document summarizes how the reference papers inform the simulator. It is a
compact English guide, not a substitute for the papers.

## Simulator Chain

```text
source -> illuminator -> reflective mask -> projection optics -> wafer focus
       -> aerial image -> resist response -> correction / optimization
```

## Core Ideas

- High-NA improves resolution but reduces depth of focus.
- Anamorphic projection is required to keep mask-side constraints manageable.
- Central obscuration and pupil shape affect contrast and sidelobes.
- Mask 3D effects create shadowing, bias, telecentricity, contrast loss,
  best-focus shift, and secondary-image risks.
- Resist behavior should be modeled in levels: threshold, blur, depth, and
  stochastic response.
- SMO / PMWO should optimize source and mask variables against interpretable
  image, resist, LWR, and regularization terms.

## Phase-to-Paper Map

| Phase | Main papers | Implementation use |
| --- | --- | --- |
| Phase 1 | 19, 15, 11 | Fourier optics, anamorphic scaling, central obscuration. |
| Phase 2 | 16, 18, 8, 5 | Source shape, relay/facet context, spectrum options. |
| Phase 3 | 14, 5 | DOF trend and focus-window interpretation. |
| Phase 4 | 12, 7, 17, 2 | Reduced mask 3D effects and absorber sensitivity. |
| Phase 5 | 4, 1, 20, 21, 13 | Resist levels, depth attenuation, stochastic limits. |
| Phase 6 | 9, 10, 6, 16 | SMO and PMWO objective design. |

## Validation Guidance

- Use 2D heatmaps and line plots for physical validation.
- Use 3D surfaces only as demo views unless the data is truly resolved across
  all plotted axes.
- Keep every reduced model labeled as reduced, qualitative, or study-grade.
- Avoid claiming process accuracy without public quantitative calibration.

## Open Questions

- How strong should the Phase 4 reduced M3D coefficients be for default demos?
- Which public values are reliable enough for quantitative DOF comparison?
- How should stochastic resist terms be weighted for Phase 6 without overfitting
  to a single paper?
- Which source parameterization gives the best balance between interpretability
  and optimization flexibility?
