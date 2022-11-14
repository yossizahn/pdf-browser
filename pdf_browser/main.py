import sys
from pathlib import Path
from typing import Optional

import fitz
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QKeyEvent, QMouseEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
)
from PyQt6.uic import loadUi


class PBMainWindow(QMainWindow):
    # widgets
    openFileButton: QPushButton
    pageBackButton: QPushButton
    pageForwardButton: QPushButton
    infoLabel: QLabel
    imageLabel: QLabel
    # state
    pdf: Optional[fitz.Document] = None
    currentPage: int = -1

    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent / "mainwindow.ui", self)
        self.openFileButton.clicked.connect(self.onOpenClicked)
        self.pageBackButton.clicked.connect(self.onBackPage)
        self.pageForwardButton.clicked.connect(self.onForwardPage)

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        if self.pdf is None:
            self.onOpenClicked()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key.Key_Right or e.key() == Qt.Key.Key_Down:
            self.onForwardPage()
        elif e.key() == Qt.Key.Key_Left or e.key() == Qt.Key.Key_Up:
            self.onBackPage()
        else:
            super().keyPressEvent(e)

    def onOpenClicked(self) -> None:
        (filename, _) = QFileDialog.getOpenFileName(
            self,
            "Select file to open...",
            filter="PDF Files (*.pdf)",
            directory=f"{Path.home()}",
        )
        if filename == "":
            return
        self.pdf = fitz.Document(filename)
        self.onDocLoaded()

    def onForwardPage(self) -> None:
        self.setCurrentPage(self.currentPage + 1)

    def onBackPage(self) -> None:
        self.setCurrentPage(self.currentPage - 1)

    def onDocLoaded(self) -> None:
        self.setCurrentPage(0)

    def setCurrentPage(self, pageNumber: int) -> None:
        if self.pdf is None:
            return
        if pageNumber >= self.pdf.page_count or pageNumber < 0:
            return
        self.currentPage = pageNumber
        self.pageForwardButton.setEnabled(pageNumber + 1 < self.pdf.page_count)
        self.pageBackButton.setEnabled(pageNumber - 1 >= 0)
        self.infoLabel.setText(
            f"{Path(self.pdf.name).name} | {self.currentPage + 1}"
            f" / {self.pdf.page_count} pages"
        )
        page: fitz.Page = self.pdf.load_page(pageNumber)
        dl: fitz.DisplayList = page.get_displaylist()
        pix: fitz.Pixmap = dl.get_pixmap()
        fmt = (
            QImage.Format.Format_RGBA8888
            if pix.alpha
            else QImage.Format.Format_RGB888
        )
        qtimg = QImage(pix.samples_ptr, pix.width, pix.height, pix.stride, fmt)
        self.imageLabel.setPixmap(QPixmap.fromImage(qtimg))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PBMainWindow()
    window.show()
    app.exec()
