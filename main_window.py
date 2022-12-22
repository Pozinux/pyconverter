from PySide6 import QtWidgets, QtCore, QtGui

from worker import Worker

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyConverter")
        self.setup_ui()
        
        self.show()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_quality = QtWidgets.QLabel("Qualité:")
        self.spn_quality = QtWidgets.QSpinBox()
        self.lbl_size = QtWidgets.QLabel("Taille:")
        self.spn_size = QtWidgets.QSpinBox()
        self.lbl_dossierOut = QtWidgets.QLabel("Dossier de sortie:")
        self.le_dossierOut = QtWidgets.QLineEdit()
        self.lw_files = QtWidgets.QListWidget()
        self.btn_convert = QtWidgets.QPushButton("Conversion")
        self.lbl_dropInfo = QtWidgets.QLabel("Déposez les images sur l'interface")

    def modify_widgets(self):
        # Alignment
        self.spn_quality.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.spn_size.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.le_dossierOut.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        # Range
        self.spn_quality.setRange(1, 100)
        self.spn_quality.setValue(75)
        self.spn_size.setRange(1, 100)
        self.spn_size.setValue(50)

        # Divers
        self.le_dossierOut.setPlaceholderText("Dossier de sortie...")
        self.le_dossierOut.setText("images_reduites")
        self.lbl_dropInfo.setVisible(False)

        self.setAcceptDrops(True)
        self.lw_files.setAlternatingRowColors(True)
        self.lw_files.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

    def create_layouts(self):
        self.main_layout = QtWidgets.QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_quality, 0, 0, 1, 1)
        self.main_layout.addWidget(self.spn_quality, 0, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_size, 1, 0, 1, 1)
        self.main_layout.addWidget(self.spn_size, 1, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_dossierOut, 2, 0, 1, 1)
        self.main_layout.addWidget(self.le_dossierOut, 2, 1, 1, 1)
        self.main_layout.addWidget(self.lw_files, 3, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_dropInfo, 4, 0, 1, 2)
        self.main_layout.addWidget(self.btn_convert, 5, 0, 1, 2)

    def setup_connections(self):
        QtGui.QShortcut(QtGui.QKeySequence("Delete"), self.lw_files, self.delete_selected_items)  # Quand on utilise la touche delete, on peut supprimer de la liste (c'est une raccourci)
        self.btn_convert.clicked.connect(self.convert_images)

    def convert_images(self):
        quality = self.spn_quality.value()
        size = self.spn_size.value() / 100.0
        folder = self.le_dossierOut.text()

        lw_items = [self.lw_files.item(index) for index in range(self.lw_files.count())]
        images_a_convertir = [1 for lw_item in lw_items if not lw_item.processed]
        if not images_a_convertir:          
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Aucune image à convertir", "Toutes les images ont déjà été converties.")
            msg_box.exec_()
            return False

        self.thread = QtCore.QThread(self)  # On créé un thread

        self.worker = Worker(images_to_convert=lw_items, quality=quality, size=size, folder=folder)

        self.worker.moveToThread(self.thread)
        self.worker.image_converted.connect(self.image_converted)  # Quand le signal image_converted est émit, on exécute la fonction image_converted
        self.thread.started.connect(self.worker.convert_images)
        self.worker.finished.connect(self.thread.quit)  # Quand le signal finished est émit, on quitte le thread
        self.thread.start()

        self.prg_dialog = QtWidgets.QProgressDialog("Conversion des images", "Annuler...", 1, len(images_a_convertir))
        self.prg_dialog.canceled.connect(self.abort)
        self.prg_dialog.show()

    def abort(self):
        self.worker.runs = False
        self.thread.quit()

    def image_converted(self, lw_item, success):  # On exécute cette fonction quand le signal image_converted du thread est émit
        if success:
            lw_item.setIcon(QtGui.QIcon("images/checked.png"))  # Si l'image est convertie, on ajoute un icone ok à l'item de la liste
            lw_item.processed = True  # On met un attribut à True pour dire que l'image a été convertie pour pas qu'on la reconvertisse si on relance (vérifié dans convert_images)
            self.prg_dialog.setValue(self.prg_dialog.value() + 1)

    def delete_selected_items(self):
        for lw_item in self.lw_files.selectedItems():
            row = self.lw_files.row(lw_item)
            self.lw_files.takeItem(row)

    def dragEnterEvent(self, event):
        self.lbl_dropInfo.setVisible(True)
        event.accept()

    def dragLeaveEvent(self, event):
        self.lbl_dropInfo.setVisible(False)

    def dropEvent(self, event):
        event.accept()
        for url in event.mimeData().urls():
            self.add_file(path=url.toLocalFile())

        self.lbl_dropInfo.setVisible(False)

    def add_file(self, path):
        items = [self.lw_files.item(index).text() for index in range(self.lw_files.count())]
        if path not in items:
            lw_item = QtWidgets.QListWidgetItem(path)
            lw_item.setIcon(QtGui.QIcon("images/unchecked.png"))  # On met un icon unchecked pour indiquer que la conversion n'a pas encore été faite pour cet élément de la liste
            lw_item.processed = False
            self.lw_files.addItem(lw_item)



app = QtWidgets.QApplication([])
main_window = MainWindow()
app.exec()
