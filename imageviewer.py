#coding=utf-8
#!/usr/bin/env python3


import sys
import time
import os
from os import walk
from xml.dom.minidom import Document
from PyQt4 import QtCore, QtGui


class TimeoutThread(QtCore.QThread):

    def __init__(self, t, f, *args, **kwargs):
        super(TimeoutThread, self).__init__()
        self.t, self.f, self.args, self.kwargs = t, f, args, kwargs
        self.start()

    def run(self):
        time.sleep(self.t)
        self.f(*self.args, **self.kwargs)

class MyLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super(MyLabel, self).__init__(parent)
        self.Drawed = False
        self.linePos = []
        self.myPenColor = QtGui.QColor(0, 255, 0)
        self.myPenWidth = 3
        self.myPenHeight = 30
        self.setMouseTracking(True)
        self.track = False
        self.curScale = 1.0
        self.finalPos = []


    def paintEvent(self, event):
        QtGui.QLabel.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        if self.Drawed:
            painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth))
            for lp, ep in self.finalPos:
                curLP = QtCore.QPoint(lp.x()*self.curScale, lp.y()*self.curScale)
                curEP = QtCore.QPoint(ep.x()*self.curScale, ep.y()*self.curScale)
                painter.drawLine(curLP, curEP)
        if self.track:
            painter.setPen(QtGui.QPen(self.myPenColor, 1))
            painter.drawLine(0, self.trackPos.y(), self.width(), self.trackPos.y())
            painter.drawLine(self.trackPos.x(), 0, self.trackPos.x(), self.height())


    def mousePressEvent(self, event):
    	# self.lastPoint = event.pos()
        # self.track = True
        pass

    def mouseMoveEvent(self, event):
        self.track = True
        self.trackPos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.endPoint = event.pos()
            self.lastPoint = QtCore.QPoint(self.endPoint.x(), self.endPoint.y()-self.myPenHeight)
            self.linePos.append([self.lastPoint, self.endPoint])
            finalLP = QtCore.QPoint(self.lastPoint.x()/self.curScale, self.lastPoint.y()/self.curScale)
            finalEP = QtCore.QPoint(self.endPoint.x()/self.curScale, self.endPoint.y()/self.curScale)
            self.finalPos.append([finalLP, finalEP])
            self.update()
            self.Drawed = True

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def penColor(self):
        return self.myPenColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def penWidth(self):
        return self.myPenWidth

    def setPenHeight(self, newHeight):
        self.myPenHeight = newHeight

    def penHeight(self):
        return self.myPenHeight

    def setScale(self, scale):
        self.curScale = scale

class ImageViewer(QtGui.QWidget):

    def __init__(
            self,
            parent=None,
            image=None,
            scale=1.0,
            horizontal_position=0.5,
            vertical_position=0.5):
        super(ImageViewer, self).__init__(parent)
        self.setMinimumSize(180, 100)

        # self.imageLabel = QtGui.QLabel()
        self.imageLabel = MyLabel()
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidget(self.imageLabel)

        self.zoom_out_btn = QtGui.QPushButton('-', self)
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        self.zoom_in_btn = QtGui.QPushButton('+', self)
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        self.next_btn = QtGui.QPushButton('Next', self)
        self.next_btn.setFixedSize(40, 30)
        self.next_btn.clicked.connect(parent.nextImage)

        self.textbox = QtGui.QLineEdit(self)
        self.textbox.resize(1000, 50)

        self.layout = QtGui.QVBoxLayout()
        self.hlayout = QtGui.QHBoxLayout()
        self.vlayout = QtGui.QVBoxLayout()
        self.hlayout.addWidget(self.scrollArea)
        self.vlayout.addWidget(self.zoom_out_btn)
        self.vlayout.addWidget(self.zoom_in_btn)
        self.vlayout.addWidget(self.next_btn)
        self.hlayout.addLayout(self.vlayout)
        self.layout.addLayout(self.hlayout)
        self.layout.addWidget(self.textbox)
        self.setLayout(self.layout)

        self.passImage = []

        self.configure(image, scale, horizontal_position, vertical_position)

        self.t = TimeoutThread(
            0.1,
            self.configure_positions,
            self.horizontal_position,
            self.vertical_position)

    def configure(
            self,
            image=None,
            scale=1.0,
            horizontal_position=0.5,
            vertical_position=0.5):
        self.configure_image(image)
        self.configure_scale(scale)
        self.configure_positions(horizontal_position, vertical_position)
        self.imageLabel.linePos = []
        self.imageLabel.finalPos = []

    def configure_image(self, image=None):
        self.image = image
        if self.image:
            self.pixmap = QtGui.QPixmap(image)
            self.imageLabel.setPixmap(self.pixmap)
            self.imageLabel.adjustSize()

    def configure_scale(self, scale=1.0):
        self.scale = scale
        self.imageLabel.setScale(scale)
        if self.image:
            self.imageLabel.resize(
                self.scale *
                self.imageLabel.pixmap().size())

    def configure_positions(
            self,
            horizontal_position=0.5,
            vertical_position=0.5):
        self.horizontal_position = horizontal_position
        self.vertical_position = vertical_position

        scroll_bar = self.scrollArea.horizontalScrollBar()
        scroll_bar.setValue(
            self.horizontal_position *
            self.imageLabel.width() -
            scroll_bar.pageStep() /
            2)

        scroll_bar = self.scrollArea.verticalScrollBar()
        scroll_bar.setValue(
            self.vertical_position *
            self.imageLabel.height() -
            scroll_bar.pageStep() /
            2)

    def save(self, filename):
        print('saved')
        painter = QtGui.QPainter(self.pixmap)
        painter.setPen(QtGui.QPen(self.imageLabel.myPenColor, self.imageLabel.myPenWidth))
        if len(self.imageLabel.finalPos) != 0:
            for lp, ep in self.imageLabel.finalPos:
                painter.drawLine(lp, ep)
        self.pixmap.save(filename, QtCore.QByteArray(str(filename.split('.')[-1])))
        xmlName = filename.split('/')[-1].split('.')[0]+'.xml'
        if self.textbox.text():
            doc = Document()
            info = doc.createElement('info')
            doc.appendChild(info)
            if len(self.imageLabel.finalPos) != 0:
                for lp, ep in self.imageLabel.finalPos:
                    coord = doc.createElement('coord')
                    strCoord = str(lp.x())+','+str(lp.y())+','+str(ep.x())+','+str(ep.y())
                    coord.appendChild(doc.createTextNode(strCoord))
                    info.appendChild(coord)
                label = doc.createElement('label')
                label.appendChild(doc.createTextNode(unicode(self.textbox.text())))
                info.appendChild(label)
            if not os.path.exists('result'):
                os.makedirs('result')
            with open('result/' + xmlName, 'w') as f:
                f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))
            self.textbox.setText('')

        self.imageLabel.linePos = []
        self.imageLabel.finalPos = []

    def zoom_out(self):
        if self.image:
            self.remember_positions()
            self.configure_scale(0.5 * self.scale)
            self.configure_positions(
                self.horizontal_position,
                self.vertical_position)

    def zoom_in(self):
        if self.image:
            self.remember_positions()
            self.configure_scale(2 * self.scale)
            self.configure_positions(
                self.horizontal_position,
                self.vertical_position)



    def remember_positions(self):
        scroll_bar = self.scrollArea.horizontalScrollBar()
        self.horizontal_position = (
            scroll_bar.value() + scroll_bar.pageStep() / 2.0) / self.imageLabel.width()

        scroll_bar = self.scrollArea.verticalScrollBar()
        self.vertical_position = (
            scroll_bar.value() + scroll_bar.pageStep() / 2.0) / self.imageLabel.height()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_1:
            if len(self.imageLabel.linePos) != 0:
                self.imageLabel.linePos.pop()
                self.imageLabel.finalPos.pop()
                self.imageLabel.update()




