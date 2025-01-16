# Fourier Transform and Beamforming Toolkit

![Tool Logo](https://via.placeholder.com/150)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/) [![GitHub Issues](https://img.shields.io/github/issues/your-username/ft-beamforming-toolkit)](https://github.com/your-username/ft-beamforming-toolkit/issues)

## Introduction
This project includes two major components: a **Fourier Transform (FT) Magnitude/Phase Mixer** and a **Beamforming Simulator**. These tools provide an interactive platform to explore signal decomposition and beamforming techniques, tailored for real-time applications in fields such as communications, medical imaging, and signal processing.

---

## Features

### Part A: FT Magnitude/Phase Mixer

#### ✨ **1. Image Viewers**
- **Grayscale Images**:
  - Open and view up to four grayscale images, each in its own viewport.
  - Automatically convert colored images to grayscale.
- **Unified Image Size**:
  - Automatically resize all images to match the smallest dimensions among them.
- **FT Components**:
  - For each image, display the following components via a dropdown menu:
    - FT Magnitude
    - FT Phase
    - FT Real
    - FT Imaginary
- **Easy Browsing**:
  - Replace any image by double-clicking its viewport to browse and load a new image.

![Image Viewers](docs/images/image_viewers.png "Image Viewers")

#### ⚖️ **2. Two Output Ports**
- Display the mixer results in two dedicated output viewports.
- Each viewport operates independently and mirrors the functionality of input viewports.

![Output Ports](docs/images/output_ports.png "Output Ports")

#### 🔬 **3. Components Mixer**
- Combine FT components from the four input images using weighted averages.
- Customize weights for:
  - Magnitude and phase
  - Real and imaginary components

![Components Mixer](docs/images/components_mixer.png "Components Mixer")

#### 🌐 **4. Regions Mixer**
- Define a rectangular region on each FT component:
  - Inner region (low frequencies)
  - Outer region (high frequencies)
- Options to include either region in the output.
- Unified region size across all four images, adjustable via resize handles.

![Regions Mixer](docs/images/regions_mixer.png "Regions Mixer")

#### ⏳ **5. Real-Time Mixing**
- Perform Inverse FFT (iFFT) to generate output images in real time.
- Includes:
  - Progress bar to indicate operation status.

![Real-Time Mixing](docs/images/real_time_mixing.png "Real-Time Mixing")

---

### Part B: Beamforming Simulator

#### ⏫ **1. Real-Time Beam Steering**
- Customize parameters to dynamically steer the beam direction:
  - Number of transmitters
  - Applied phase shifts
  - Operating frequency (real-time updates)

![Beam Steering](docs/images/beam_steering.png "Beam Steering")

#### 🗺️ **2. Array Geometry**
- Support for linear and curved array geometries:
  - Adjustable curvature parameters for curved arrays.

![Array Geometry](docs/images/array_geometry.png "Array Geometry")

#### 💡 **3. Visualization**
- Display constructive/destructive interference maps and beam profiles in synchronized viewers.

![Beamforming Maps](docs/images/beamforming_maps.png "Beamforming Maps")

#### 🛠️ **4. Multi-Array Support**
- Add multiple phased array units to the system.
- Customize location and parameters of each unit.

![Multi-Array Support](docs/images/multi_array_support.png "Multi-Array Support")

#### 🔄 **5. Scenario Management**
- Include at least three predefined scenarios inspired by:
  - 5G communications
  - Ultrasound imaging
  - Tumor ablation
- Load, visualize, and fine-tune scenarios via parameter settings files.

![Scenario Management](docs/images/scenario_management.png "Scenario Management")

---

## Project Structure

### Directories
- **src/**: Source code for both FT mixer and beamforming simulator.
- **data/**: Sample images and parameter files for scenarios.
- **docs/**: Documentation and user guides.

### Files
- **README.md**: Project overview and setup instructions.
- **requirements.txt**: List of dependencies.
- **ft_mixer.py**: Implementation of the FT Magnitude/Phase Mixer.
- **beamforming_simulator.py**: Implementation of the Beamforming Simulator.
- **ui_design.ui**: Qt Designer file for the graphical user interface.

---

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/ft-beamforming-toolkit.git
   cd ft-beamforming-toolkit
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

---

## Usage

### FT Mixer
- Open and manipulate grayscale images.
- Explore FT components and perform real-time mixing.

### Beamforming Simulator
- Adjust array geometry and parameters to visualize beam patterns.
- Load predefined scenarios or create custom setups.

---

## License
This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments
- Tutorials and inspiration from [relevant links].
- Contributions by [Team Name/Group].

For any issues or contributions, please open an issue or submit a pull request on the [GitHub repository](https://github.com/your-username/ft-beamforming-toolkit).

