# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, pyqtProperty,
                          QObject, QThread, QDir)
from PyQt5.QtWidgets import (QFrame, QFileDialog)
from PyQt5.QtGui import QPixmap

import os
import numpy as np
from PIL import Image
from matplotlib import cm

class QRayleighSommerfeld(QFrame):

    def __init__(self, parent = None):
        super(QRayleighSommerfeld, self).__init__(parent)

        dir = os.path.dirname(os.path.abspath(__file__))
        uifile = os.path.join(dir, 'QRayleighSommerfeld.ui')
        uic.loadUi(uifile, self)
        
        self.openImage.clicked.connect(self.dispImage)

#slots
    @pyqtSlot()
    def dispImage(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/home/group/data/", "Image files (*.jpg *.png")
        self.labelImage.setPixmap(QPixmap(filename))
        channels_count = 4
        pixmap = QPixmap(filename)
        image = pixmap.toImage()
        s = image.bits().asstring(1280 * 1024 * channels_count)
        im = np.fromstring(s, dtype=np.uint8).reshape((1280, 1024, channels_count))
        nim = (im-np.min(im))/(np.max(im)-np.min(im))
        cim = Image.fromarray(np.uint8(cm.gist_earth(nim)*255))
    		
#properties
    @pyqtProperty(str)
    def filename(self):
        return str(self.saveEdit.text())
        
    @filename.setter
    def filename(self, filename):
        self.saveEdit.setText(os.path.expanduser(filename))
        self.dispname = self.filename
        
    @pyqtProperty(str)
    def dispname(self):
        return str(self.openImage.text())

    @dispname.setter
    def dispname(self, filename):
        if not (self.is_playing()):
            self.openImage.setText(os.path.expanduser(filename))


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    wid = QRayleighSommerfeld()
    wid.show()
    sys.exit(app.exec_())
