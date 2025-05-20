# Lucida

Lucida is a tool for analyzing microscopy videos, focusing on particle detection and their blinking behavior. This project aims to support researchers working with fluorescence microscopy data, especially in single-molecule experiments.

## Features

- Automatic particle detection in TIFF videos.
- Calculation of particle center coordinates with adjacent filtering.
- Temporal analysis of fluorescence intensity for each particle.
- Generation of intensity vs. time plots for selected particles.
- Customizable filtering based on mean intensity, standard deviation, and threshold-crossing events.

## Requirements

- Python 3.8+
- Required libraries:
  - `numpy`
  - `pandas`
  - `Pillow`
  - `matplotlib`
  - `opencv-python`
  - `easygui`
  - `tqdm`

You can install the required packages with:

```bash
pip install numpy pandas Pillow matplotlib opencv-python easygui tqdm
```

## How to Use

1. Run the script `identificador_particulas.py`:
   - Select the TIFF file to be analyzed.
   - The script will detect bright particles based on an automatically calculated threshold.
   - Detected particle coordinates will be saved to a `centros.csv` file.

2. Run the script `analise_intermitencia.py`:
   - Select the same TIFF file.
   - The script will use `centros.csv` to extract intensity over time for each particle.
   - Filters will be applied, and plots will be saved for selected particles.

## Output Files

- `centros.csv`: contains X/Y coordinates of particles, intensity threshold, and average intensity.
- `particulaX-xY-yZ.png`: intensity vs. time plots for filtered particles.

## License

This project is licensed under the MIT License. Feel free to use, modify, and share it.

---

**Lucida** — A tool for single molecule intermittency analysis