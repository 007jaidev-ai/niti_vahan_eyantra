# Niti Vahan - eYRC 2026-27 (Team NV#3156)

## Setup

### 1. Install Miniconda
Download from https://docs.conda.io/en/latest/miniconda.html and install with defaults.

### 2. Clone this repo
```
git clone https://github.com/007jaidev-ai/niti_vahan_eyantra.git
cd niti_vahan_eyantra
```

### 3. Create the conda environment
```
conda env create -f environment.yml
```
If you get a Terms of Service error, run these first:
```
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
```

### 4. Activate the environment
```
conda activate NV_3156
```

### 5. Verify
```
python -c "import cv2, numpy, coppeliasim_zmqremoteapi_client; print('ok')"
```

### 6. Install CoppeliaSim
Download CoppeliaSim Edu from https://www.coppeliarobotics.com/downloads — install the Windows x86_64 version.
