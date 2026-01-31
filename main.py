import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.showFullScreen()
sys.exit(app.exec_())
