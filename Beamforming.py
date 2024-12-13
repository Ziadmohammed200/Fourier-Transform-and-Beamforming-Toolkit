import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QSlider, QSpinBox, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt

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
    def __init__(self, name, num_elements=4, spacing=0.5, axis='x', speed=3e8, frequency=1e9, geometry='linear', radius=1.0, steering_angle=0, semicircle=False):
        self.name = name
        self.num_elements = num_elements
        self.spacing = spacing
        self.axis = axis
        self.speed = speed
        self.frequency = frequency
        self.geometry = geometry
        self.radius = radius
        self.steering_angle = np.deg2rad(steering_angle)
        self.semicircle = semicircle  # New attribute for semicircular arrays
        self.position_x = 0  # Added for compatibility
        self.position_y = 0  # Added for compatibility
        self.enabled = True  # New attribute

    def compute_array_factor(self, theta):
        """Compute the array factor based on the array configuration."""
        wavelength = self.speed / self.frequency
        k = 2 * np.pi / wavelength  # Wave number

        if self.geometry == 'linear':
            if self.axis == 'x':
                positions = np.arange(self.num_elements) * self.spacing + self.position_x
            elif self.axis == 'y':
                positions = np.zeros(self.num_elements)  # For now, assume all elements along x=0
            else:
                raise ValueError("Unsupported axis. Use 'x' or 'y'.")
            phase_shifts = k * positions * np.cos(theta - self.steering_angle)

        elif self.geometry == 'curved':
            angles = np.linspace(0, np.pi, self.num_elements) if self.semicircle else np.linspace(0, 2 * np.pi, self.num_elements)
            positions = self.radius * np.sin(angles) + self.position_x
            phase_shifts = k * positions * np.cos(theta - self.steering_angle)

        else:
            raise ValueError("Unsupported geometry. Use 'linear' or 'curved'.")

        array_factor = np.sum(np.exp(1j * phase_shifts))
        return np.abs(array_factor)


