# Fourier Transform and Beamforming Toolkit

## Introduction
This project includes two major components: a Fourier Transform (FT) Magnitude/Phase Mixer and a Beamforming Simulator. Together, these tools provide a comprehensive understanding of signal decomposition and beamforming techniques for real-time applications in fields such as communications, medical imaging, and signal processing.

---

## Features

### Part A: FT Magnitude/Phase Mixer or Emphasizer

#### **1. Image Viewers**
- **Grayscale Images**:
  - Open and view up to four grayscale images, each in its own viewport.
  - Automatically convert colored images to grayscale.
- **Unified Image Size**:
  - Automatically resize all images to match the smallest dimensions among them.
- **FT Components**:
  - For each image, display the following components via a dropdown menu:
    1. FT Magnitude
    2. FT Phase
    3. FT Real
    4. FT Imaginary
- **Easy Browsing**:
  - Replace any image by double-clicking its viewport to browse and load a new image.

*(Insert image/video showcasing image viewers and component selection)*

#### **2. Two Output Ports**
- Display the mixer results in one of two dedicated output viewports.
- Each viewport operates independently and mirrors the functionality of input viewports.

#### **3. Brightness/Contrast Adjustments**
- Modify brightness and contrast of any image or FT component via mouse drag:
  - Up/Down: Adjust brightness
  - Left/Right: Adjust contrast

*(Insert image demonstrating brightness/contrast adjustment)*

#### **4. Components Mixer**
- Combine FT components from the four input images using weighted averages.
- Customize weights for:
  - Magnitude and phase
  - Real and imaginary components
- Intuitive slider-based UI for setting component weights.

*(Insert image of component mixing interface with sliders)*

#### **5. Regions Mixer**
- Define a rectangular region on each FT component:
  - Inner region (low frequencies)
  - Outer region (high frequencies)
- Options to include either region in the output.
- Highlight the selected region with semi-transparent coloring or hashing.
- Unified region size across all four images, adjustable via sliders or resize handles.

*(Insert image showing region selection and highlighting)*

#### **6. Real-Time Mixing**
- Perform Inverse FFT (iFFT) to generate output images in real time.
- Features include:
  - Progress bar to indicate the status of the operation.
  - Thread management to cancel ongoing operations and prioritize new requests.

*(Insert video of real-time mixing with progress bar)*

---

### Part B: Beamforming Simulator

#### **1. Real-Time Beam Steering**
- Customize parameters to steer the beam direction dynamically:
  - Number of transmitters/receivers
  - Applied delays/phase shifts
  - Number of operating frequencies (with real-time updates)

#### **2. Array Geometry**
- Support for linear and curved array geometries:
  - Adjustable curvature parameters for curved arrays.

#### **3. Visualization**
- Display constructive/destructive interference maps and beam profiles in synchronized viewers.

*(Insert image/video of beamforming maps and profiles)*

#### **4. Multi-Array Support**
- Add multiple phased array units to the system.
- Customize location and parameters of each unit.

#### **5. Scenario Management**
- Include at least three predefined scenarios inspired by:
  - 5G communications
  - Ultrasound imaging
  - Tumor ablation
- Load, visualize, and fine-tune scenarios via parameter settings files.

*(Insert video showcasing scenarios and parameter customization)*

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

1. **FT Mixer**:
   - Open and manipulate grayscale images.
   - Explore FT components and perform real-time mixing.

2. **Beamforming Simulator**:
   - Adjust array geometry and parameters to visualize beam patterns.
   - Load predefined scenarios or create custom setups.

---

## License
This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments
- Tutorials and inspiration from [relevant links].
- Contributions by [Team Name/Group].


