# High-NA EUV Lithography Simulator

Research and education simulator for 0.55 NA EUV lithography. The code follows
the source -> illumination -> reflective mask -> anamorphic projection -> wafer
-> resist path with reduced Fourier optics, depth-of-focus, Mask 3D, and
photoresist models.

## Study Purpose / 스터디 목적

This is a **study-purpose simulator**, not a paper, report, or industry
deployment tool. Goals:

1. **Build** a working simulation of 0.55 NA EUV lithography.
2. **Visualize** results in 3D: focus stack, pupil wavefront, and resist depth.
3. **Understand qualitatively**:
   - the structural pipeline: source -> mask -> optics -> wafer -> resist
   - what a good result looks like at each stage
   - which input parameters can be fine-tuned and how the output responds

**This is not**:

- Paper or report writing.
- Real-equipment 1:1 replication or reverse engineering.
- Industry-grade quantitative validation. Data and paper sources are
  inconsistent, so strict industrial validation is out of scope.

본 프로젝트는 **스터디 목적의 시뮬레이터**입니다. 데이터·논문 출처가
일관되지 않으므로 정량적 산업 검증은 범위 밖이며, 다음을 정성적으로 학습합니다:

1. 시뮬레이션을 만들어서 작동시키기: Build.
2. 결과를 3D로 시각화하여 구조와 흐름 보기: Visualize.
3. 좋은 결과가 무엇인지 정성 파악하고, 입력 미세조정이 출력에 미치는 영향 학습:
   Understand and fine-tune.

**엄격한 산업 정량 검증은 추구하지 않습니다.** 일단 구현 -> 결과 확인
-> 미세조정 -> 활용 학습이 핵심입니다.

## Quick Start

```bash
python -m pip install -r requirements-dev.txt
pytest tests/ -v
jupyter lab notebooks/0_first_aerial_image.ipynb
```

## Current Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Scalar Fourier optics MVP: pupil, mask, aerial image | Complete |
| 2 | Partial coherence / illuminator | Pending |
| 3 | Wafer topography and DOF | Complete through k2 fitting |
| 4 | Mask 3D effects | Part 04: rigorous-data import and aerial regression hooks |
| 5 | Photoresist: threshold, blur, depth, stochastic | Complete through calibration exit gates |
| 6 | SMO / PMWO / OPC / ILT | Pending |

## Notebook Demos

- `notebooks/0_first_aerial_image.ipynb`
- `notebooks/3d_focus_stack.ipynb` - 3D focus and contrast sweeps.
- `notebooks/3d_pupil_wavefront.ipynb` - 3D Zernike mode comparison.
- `notebooks/3d_resist_depth.ipynb` - 3D dose-depth absorption sweep.
- `notebooks/3_M3D_effects.ipynb`
- `notebooks/4a_threshold_resist.ipynb`
- `notebooks/4b_resist_levels.ipynb`

## Main References

- `PROJECT_OVERVIEW.md` - project inventory, roadmap, and operating context.
- `진행계획서.md` - phase plan, KPIs, WBS, and risk register.
- `docs/phase4_M3D_design.md` - Phase 4 Mask 3D boundary, lookup import, and aerial-regression model.
- `docs/phase5_resist_models.md` - Phase 5 resist model stack.
- `docs/study_grade_relaxation.md` - study-purpose strictness and audit severity policy.
- `docs/github_claude_automerge_setup.md` - GitHub automation setup.
- `audits/AUDIT_LOG.md` - audit and mitigation task tracking.

## License

Research and education use. Commercial use requires separate agreement.