class BeamformingSimulator:
    def __init__(self):
        self.phased_arrays = []

    def add_phased_array(self, phased_array):
        self.phased_arrays.append(phased_array)

    def simulate(self, theta):
        """Combine array factors from all enabled phased arrays."""
        total_output = 0
        for phased_array in self.phased_arrays:
            if phased_array.enabled:
                total_output += phased_array.compute_array_factor(theta)
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
        start_wave_button = QPushButton("Start Wave Emission")
        start_wave_button.clicked.connect(self.start_wave_animation)
        stop_wave_button = QPushButton("Stop Wave Emission")
        stop_wave_button.clicked.connect(self.stop_wave_animation)

        wave_control_layout.addWidget(start_wave_button)
        wave_control_layout.addWidget(stop_wave_button)
        self.control_panel.addLayout(wave_control_layout)

        # Add phased array button
        add_array_button = QPushButton("Add Phased Array")
        add_array_button.clicked.connect(self.add_phased_array)
        self.control_panel.addWidget(add_array_button)

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

        # Wave Emission Plot
        self.figure_wave = plt.figure(figsize=(8, 8))
        self.canvas_wave = FigureCanvas(self.figure_wave)
        plot_layout.addWidget(self.canvas_wave)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        plot_layout.addWidget(self.canvas)

        # Array Geometry Plot
        self.figure_geometry = plt.figure()
        self.canvas_geometry = FigureCanvas(self.figure_geometry)
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
            print(phased_array.speed, phased_array.frequency / int(10 ^ 6))
            c, f = phased_array.speed/int(1e8), phased_array.frequency / int(1e8) *0.2
            print(c, f)
            lambda0 = c / f
            N = phased_array.num_elements

            xs = np.linspace(-lambda0, lambda0, N)
            ys = np.zeros_like(xs)
            for i in range(N):
                e = Emitter(xs[i], ys[i], c, f, 0)
                phase = CalculatePhaseFromFocus(0, 20, e)
                e.SetPhase(phase)
                self.emitter_array.AddEmitter(e)

            self.emitter_array.RemoveOffset()

    def setup_wave_plot(self):
        """Setup the dynamic wave interference plot as a heat map"""
        self.figure_wave.clear()  # Clear previous plot
        ax = self.figure_wave.add_subplot(111)
        ax.set_xlim([-50, 50])
        ax.set_ylim([-50, 50])
        ax.set_aspect(1)
        ax.grid(alpha=0.2)
        ax.set_title("Wave Interference Heat Map")

        # Create a 2D grid for interference calculation
        x = np.linspace(-50, 50, 200)
        y = np.linspace(-50, 50, 200)
        X, Y = np.meshgrid(x, y)

        # Calculate interference at each point from different phased arrays
        interference = np.zeros_like(X, dtype=float)
        for phased_array in self.simulator.phased_arrays:
            if not phased_array.enabled:
                continue

            wavelength = phased_array.speed / phased_array.frequency

            # Calculate element positions based on array geometry
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
                else:  # y-axis
                    element_positions = np.array([
                        [phased_array.position_x, y_pos]
                        for y_pos in np.linspace(
                            phased_array.position_y - (phased_array.num_elements - 1) * phased_array.spacing / 2,
                            phased_array.position_y + (phased_array.num_elements - 1) * phased_array.spacing / 2,
                            phased_array.num_elements
                        )
                    ])
            elif phased_array.geometry == 'curved':
                # For curved arrays, calculate positions on arc/semicircle
                angles = np.linspace(0, np.pi, phased_array.num_elements) if phased_array.semicircle else np.linspace(0,
                                                                                                                      2 * np.pi,
                                                                                                                      phased_array.num_elements)
                element_positions = np.array([
                    [phased_array.position_x + phased_array.radius * np.cos(angle),
                     phased_array.position_y + phased_array.radius * np.sin(angle)]
                    for angle in angles
                ])

            # Calculate wave interference from each element
            for element_pos in element_positions:
                # Calculate phase and distance with steering angle
                distance = np.sqrt((X - element_pos[0]) ** 2 + (Y - element_pos[1]) ** 2)
                phase = distance * (2 * np.pi / wavelength) + phased_array.steering_angle
                interference += np.cos(phase)

        # Normalize interference
        range_value = interference.max() - interference.min()
        if range_value > 0:
            interference = (interference - interference.min()) / range_value

        # Create heat map
        self.im = ax.imshow(interference, extent=[-50, 50, -50, 50],
                            origin='lower', cmap='coolwarm', alpha=0.7)
        plt.colorbar(self.im, ax=ax, label='Interference Intensity')

        # Add array element points
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
                angles = np.linspace(0, np.pi, phased_array.num_elements) if phased_array.semicircle else np.linspace(0,
                                                                                                                      2 * np.pi,
                                                                                                                      phased_array.num_elements)
                element_x = phased_array.position_x + phased_array.radius * np.cos(angles)
                element_y = phased_array.position_y + phased_array.radius * np.sin(angles)

            ax.scatter(element_x, element_y, color='black', marker='^', s=30)

        self.canvas_wave.draw()




 # Remove start_wave_animation and stop_wave_animation methods
    def start_wave_animation(self):
        """Start the wave emission animation with a heat map of interference."""

        def init():
            ax = self.figure_wave.add_subplot(111)
            ax.set_xlim([-50, 50])
            ax.set_ylim([-50, 50])
            ax.set_aspect(1)
            ax.grid(alpha=0.2)
            ax.set_title("Wave Interference Heat Map")

            # Initialize an empty heat map
            x = np.linspace(-50, 50, 200)
            y = np.linspace(-50, 50, 200)
            self.X, self.Y = np.meshgrid(x, y)
            self.interference = np.zeros_like(self.X, dtype=float)

            # Create the image for the heat map
            self.im = ax.imshow(
                self.interference,
                extent=[-50, 50, -50, 50],
                origin='lower',
                cmap='coolwarm',
                alpha=0.7
            )
            plt.colorbar(self.im, ax=ax, label='Interference Intensity')

            return [self.im]

        def update(frame_number):
            # Create a new interference calculation for each frame
            self.interference = np.zeros_like(self.X, dtype=float)

            # Loop through active phased arrays
            for phased_array in self.simulator.phased_arrays:
                if not phased_array.enabled:
                    continue

                wavelength = phased_array.speed / phased_array.frequency

                # Dynamically adjust phase based on time
                dynamic_steering = phased_array.steering_angle + np.sin(frame_number * 0.1) * np.pi / 4

                # Calculate element positions
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
                    angles = np.linspace(0, np.pi,
                                         phased_array.num_elements) if phased_array.semicircle else np.linspace(0,
                                                                                                                2 * np.pi,
                                                                                                                phased_array.num_elements)
                    element_positions = np.array([
                        [phased_array.position_x + phased_array.radius * np.cos(angle),
                         phased_array.position_y + phased_array.radius * np.sin(angle)]
                        for angle in angles
                    ])

                # Calculate wave interference from each element
                for element_pos in element_positions:
                    # Calculate phase and distance with dynamic steering
                    distance = np.sqrt((self.X - element_pos[0]) ** 2 + (self.Y - element_pos[1]) ** 2)
                    phase = distance * (2 * np.pi / wavelength) + dynamic_steering
                    self.interference += np.cos(phase)

            # Normalize interference
            range_value = self.interference.max() - self.interference.min()
            if range_value > 0:
                self.interference = (self.interference - self.interference.min()) / range_value

            # Update the heat map
            self.im.set_array(self.interference)
            return [self.im]

        # Check if animation is already running
        if self.animation is None:
            self.figure_wave.clear()  # Clear any previous plots
            self.animation = FuncAnimation(self.figure_wave, update, init_func=init, interval=50, blit=True, frames=200)
        self.canvas_wave.draw()

    def stop_wave_animation(self):
        """Stop the wave emission animation"""
        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
            # Reset the plot
            self.figure_wave.clear()
            self.setup_wave_plot()
            self.canvas_wave.draw()

    def add_default_array(self):
        default_array = PhasedArray(name="Default Array")
        self.simulator.add_phased_array(default_array)
        self.array_selection_combobox.addItem(default_array.name)
        self.update_controls_for_selected_array()

    def add_phased_array(self):
        array_name = f"Array {len(self.simulator.phased_arrays) + 1}"
        phased_array = PhasedArray(name=array_name)
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

        # Spacing unit selector
        spacing_unit_label = QLabel("Spacing Units:")
        spacing_unit_combobox = QComboBox()
        spacing_unit_combobox.addItems(["Meters", "Wavelength (λ)"])
        spacing_unit_combobox.currentTextChanged.connect(
            lambda value, pa=phased_array: self.update_spacing_units(pa, value))
        self.array_controls_layout.addWidget(spacing_unit_label)
        self.array_controls_layout.addWidget(spacing_unit_combobox)

        # Spacing slider
        spacing_label = QLabel(f"Spacing (m): {phased_array.spacing}")
        spacing_slider = QSlider(Qt.Horizontal)
        spacing_slider.setRange(1, 100)
        spacing_slider.setValue(int(phased_array.spacing * 100))
        spacing_slider.valueChanged.connect(
            lambda value, pa=phased_array, lbl=spacing_label: self.update_spacing_slider(pa, value, lbl, spacing_unit_combobox.currentText()))
        self.array_controls_layout.addWidget(spacing_label)
        self.array_controls_layout.addWidget(spacing_slider)
        # Add control for speed
        speed_label = QLabel(f"Speed (m/s): {phased_array.speed:.1e}")
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setRange(1, 100)
        speed_slider.setValue(int(phased_array.speed / 3e6))
        speed_slider.valueChanged.connect(
            lambda value, pa=phased_array, lbl=speed_label: self.update_slider(pa, 'speed', value * 3e6, lbl, "Speed (m/s):"))
        self.array_controls_layout.addWidget(speed_label)
        self.array_controls_layout.addWidget(speed_slider)

        frequency_label = QLabel(f"Frequency (GHz): {phased_array.frequency / 1e9:.2f}")
        frequency_slider = QSlider(Qt.Horizontal)
        frequency_slider.setRange(1, 100)
        frequency_slider.setValue(int(phased_array.frequency / 1e9))
        frequency_slider.valueChanged.connect(
            lambda value, pa=phased_array, lbl=frequency_label: self.update_slider(pa, 'frequency', value * 1e9, lbl, "Frequency (GHz):"))
        self.array_controls_layout.addWidget(frequency_label)
        self.array_controls_layout.addWidget(frequency_slider)

        steering_label = QLabel(f"Steering Angle (°): {np.rad2deg(phased_array.steering_angle):.1f}")
        steering_slider = QSlider(Qt.Horizontal)
        steering_slider.setRange(-90, 90)
        steering_slider.setValue(int(np.rad2deg(phased_array.steering_angle)))
        steering_slider.valueChanged.connect(
            lambda value, pa=phased_array, lbl=steering_label: self.update_slider(pa, 'steering_angle', np.deg2rad(value), lbl, "Steering Angle (°):"))
        self.array_controls_layout.addWidget(steering_label)
        self.array_controls_layout.addWidget(steering_slider)

        radius_label = QLabel(f"Radius (m): {phased_array.radius:.2f}")
        radius_slider = QSlider(Qt.Horizontal)
        radius_slider.setRange(1, 100)
        radius_slider.setValue(int(phased_array.radius * 10))
        radius_slider.valueChanged.connect(
            lambda value, pa=phased_array, lbl=radius_label: self.update_slider(pa, 'radius', value / 10, lbl, "Radius (m):"))
        self.array_controls_layout.addWidget(radius_label)
        self.array_controls_layout.addWidget(radius_slider)

        geometry_label = QLabel("Geometry:")
        geometry_combobox = QComboBox()
        geometry_combobox.addItems(["Linear", "Curved"])
        geometry_combobox.setCurrentText(phased_array.geometry.capitalize())
        geometry_combobox.currentTextChanged.connect(
            lambda value, pa=phased_array: self.update_attribute(pa, 'geometry', value.lower()))
        self.array_controls_layout.addWidget(geometry_label)
        self.array_controls_layout.addWidget(geometry_combobox)

        axis_label = QLabel("Axis (for Linear Arrays):")
        axis_combobox = QComboBox()
        axis_combobox.addItems(["x", "y"])
        axis_combobox.setCurrentText(phased_array.axis)
        axis_combobox.currentTextChanged.connect(
            lambda value, pa=phased_array: self.update_attribute(pa, 'axis', value))
        self.array_controls_layout.addWidget(axis_label)
        self.array_controls_layout.addWidget(axis_combobox)

        # Position in X and Y
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

        semicircle_checkbox = QCheckBox("Semi-Circle Mode")
        semicircle_checkbox.setChecked(phased_array.semicircle)
        semicircle_checkbox.stateChanged.connect(
            lambda state, pa=phased_array: self.update_attribute(pa, 'semicircle', state == Qt.Checked))
        self.array_controls_layout.addWidget(semicircle_checkbox)

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
        self.update_plots()

    def update_slider(self, phased_array, attribute, value, label, label_text):
        setattr(phased_array, attribute, value)
        if attribute == 'steering_angle':
            label.setText(f"{label_text} {np.degrees(float(value)):.2f}")
        else:
            label.setText(f"{label_text} {value:.2f}")
        self.update_plots()
    def update_spacing_units(self, phased_array, unit):
        """Update spacing unit between meters and wavelength (λ)."""
        wavelength = phased_array.speed / phased_array.frequency
        if unit == "Wavelength (λ)":
            phased_array.spacing = phased_array.spacing / wavelength  # Convert meters to λ
        elif unit == "Meters":
            phased_array.spacing = phased_array.spacing * wavelength  # Convert λ to meters
        self.update_plots()

    def update_spacing_slider(self, phased_array, value, label, unit):
        """Update spacing value dynamically based on the selected unit."""
        wavelength = phased_array.speed / phased_array.frequency
        if unit == "Meters":
            phased_array.spacing = value / 100
            label.setText(f"Spacing (m): {phased_array.spacing:.2f}")
        elif unit == "Wavelength (λ)":
            phased_array.spacing = (value / 100) * wavelength
            label.setText(f"Spacing (λ): {phased_array.spacing / wavelength:.2f}")
        self.update_plots()


    def toggle_full_circle_mode(self, state):
        self.full_circle_mode = state == Qt.Checked
        self.update_plots()

    def update_plots(self):
        theta = np.linspace(-np.pi, np.pi, 1000) if self.full_circle_mode else np.linspace(-np.pi / 2, np.pi / 2, 1000)
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
        self.canvas.draw()

        # Update the wave plot with new parameters
        self.setup_wave_plot()

        self.figure_geometry.clear()
        ax_geometry = self.figure_geometry.add_subplot(111)
        colors = plt.cm.get_cmap('tab10', len(self.simulator.phased_arrays))
        for i, phased_array in enumerate(self.simulator.phased_arrays):
            if phased_array.geometry == 'linear':
                positions = np.arange(phased_array.num_elements) * phased_array.spacing + phased_array.position_x
                if phased_array.axis == 'x':
                    ax_geometry.scatter(positions, [i] * len(positions), label=phased_array.name, color=colors(i))
                elif phased_array.axis == 'y':
                    ax_geometry.scatter([i] * len(positions), positions, label=phased_array.name, color=colors(i))
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
    sys.exit(app.exec_())
