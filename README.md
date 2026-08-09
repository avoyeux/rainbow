# RAINBOW

3D visualisation and re-projection of a solar protuberance (the "Rainbow" event, 23–25 July 2012), observed by STEREO and SDO, to study the periodic properties of coronal rain. The 3D visualisation relies on the [K3D](https://github.com/K3D-tools/K3D-jupyter) Jupyter library.

Requires Python >= 3.12.3

## Setup

Create a virtual environment, then install the project (dependencies are defined in `pyproject.toml`):

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install .
```

> Jupyter can then be used from the notebook in `src/animation/animation_vis.ipynb`.

## Structure

- `src/animation/` — K3D 3D visualisation of the filament data and its polynomial fit ([animation_code.py](src/animation/animation_code.py)) with the entry-point notebook [animation_vis.ipynb](src/animation/animation_vis.ipynb).
- `src/projection/` — orthographic re-projection of the polynomial fit onto the SDO point of view, envelope extraction, image warping and plotting.
- `src/data/` — HDF5 data creation from the STEREO/SDO acquisitions ([cubes.py](src/data/cubes.py)), fake data generation, polynomial fitting and merging of real + fake data.
- `src/miscellaneous/` — small utilities such as PNG-to-video conversion.
- `src/tests/` & `src/manual_tests/` — automated and manual tests.
- `src/archive/` — deprecated and legacy code (kept for reference).
- `config/` — configuration settings (`config.yml`). 