# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, pyqtProperty,
                          QObject, QThread, QDir)
from PyQt5.QtWidgets import (QFrame, QFileDialog)
from PyQt5.QtGui import QPixmap
from rayleighsommerfeld import rayleighsommerfeld

import os
import numpy as np
from PIL import Image
from matplotlib import cm
import cv2

class QRayleighSommerfeld(QFrame):

    def __init__(self, parent = None):
        super(QRayleighSommerfeld, self).__init__(parent)

        dir = os.path.dirname(os.path.abspath(__file__))
        uifile = os.path.join(dir, 'QRayleighSommerfeld.ui')
        uic.loadUi(uifile, self)

        #handle buttons/displays
        self.openImage.clicked.connect(self.dispImage)
        self.backPropagate.clicked.connect(self.propagate)

        #handle sliders
        self.zmax_slider.valueChanged.connect(self.updateValues)
        self.zmin_slider.valueChanged.connect(self.updateValues)
        self.dz_slider.valueChanged.connect(self.updateValues)

        #handle checkboxes
        self.phaseCheckbox.toggled.connect(self.handlePhaseToggled)
        self.intensityCheckbox.toggled.connect(self.handleIntToggled)

#slots
    @pyqtSlot()
    def dispImage(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/home/group/data/", "Image files (*.jpg *.png")
        self.labelImage.setPixmap(QPixmap(filename))
        channels_count = 4
        pixmap = QPixmap(filename)
        image = pixmap.toImage()
        s = image.bits().asstring(1280 * 1024 * channels_count)
        arr = np.fromstring(s, dtype=np.uint8).reshape((1280, 1024, channels_count))
        self.arr = arr

    def updateValues(self):
        zmax = self.zmax_slider.value()
        zmin = self.zmin_slider.value()
        dz = self.dz_slider.value()
        self.zmax = zmax
        self.zmin = zmin
        self.dz = dz

    def propagate(self):
        zmin, zmax = self.zmin, self.zmax
        n = int((zmax - zmin)/self.dz)
        mpp = 0.048
        z = np.linspace(zmin, zmax, n)/mpp
        b = self.arr[:,:,0]
        rs = rayleighsommerfeld(b, z, magnification = mpp, nozphase = True)
        bz = np.abs(rs).astype(float)
        phi = np.angle(rs - 1.)
        self.phi = phi
        self.bz = bz
        if self.phase_state:
            print(phi)
        else:
            print(bz)

    def handlePhaseToggled(self,state):
        phase_state = state
        self.phase_state = state
        
    def handleIntToggled(self,state):
        intensity_state = state
        self.intensity_state = state
        
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
