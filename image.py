import os

from PIL import Image


class CustomImage:
    def __init__(self, path, folder="reduced"):
        self.image = Image.open(path)
        self.width, self.height = self.image.size
        self.path = path
        #self.reduced_path = os.path.join(os.path.dirname(self.path), folder, os.path.basename(self.path))  # Pour créer le dossier des images réduites là où sont les images réduites
        self.reduced_path = os.path.join(os.path.dirname(__file__), folder, os.path.basename(self.path))  # Pour créer le dossier des images réduites là où s'exécute le script Python

    def reduce_image(self, size=0.5, quality=75):
        new_width = round(self.width * size)
        new_height = round(self.height * size)
        self.image = self.image.resize((new_width, new_height))
        parent_dir = os.path.dirname(self.reduced_path)

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        self.image.save(self.reduced_path, 'JPEG', quality=quality)
        return os.path.exists(self.reduced_path)


# Dans le cas où on executerait ce fichier directement
if __name__ == '__main__':
    i = CustomImage("C:\\Users\\admin\\Desktop\\test.jpeg")
    i.reduce_image(size=1, quality=50)