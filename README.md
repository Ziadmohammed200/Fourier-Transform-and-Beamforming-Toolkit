# Fourier Transform and Beamforming Toolkit


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

![Image Viewers](https://github.com/marcilino-adel/Image-mixer-and-Beamforming/blob/56211bc0c856e82ac090ae61f2cfa64b88ce6e7a/Photos/Image%20Mixer%201.png)

#### ⚖️ **2. Two Output Ports**
- Display the mixer results in two dedicated output viewports.
- Each viewport operates independently and mirrors the functionality of input viewports.

![Output Ports](https://github.com/marcilino-adel/Image-mixer-and-Beamforming/blob/56211bc0c856e82ac090ae61f2cfa64b88ce6e7a/Photos/Image%20Mixer%202.png)

#### 🔬 **3. Components Mixer**
- Combine FT components from the four input images using weighted averages.
- Customize weights for:
  - Magnitude and phase
  - Real and imaginary components

![Components Mixer](https://github.com/marcilino-adel/Image-mixer-and-Beamforming/blob/56211bc0c856e82ac090ae61f2cfa64b88ce6e7a/Photos/Image%20Mixer%203.png)
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

![Beam Steering](https://github.com/marcilino-adel/Image-mixer-and-Beamforming/blob/56211bc0c856e82ac090ae61f2cfa64b88ce6e7a/Photos/2D%20Beamforming%20Simulator%202.png)
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

![Scenario Management](https://github.com/marcilino-adel/Image-mixer-and-Beamforming/blob/56211bc0c856e82ac090ae61f2cfa64b88ce6e7a/Photos/2D%20Beamforming%20Simulator%20sc1.png)
![Scenario Management2](https://github.com/marcilino-adel/Image-mixer-and-Beamforming/blob/56211bc0c856e82ac090ae61f2cfa64b88ce6e7a/Photos/2D%20Beamforming%20Simulator%20sc2.png)
![Scenario Management3](https://github.com/marcilino-adel/Image-mixer-and-Beamforming/blob/56211bc0c856e82ac090ae61f2cfa64b88ce6e7a/Photos/2D%20Beamforming%20Simulator%20sc3.png)

---

## Project Structure

### Directories
- **src/**: Source code for both FT mixer and beamforming simulator.
- **images/**: Sample images 
- **Photos/**: Screen shoots.

### Files
- **README.md**: Project overview and setup instructions.
- **requirements.txt**: List of dependencies.
- **main.py**: Implementation of the FT Magnitude/Phase Mixer.
- **Beamforming.py**: Implementation of the Beamforming Simulator.
- **ImageLabel.ui**: To handle image label.

---

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Steps
1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/your-username/ft-beamforming-toolkit.git](https://github.com/marcilino-adel/Image-mixer-and-Beamforming.git)
   cd ft-beamforming-toolkit
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python main.py for image mixer
   python Beanforming.py for Beamform
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


## Contributors
- [Ziad Mohamed](https://github.com/Ziadmohammed200) 
- [Marcilino Adel](https://github.com/marcilino-adel)
- [Ahmed Etman](https://github.com/AhmedEtma)
- [Pavly Awad](https://github.com/PavlyAwad)
- [Ahmed Rafat](https://github.com/AhmeedRaafatt)

