# Lucida

Lucida is a tool for analyzing fluorescence microscopy videos, with a focus on detecting particles and studying their blinking behavior over time. It is designed to help researchers process sequences of TIFF images and extract useful information about fluorescent particle dynamics.

## Features

- Detects bright particles in microscopy TIFF videos.
- Filters out adjacent or redundant detections.
- Measures the temporal intensity variation of each detected particle.
- Applies statistical filters to select relevant particles.
- Saves CSV and PNG outputs for further analysis or publication.

## Folder Structure

```
Lucida/
├── main.py
├── identificador_particulas.py
├── utils.py
├── analise_intermitencia.py
```

## Requirements

- Python 3.8+
- Required libraries:
  - `numpy`
  - `pandas`
  - `Pillow`
  - `matplotlib`
  - `opencv-python`
  - `tqdm`
  - `easygui`

Install all dependencies using pip:

```bash
pip install numpy pandas Pillow matplotlib opencv-python easygui tqdm
```

## How to Use

1. Run the main script:

```bash
python main.py
```

2. A folder selection dialog will appear. Choose the directory containing your `.tif` files.

3. For each `.tif` file, the program will:
   - Move it to a new subfolder.
   - Detect particles and save their coordinates in `centros.csv`.
   - Analyze intermittency and save plots (`particulaN-xX-yY.png`).

## Output Files

- `centros.csv`: CSV file containing the detected particle positions (X, Y), threshold value, and average intensity.
- `particulaN-xX-yY.png`: Plots of fluorescence intensity over time for each selected particle.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**Lucida** — A tool for single molecule intermittency analysis