from queue import *

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.imageViewer = ImageViewer(self, None)
        self.imageViewer.mainWindow = self
        self.setCentralWidget(self.imageViewer)

        self.createActions()
        self.createMenus()
        self.imgQueue = Queue()

    def createMenus(self):
        fileMenu = QtGui.QMenu("&File", self)
        fileMenu.addAction(self.openAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QtGui.QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addAction(self.penHeightAct)
        optionMenu.addSeparator()

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
            triggered=self.open)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
            triggered=self.close)

        self.penColorAct = QtGui.QAction("&Pen Color...", self,
            triggered=self.penColor)

        self.penWidthAct = QtGui.QAction("Pen &Width...", self,
            triggered=self.penWidth)

        self.penHeightAct = QtGui.QAction("Pen &Height...", self,
                                         triggered=self.penHeight)


    def open(self):
        fileName = str(QtGui.QFileDialog.getOpenFileName(self, "Open File",
            QtCore.QDir.currentPath()))
        if fileName:
            while self.imgQueue.empty() == False:
                self.imgQueue.get()
            self.imageViewer.configure(fileName)
            splitDir = fileName.split('/')
            self.imgDir = ''
            for i in range(len(splitDir) - 1):
                self.imgDir += splitDir[i] + '/'
            for (dirpath, dirname, filename) in walk(self.imgDir):
                for file in filename:
                    ext = file.split('.')[-1].lower()
                    if (ext == 'jpg' or ext == 'png' or ext == 'jpeg' or ext == 'bmp')\
                            and str(file) != splitDir[-1]:
                        self.imgQueue.put(file)
                break
            self.curfile = splitDir[-1]

    def close(self):
        QtCore.QCoreApplication.instance().quit()

    def penColor(self):
        newColor = QtGui.QColorDialog.getColor(self.imageViewer.imageLabel
                                               .penColor())
        if newColor.isValid():
            self.imageViewer.imageLabel.setPenColor(newColor)

    def penWidth(self):
        newWidth, ok = QtGui.QInputDialog.getInteger(self, "ImageViewer",
            "Select pen width:", self.imageViewer.imageLabel.penWidth(), 1, 50, 1)
        if ok:
            self.imageViewer.imageLabel.setPenWidth(newWidth)

    def penHeight(self):
        newHeight, ok = QtGui.QInputDialog.getInteger(self, "ImageViewer",
            "Select pen height:", self.imageViewer.imageLabel.penHeight(), 1, 50,1)
        if ok:
            self.imageViewer.imageLabel.setPenHeight(newHeight)

    def nextImage(self):
        self.imageViewer.save(self.imgDir+self.curfile)
        self.imgQueue.put(self.curfile)
        self.curfile = self.imgQueue.get()
        self.imageViewer.configure(self.imgDir+self.curfile)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.resize(500, 500)
    win.show()
    sys.exit(app.exec_())

