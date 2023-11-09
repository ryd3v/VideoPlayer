import sys

import gi
from PyQt6.QtGui import QAction

gi.require_version('Gst', '1.0')
from gi.repository import Gst
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMenuBar, QPushButton, \
    QHBoxLayout

Gst.init(None)


class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.pipeline = Gst.parse_launch("playbin")
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.enable_sync_message_emission()
        self.bus.connect('message', self.on_message)
        self.bus.connect('sync-message::element', self.on_sync_message)

    def set_video(self, file_path):
        self.pipeline.set_property('uri', 'file://' + file_path)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.pipeline.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)

    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            message.src.set_property('force-aspect-ratio', True)
            message.src.set_window_handle(self.winId())

    def play(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.video_widget = VideoWidget(self)
        self.setCentralWidget(self.video_widget)
        self.resize(400, 100)
        self.setup_menu_bar()

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.video_widget.play)
        self.play_button.setStyleSheet("""
                                            QPushButton {
                                                background-color: #3b82f6;
                                                border-radius: 8px;
                                                height: 30px;
                                            }
                                            QPushButton:hover {
                                                background-color: #27272a;
                                            }
                                            QPushButton:pressed {
                                                background-color: #2563eb;
                                            }
                                        """)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.video_widget.pause)
        self.pause_button.setStyleSheet("""
                                            QPushButton {
                                                background-color: #3b82f6;
                                                border-radius: 8px;
                                                height: 30px;
                                            }
                                            QPushButton:hover {
                                                background-color: #27272a;
                                            }
                                            QPushButton:pressed {
                                                background-color: #2563eb;
                                            }
                                        """)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.video_widget.stop)
        self.stop_button.setStyleSheet("""
                                            QPushButton {
                                                background-color: #3b82f6;
                                                border-radius: 8px;
                                                height: 30px;
                                            }
                                            QPushButton:hover {
                                                background-color: #27272a;
                                            }
                                            QPushButton:pressed {
                                                background-color: #2563eb;
                                            }
                                        """)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget)  # This would be your video display widget
        main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setup_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if file_name:
            self.video_widget.stop()
            self.video_widget.set_video(file_name)
            self.video_widget.play()

    def closeEvent(self, event):
        self.video_widget.stop()
        super(MainWindow, self).closeEvent(event)

    def closeEvent(self, event):
        self.video_widget.stop()
        super(MainWindow, self).closeEvent(event)


app = QApplication(sys.argv)
app.setStyle("Fusion")
main_window = MainWindow()
main_window.setWindowTitle("VideoPlayer")
main_window.show()
main_window.video_widget.play()
sys.exit(app.exec())
