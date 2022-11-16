# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5.QtCore import *#(pyqtSignal, pyqtSlot, pyqtProperty,
                          #QObject, QThread, QDir, QRect)
from PyQt5.QtWidgets import *#(QFrame, QFileDialog)
from PyQt5.QtGui import *#QPixmap, QImage, QBrush, QPainter

from ROI import *
from ROI import ROI as roi
from rayleighsommerfeld import rayleighsommerfeld
#ROI code from https://raw.githubusercontent.com/martindurant/misc/master/ROI.py

import os, io
import numpy as np
from PIL import Image
from matplotlib import cm
import matplotlib.pyplot as plt
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
        self.displayResultsButton.clicked.connect(self.changeDisp)
        self.getCrop.clicked.connect(self.crop)

        #handle sliders
        self.zmax_slider.valueChanged.connect(self.updateValues)
        self.zmin_slider.valueChanged.connect(self.updateValues)
        self.dz_slider.valueChanged.connect(self.updateValues)
        self.setz_value.valueChanged.connect(self.updateValues)

        #handle checkboxes
        self.phaseCheckbox.toggled.connect(self.handlePhaseToggled)
        self.intensityCheckbox.toggled.connect(self.handleIntToggled)

    def dispImage(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/home/group/data/", "Image files (*.jpg *.png")
        a = cv2.imread(filename, 0)
        h, w = a.shape
        bytesPerLine = w
        qImg = QImage(a.data, w, h, bytesPerLine, QImage.Format_Grayscale8)
        self.qImg = qImg
        image = QPixmap.fromImage(qImg)
        self.labelImage.setPixmap(image.scaled(681, 511))
        self.arr = a

    def updateValues(self):
        zmax = self.zmax_slider.value()
        zmin = self.zmin_slider.value()
        dz = self.dz_slider.value()
        zdisp = self.setz_value.value()
        self.zmax = zmax
        self.zmin = zmin
        self.dz = dz
        self.zdisp = zdisp

    def propagate(self):
        zmin, zmax = self.zmin, self.zmax
        n = int((zmax - zmin)/self.dz)
        mpp = 0.048
        z = np.linspace(zmin, zmax, n)/mpp
        b = self.arr
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

    def changeDisp(self):
        n = int((self.zmax - self.zmin)/self.dz)
        i = (self.zdisp - self.zmin)/(self.zmax - self.zmin)*n
        if self.phase_state:
            arr = self.phi[:,:,int(i)]
        else:
            arr = self.bz[:,:,int(i)]
        filename = 'frame{}.png'.format(self.zdisp)
        cv2.imwrite(filename, arr)
        self.labelImage.setPixmap(QPixmap(filename).scaled(681,511))
        pixmap = QPixmap(filename)
        image = pixmap.toImage()

    def crop(self):
        image = self.qImg
        image.convertToFormat(QImage.Format_ARGB32)
        #crop
        imgsize = min(image.width(), image.height())
        rect = QRect(200, 100, imgsize, imgsize)
        image = image.copy(rect)
        crop_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
        crop_img.fill(Qt.transparent)
        brush = QBrush(image)
        painter = QPainter(crop_img)
        painter.setBrush(brush)
        painter.setPen(Qt.blue)
        painter.drawRect(200,100,imgsize,imgsize)
        painter.end()
        pm = QPixmap.fromImage(crop_img)
        self.labelImage.setPixmap(pm.scaled(681, 511))

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
