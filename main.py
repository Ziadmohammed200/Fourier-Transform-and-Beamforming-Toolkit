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
        self.scroll_scale=0
        self.image_id = 0
        self.freq_component_combobox = []
        self.freq_component_label = []
        self.mixed_magnitude=None
        self.mixed_phase=None
        self.image_phases = [[[0]],[[0]],[[0]],[[0]]]
        self.image_magnitudes = [[[0]],[[0]],[[0]],[[0]]]
        self.image_real_part = [[[0]],[[0]],[[0]],[[0]]]
        self.image_imaginary_part = [[[0]],[[0]],[[0]],[[0]]]
        self.weighted_magnitude = [np.zeros((1, 1))] * 4
        self.weighted_phase = [np.zeros((1, 1))] * 4
        self.selected_port_indx = 0
        self.i=0
        self.is_updating_output = False
        self.start = 1
        self.output_label = []
        self.sliders = []
        self.mixer_region = []
        self.f_shift = [[0],[0],[0],[0]]
        self.selected_port = 'Port 1'
        self.selected_mixer_region = "Inner"
        self.output_combo = []
        self.combo = []
        self.selected_magnitude =  [[[0]],[[0]],[[0]],[[0]]]
        self.selected_phase =  [[[0]],[[0]],[[0]],[[0]]]
        self.selected_real =  [[[0]],[[0]],[[0]],[[0]]]
        self.selected_imaginary =  [[[0]],[[0]],[[0]],[[0]]]
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
        self.process_button = QtWidgets.QPushButton("Update")
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #282828; /* Dark background */
                border: 2px solid #444; /* Border color */
                border-radius: 10px; /* Rounded corners */
                text-align: center; /* Centered text */
                color: white; /* Text color */
                font-size: 12px; /* Font size */
                padding: 5px 5px; /* Padding for the button */
            }
            QPushButton:hover {
                background-color: #8B0047; /* Deep red on hover */
                border: 2px solid #8B0047; /* Same color border on hover */
            }
        """)

        # Connect the button to a function if needed
        self.process_button.clicked.connect(self.update_output)

        # Add the button to the layout
        right_layout.addWidget(self.process_button)

        # Add a stretch after the button to ensure the layout behaves as expected
        right_layout.addStretch()

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
            target_size = (400, 250)
            image = image.resize(target_size, Image.NEAREST)
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
                self.image_magnitudes[0] = magnitude
                self.image_phases[0] = phase
                self.image_real_part[0] = real
                self.image_imaginary_part[0] = imaginary
                self.f_shift[0] = f_shift
                self.update_magnitude_and_phase_list()

            elif self.image_id == 1:
                self.image_labels[1].setPixmap(pixmap.scaled(self.image_labels[1].size(), QtCore.Qt.KeepAspectRatio,
                                                             QtCore.Qt.SmoothTransformation))
                magnitude, phase, f_shift = self.compute_magnitude_and_phase(self.image_list[self.image_id])
                real, imaginary = self.compute_real_and_imaginary(image_array)
                self.image_magnitudes[1] = magnitude
                self.image_phases[1] = phase
                self.image_real_part[1] = real
                self.image_imaginary_part[1] = imaginary
                self.f_shift[1] = f_shift
                self.update_magnitude_and_phase_list()


            elif self.image_id == 2:
                self.image_labels[2].setPixmap(pixmap.scaled(self.image_labels[2].size(), QtCore.Qt.KeepAspectRatio,
                                                             QtCore.Qt.SmoothTransformation))
                magnitude, phase, f_shift = self.compute_magnitude_and_phase(self.image_list[self.image_id])
                real, imaginary = self.compute_real_and_imaginary(image_array)
                self.image_magnitudes[2] = magnitude
                self.image_phases[2] = phase
                self.image_real_part[2] = real
                self.image_imaginary_part[2] = imaginary
                self.f_shift[2] = f_shift
                self.update_magnitude_and_phase_list()


            else:
                self.image_labels[3].setPixmap(pixmap.scaled(self.image_labels[3].size(), QtCore.Qt.KeepAspectRatio,
                                                             QtCore.Qt.SmoothTransformation))
                magnitude, phase, f_shift = self.compute_magnitude_and_phase(self.image_list[self.image_id])
                real, imaginary = self.compute_real_and_imaginary(image_array)
                self.image_magnitudes[3] = magnitude
                self.image_phases[3] = phase
                self.image_real_part[3] = real
                self.image_imaginary_part[3] = imaginary
                self.f_shift[3] = f_shift
                self.update_magnitude_and_phase_list()

    def show_freq_components(self, index, value):
        try:
            if value == 'FT Magnitude':
                self.plot_magnitude(self.f_shift[index], index)
            elif value == "FT Phase":
                self.plot_phase(self.image_phases[index], index)
            elif value == "FT Real Components":
                self.plot_real(self.image_real_part[index], index)
            elif value == "FT Imaginary Components":
                self.plot_imaginary(self.image_imaginary_part[index], index)
            else:
                return
        except:
            message = QMessageBox()
            message.setIcon(QMessageBox.Warning)
            message.setWindowTitle("Error !")
            message.setText("Upload image first")
            message.exec_()
            self.freq_component_combobox[index].setCurrentText("Choose FT Component")


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
        self.update_magnitude_and_phase_list()

    def select_port(self, index, value):
        self.selected_port = value
        self.selected_port_indx = index
        self.update_output()

    #
    def change_output_freq_components(self,index,value):
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
        if self.is_updating_output:
            return
        # try :
        rect = None
        for label in self.freq_component_label:
            rect = label.selection_rect
            if rect is not None:
                break

        if rect is not None:
            try:
                self.is_updating_output = True
                width = rect.width()
                height = rect.height()

                if self.image_magnitudes[0][0][0] > 0:
                    center_x = self.image_magnitudes[0].shape[1] // 2
                    center_y = self.image_magnitudes[0].shape[0] // 2
                    self.i=0
                elif self.image_magnitudes[1][0][0] > 0:
                    center_x = self.image_magnitudes[1].shape[1] // 2
                    center_y = self.image_magnitudes[1].shape[0] // 2
                    self.i=1
                elif self.image_magnitudes[2][0][0] > 0:
                    center_x = self.image_magnitudes[2].shape[1] // 2
                    center_y = self.image_magnitudes[2].shape[0] // 2
                    self.i=2
                else:
                    center_x = self.image_magnitudes[3].shape[1] // 2
                    center_y = self.image_magnitudes[3].shape[0] // 2
                    self.i=3



                start_x = max(center_x - width // 2, 0)
                start_y = max(center_y - height // 2, 0)
                end_x = min(center_x + width // 2, self.image_magnitudes[self.i].shape[1])
                end_y = min(center_y + height // 2, self.image_magnitudes[self.i].shape[0])

                for i in range(4):
                    # Create a mask for the inner rectangle
                    if self.image_magnitudes[i][0][0] != 0:
                        mask = np.zeros_like(self.image_magnitudes[i], dtype=bool)
                        mask[start_y:end_y, start_x:end_x] = True

                        if self.selected_mixer_region == "Inner":

                            selected_region = np.where(mask, self.image_magnitudes[i], 0)
                            selected_phase = np.where(mask, self.image_phases[i], 0)
                            selected_real = np.where(mask, self.image_real_part[i], 0)
                            selected_imaginary = np.where(mask, self.image_imaginary_part[i], 0)

                        else:

                            selected_region = np.where(~mask, self.image_magnitudes[i], 0)
                            selected_phase = np.where(~mask, self.image_phases[i], 0)
                            selected_real = np.where(~mask, self.image_real_part[i], 0)
                            selected_imaginary = np.where(~mask, self.image_imaginary_part[i], 0)

                        self.selected_magnitude[i]=selected_region
                        self.selected_phase[i] = selected_phase
                        self.selected_real[i]=selected_real
                        self.selected_imaginary[i]=selected_imaginary
                self.update_output()
            finally:
                self.is_updating_output = False

    def handle_scroll_direction(self, event):
        """Handle the wheel event and process it."""
        # Define scaling limits
        min_scale = 0.2
        max_scale = 2.0
        step = 0.02

        # Define contrast limits
        min_contrast = 0.5
        max_contrast = 2.0
        contrast_step = 0.1

        if event == 'down':
            new_scale = max(self.scroll_scale - step, min_scale)
        elif event=='up':
            new_scale = min(self.scroll_scale + step, max_scale)
        elif event == 'right':
            print('right')
        else:
            print('left')

        # If the scale hasn't changed, no need to update
        if new_scale == self.scroll_scale:
            return

        # Update the scroll scale
        self.scroll_scale = new_scale
        print(self.scroll_scale)

        # Scale the mixed magnitude and update the output
        scaled_magnitude = self.mixed_magnitude * self.scroll_scale
        self.update_output_image_after_scroll(scaled_magnitude, self.mixed_phase)


    def update_output_image_after_scroll(self, magnitude, phase):

        # Generate the output image
        out_image = self.create_image_from_components(magnitude, phase)

        # Convert the image to a pixmap
        scaled_pixmap_mag_phase = self.convert_to_pixmap(out_image, self.output_label[0].size())

        # Update the label
        if self.selected_port == "Port 1":
            self.output_label[0].setPixmap(scaled_pixmap_mag_phase)
        else:
            self.output_label[1].setPixmap(scaled_pixmap_mag_phase)


    def update_output(self):

            if not isinstance(self.selected_magnitude[0],list):
                mixed_magnitude = np.zeros_like(self.selected_magnitude[0])
                mixed_phase = np.zeros_like(self.selected_phase[0],dtype='complex128')  # Allow complex numbers
                mixed_real = np.zeros_like(self.selected_real[0])
                mixed_imaginary = np.zeros_like(self.selected_imaginary[0])
            elif not isinstance(self.selected_magnitude[1],list):
                mixed_magnitude = np.zeros_like(self.selected_magnitude[1])
                mixed_phase = np.zeros_like(self.selected_phase[1],dtype='complex128')  # Allow complex numbers
                mixed_real = np.zeros_like(self.selected_real[1])
                mixed_imaginary = np.zeros_like(self.selected_imaginary[1])
            elif not isinstance(self.selected_magnitude[2],list):
                mixed_magnitude = np.zeros_like(self.selected_magnitude[2])
                mixed_phase = np.zeros_like(self.selected_phase[2],dtype='complex128')  # Allow complex numbers
                mixed_real = np.zeros_like(self.selected_real[2])
                mixed_imaginary = np.zeros_like(self.selected_imaginary[2])
            else:
                mixed_magnitude = np.zeros_like(self.selected_magnitude[3])
                mixed_phase = np.zeros_like(self.selected_phase[3],dtype='complex128')  # Allow complex numbers
                mixed_real = np.zeros_like(self.selected_real[3])
                mixed_imaginary = np.zeros_like(self.selected_imaginary[3])

            total_parts = 10
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(total_parts)
            self.progress_bar.setValue(0)
            for i in range(total_parts):
                self.progress_bar.setValue(i + 1)
                QCoreApplication.processEvents()
            for i in range(4):

                self.combo.append(self.output_combo[i].currentText())
                weight = self.sliders[i].value() / 100.0

                if self.output_combo[i].currentText() == "Magnitude":
                    if not isinstance(self.selected_magnitude[i],list):
                        mixed_magnitude += weight * self.selected_magnitude[i]
                        self.scroll_scale +=weight
                elif self.output_combo[i].currentText() == "Phase":
                    if not isinstance(self.selected_phase[i],list):
                        mixed_phase += weight*np.exp(1j * (weight * self.selected_phase[i]))
                elif self.output_combo[i].currentText() == "Real part":
                    if not isinstance(self.selected_real[i],list):
                        mixed_real += weight * self.selected_real[i]
                else:
                    if not isinstance(self.selected_imaginary[i],list):
                        mixed_imaginary += weight * self.selected_imaginary[i]
            mixed_phase = np.angle(mixed_phase)
            self.mixed_magnitude=np.copy(mixed_magnitude)
            self.mixed_phase=np.copy(mixed_phase)

            # Create mixed images
            output_mag_and_phase_image = self.create_image_from_components(mixed_magnitude, mixed_phase)
            output_real_and_imaginary_image = self.create_image_from_real_and_imaginary(mixed_real, mixed_imaginary)
            scaled_pixmap_mag_phase = self.convert_to_pixmap(output_mag_and_phase_image, self.output_label[0].size())
            scaled_pixmap_real_imag = self.convert_to_pixmap(output_real_and_imaginary_image,
                                                             self.output_label[0].size())

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

            # Convert images to QPixmap
    def convert_to_pixmap(self,image, label_size):
        qimage = QImage(
            image.data, image.shape[1], image.shape[0],
            image.strides[0], QImage.Format_Grayscale8
        )
        pixmap = QPixmap.fromImage(qimage)
        return pixmap.scaled(label_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def change_slider(self, index, value):
        self.update_output()


app = QtWidgets.QApplication([])
window = UI()
window.show()
app.exec_()
