import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QRegularExpressionValidator
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QSlider, QSpinBox, QCheckBox, QComboBox, QLineEdit, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QRegularExpression
from matplotlib import transforms

import logging
logging.basicConfig(
    level=logging.DEBUG,  # Adjust level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("beamforming_simulator.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)


# Wave Emission Simulation (from first script)
def CalculatePhaseFromFocus(x, y, e):
    return np.sqrt(np.sum((e.r-np.array([x, y]))**2))*(2*np.pi/e.lambda0)
class Emitter():
    def __init__(self, x, y, c, f, phi, rMax=100, color="tab:blue", alpha=0.6):
        self.r, self.c, self.f, self.rMax, self.alpha = np.array(
            [x, y]), c, f, rMax, alpha
        self.color = color
        self.SetUp()
        self.SetPhase(phi)

    def Increment(self, dt):
        self.t += dt
        if self.t < self.t0:
            return
        for i, circle in enumerate(self.circles):
            r = i*self.lambda0 + self.Wrap(self.lambda0*self.phi/(2*np.pi) +
                                           self.c * self.t, self.lambda0)
            circle.set_height(2*r)
            circle.set_width(2*r)
            circle.set_alpha(self.alpha if i < ((self.t-self.t0)/self.T) else 0)

    def SetPhase(self, phi):
        self.phi = self.Wrap(phi, 2*np.pi)
        self.t0 = self.T*(1-self.phi/(2*np.pi))
        self.t = 0

    def SetUp(self):
        self.lambda0 = self.c/self.f
        self.T = 1./self.f
        self.N = int(np.ceil(self.rMax/self.lambda0))
        self.circles = [plt.Circle(xy=tuple(self.r), fill=False, lw=2,
                                   radius=0, alpha=self.alpha,
                                   color=self.color)
                        for i in range(self.N)]

    def Wrap(self, x, x_max):
        if x >= 0:
            return x - np.floor(x/x_max) * x_max
        if x < 0:
            return x_max - (-x - np.floor(-x/x_max) * x_max)

class EmitterArray():
    def __init__(self):
        self.emitters = []

    def AddEmitter(self, e):
        self.emitters.append(e)

    def Increment(self, dt):
        for emitter in self.emitters:
            emitter.Increment(dt)

    def GetCircles(self):
        circles = []
        for emitter in self.emitters:
            circles.extend(emitter.circles)
        return circles

    def RemoveOffset(self):
        offsets = []
        for emitter in self.emitters:
            offsets.append(emitter.t0)
        offset_min = np.min(offsets)
        for emitter in self.emitters:
            emitter.Increment(offset_min)

    @property
    def circles(self):
        return self.GetCircles()



class PhasedArray:
    def __init__(self, name, num_elements=4, spacing_value=50, spacing=0.5, spacing_unit="Meters",
                 axis='x', speed=3e8, frequency=1e9, geometry='linear', radius=1.0,
                 steering_angle=0, semicircle=True, position_x=0, position_y=0):
        self.name = name
        self.num_elements = num_elements
        self.spacing = spacing
        self.spacing_value = spacing_value
        self.axis = axis
        self.spacing_unit = spacing_unit
        self.speed = speed
        self.frequency = frequency
        self.geometry = geometry
        self.radius = radius
        self.units = [1e8, 1e9]
        self.steering_angle = np.deg2rad(steering_angle)
        self.semicircle = semicircle
        self.position_x = position_x
        self.position_y = position_y
        self.enabled = True

    def compute_array_factor(self, theta):
        """Compute the array factor based on the array configuration."""
        wavelength = float(self.speed) / float(self.frequency)
        k = 2 * np.pi / wavelength  # Wave number

        # Calculate element positions and phase shifts
        if self.geometry == 'linear':
            if self.axis == 'x':
                positions = np.arange(self.num_elements) * self.spacing + self.position_x
            elif self.axis == 'y':
                positions = np.arange(self.num_elements) * self.spacing + self.position_y
                # positions = np.zeros(self.num_elements)
            else:
                raise ValueError("Unsupported axis. Use 'x' or 'y'.")
            phase_shifts = k * positions * np.cos(theta - self.steering_angle)

        # elif self.geometry == 'curved':
        #     angles = np.linspace(0, np.pi, self.num_elements) if self.semicircle else np.linspace(0, 2 * np.pi, self.num_elements)
        #     positions = self.radius * np.sin(angles) + self.position_x
        #     phase_shifts = k * positions * np.cos(theta - self.steering_angle)
        elif self.geometry == 'curved':
            # Define angular positions of elements (semi-circle or full circle)
            angles = np.linspace(0, np.pi, self.num_elements) if self.semicircle else np.linspace(0, 2 * np.pi, self.num_elements)

            # Compute the x and y positions of each element
            x_positions = self.radius * np.cos(angles) + self.position_x
            y_positions = self.radius * np.sin(angles) + self.position_y

            # Calculate the phase shifts for each element
            # Assuming far-field approximation and theta defines the observation direction
            phase_shifts = k * (
                x_positions * np.cos(theta - self.steering_angle) +
                y_positions * np.sin(theta - self.steering_angle)
            )
            # phase_shifts = k * (
            #         x_positions * np.cos(self.steering_angle) +
            #         y_positions * np.sin(self.steering_angle)
            #     )



        else:
            raise ValueError("Unsupported geometry. Use 'linear' or 'curved'.")

        # Compute array factor with normalization for shape stability
        array_factor = np.sum(np.exp(1j * phase_shifts))
        array_factor_magnitude = np.abs(array_factor)

        # Normalize the array factor by the number of elements (N)
        normalized_array_factor = array_factor_magnitude / self.num_elements
        return normalized_array_factor


class BeamformingSimulator:
    def __init__(self):
        self.phased_arrays = []
        logger.info("Initialized Beamforming Simulator.")

    def add_phased_array(self, phased_array):
        logger.debug(f"Adding Phased Array: {phased_array.name}")
        self.phased_arrays.append(phased_array)
        logger.info(f"Phased Array '{phased_array.name}' added.")

    def simulate(self, theta):
        """Combine array factors from all enabled phased arrays."""
        total_output = 0
        logger.debug(f"Simulating for angle {theta:.2f} radians...")
        for phased_array in self.phased_arrays:
            if phased_array.enabled:
                total_output += phased_array.compute_array_factor(theta)
        if len(self.phased_arrays) > 1:
            return self.normalize_total_output(total_output)
        return total_output

    def normalize_total_output(self, total_output):
        """Normalize total output to account for aperture efficiency."""
        if len(self.phased_arrays) > 0:
            max_aperture_size = max([phased_array.num_elements for phased_array in self.phased_arrays])
            normalized_output = total_output / max_aperture_size
            return normalized_output
        return total_output



class BeamformingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.simulator = BeamformingSimulator()
        self.full_circle_mode = False
        self.plot_mode = "Polar"  # New attribute for plot mode

        # Wave Emission Setup
        self.emitter_array = EmitterArray()
        #self.setup_wave_emitters()

        self.init_ui()
        self.animation = None



    def init_ui(self):
        self.setWindowTitle("2D Beamforming Simulator")
        self.setGeometry(100, 100, 1600, 900)

        # Main layout
        main_layout = QHBoxLayout()

        # Control panel for phased arrays
        self.control_panel = QVBoxLayout()

        # Array selection combo box
        self.array_selection_combobox = QComboBox()
        self.array_selection_combobox.currentIndexChanged.connect(self.update_controls_for_selected_array)
        self.control_panel.addWidget(self.array_selection_combobox)

        # Wave Emission Control Buttons
        wave_control_layout = QHBoxLayout()

        add_array_button = QPushButton("Add Phased Array")
        add_array_button.clicked.connect(self.add_phased_array)
        clear_array_button = QPushButton("Clear All")
        clear_array_button.clicked.connect(self.clear_phased_array)

        wave_control_layout.addWidget(add_array_button)
        wave_control_layout.addWidget(clear_array_button)
        self.control_panel.addLayout(wave_control_layout)



        # Wave Emission Control Buttons
        simulation_layout = QHBoxLayout()
        first_button = QPushButton("5G simulation")
        first_button.clicked.connect(self.fifth_generation_simulation)
        second_button = QPushButton("Ultrasound simulation")
        second_button.clicked.connect(self.ultrasound_simulation)
        fourth_button = QPushButton("Tumor ablation simulation")
        fourth_button.clicked.connect(self.tumor_ablation_simulation2)
        third_button = QPushButton("Tumor ablation simulation2")
        third_button.clicked.connect(self.tumor_ablation_simulation)



        simulation_layout.addWidget(first_button)
        simulation_layout.addWidget(second_button)
        simulation_layout.addWidget(fourth_button)
        simulation_layout.addWidget(third_button)



        self.control_panel.addLayout(simulation_layout)

        # Checkbox for full-circle mode
        self.full_circle_checkbox = QCheckBox("Full Circle Mode (360°)")
        self.full_circle_checkbox.stateChanged.connect(self.toggle_full_circle_mode)
        self.control_panel.addWidget(self.full_circle_checkbox)
        # Add a small spacing or margin
        self.control_panel.setSpacing(10)  # Consistent spacing between widgets

        # Plot mode combo box
        plot_mode_layout = QHBoxLayout()
        plot_mode_label = QLabel("Plot Mode:")
        self.plot_mode_combobox = QComboBox()
        self.plot_mode_combobox.addItems(["Polar", "Rectangular"])
        self.plot_mode_combobox.currentIndexChanged.connect(self.update_plots)
        # Adding the label and combobox together
        plot_mode_layout.addWidget(plot_mode_label)
        plot_mode_layout.addWidget(self.plot_mode_combobox)
        self.control_panel.addLayout(plot_mode_layout)


        # Controls layout for the selected array
        self.array_controls_layout = QVBoxLayout()
        self.control_panel.addLayout(self.array_controls_layout)

        # Plot area
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()


        plot_layout2 = QHBoxLayout()

        # Plot 1: Wave Emission Plot
        self.figure_wave = plt.figure(figsize=(8, 8))
        self.canvas_wave = FigureCanvas(self.figure_wave)
        self.canvas_wave.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_layout2.addWidget(self.canvas_wave, stretch=1)  # Assign equal stretch factor

        # Plot 2: Another Plot
        self.figure = plt.figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.figure.subplots_adjust(top=0.8)
        plot_layout2.addWidget(self.canvas, stretch=1)  # Assign equal stretch factor
        plot_layout.addLayout(plot_layout2)

        # Array Geometry Plot
        self.figure_geometry = plt.figure(figsize=(6, 6))
        self.canvas_geometry = FigureCanvas(self.figure_geometry)
        self.canvas_geometry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.figure_geometry.subplots_adjust(bottom=0.15)


        plot_layout.addWidget(self.canvas_geometry)

        plot_widget.setLayout(plot_layout)

        main_layout.addLayout(self.control_panel, 2)
        main_layout.addWidget(plot_widget, 5)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.add_default_array()  # Add default array during initialization
        self.setup_wave_plot()  # Setup initial wave plot
        self.update_plots()  # Ensure plots are updated for the default array

    def setup_wave_emitters(self, phased_array):
            # write here the if conditional for the linear or curved arrays
            # Setup wave emitters similar to the first script's Demo 3
            # obj1= PhasedArray()
            # print(phased_array.units[0],phased_array.units[1])
            logger.info(f"Phased Array '{phased_array.units[0],phased_array.units[1]}' units.")
            speed, freq = float(phased_array.speed)/float(phased_array.units[0]), float(phased_array.frequency) / float(phased_array.units[1])
            # print(speed, freq)
            logger.info(f"Phased Array '{speed, freq}' speed and frequency.")
            # if speed<freq:
            #     speed+=2*freq
            #     print(speed)
            lambda0 = speed / freq
            N = phased_array.num_elements

            # xs = np.linspace(-lambda0, lambda0, N)
            xs = np.linspace(-1, 1, N)
            ys = np.zeros_like(xs)
            for i in range(N):
                e = Emitter(xs[i], ys[i], speed, freq, 0)
                phase = CalculatePhaseFromFocus(0, 20, e)
                e.SetPhase(phase)
                self.emitter_array.AddEmitter(e)

            self.emitter_array.RemoveOffset()

    def setup_wave_plot(self):
        """Setup the dynamic wave interference plot as a heat map"""
        self.figure_wave.clear()

        # Create subplot with equal aspect ratio
        ax = self.figure_wave.add_subplot(111)
        ax.set_aspect('equal')

        # Define the original grid size (visible plot limits)
        # grid_limit = 50
        # original_size = 2 * grid_limit

        # Calculate diagonal length for rotation (expanded grid size)
        # diagonal_length = np.sqrt(2) * original_size
        # expanded_limit = diagonal_length / 2
        grid_limit = 1e7
        expanded_limit = np.sqrt(2) * grid_limit

        # Create an expanded 2D grid for interference calculation
        x = np.linspace(-expanded_limit, expanded_limit, 500)
        y = np.linspace(-expanded_limit, expanded_limit, 500)
        X, Y = np.meshgrid(x, y)

        # Calculate interference at each point from different phased arrays
        interference = np.zeros_like(X, dtype=float)

        # Store the first enabled array's steering angle for plot rotation
        rotation_angle = 0
        for phased_array in self.simulator.phased_arrays:
            if phased_array.enabled:
                rotation_angle = np.degrees(phased_array.steering_angle)
                break

        for phased_array in self.simulator.phased_arrays:
            if not phased_array.enabled:
                continue

            # wavelength = float(phased_array.speed) / float(phased_array.frequency)
            wavelength = float(phased_array.speed) / float(phased_array.frequency)
            k = 2 * np.pi / wavelength


            # Calculate element positions and interference
            if phased_array.geometry == 'linear':
                if phased_array.axis == 'x':
                    element_positions = np.array([
                        [x_pos, phased_array.position_y]
                        for x_pos in np.linspace(
                            phased_array.position_x - (phased_array.num_elements - 1) * phased_array.spacing / 2,
                            phased_array.position_x + (phased_array.num_elements - 1) * phased_array.spacing / 2,
                            phased_array.num_elements
                        )
                    ])
                else:
                    element_positions = np.array([
                        [phased_array.position_x, y_pos]
                        for y_pos in np.linspace(
                            phased_array.position_y - (phased_array.num_elements - 1) * phased_array.spacing / 2,
                            phased_array.position_y + (phased_array.num_elements - 1) * phased_array.spacing / 2,
                            phased_array.num_elements
                        )
                    ])
            elif phased_array.geometry == 'curved':
                angles = np.linspace(0, -np.pi, phased_array.num_elements) if phased_array.semicircle else np.linspace(0,
                                                                                                                      2 * np.pi,
                                                                                                                      phased_array.num_elements)
                element_positions = np.array([
                    [phased_array.position_x + phased_array.radius * np.cos(angle),
                     phased_array.position_y + phased_array.radius * np.sin(angle)]
                    for angle in angles
                ])

            for element_pos in element_positions:
                distance = np.sqrt((X - element_pos[0]) ** 2 + (Y - element_pos[1]) ** 2)
                # phase = 2 * np.pi * distance / wavelength
                # phase = (2 * np.pi * distance / wavelength) % (2 * np.pi)
                # Normalize phase differences relative to reference wavelength
                phase = (2 * np.pi * distance / wavelength) % (2 * np.pi)
                normalized_phase = phase / (2 * np.pi)  # Normalize to [0, 1]

                # Add normalized phase contribution
                interference += np.cos(2 * np.pi * normalized_phase)
                r = np.sqrt((X - element_pos[0])**2 + (Y - element_pos[1])**2)
                # theta = np.arctan2(Y - element_pos[1], X - element_pos[0])
                phase_shift = k * r + phased_array.steering_angle
                interference += np.cos(phase_shift)

                # interference += np.cos(phase)

        # Normalize interference
        range_value = (interference.max() - interference.min())/phased_array.num_elements
        if range_value > 0:
            interference = (interference - interference.min()) / range_value

        # Set up the rotated plot
        tr = transforms.Affine2D().rotate_deg(rotation_angle) + ax.transData

        # Display the expanded heatmap
        self.im = ax.imshow(interference, extent=(-expanded_limit, expanded_limit, -expanded_limit, expanded_limit),
                            origin='lower', cmap='coolwarm', alpha=0.7, transform=tr)

        # Set up the plot limits to crop the display to the original size
        ax.set_xlim(-grid_limit, grid_limit)
        ax.set_ylim(-grid_limit, grid_limit)
        ax.grid(True, alpha=0.2)

        # Add colorbar
        plt.colorbar(self.im, ax=ax, label='Interference Intensity')

        # Set title with rotation angle
        ax.set_title(f"Wave Interference Heat Map (Rotated {rotation_angle:.1f}°)")

        # Add axis labels
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Distance (m)")

        # Add array element positions
        for phased_array in self.simulator.phased_arrays:
            if not phased_array.enabled:
                continue

            if phased_array.geometry == 'linear':
                if phased_array.axis == 'x':
                    element_x = np.linspace(
                        phased_array.position_x - (phased_array.num_elements - 1) * phased_array.spacing / 2,
                        phased_array.position_x + (phased_array.num_elements - 1) * phased_array.spacing / 2,
                        phased_array.num_elements
                    )
                    element_y = np.full_like(element_x, phased_array.position_y)
                else:
                    element_y = np.linspace(
                        phased_array.position_y - (phased_array.num_elements - 1) * phased_array.spacing / 2,
                        phased_array.position_y + (phased_array.num_elements - 1) * phased_array.spacing / 2,
                        phased_array.num_elements
                    )
                    element_x = np.full_like(element_y, phased_array.position_x)
            elif phased_array.geometry == 'curved':
                angles = np.linspace(0, -np.pi, phased_array.num_elements) if phased_array.semicircle else np.linspace(0,
                                                                                                                      2 * np.pi,
                                                                                                                      phased_array.num_elements)
                element_x = phased_array.position_x + phased_array.radius * np.cos(angles)
                element_y = phased_array.position_y + phased_array.radius * np.sin(angles)

            # Plot array elements with the same rotation transform
            ax.scatter(element_x, element_y, color='black', marker='^', s=30, transform=tr)

        self.canvas_wave.draw()


    def add_default_array(self):
        default_array = PhasedArray(name="Default Array")
        self.simulator.add_phased_array(default_array)
        self.array_selection_combobox.addItem(default_array.name)
        self.update_controls_for_selected_array()
        self.update_plots()
    # self.clear_phased_array
    def clear_phased_array(self):
        self.simulator.phased_arrays=[]
        self.array_selection_combobox.clear()
        self.add_default_array()

    def add_phased_array(self):
        array_name = f"Array {len(self.simulator.phased_arrays) + 1}"
        phased_array = PhasedArray(name=array_name)
        self.simulator.add_phased_array(phased_array)
        self.array_selection_combobox.addItem(array_name)
        self.update_controls_for_selected_array()
        self.update_plots()


    def fifth_generation_simulation(self):
        self.simulator.phased_arrays=[]
        self.array_selection_combobox.clear()
        array_name = "5G array"
        spacing=(float(3e8)/float(28e9))*0.49
        phased_array = PhasedArray(name=array_name, num_elements=16, spacing_value=49,spacing=spacing,spacing_unit= "Wavelength (λ)",axis='x', speed=3e8, frequency=28e9)
        self.simulator.add_phased_array(phased_array)
        self.array_selection_combobox.addItem(array_name)
        self.update_controls_for_selected_array()
        self.update_plots()

    def ultrasound_simulation(self):
        self.simulator.phased_arrays=[]
        self.array_selection_combobox.clear()
        array_name = "Ultrasound array"
        spacing=(float(1540)/float(5e6))*0.06
        phased_array = PhasedArray(name=array_name, num_elements=16, spacing_value=6,spacing=spacing,spacing_unit= "Wavelength (λ)",axis='x', speed=1.54e3, frequency=5e6)
        phased_array.units=[1e3,1e6]
        self.simulator.add_phased_array(phased_array)
        self.array_selection_combobox.addItem(array_name)
        self.update_controls_for_selected_array()
        self.update_plots()


    def tumor_ablation_simulation(self):
        self.simulator.phased_arrays=[]
        self.array_selection_combobox.clear()
        array_name = "Tumor ablation array"

        phased_array = PhasedArray(name=array_name, num_elements=64,geometry='curved',axis='x', speed=1540, frequency=0.5e6,radius=0.07,semicircle=True)
        phased_array.units=[1e3,1e6]
        self.simulator.add_phased_array(phased_array)
        self.array_selection_combobox.addItem(array_name)
        self.update_controls_for_selected_array()
        self.update_plots()
    def tumor_ablation_simulation2(self):
        self.simulator.phased_arrays=[]
        self.array_selection_combobox.clear()
        array_name = "Tumor ablation array"
        spacing=(float(1540)/float(5e6))*0.49
        phased_array = PhasedArray(name=array_name, num_elements=32, spacing_value=49,spacing=spacing,spacing_unit= "Wavelength (λ)",axis='x', speed=1540, frequency=5e6)
        phased_array.units=[1e3,1e6]
        self.simulator.add_phased_array(phased_array)
        self.array_selection_combobox.addItem(array_name)
        self.update_controls_for_selected_array()
        self.update_plots()

    def update_controls_for_selected_array(self):
        for i in reversed(range(self.array_controls_layout.count())):
            widget = self.array_controls_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        selected_index = self.array_selection_combobox.currentIndex()
        if selected_index == -1:
            return
        selected_array = self.simulator.phased_arrays[selected_index]
        self.populate_controls_for_array(selected_array)

    def populate_controls_for_array(self, phased_array):
        elements_label = QLabel("Number of Elements:")
        elements_spinbox = QSpinBox()
        elements_spinbox.setRange(2, 100)
        elements_spinbox.setValue(phased_array.num_elements)
        elements_spinbox.valueChanged.connect(
            lambda value, pa=phased_array: self.update_attribute(pa, 'num_elements', value))
        self.array_controls_layout.addWidget(elements_label)
        self.array_controls_layout.addWidget(elements_spinbox)

        geometry_label = QLabel("Geometry:")
        geometry_combobox = QComboBox()
        geometry_combobox.addItems(["Linear", "Curved"])
        geometry_combobox.setCurrentText(phased_array.geometry.capitalize())
        geometry_combobox.currentTextChanged.connect(
            lambda value, pa=phased_array: self.update_attribute(pa, 'geometry', value.lower()))
        self.array_controls_layout.addWidget(geometry_label)
        self.array_controls_layout.addWidget(geometry_combobox)

        if phased_array.geometry.capitalize() == "Linear":

            spacing_unit_label = QLabel("Spacing Units:")
            spacing_unit_combobox = QComboBox()
            spacing_unit_combobox.addItems(["Meters", "Wavelength (λ)"])
            spacing_unit_combobox.setCurrentText(phased_array.spacing_unit)
            spacing_unit_combobox.currentTextChanged.connect(
                lambda value, pa=phased_array: self.update_spacing_units(pa, value))
            self.array_controls_layout.addWidget(spacing_unit_label)
            self.array_controls_layout.addWidget(spacing_unit_combobox)


            if phased_array.spacing_unit == "Meters":
                spacing_label = QLabel(f"Spacing in (m): {phased_array.spacing_value/100}")
            else:
                spacing_label = QLabel(f"Spacing in (λ): {phased_array.spacing_value/100}")
            spacing_slider = QSlider(Qt.Horizontal)
            spacing_slider.setRange(1, 100)
            spacing_slider.setValue(int(phased_array.spacing_value))
            spacing_slider.valueChanged.connect(
                lambda value, pa=phased_array, lbl=spacing_label: self.update_spacing_slider(pa, value, lbl, spacing_unit_combobox.currentText()))
            self.array_controls_layout.addWidget(spacing_label)
            self.array_controls_layout.addWidget(spacing_slider)

        else:
            radius_label = QLabel(f"Radius (m): {phased_array.radius:.2f}")
            radius_slider = QSlider(Qt.Horizontal)
            radius_slider.setRange(1, 100)
            radius_slider.setValue(int(phased_array.radius * 100))
            radius_slider.valueChanged.connect(
                lambda value, pa=phased_array, lbl=radius_label: self.update_slider(pa, 'radius', value / 100, lbl, "Radius (m):"))
            self.array_controls_layout.addWidget(radius_label)
            self.array_controls_layout.addWidget(radius_slider)



        speed_label = QLabel("Speed (m/s):")
        self.speed_input = QLineEdit()
        self.setup_scientific_input(phased_array,self.speed_input, "speed", 1, 3e8, default=phased_array.speed)
        self.array_controls_layout.addWidget(speed_label)
        self.array_controls_layout.addWidget(self.speed_input)


        frequency_label = QLabel("Frequency (Hz):")
        self.frequency_input = QLineEdit()
        self.setup_scientific_input(phased_array,self.frequency_input, "frequency", 1e3, 1e12, default=phased_array.frequency)
        self.array_controls_layout.addWidget(frequency_label)
        self.array_controls_layout.addWidget(self.frequency_input)

        steering_label = QLabel(f"Steering Angle (°): {np.rad2deg(phased_array.steering_angle):.1f}")
        steering_slider = QSlider(Qt.Horizontal)
        steering_slider.setRange(-90, 90)
        steering_slider.setValue(int(np.rad2deg(phased_array.steering_angle)))
        steering_slider.valueChanged.connect(
            lambda value, pa=phased_array, lbl=steering_label: self.update_slider(pa, 'steering_angle', np.deg2rad(value), lbl, "Steering Angle (°):"))
        self.array_controls_layout.addWidget(steering_label)
        self.array_controls_layout.addWidget(steering_slider)


        # axis_label = QLabel("Axis (for Linear Arrays):")
        # axis_combobox = QComboBox()
        # axis_combobox.addItems(["x", "y"])
        # axis_combobox.setCurrentText(phased_array.axis)
        # axis_combobox.currentTextChanged.connect(
        #     lambda value, pa=phased_array: self.update_attribute(pa, 'axis', value))
        # self.array_controls_layout.addWidget(axis_label)
        # self.array_controls_layout.addWidget(axis_combobox)


        position_x_label = QLabel("Position X (m):")
        position_x_spinbox = QSpinBox()
        position_x_spinbox.setRange(-10, 10)
        position_x_spinbox.setValue(phased_array.position_x)
        position_x_spinbox.valueChanged.connect(
            lambda value, pa=phased_array: self.update_attribute(pa, 'position_x', value))
        self.array_controls_layout.addWidget(position_x_label)
        self.array_controls_layout.addWidget(position_x_spinbox)

        position_y_label = QLabel("Position Y (m):")
        position_y_spinbox = QSpinBox()
        position_y_spinbox.setRange(-10, 10)
        position_y_spinbox.setValue(phased_array.position_y)
        position_y_spinbox.valueChanged.connect(
            lambda value, pa=phased_array: self.update_attribute(pa, 'position_y', value))
        self.array_controls_layout.addWidget(position_y_label)
        self.array_controls_layout.addWidget(position_y_spinbox)

        # semicircle_checkbox = QCheckBox("Semi-Circle Mode")
        # semicircle_checkbox.setChecked(phased_array.semicircle)
        # semicircle_checkbox.stateChanged.connect(
        #     lambda state, pa=phased_array: self.update_attribute(pa, 'semicircle', state == Qt.Checked))
        # self.array_controls_layout.addWidget(semicircle_checkbox)

        enabled_checkbox = QCheckBox("Enable Array")
        enabled_checkbox.setChecked(phased_array.enabled)
        enabled_checkbox.stateChanged.connect(
            lambda state, pa=phased_array: self.toggle_array_effect(pa, state == Qt.Checked))
        self.array_controls_layout.addWidget(enabled_checkbox)


    def toggle_array_effect(self, phased_array, enabled):
        phased_array.enabled = enabled
        self.update_plots()

    def update_attribute(self, phased_array, attribute, value):
        setattr(phased_array, attribute, value)
        if attribute == 'geometry':
            self.update_controls_for_selected_array()
        self.update_plots()

    def update_slider(self, phased_array, attribute, value, label, label_text):
        setattr(phased_array, attribute, value)
        if attribute == 'steering_angle':
            label.setText(f"{label_text} {np.degrees(float(value)):.2f}")
        else:
            label.setText(f"{label_text} {value:.2f}")
        self.update_plots()
    def setup_scientific_input(self, phased_array,widget, attribute, min_value, max_value, default):

        regex = QRegularExpression(r"^[+-]?\d*\.?\d+e[+-]?\d+$")
        validator = QRegularExpressionValidator(regex)
        widget.setValidator(validator)


        widget.setText(f"{default:.1e}")


        widget.editingFinished.connect(lambda attr=attribute, w=widget: self.save_scientific_input(phased_array,w, attr, min_value, max_value))


    def save_scientific_input(self,phased_array, widget, attribute, min_value, max_value):
        text = widget.text()
        try:

            value = float(text)
            exponent = int(text.split("e+")[-1])
            print(exponent)
            if attribute == 'speed':
                phased_array.units[0] = 10 **( exponent)
            elif attribute == 'frequency':
                phased_array.units[1] = 10 ** (exponent)

            # Check if value is within range
            if not (min_value <= value <= max_value):
                raise ValueError(f"Value out of range ({min_value:.1e} - {max_value:.1e})")

            # Save the value back to the phased_array attribute
            setattr(phased_array, attribute, value)
            print(f"Updated {attribute} to {value:.1e}")
            # def update_spacing_units(self, phased_array, unit):
            if phased_array.geometry== 'linear':
                self.update_spacing_units(phased_array,phased_array.spacing_unit)
            self.update_plots()

        except ValueError as e:
            # Show error message if validation fails
            QMessageBox.warning(self, "Invalid Input", str(e))
            # Reset to the last valid value
            widget.setText(f"{getattr(phased_array, attribute):.1e}")



    def update_spacing_units(self, phased_array, unit):

        phased_array.spacing_unit = unit

        for i in range(self.array_controls_layout.count()):
            widget = self.array_controls_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and "Spacing in" in widget.text():
                spacing_label = widget
                break
        else:
            raise ValueError("Spacing label not found in layout.")


        self.update_spacing_slider(phased_array, phased_array.spacing_value, spacing_label, unit)


    def update_spacing_slider(self, phased_array, value, label, unit):

        wavelength=float(phased_array.speed)/float(phased_array.frequency)
        phased_array.spacing_value = value

        if unit == "Meters":
            label.setText(f"Spacing in (m): {phased_array.spacing_value/100:.2f}")
            phased_array.spacing = value / 100
        elif unit == "Wavelength (λ)":
            phased_array.spacing=(value / 100 )* wavelength
            label.setText(f"Spacing in (λ): {phased_array.spacing_value/100:.2f}")


        self.update_plots()


    def toggle_full_circle_mode(self, state):
        self.full_circle_mode = state == Qt.Checked
        self.update_plots()

    def update_plots(self):
        theta = np.linspace(-np.pi, np.pi, 1000) if self.full_circle_mode else np.linspace(0, np.pi , 1000)
        array_factor = [self.simulator.simulate(t) for t in theta]
        array_factor_db = 20 * np.log10(np.maximum(array_factor, 1e-12))

        self.figure.clear()
        if self.plot_mode_combobox.currentText() == "Polar":
            ax = self.figure.add_subplot(111, polar=True)
            ax.plot(theta, array_factor_db)
            ax.set_title("Beam Pattern (Polar)")
        else:
            ax = self.figure.add_subplot(111)
            ax.plot(np.degrees(theta), array_factor_db)
            ax.set_xlabel("Angle (°)")
            ax.set_ylabel("Directivity (dB)")
            ax.set_title("Beam Pattern (Rectangular)")
            ax.grid(True)
            self.figure.subplots_adjust(bottom=0.2)
        ax.legend()

        self.canvas.draw()

        # Update geometry visualization (array layout)
        self.update_geometry_plot()


        # Update the wave plot with new parameters
        self.setup_wave_plot()



    def update_geometry_plot(self):
        self.figure_geometry.clear()
        ax_geometry = self.figure_geometry.add_subplot(111)
        colors = plt.cm.get_cmap('tab10', len(self.simulator.phased_arrays))
        for i, phased_array in enumerate(self.simulator.phased_arrays):
            if phased_array.geometry == 'linear':
                positions = np.arange(phased_array.num_elements) * phased_array.spacing + phased_array.position_x
                if phased_array.axis == 'x':
                    ax_geometry.scatter(positions, [phased_array.position_y] * len(positions), label=phased_array.name, color=colors(i))
                elif phased_array.axis == 'y':
                    ax_geometry.scatter([phased_array.position_x] * len(positions), positions, label=phased_array.name, color=colors(i))
            elif phased_array.geometry == 'curved':
                angles = np.linspace(0, -np.pi, phased_array.num_elements) if phased_array.semicircle else np.linspace(0, 2 * np.pi, phased_array.num_elements)
                x_positions = phased_array.radius * np.cos(angles)+phased_array.position_x
                y_positions = phased_array.radius * np.sin(angles)+phased_array.position_y
                ax_geometry.scatter(x_positions, y_positions, label=phased_array.name, color=colors(i))
            self.setup_wave_emitters(phased_array)

        ax_geometry.set_xlabel("Position (m)")
        ax_geometry.set_ylabel("Array Index")
        ax_geometry.set_title("Array Geometry")
        ax_geometry.grid(True)
        ax_geometry.legend()
        self.canvas_geometry.draw()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = BeamformingGUI()
    gui.show()
    # sys.exit(app.exec_())
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
    finally:
        logger.info("Beamforming Simulator exited.")
