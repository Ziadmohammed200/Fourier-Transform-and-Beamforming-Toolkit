from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QPalette, QWheelEvent
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QComboBox, QWidget, QGridLayout, \
    QProgressBar, QMessageBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QComboBox, QSlider, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QFileDialog, QComboBox, QGridLayout, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
import sys
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QComboBox, QSlider, QWidget, QHBoxLayout
from PyQt5 import QtCore
import numpy as np
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PIL import Image, ImageQt
from PyQt5.QtCore import Qt, QRect, QObject, pyqtSignal, QPoint, QCoreApplication
from PyQt5.QtCore import QSize  # If you're using PyQt5
from ImageLabel import ImageLabel
from ImageLabel import SelectionManager
from ImageLabel import ScrollableLabel


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Mixer")
        self.setGeometry(100, 100, 1200, 700)
        self.dark_theme()
        self.image_labels = []
        self.image_list = {}
        self.image_id = 0
        self.freq_component_combobox = []
        self.freq_component_label = []
        self.image_phases = []
        self.image_magnitudes = []
        self.image_real_part = []
        self.image_imaginary_part = []
        self.weighted_magnitude = [np.zeros((1, 1))] * 4
        self.weighted_phase = [np.zeros((1, 1))] * 4
        self.selected_port_indx = 0
        self.start = 1
        self.output_label = []
        self.sliders = []
        self.mixer_region = []
        self.f_shift = []
        self.selected_port = 'Port 1'
        self.selected_mixer_region = "Inner"
        self.output_combo = []
        self.combo = []
        self.selected_magnitude = []
        self.selected_phase = []
        self.selected_real = []
        self.selected_imaginary = []
        self.combined_magnitude = None
        self.combined_phase = None
        self.start_point = None
        self.end_point = None
        self.selection_rect = None
        self.retangle = None
        self.selection_manager = SelectionManager()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFormat("Loading: %p%")  # %p% shows the percentage
        # self.progress_bar.setRange(0, 0)
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.selection_manager.selection_changed.connect(self.update_magnitude_and_phase_list)

        # section 1: input images
        section1_layout = QGridLayout()
        for i in range(4):
            # making 4 image lables
            original_image_label = QLabel(f"Original Image {i + 1}")
            image_label = QLabel(f"Add Image {i + 1}")
            image_label.setFixedSize(400, 250)  # 400 is the width, 250 is th eheight
            image_label.setStyleSheet("border: 1px solid #444; background-color: #333; color: white;")
            image_label.setAlignment(QtCore.Qt.AlignCenter)

            image_label.mouseDoubleClickEvent = lambda event, idx=i: self.load_image(idx)
            image_label.setScaledContents(True)

            # Add label to the list
            self.image_labels.append(image_label)

            # Create a combo box
            combo_box = QComboBox()
            combo_box.addItems(
                ["Choose FT Component", 'FT Magnitude', 'FT Phase', "FT Real Components", "FT Imaginary Components"])
            combo_box.setStyleSheet("""
                QComboBox {
                    background-color: #8B0047; 
                    color: #FFFFFF; /* White text for readability */
                    border: 1px solid #555; /* Subtle border for structure */
                    border-radius: 5px; /* Smooth rounded corners */
                    padding: 5px; /* Padding for spacing */
                }
                QComboBox:hover {
                    border: 1px solid #00BFFF; /* Highlight border on hover */
                }

                QComboBox QAbstractItemView {
                    background-color: #2E2E2E; /* Dropdown list background */
                    color: #FFFFFF; /* List item text color */
                    selection-background-color: #00BFFF; /* Highlight selected item */
                    selection-color: #FFFFFF; /* Selected text color */
                    border: 1px solid #555; /* Border for the dropdown */
                }
            """)
            self.freq_component_combobox.append(combo_box)
            combo_box.currentIndexChanged.connect(
                lambda index, combo=combo_box, idx=i: self.show_freq_components(idx, combo.currentText())
            )

            section1_layout.addWidget(original_image_label, 0, i)
            section1_layout.addWidget(image_label, 1, i)
            section1_layout.addWidget(combo_box, 2, i)

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #282828; /* Dark background */
                border: 2px solid #444; /* Border color */
                border-radius: 10px; /* Rounded corners */
                text-align: center; /* Centered text */
                color: white; /* Text color */
                font-size: 12px; /* Font size */
            }
            QProgressBar::chunk {
                background-color: #8B0047; /* Chunk (filled part) color */
                border-radius: 8px; /* Smooth rounded edges for the progress chunk */
                margin: 1px; /* Add spacing between chunks */
            }
        """)
        # Section 2
        section2_layout = QGridLayout()
        for i in range(4):
            ft_label = ImageLabel(self.selection_manager)
            ft_label.setFixedSize(400, 250)
            ft_label.setStyleSheet("border: 1px solid #444; background-color: #333; color: white;")
            ft_label.setAlignment(QtCore.Qt.AlignCenter)
            section2_layout.addWidget(ft_label, 0, i)
            self.freq_component_label.append(ft_label)
            ft_label.setScaledContents(True)

        # section 3: output images
        section3_layout = QHBoxLayout()
        for i in range(2):
            output_label = ScrollableLabel(f"Output {i + 1}")
            output_label.setFixedSize(800, 400)
            output_label.setStyleSheet("border: 1px solid #444; background-color: #333; color: white;")
            output_label.setAlignment(QtCore.Qt.AlignCenter)
            self.output_label.append(output_label)
            section3_layout.addWidget(output_label)
        self.output_label[0].scrollDirectionChanged.connect(self.handle_scroll_direction)
        self.output_label[1].scrollDirectionChanged.connect(self.handle_scroll_direction)

        left_layout.addLayout(section1_layout)
        left_layout.addLayout(section2_layout)
        left_layout.addLayout(section3_layout)

        right_layout = QVBoxLayout()

        def create_widget(label_text, combo_items, counter):
            # the container for the group
            container = QWidget()
            container_layout = QVBoxLayout()

            # label
            label = QLabel(label_text)
            label.setStyleSheet("color: white; font-size: 14px;")
            container_layout.addWidget(label)

            # slider
            slider = QSlider(QtCore.Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(0)
            slider_value_label = QLabel("0%")
            slider_value_label.setStyleSheet("color: #ffcce6; font-size: 12px; font-weight: bold;")
            slider.valueChanged.connect(lambda value, lbl=slider_value_label: lbl.setText(f"{value}%"))
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #F8F8F8; /* Light gray groove */
                    border-radius: 3px; /* Smooth rounded edges */
                }
                QSlider::handle:horizontal {
                    background: #8B0047; /* Deep red for the handle */
                    border: none;
                    width: 20px;
                    height: 20px;
                    margin: -7px 0; /* Centers the handle */
                    border-radius: 10px; /* Circular handle */
                }
                QSlider::handle:horizontal:hover {
                    background: rgba(139, 0, 71, 0.8); /* Transparent red for hover effect */
                    box-shadow: 0px 0px 10px rgba(139, 0, 71, 0.5); /* Glow effect */
                }
                QSlider::sub-page:horizontal {
                    background: #8B0047; /* Deep red for the progress bar */
                    border-radius: 3px;
                }
                QSlider::add-page:horizontal {
                    background: #D3D3D3; /* Light gray for the unfilled portion */
                    border-radius: 3px;
                }
            """)

            self.sliders.append(slider)
            container_layout.addWidget(slider)
            container_layout.addWidget(slider_value_label)

            # combobox
            combobox = QComboBox()
            combobox.addItems(combo_items)
            combobox.setStyleSheet("""
                QComboBox {
                    background-color: #8B0047; 
                    color: #FFFFFF; /* White text for readability */
                    border: 1px solid #555; /* Subtle border for structure */
                    border-radius: 5px; /* Smooth rounded corners */
                    padding: 5px; /* Padding for spacing */
                }
                QComboBox:hover {
                    border: 1px solid #00BFFF; /* Highlight border on hover */
                }
            """)
            self.output_combo.append(combobox)

            container_layout.addWidget(combobox)

            # set layout for the container
            container.setLayout(container_layout)
            return container

        # mixer O/p Section
        mixer_output_combobox = QComboBox()
        mixer_output_combobox.addItems(["Port 1", "Port 2"])
        mixer_output_combobox.currentIndexChanged.connect(
            lambda index, combo=mixer_output_combobox: self.select_port(index, combo.currentText())
        )
        mixer_output_combobox.setStyleSheet("""
                QComboBox {
                    background-color: #8B0047; 
                    color: #FFFFFF; /* White text for readability */
                    border: 1px solid #555; /* Subtle border for structure */
                    border-radius: 5px; /* Smooth rounded corners */
                    padding: 5px; /* Padding for spacing */
                }
                QComboBox:hover {
                    border: 1px solid #00BFFF; /* Highlight border on hover */
                }
            """)

        # create frame for the Mixer Output group
        mixer_output_label = QLabel("Mixer Output")
        mixer_output_label.setStyleSheet("color: white; font-size: 14px;")
        mixer_output_layout = QVBoxLayout()
        mixer_output_layout.addWidget(mixer_output_label)
        mixer_output_layout.addWidget(mixer_output_combobox)
        mixer_output_frame = QWidget()
        mixer_output_frame.setLayout(mixer_output_layout)

        right_layout.addWidget(mixer_output_frame)

        # mixer Region Section
        mixer_region_combobox = QComboBox()
        mixer_region_combobox.addItems(["Inner", "Outer"])
        mixer_region_combobox.currentIndexChanged.connect(
            lambda index, combo=mixer_region_combobox: self.select_mixer_region(index, combo.currentText())
        )
        mixer_region_combobox.setStyleSheet("""
                QComboBox {
                    background-color: #8B0047; 
                    color: #FFFFFF; /* White text for readability */
                    border: 1px solid #555; /* Subtle border for structure */
                    border-radius: 5px; /* Smooth rounded corners */
                    padding: 5px; /* Padding for spacing */
                }
                QComboBox:hover {
                    border: 1px solid #00BFFF; /* Highlight border on hover */
                }
            """)
        self.mixer_region.append(mixer_region_combobox)
        # create frame for the Mixer Region group
        mixer_region_label = QLabel("Mixer Region")
        mixer_region_label.setStyleSheet("color: white; font-size: 14px;")
        mixer_region_layout = QVBoxLayout()
        mixer_region_layout.addWidget(mixer_region_label)
        mixer_region_layout.addWidget(mixer_region_combobox)
        mixer_region_frame = QWidget()
        mixer_region_frame.setLayout(mixer_region_layout)

        right_layout.addWidget(mixer_region_frame)

        for i in range(4):
            combo_items = ["Phase", "Magnitude", "Real part", "imaginary part"]
            counter = i
            bordered_widget = create_widget(f"Component {i + 1}", combo_items, counter)
            right_layout.addWidget(bordered_widget)

        right_layout.setSpacing(40)  # spacing between elements for clarity
        right_layout.setContentsMargins(10, 10, 10, 10)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        right_layout.addWidget(self.progress_bar)

        right_layout.addStretch()  # filling remaining space and ensure a consistent layout
        for index, slider in enumerate(self.sliders):
            slider.valueChanged.connect(lambda value, idx=index: self.change_slider(idx, value))
        for index, mixer in enumerate(self.mixer_region):
            mixer.currentIndexChanged.connect(lambda value=mixer, idx=index: self.change_slider(idx, value))

        for index, freq_combo in enumerate(self.output_combo):
            freq_combo.currentIndexChanged.connect(
                lambda value=freq_combo, idx=index: self.change_output_freq_components(idx, value))

        for index, freq_combo in enumerate(self.output_combo):
            freq_combo.currentIndexChanged.connect(
                lambda value=freq_combo, idx=index: self.change_slider(idx, value))

        main_layout.addLayout(left_layout, 4)
        main_layout.addLayout(right_layout, 1)

        # central Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(40, 40, 40))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        self.setPalette(dark_palette)
        self.setStyleSheet("background-color: #282828; color: white; font-family: Arial; font-size: 14px;")

    def load_image(self, label_index):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            image = Image.open(file_path).convert('L')
            image_array = np.array(image)
            self.image_id = label_index
            self.image_list[self.image_id] = image_array
            height, width = image_array.shape
            qimage = QImage(image_array.data, width, height, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimage)

            if self.image_id == 0:
                self.image_labels[0].setPixmap(pixmap.scaled(self.image_labels[0].size(), QtCore.Qt.KeepAspectRatio,
                                                             QtCore.Qt.SmoothTransformation))
                magnitude, phase, f_shift = self.compute_magnitude_and_phase(image_array)
                real, imaginary = self.compute_real_and_imaginary(image_array)
                self.image_magnitudes.append(magnitude)
                self.image_phases.append(phase)
                self.image_real_part.append(real)
                self.image_imaginary_part.append(imaginary)
                self.f_shift.append(f_shift)
            elif self.image_id == 1:
                self.image_labels[1].setPixmap(pixmap.scaled(self.image_labels[1].size(), QtCore.Qt.KeepAspectRatio,
                                                             QtCore.Qt.SmoothTransformation))
                magnitude, phase, f_shift = self.compute_magnitude_and_phase(self.image_list[self.image_id])
                real, imaginary = self.compute_real_and_imaginary(image_array)
                self.image_magnitudes.append(magnitude)
                self.image_phases.append(phase)
                self.image_real_part.append(real)
                self.image_imaginary_part.append(imaginary)
                self.f_shift.append(f_shift)

            elif self.image_id == 2:
                self.image_labels[2].setPixmap(pixmap.scaled(self.image_labels[2].size(), QtCore.Qt.KeepAspectRatio,
                                                             QtCore.Qt.SmoothTransformation))
                magnitude, phase, f_shift = self.compute_magnitude_and_phase(self.image_list[self.image_id])
                real, imaginary = self.compute_real_and_imaginary(image_array)
                self.image_magnitudes.append(magnitude)
                self.image_phases.append(phase)
                self.image_real_part.append(real)
                self.image_imaginary_part.append(imaginary)
                self.f_shift.append(f_shift)

            else:
                self.image_labels[3].setPixmap(pixmap.scaled(self.image_labels[3].size(), QtCore.Qt.KeepAspectRatio,
                                                             QtCore.Qt.SmoothTransformation))
                magnitude, phase, f_shift = self.compute_magnitude_and_phase(self.image_list[self.image_id])
                real, imaginary = self.compute_real_and_imaginary(image_array)
                self.image_magnitudes.append(magnitude)
                self.image_phases.append(phase)
                self.image_real_part.append(real)
                self.image_imaginary_part.append(imaginary)
                self.f_shift.append(f_shift)

    def show_freq_components(self, index, value):
        print(index, value)
        if value == 'FT Magnitude':
            self.plot_magnitude(self.f_shift[index], index)
        elif value == "FT Phase":
            self.plot_phase(self.image_phases[index], index)
        elif value == "FT Real Components":
            print("enter real")
            self.plot_real(self.image_real_part[index], index)
        else:
            print("enter imaginary")
            self.plot_imaginary(self.image_imaginary_part[index], index)

    def compute_magnitude_and_phase(self, image_data):
        image_fourier_transform = np.fft.fft2(image_data)
        f_shift = np.fft.fftshift(image_fourier_transform)
        magnitude = np.abs(f_shift)
        phase = np.angle(f_shift)
        return magnitude, phase, f_shift

    def plot_magnitude(self, f_shift, index):
        magnitude_spectrum = 20 * np.log(np.clip(np.abs(f_shift), 1e-10, None) + 1)
        magnitude_spectrum = np.uint8(np.clip(magnitude_spectrum, 0, 255))
        height, width = magnitude_spectrum.shape
        qimage = QImage(magnitude_spectrum.data, width, height, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        self.freq_component_label[index].setPixmap(pixmap)

    def plot_phase(self, phase_spectrum, index):
        phase_spectrum_normalized = np.uint8(np.clip(((phase_spectrum + np.pi) / (2 * np.pi)) * 255, 0, 255))
        height, width = phase_spectrum_normalized.shape
        qimage = QImage(phase_spectrum_normalized.data, width, height, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        self.freq_component_label[index].setPixmap(
            pixmap.scaled(self.freq_component_label[index].size(), QtCore.Qt.KeepAspectRatio,
                          QtCore.Qt.SmoothTransformation))

    def compute_real_and_imaginary(self, image_data):
        # Compute the Fourier Transform
        image_fourier_transform = np.fft.fft2(image_data)
        # Extract the real part of the Fourier Transform
        f_shift = np.fft.fftshift(image_fourier_transform)
        real_part = np.real(f_shift)
        imaginary_part = np.imag(f_shift)
        return real_part, imaginary_part

    def plot_real(self, real_part, index):
        real_part_normalized = np.uint8(np.clip(real_part, 0, 255))
        height, width = real_part_normalized.shape
        qimage = QImage(real_part_normalized.data, width, height, QImage.Format_Grayscale8)
        # Convert QImage to QPixmap and set it on the label
        pixmap = QPixmap.fromImage(qimage)
        self.freq_component_label[index].setPixmap(
            pixmap.scaled(self.freq_component_label[index].size(), QtCore.Qt.KeepAspectRatio,
                          QtCore.Qt.SmoothTransformation))

    def plot_imaginary(self, imaginary_part, index):
        imaginary_part_normalized = np.uint8(np.clip(imaginary_part, 0, 255))
        height, width = imaginary_part_normalized.shape
        qimage = QImage(imaginary_part_normalized.data, width, height, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        self.freq_component_label[index].setPixmap(
            pixmap.scaled(self.freq_component_label[index].size(), QtCore.Qt.KeepAspectRatio,
                          QtCore.Qt.SmoothTransformation))

    def select_mixer_region(self, index, value):
        self.selected_mixer_region = value
        print(f'selected = {value}')
        self.update_magnitude_and_phase_list()

    def select_port(self, index, value):
        self.selected_port = value
        self.selected_port_indx = index

    #
    def change_output_freq_components(self, index, value):
        # if index == 0:
        #     if value == 1 or value == 0:
        #         self.output_combo[1].setCurrentText("Magnitude")
        #         self.output_combo[2].setCurrentText("Phase")
        #         self.output_combo[3].setCurrentText("Magnitude")
        #     else :
        #         self.output_combo[1].setCurrentText("Imaginary part")
        #         self.output_combo[2].setCurrentText("Real part")
        #         self.output_combo[3].setCurrentText("Imaginary part")
        pass

    def create_image_from_components(self, magnitude, phase):
        dft_shift = magnitude * np.exp(1j * phase)
        dft = np.fft.ifftshift(dft_shift)
        img_back = np.abs(np.fft.ifft2(dft))
        return np.uint8(np.clip(img_back, 0, 255))

    def create_image_from_real_and_imaginary(self, real, imaginary):
        dft_shift = real + 1j * imaginary
        dft = np.fft.ifftshift(dft_shift)
        img_back = np.abs(np.fft.ifft2(dft))
        return np.uint8(np.clip(img_back, 0, 255))

    def update_magnitude_and_phase_list(self):
        rect = self.freq_component_label[0].selection_rect
        # Rectangle dimensions
        width = rect.width()
        height = rect.height()

        # Compute the center of the frequency domain
        center_x = self.image_magnitudes[0].shape[1] // 2
        center_y = self.image_magnitudes[0].shape[0] // 2

        # Define the low-frequency rectangle around the center
        start_x = max(center_x - width // 2, 0)
        start_y = max(center_y - height // 2, 0)
        end_x = min(center_x + width // 2, self.image_magnitudes[0].shape[1])
        end_y = min(center_y + height // 2, self.image_magnitudes[0].shape[0])

        self.selected_magnitude.clear()
        self.selected_phase.clear()
        self.selected_real.clear()
        self.selected_imaginary.clear()

        if self.selected_mixer_region == "Inner":
            print("Selecting low-frequency region (inner rectangle)")
            for i in range(4):
                # Full magnitude spectrum
                full_magnitude = self.image_magnitudes[i]

                # Low-frequency region
                selected_region = self.image_magnitudes[i][start_y:end_y, start_x:end_x]
                selected_phase = self.image_phases[i][start_y:end_y, start_x:end_x]
                selected_real = self.image_real_part[i][start_y:end_y, start_x:end_x]
                selected_imaginary = self.image_imaginary_part[i][start_y:end_y, start_x:end_x]

                # Calculate normalization factor
                normalization_factor = np.sum(selected_region) / np.sum(full_magnitude)

                # Normalize the low-frequency magnitudes
                selected_region = selected_region / normalization_factor
                scaling_factor = 0.8  # Adjust this value (0.5-1.0) to control brightness further
                selected_region = selected_region * scaling_factor

                # Store normalized values
                self.selected_magnitude.append(selected_region)
                self.selected_phase.append(selected_phase)
                self.selected_real.append(selected_real)
                self.selected_imaginary.append(selected_imaginary)

        else:
            print("Selecting high-frequency region (outer region)")
            for i in range(4):
                # Create a mask to exclude the inner rectangle
                mask = np.ones_like(self.image_magnitudes[i], dtype=bool)
                mask[start_y:end_y, start_x:end_x] = False

                # High-frequency region
                outer_magnitude = self.image_magnitudes[i][mask]
                outer_phase = self.image_phases[i][mask]
                outer_real = self.image_real_part[i][mask]
                outer_imaginary = self.image_imaginary_part[i][mask]

                # Reconstruct the full-sized arrays with the outer region
                selected_magnitude = np.zeros_like(self.image_magnitudes[i])
                selected_phase = np.zeros_like(self.image_phases[i])
                selected_real = np.zeros_like(self.image_real_part[i])
                selected_imaginary = np.zeros_like(self.image_imaginary_part[i])

                selected_magnitude[mask] = outer_magnitude
                selected_phase[mask] = outer_phase
                selected_real[mask] = outer_real
                selected_imaginary[mask] = outer_imaginary

                # Store the outer region
                self.selected_magnitude.append(selected_magnitude)
                self.selected_phase.append(selected_phase)
                self.selected_real.append(selected_real)
                self.selected_imaginary.append(selected_imaginary)

    def handle_scroll_direction(self, event):
        """Handle the wheel event and process it."""
        # Check the direction of the scroll
        if event == 'down':
            print('down')
        else:
            print('up')

    def update_output(self):
        try:
            # Initialize combined magnitude, phase, real, and imaginary components
            mixed_magnitude = np.zeros_like(self.selected_magnitude[0])
            mixed_phase = np.zeros_like(self.selected_phase[0], dtype=np.complex128)  # Allow complex numbers
            mixed_real = np.zeros_like(self.selected_real[0])
            mixed_imaginary = np.zeros_like(self.selected_imaginary[0])

            # Configure progress bar
            total_parts = 1000
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(total_parts)
            self.progress_bar.setValue(0)
            for i in range(total_parts):
                self.progress_bar.setValue(i + 1)
                QCoreApplication.processEvents()

            # Averaging weights
            total_weight = sum([self.sliders[i].value() for i in range(4)]) / 100.0
            if total_weight == 0:
                raise ValueError("Weights are zero. Adjust sliders to assign weights.")

            # Mixing components based on user selection
            for i in range(4):
                self.combo.append(self.output_combo[i].currentText())
                weight = self.sliders[i].value() / 100.0

                if self.output_combo[i].currentText() == "Magnitude":
                    mixed_magnitude += weight * self.selected_magnitude[i]
                elif self.output_combo[i].currentText() == "Phase":
                    # Convert phase to complex for proper averaging
                    mixed_phase += weight * np.exp(1j * self.selected_phase[i])
                elif self.output_combo[i].currentText() == "Real part":
                    mixed_real += weight * self.selected_real[i]
                else:
                    mixed_imaginary += weight * self.selected_imaginary[i]

            # Finalize magnitude and phase
            mixed_magnitude /= total_weight
            mixed_phase = np.angle(mixed_phase)  # Extract phase from complex average

            # Create mixed images
            output_mag_and_phase_image = self.create_image_from_components(mixed_magnitude, mixed_phase)
            output_real_and_imaginary_image = self.create_image_from_real_and_imaginary(mixed_real, mixed_imaginary)

            # Convert images to QPixmap
            def convert_to_pixmap(image, label_size):
                qimage = QImage(
                    image.data, image.shape[1], image.shape[0],
                    image.strides[0], QImage.Format_Grayscale8
                )
                pixmap = QPixmap.fromImage(qimage)
                return pixmap.scaled(label_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

            scaled_pixmap_mag_phase = convert_to_pixmap(output_mag_and_phase_image, self.output_label[0].size())
            scaled_pixmap_real_imag = convert_to_pixmap(output_real_and_imaginary_image, self.output_label[0].size())

            # Set the output to the appropriate QLabel
            if self.selected_port == "Port 1" and ("Magnitude" in self.combo or "Phase" in self.combo):
                self.output_label[0].setPixmap(scaled_pixmap_mag_phase)
            elif self.selected_port == "Port 1":
                self.output_label[0].setPixmap(scaled_pixmap_real_imag)
            elif self.selected_port == "Port 2" and ("Magnitude" in self.combo or "Phase" in self.combo):
                self.output_label[1].setPixmap(scaled_pixmap_mag_phase)
            else:
                self.output_label[1].setPixmap(scaled_pixmap_real_imag)

            # Clear combo list
            self.combo.clear()

        except ValueError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Error: select a region")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def change_slider(self, index, value):
        self.update_output()
        print("A")


app = QtWidgets.QApplication([])
window = UI()
window.show()
app.exec_()
