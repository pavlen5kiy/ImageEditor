import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageEnhance

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui_file import Ui_MainWindow


class ImageEditor(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())

        Path("/Users/pavelvolkov/ImageEditor").mkdir(parents=True,
                                                     exist_ok=True)

        # Opening an image
        self.open_image()
        self.backing_up = False

        # Info window
        self.alert = QMainWindow()
        self.alert.setWindowTitle('Before you start')
        self.alert.setFixedSize(300, 210)
        self.alert.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.iconLabel = QLabel(self.alert)
        self.iconLabel.setPixmap(
            QPixmap('78.png').scaled(100, 100, Qt.KeepAspectRatio))
        self.iconLabel.setAlignment(Qt.AlignCenter)
        self.iconLabel.setGeometry(100, 0, 100, 100)

        self.textLabel = QLabel(self.alert)
        self.textLabel.setText(
            'Image Editor 7.8\nby pav1en5kiy\n\nREMEMBER!\nThis app uses '
            'complicated algorithms, '
            ' so you should wait before some operations complete.')
        self.textLabel.setWordWrap(
            True)
        self.textLabel.setOpenExternalLinks(True)
        self.textLabel.setAlignment(Qt.AlignCenter)
        self.textLabel.setGeometry(0, 100, 300,
                                   100)
        self.alert.show()

        # Sliders
        self.horizontalSlider.hide()  # just keeps everything in right place

        self.rChange.sliderReleased.connect(self.rchange)
        self.rChange.valueChanged.connect(
            lambda x: self.rValue.setValue(self.rChange.value()))

        self.gChange.sliderReleased.connect(self.gchange)
        self.gChange.valueChanged.connect(
            lambda x: self.gValue.setValue(self.gChange.value()))

        self.bChange.sliderReleased.connect(self.bchange)
        self.bChange.valueChanged.connect(
            lambda x: self.bValue.setValue(self.bChange.value()))

        self.aChange.sliderReleased.connect(self.achange)
        self.aChange.valueChanged.connect(
            lambda x: self.aValue.setValue(self.aChange.value()))

        # Function buttons
        self.resetButton.clicked.connect(self.reset)
        self.saveButton.clicked.connect(self.save_image)
        self.openButton.clicked.connect(self.open_image)

        # Transform buttons
        self.rotateButton.clicked.connect(self.rotate)
        self.mirrorButton.clicked.connect(self.mirror)

        # Effect buttons
        self.grayscaleButton.clicked.connect(self.grayscale)
        self.negativeButton.clicked.connect(self.negative)
        self.rgbToBgrButton.clicked.connect(self.rgb_to_bgr)
        self.blurButton.clicked.connect(self.blur)
        self.quantizeButton.clicked.connect(self.quantize)
        self.colorAdjustButton.clicked.connect(self.color_adjust)
        self.grayscaleButton.clicked.connect(self.grayscale)
        self.contrastButton.clicked.connect(self.contrast)
        self.brightnessButton.clicked.connect(self.brightness)
        self.sharpnessButton.clicked.connect(self.sharpness)

    def keyPressEvent(self, event):

        # Original image view
        if int(event.modifiers()) == (
                QtCore.Qt.ControlModifier + QtCore.Qt.AltModifier):
            if event.key() == QtCore.Qt.Key_O:
                self.origView = QMainWindow()
                self.origView.setWindowTitle('Original image')
                self.origView.setFixedSize(self.orig_image.width(),
                                           self.orig_image.height())

                self.imView = QLabel(self.origView)
                self.imView.resize(self.orig_image.width(),
                                   self.orig_image.height())
                self.imView.move(0, 0)
                self.imView.setPixmap(QPixmap(self.orig_image))

                self.origView.show()

        # Current image view
        if int(event.modifiers()) == (
                QtCore.Qt.ControlModifier + QtCore.Qt.AltModifier):
            if event.key() == QtCore.Qt.Key_C:
                self.currView = QMainWindow()
                self.currView.setWindowTitle('Current image')
                self.currView.setFixedSize(self.curr_image.width(),
                                           self.curr_image.height())

                self.imView = QLabel(self.currView)
                self.imView.resize(self.curr_image.width(),
                                   self.curr_image.height())
                self.imView.move(0, 0)
                self.imView.setPixmap(QPixmap(self.curr_image))

                self.currView.show()

        # Undo
        if int(event.modifiers()) == (QtCore.Qt.ControlModifier):
            if event.key() == QtCore.Qt.Key_Z:
                if -len(self.imBackup) < self.current <= -1:
                    self.current -= 1
                    self.curr_image = self.imBackup[self.current][0].copy()
                    self.backing_up = True
                    self.rChange.setValue(self.imBackup[self.current][1])
                    self.gChange.setValue(self.imBackup[self.current][2])
                    self.bChange.setValue(self.imBackup[self.current][3])
                    self.aChange.setValue(self.imBackup[self.current][4])
                    self.backing_up = False
                    self.pixmap = QPixmap(self.curr_image)
                    self.imageView.setPixmap(self.pixmap)

                    self.statusbar.showMessage('Undo')

        # Redo
        if int(event.modifiers()) == (QtCore.Qt.ControlModifier):
            if event.key() == QtCore.Qt.Key_Y:
                if (-len(self.imBackup) <= self.current < -1):
                    self.current += 1
                    self.curr_image = self.imBackup[self.current][0].copy()
                    self.backing_up = True
                    self.rChange.setValue(self.imBackup[self.current][1])
                    self.gChange.setValue(self.imBackup[self.current][2])
                    self.bChange.setValue(self.imBackup[self.current][3])
                    self.aChange.setValue(self.imBackup[self.current][4])
                    self.backing_up = False
                    self.pixmap = QPixmap(self.curr_image)
                    self.imageView.setPixmap(self.pixmap)

                    self.statusbar.showMessage('Redo')

    def open_image(self):
        '''Opens an image'''

        self.fname = QFileDialog.getOpenFileName(
            self, 'Choose a file', '',
            'Image (*.jpg);;Image (*.png);;Image (*.jpeg);;Image (*.bmp);;All files (*)')[
            0]

        # Saving original image's size
        self.orig_image = QImage(self.fname).convertToFormat(
            QImage.Format_ARGB32)

        self.orig_x = self.orig_image.width()
        self.orig_y = self.orig_image.height()

        # Saving scaled image's size
        self.orig_image = QImage(self.fname).scaled(720, 720,
                                                    QtCore.Qt.KeepAspectRatio)
        self.res_x = self.orig_image.width()
        self.res_y = self.orig_image.height()

        self.curr_image = self.orig_image.copy()
        self.pixmap = QPixmap(self.curr_image)
        self.imageView.setPixmap(self.pixmap)

        self.statusbar.showMessage(f'New image opened; '
                                   f'original size: {self.orig_x}x'
                                   f'{self.orig_y}; '
                                   f'resized to {self.res_x}x{self.res_y}')

        # Saving original color channels
        self.mainR = []
        self.mainG = []
        self.mainB = []
        self.mainA = []
        for y in range(self.curr_image.height()):
            self.mainR.append([])
            self.mainG.append([])
            self.mainB.append([])
            self.mainA.append([])
            for x in range(self.curr_image.width()):
                r, g, b, a = QColor(self.curr_image.pixel(x, y)).getRgb()
                self.mainR[y].append(r)
                self.mainG[y].append(g)
                self.mainB[y].append(b)
                self.mainA[y].append(a)

        # Backing up for undoing and redoing
        self.imBackup = [(self.orig_image.copy(),
                          self.rChange.value(),
                          self.gChange.value(),
                          self.bChange.value(),
                          self.aChange.value())]
        self.current = -1

    def reset(self):
        '''Discards all changes'''

        # Alert
        self.msgBox = QMessageBox(self)
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setText('Do you want to discard changes?')
        self.msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        res = self.msgBox.exec_()

        if res == QMessageBox.Yes:
            # Reset channel sliders
            self.rChange.setMaximum(100)
            self.gChange.setMaximum(100)
            self.bChange.setMaximum(100)
            self.aChange.setMaximum(100)

            self.rChange.setMinimum(0)
            self.gChange.setMinimum(0)
            self.bChange.setMinimum(0)
            self.aChange.setMinimum(0)

            self.rChange.setValue(100)
            self.gChange.setValue(100)
            self.bChange.setValue(100)
            self.aChange.setValue(100)

            self.rValue.setValue(100)
            self.gValue.setValue(100)
            self.bValue.setValue(100)
            self.aValue.setValue(100)

            self.curr_image = self.orig_image.copy().convertToFormat(
                QImage.Format_ARGB32)
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            # Backing up for undoing and redoing
            self.imBackup = [[self.orig_image.copy(),
                              self.rChange.value(),
                              self.gChange.value(),
                              self.bChange.value(),
                              self.aChange.value()]]
            self.current = -1

            self.statusbar.showMessage('All changes discarded')

    def save_image(self):
        '''Saves image with given filename'''

        filename, ok_pressed = QInputDialog.getText(self, 'Save image',
                                                    'Enter file name '
                                                    '(with format):')

        if ok_pressed:
            self.curr_image.save(f'/Users/pavelvolkov/ImageEditor/{filename}')

            self.statusbar.showMessage(f'Image saved as "{filename}"')

    def history(self):
        '''Backup'''
        self.imBackup = (self.imBackup[:self.current] +
                         [self.imBackup[self.current]])
        self.current = -1
        self.imBackup.append([self.curr_image.copy(),
                              self.rChange.value(),
                              self.gChange.value(),
                              self.bChange.value(),
                              self.aChange.value()])

    def rotate(self):
        '''Opens rotation directions dialog'''

        direction, ok_pressed = QInputDialog.getItem(self,
                                                     'Rotate',
                                                     'Choose direction:',
                                                     ('Left', 'Right'),
                                                     1,
                                                     False)

        if ok_pressed:
            if direction == 'Left':
                self.left()
            else:
                self.right()

    def left(self):
        '''Rotates image left by given degree'''

        degree, ok_pressed = QInputDialog.getInt(self, 'Rotate left',
                                                 'Enter rotation degree:',
                                                 90, 0, 360, 90)

        if ok_pressed:
            # QTransform
            self.transf = QTransform()
            self.transf.rotate(-degree)

            self.curr_image = self.curr_image.transformed(self.transf)
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(f'Image rotated {degree}° to the left')

            self.history()

    def right(self):
        '''Rotates image right by given degree'''

        degree, ok_pressed = QInputDialog.getInt(self, 'Rotate right',
                                                 'Enter rotation degree:',
                                                 90, 0, 360, 90)

        if ok_pressed:
            # QTransform
            self.transf = QTransform()
            self.transf.rotate(degree)

            self.curr_image = self.curr_image.transformed(self.transf)
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(f'Image rotated {degree}° to the right')

            self.history()

    def mirror(self):
        '''Opens mirror types dialog'''

        direction, ok_pressed = QInputDialog.getItem(self, 'Rotate',
                                                     'Choose mirror type:',
                                                     ('Vertically',
                                                      'Horizontally'), 0,
                                                     False)

        if ok_pressed:
            if direction == 'Vertically':
                self.y_flip()
            else:
                self.x_flip()

    def y_flip(self):
        '''Mirrors image vertically'''

        self.curr_image = self.curr_image.mirrored(True, False)
        self.pixmap = QPixmap(self.curr_image)
        self.imageView.setPixmap(
            self.pixmap.scaled(720, 720, QtCore.Qt.KeepAspectRatio))

        self.statusbar.showMessage('Image mirrored vertically')

        self.history()

    def x_flip(self):
        '''Mirrors image horizontally'''

        self.curr_image = self.curr_image.mirrored(False, True)
        self.pixmap = QPixmap(self.curr_image)
        self.imageView.setPixmap(
            self.pixmap.scaled(720, 720, QtCore.Qt.KeepAspectRatio))

        self.statusbar.showMessage('Image mirrored horizontally')

        self.history()

    def grayscale(self):
        '''Turns image into grayscale'''

        self.curr_image.save('curr_image.png')
        im = Image.open('curr_image.png')

        enhancer = ImageEnhance.Color(im)
        enhancer.enhance(0).save('curr_image.png')

        self.curr_image = QImage('curr_image.png')
        self.pixmap = QPixmap(self.curr_image)
        self.imageView.setPixmap(
            self.pixmap.scaled(720, 720, QtCore.Qt.KeepAspectRatio))

        self.statusbar.showMessage('Grayscale applied')

        self.history()

    def negative(self):
        '''Turns image into negative'''

        self.curr_image.invertPixels()

        self.pixmap = QPixmap(self.curr_image)
        self.imageView.setPixmap(
            self.pixmap.scaled(720, 720, QtCore.Qt.KeepAspectRatio))

        self.statusbar.showMessage('Negative applied')

        self.history()

    def rgb_to_bgr(self):
        '''Swaps R channel with B channel'''

        self.curr_image = self.curr_image.rgbSwapped()

        self.pixmap = QPixmap(self.curr_image)
        self.imageView.setPixmap(
            self.pixmap.scaled(720, 720, QtCore.Qt.KeepAspectRatio))

        self.statusbar.showMessage('RGB to BGR applied')

        self.history()

    def rchange(self):
        '''Changes R channel percentage'''

        if not self.backing_up:

            # Disable function buttons to avoid interface issues
            self.resetButton.setEnabled(False)
            self.openButton.setEnabled(False)
            self.saveButton.setEnabled(False)

            for y in range(self.curr_image.height()):
                for x in range(self.curr_image.width()):
                    r, g, b, a = QColor(
                        self.curr_image.pixel(x, y)).getRgb()
                    r = int(self.mainR[y][x] * self.rChange.value() / 100)
                    self.curr_image.setPixel(x, y,
                                             QColor(r, g, b, a).rgb())

            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            # Enable
            self.resetButton.setEnabled(True)
            self.openButton.setEnabled(True)
            self.saveButton.setEnabled(True)

            self.statusbar.showMessage(f'R channel set to '
                                       f'{self.rChange.value()}%')

            self.history()

        return

    def gchange(self):
        '''Changes G channel percentage'''

        if not self.backing_up:

            # Disable function buttons to avoid interface issues
            self.resetButton.setEnabled(False)
            self.openButton.setEnabled(False)
            self.saveButton.setEnabled(False)

            for y in range(self.curr_image.height()):
                for x in range(self.curr_image.width()):
                    r, g, b, a = QColor(
                        self.curr_image.pixel(x, y)).getRgb()
                    g = int(self.mainG[y][x] * self.gChange.value() / 100)
                    self.curr_image.setPixel(x, y,
                                             QColor(r, g, b, a).rgb())

            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            # Enable
            self.resetButton.setEnabled(True)
            self.openButton.setEnabled(True)
            self.saveButton.setEnabled(True)

            self.statusbar.showMessage(f'G channel set to '
                                       f'{self.gChange.value()}%')

            self.history()

        return

    def bchange(self):
        '''Changes B channel percentage'''

        if not self.backing_up:

            # Disable function buttons to avoid interface issues
            self.resetButton.setEnabled(False)
            self.openButton.setEnabled(False)
            self.saveButton.setEnabled(False)

            for y in range(self.curr_image.height()):
                for x in range(self.curr_image.width()):
                    r, g, b, a = QColor(
                        self.curr_image.pixel(x, y)).getRgb()
                    b = int(self.mainB[y][x] * self.bChange.value() / 100)
                    self.curr_image.setPixel(x, y,
                                             QColor(r, g, b, a).rgb())

            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            # Enable
            self.resetButton.setEnabled(True)
            self.openButton.setEnabled(True)
            self.saveButton.setEnabled(True)

            self.statusbar.showMessage(f'B channel set to '
                                       f'{self.bChange.value()}%')

            self.history()

        return

    def achange(self):
        '''Changes Alpha channel percentage'''

        if not self.backing_up:
            self.curr_image = self.curr_image.convertToFormat(
                QImage.Format_ARGB32)

            # Disable function buttons to avoid interface issues
            self.resetButton.setEnabled(False)
            self.openButton.setEnabled(False)
            self.saveButton.setEnabled(False)

            for y in range(self.curr_image.height()):
                for x in range(self.curr_image.width()):
                    r, g, b, a = QColor(
                        self.curr_image.pixel(x, y)).getRgb()
                    a = int(self.mainA[y][x] * self.aChange.value() / 100)
                    self.curr_image.setPixel(x, y,
                                             QColor(r, g, b, a).rgba())

            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            # Enable
            self.resetButton.setEnabled(True)
            self.openButton.setEnabled(True)
            self.saveButton.setEnabled(True)

            self.statusbar.showMessage(f'Alpha channel set to '
                                       f'{self.aChange.value()}%')

            self.history()

        return

    def blur(self):
        '''Blurs image by given radius'''

        radius, ok_pressed = QInputDialog.getInt(self, 'Gaussian blur',
                                                 'Enter blur radius:',
                                                 5, 1)

        if ok_pressed:
            self.curr_image.save('curr_image.png')
            im = Image.open('curr_image.png')

            im2 = im.filter(ImageFilter.GaussianBlur(radius=radius))
            im2.save('curr_image.png')

            self.curr_image = QImage('curr_image.png').scaled(720, 720,
                                                              QtCore.Qt.KeepAspectRatio)
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(f'Blur applied with radius={radius}')

            self.history()

    def quantize(self):
        '''Quantizes image by given colors'''

        colors, ok_pressed = QInputDialog.getInt(self, 'Quantize',
                                                 'Enter quantize:',
                                                 16, 1, max=255)

        if ok_pressed:
            self.curr_image.save('curr_image.png')
            im = Image.open('curr_image.png')

            im2 = im.quantize(colors)
            im2.save('curr_image.bmp')
            self.curr_image = QImage('curr_image.bmp')

            self.curr_image = self.curr_image.convertToFormat(
                QImage.Format_ARGB32).scaled(720, 720,
                                             QtCore.Qt.KeepAspectRatio)
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(
                f'Quantize applied with colors={colors}')

            self.history()

    def color_adjust(self):
        '''Adjusts image color by given factor'''

        adjust, ok_pressed = QInputDialog.getDouble(self, 'Color adjust',
                                                    'Enter adjust factor:',
                                                    1.0, 0.0, decimals=1)

        if ok_pressed:
            self.curr_image.save('curr_image.png')
            im = Image.open('curr_image.png')

            enhancer = ImageEnhance.Color(im)
            enhancer.enhance(adjust).save('curr_image.png')

            self.curr_image = QImage('curr_image.png').scaled(720, 720,
                                                              QtCore.Qt.KeepAspectRatio)
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(f'Color adjusted with factor={adjust}')

            self.history()

    def contrast(self):
        '''Adjusts image contrast by given factor'''

        adjust, ok_pressed = QInputDialog.getDouble(self, 'Contrast',
                                                    'Enter contrast factor:',
                                                    1.0, 0.0, decimals=1)

        if ok_pressed:
            self.curr_image.save('curr_image.png')
            im = Image.open('curr_image.png')

            enhancer = ImageEnhance.Contrast(im)
            enhancer.enhance(adjust).save('curr_image.png')

            self.curr_image = QImage('curr_image.png')
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(
                f'Contrast adjusted with factor={adjust}')

            self.history()

    def brightness(self):
        '''Adjusts image brightness by given factor'''

        adjust, ok_pressed = QInputDialog.getDouble(self, 'Brightness',
                                                    'Enter brightness factor:',
                                                    1.0, 0.0, decimals=1)

        if ok_pressed:
            self.curr_image.save('curr_image.png')
            im = Image.open('curr_image.png')

            enhancer = ImageEnhance.Brightness(im)
            enhancer.enhance(adjust).save('curr_image.png')

            self.curr_image = QImage('curr_image.png')
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(
                f'Brightness adjusted with factor={adjust}')

            self.history()

    def sharpness(self):
        '''Adjusts image sharpness by given factor'''

        adjust, ok_pressed = QInputDialog.getDouble(self, 'Sharpness',
                                                    'Enter sharpness factor:',
                                                    1.0, 0.0, decimals=1)

        if ok_pressed:
            self.curr_image.save('curr_image.png')
            im = Image.open('curr_image.png')

            enhancer = ImageEnhance.Sharpness(im)
            enhancer.enhance(adjust).save('curr_image.png')

            self.curr_image = QImage('curr_image.png')
            self.pixmap = QPixmap(self.curr_image)
            self.imageView.setPixmap(self.pixmap)

            self.statusbar.showMessage(
                f'Sharpness adjusted with factor={adjust}')

            self.history()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageEditor()
    ex.show()
    sys.exit(app.exec_())
