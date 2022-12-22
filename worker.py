from PySide6 import QtCore
from image import CustomImage


# C'est cette classe qui va effecuter le travail long dans le Thread
class Worker(QtCore.QObject):
    image_converted = QtCore.Signal(object, bool)  # On créé un signal qui s'appelle image_converted et qui envoie des infos (un objet Python généric correspondant au image_lw_item et un Booléen pour indiquer le success ou non de la conversion) quand il est émit
    finished = QtCore.Signal()  # On créé un signal qui s'appelle finished

    def __init__(self, images_to_convert, quality, size, folder):
        super().__init__()
        self.images_to_convert = images_to_convert
        self.quality = quality
        self.size = size
        self.folder = folder
        self.runs = True

    def convert_images(self):
        for image_lw_item in self.images_to_convert:
            if self.runs and not image_lw_item.processed:
                image = CustomImage(path=image_lw_item.text(), folder=self.folder)
                success = image.reduce_image(size=self.size, quality=self.quality)
                self.image_converted.emit(image_lw_item, success)  # On émet le signal quand une image est convertie et avec ce signal on envoit le nom de l'item de la liste et un booléen de success ou pas

        self.finished.emit()  # Quand on sort de la boucle qui converti toutes les images, cela signifie que la thread a fini son job donc on émet le signal finished
