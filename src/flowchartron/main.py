import os
import sys
from flowchartron.diagramMaker import FlowChart
from flowchartron.chart_gen import DrawIOBrowser, cp
from flowchartron.elements_db import BlockStyleDB
from flowchartron.xml_gen import generate_XML
from flowchartron.window import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QLabel, QProgressBar
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QObject, QThread, pyqtSignal

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

class GPTWorker(QObject):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    def __init__(self, program_source: str, progressBar: QProgressBar):
        super().__init__()
        self.program_source = program_source,
        self.progressBar = progressBar

    def run(self):
        try:
            xml = generate_XML(self.program_source[0], self.progress)
        except:
            xml = ""
        self.finished.emit(xml)

class BrowserWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self, browser: DrawIOBrowser, drawio_file: str, output_path: str):
        super().__init__()
        self.browser = browser,
        self.drawio_file = drawio_file,
        self.output_path = output_path,

    def run(self):
        try:
            self.browser[0].export_to_png(self.drawio_file[0], self.output_path[0], self.progress)
        except:
            pass
        self.finished.emit()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.imageLabel = QLabel()
        self.imgScrollArea.setWidget(self.imageLabel)

        self.__flowchart__ = FlowChart()
        self.__browser__ = DrawIOBrowser()
        self.style_db = BlockStyleDB(os.path.join(self.__browser__._WORKING_DIRECTORY, "cool_db.db"))

        self.XMLGenButton.clicked.connect(self.generate_XML)
        self.imgGenButton.clicked.connect(self.gen_img)
        self.imgSaveButton.clicked.connect(self.save_file)
        self.imgCopyButton.clicked.connect(self.clipboard)

    def generate_XML(self):
        program_source = self.codeBlock.toPlainText()
        if program_source == "":
            msgBox = QMessageBox()
            msgBox.setText("Введите текст!")
            msgBox.exec()
            return

        self.XMLGenButton.setEnabled(False)
        self.codeBlock.setEnabled(False)

        self.threadXML = QThread()
        self.worker = GPTWorker(program_source, self.XMLGenProgressBar)
        self.worker.moveToThread(self.threadXML)

        self.threadXML.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_generated_xml)
        self.worker.finished.connect(self.threadXML.quit)
        self.worker.progress.connect(self.handle_xml_progress)

        self.threadXML.start()

    def handle_xml_progress(self, result: int):
        match result:
            case 0:
                self.XMLGenProgressBar.setFormat("Ожидание действий пользователя...(%v/%m)")
            case 1:
                self.XMLGenProgressBar.setFormat("Запрос базовой диаграммы...(%v/%m)")
            case 2:
                self.XMLGenProgressBar.setFormat("Украшение блоков...(%v/%m)")
            case 3:
                self.XMLGenProgressBar.setFormat("Перевод в естественный язык...(%v/%m)")
            case 4:
                self.XMLGenProgressBar.setFormat("Перевод на русский...(%v/%m)")
            case 5:
                self.XMLGenProgressBar.setFormat("Исправление XML...(%v/%m)")

        self.XMLGenProgressBar.setValue(result)

    def handle_generated_xml(self, result: str):
        self.codeBlock.setEnabled(True)
        self.XMLGenButton.setEnabled(True)
        print(result)

        if result == "":
            msgBox = QMessageBox(self)
            msgBox.setText("Не удалось сгенерировать XML")
            msgBox.exec()
            return
        try:
            self.__flowchart__.parse_XML(result, self.style_db)
        except:
            msgBox = QMessageBox(self)
            msgBox.setText("Не удалось сгенерировать XML")
            msgBox.setInformativeText("Сгенерированный XML неверного формата")
            msgBox.exec()
            return

        self.XMLBlock.setPlainText(result)

    def gen_img(self):
        xml = self.XMLBlock.toPlainText()
        try:
            self.__flowchart__.parse_XML(xml, self.style_db)
        except:
            msgBox = QMessageBox(self)
            msgBox.setText("Не удалось извлечь XML")
            msgBox.setInformativeText("XML неверного формата")
            msgBox.exec()
            return

        self.imgGenButton.setEnabled(False)
        self.XMLBlock.setEnabled(False)

        self.tmpfile = os.path.join(self.__browser__._WORKING_DIRECTORY, "tmp.drawio")
        self.png_path = os.path.join(self.__browser__._WORKING_DIRECTORY, "output.png")

        self.__flowchart__.parse_XML(xml, self.style_db)
        drawio_flowchart = self.__flowchart__.chart_compile(self.style_db)

        with open(self.tmpfile, "w") as F:
            F.write(drawio_flowchart)

        self.threadPNG = QThread()
        self.worker = BrowserWorker(self.__browser__, self.tmpfile, self.png_path)
        self.worker.moveToThread(self.threadPNG)

        self.threadPNG.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_generated_img)
        self.worker.finished.connect(self.threadPNG.quit)
        self.worker.progress.connect(self.handle_img_progress)

        self.threadPNG.start()

    def handle_img_progress(self, result: int):
        match result:
            case 0:
                self.XMLGenProgressBar.setFormat("Ожидание действий пользователя...(%v/%m)")
            case 1:
                self.imgGenProgressBar.setFormat("Открытие draw.io...(%v/%m)")
            case 2:
                self.imgGenProgressBar.setFormat("Выгрузка файла .drawio...(%v/%m)")
            case 3:
                self.imgGenProgressBar.setFormat("Загрузка файла...(%v/%m)")
        self.imgGenProgressBar.setValue(result)

    def handle_generated_img(self):
        self.imgGenButton.setEnabled(True)
        self.XMLBlock.setEnabled(True)

        if not os.path.exists(self.png_path):
            msgBox = QMessageBox()
            msgBox.setText("Не удалось экспортировать блок-схему")
            msgBox.exec()
            self.imgGenProgressBar.setFormat("Ожидание действий пользователя...(%p/%m)")

        flowchartQImage = QImage(self.png_path)
        self.imageLabel.setPixmap(QPixmap.fromImage(flowchartQImage))

    def save_file(self):
        tmpfile = os.path.join(self.__browser__._WORKING_DIRECTORY, "tmp.drawio")
        png_path = os.path.join(self.__browser__._WORKING_DIRECTORY, "output.png")

        if not os.path.isfile(png_path):
            msgBox = QMessageBox(self)
            msgBox.setText("Сгенерируйте изображение!")
            msgBox.exec()
            return

        options = QFileDialog.Options()
        output_path, _ = QFileDialog.getSaveFileName(
                self, 
                'Save File', 
                '', 
                'draw.io Files (*.drawio);;Images (*.png)', 
                options=options
                )

        if output_path:
            extension = output_path.split(os.extsep)[-1]
            if extension == "drawio":
                cp(tmpfile, output_path)
            if extension == "png":
                cp(png_path, output_path)

    def clipboard(self):
        png_path = os.path.join(self.__browser__._WORKING_DIRECTORY, "output.png")

        if not os.path.isfile(png_path):
            msgBox = QMessageBox(self)
            msgBox.setText("Сгенерируйте изображение!")
            msgBox.exec()
            return

        image = QImage(png_path)
        clipboard = QApplication.clipboard()
        clipboard.setImage(image)

if __name__ == "__main__":
    main()
