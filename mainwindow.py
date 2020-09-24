import sys
import cv2
import numpy as np
import pyautogui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox, QHBoxLayout, QMainWindow, QPushButton, QStylePainter, QApplication, QVBoxLayout, QWidget, QGridLayout, QCheckBox
from threading import Thread
import pyautogui
import os

# Edit your comp below (Keep champion names in lower case)
comps = {
    "Chosen Brawlers": ["maokai", "tahm kench", "sylas", "vi", "nunu", "ashe", "warwick", "sett"],
    "Chosen Sharpshooters": ["nidalee", "vayne", "teemo", "jinx", "aatrox", "cassiopeia", "jhin", "sejuani", "zilean"],
    "Elderwood Brawlers": ["maokai", "lulu", "nunu", "lux", "ashe", "warwick", "ezreal", "sett"],
    "Chosen Cultists": ["elise", "twisted fate", "pyke", "kalista", "evelynn", "aatrox", "jhin", "zilean"],
    "Chosen Dusks": ["vayne", "thresh", "aatrox", "cassiopeia", "jhin", "riven", "lillia", "zilean"],
    "Dusk Cultists": ["elise", "pyke", "kalista", "aatrox", "cassiopeia", "jhin", "riven", "zilean"],
    "Spirit Vanguards": ["thresh", "yuumi", "aatrox", "ahri", "cassiopeia", "sejuani", "shen", "zilean"],
    "Moonlight Assassins": ["lissandra", "diana", "pyke", "sylas", "akali", "katarina", "talon"],
    "Cultist Shades": ["zed", "pyke", "kalista", "evelynn", "aatrox", "jhin", "kayn", "zilean"],
    "Spirit Shades": ["janna", "teemo", "zed", "evelynn", "kindred", "yuumi", "ahri", "kayn"],
    "Chosen Duelists": ["fiora", "yasuo", "jax", "kalista", "janna", "shen", "lee sin", "yone"],
    "Chosen Warlords": ["garen", "nidalee", "jarvan", "pyke", "vi", "katarina", "xin zhao", "azir"],
    "Enlightened Assassins": ["fiora", "nami", "janna", "pyke", "irelia", "morgana", "shen", "talon"],
    "Keeper Sharpshooters": ["nidalee", "vayne", "jarvan", "jinx", "kennen", "jhin", "riven", "azir"],
    "Dusk Mages": ["hecarim", "lulu", "thresh", "veigar", "yuumi", "cassiopeia", "riven", "lillia"],
    "Moonlight Hunters": ["lissandra", "aphelios", "sylas", "kindred", "yuumi", "ashe", "cassiopeia", "warwick"],
    "Divine Vanguards": ["wukong", "garen", "janna", "irelia", "lux", "aatrox", "sejuani", "shen"]
}

# Storing champion images in champ_cards dictionary
champ_cards = dict()
cwd = os.getcwd()
for champ in os.listdir(".\champ_cards"):
    if champ.endswith(".png"):
        champ_cards[champ[:-4]] = cv2.imread(cwd + f"\\champ_cards\\{champ}", 0)

def crop_ss(selectedComps):
    # cv2.matchTemplate documentation:
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html
    # 
    # Taking screenshot and matching champion images from user selected comp to the screenshot

    while True:
        try:
            img_rgb = pyautogui.screenshot()
            break
        except:
            raise Exception("OSError: screen grab failed")

    img_gray = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_BGR2GRAY)

    lst = np.array([])

    for comp in selectedComps:
        for champ in comps[comp]:
            template = champ_cards[champ]
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

            # Lower threshold variable value if the program gets false negatives
            # Increase threshold variable value if the program gets false positives
            threshold = 0.75
            
            loc = np.where(res >= threshold)
            lst = np.concatenate([lst, loc[1]])
    return lst

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selectedComps = list()
        self.setWindowTitle('TFT Overlay v1.0 by junschoi')
        self.setGeometry(1600,30,0,0)
        self.setupWidgets()
    
    def setupWidgets(self):
        self.thread = QThread()
        self.thread.start()
        
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        
        self.centralWidget = QWidget(self)
        
        self.CBdict = dict()
        grid = QGridLayout()
        
        row = 0
        column = 0
        for comp in list(comps.keys()):
            self.CBdict[comp] = QCheckBox(comp) # Each comp in comps is QCheckBox
            grid.addWidget(self.CBdict[comp], row, column) # Add each comp QCheckBox to grid
            self.CBdict[comp].clicked.connect(lambda _, cb=self.CBdict[comp]: self.CBClicked(cb=cb))
            row += 1
            if row % 12 == 0:
                column += 1
                row = 0
        
        self.startButton = QPushButton("Start")
        self.stopButton = QPushButton("Stop")
        self.stopButton.setEnabled(False)
        self.startButton.clicked.connect(self.startThread)
        self.stopButton.clicked.connect(self.stopThread)
        mainLayout = QVBoxLayout(self.centralWidget)
        startStopLayout = QHBoxLayout()
        startStopLayout.addWidget(self.startButton)
        startStopLayout.addWidget(self.stopButton)
        mainLayout.addLayout(grid)
        mainLayout.addLayout(startStopLayout)
        self.setCentralWidget(self.centralWidget)
        self.show()

    def CBClicked(self, cb):
        if cb.isChecked():
            self.selectedComps.append(cb.text())
        else:
            self.selectedComps.remove(cb.text())
        self.t3 = Thread(target = self.worker.reload_comps, args=(self.selectedComps,))
        self.t3.start()
    
    def startThread(self):
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.t1 = Thread(target = self.worker.run)
        self.t1.start()
    
    def stopThread(self):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.t2 = Thread(target = self.worker.stop)
        self.t2.start()
        self.thread.quit()
        self.thread.wait()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message", "Are you sure to quit?")
        if reply == QMessageBox.Yes:
            self.t2 = Thread(target = self.worker.stop)
            self.t2.start()
            event.accept()
        else:
            event.ignore()


class Worker(QThread):
    active = pyqtSignal(object)

    def __init__(self):
        super(Worker, self).__init__()
        self.selectedComps = list()
        self._sleep = False
    
    def reload_comps(self, selectedComps):
        self.selectedComps = selectedComps
    
    @pyqtSlot()
    def run(self):
        self.running = True
        while self.running:
            lst = crop_ss(self.selectedComps)
            QThread.msleep(100)
            self.active.emit(lst)
    
    def stop(self):
        self.running = False


class Mask(QMainWindow):
    def __init__(self, box):
        super().__init__()
        self.resize(500,500)
        self.box = box

    def paintEvent(self, event=None):
        painter = QStylePainter()
        painter.begin(self)
        painter.setOpacity(0.4)
        painter.setBrush(Qt.green)
        painter.drawRect(self.rect())
        self.setGeometry(self.box[0], self.box[1], self.box[2]-self.box[0], self.box[3]-self.box[1])
    
    def mousePressEvent(self, event):
        self.close()

class Controller:
    def __init__(self):
        self.Show_MainWindow()

    def Show_MainWindow(self):
        self.box1 = [479, 1038, 672, 1071] # 927 / 1038 for y1
        self.box2 = [680, 1038, 873, 1071]
        self.box3 = [881, 1038, 1074, 1071]
        self.box4 = [1082, 1038, 1275, 1071]
        self.box5 = [1283, 1038, 1476, 1071]
        self.ui = MainWindow()
        self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.ui.worker.active.connect(self.run)
        self.ui.show()
        self.ui1 = Mask(self.box1)
        self.ui2 = Mask(self.box2)
        self.ui3 = Mask(self.box3)
        self.ui4 = Mask(self.box4)
        self.ui5 = Mask(self.box5)

    def run(self, lst):
        self.mask1() if any([x for x in lst if x in range(479-5, 479+5)]) else self.ui1.close()
        self.mask2() if any([x for x in lst if x in range(680-5, 680+5)]) else self.ui2.close()
        self.mask3() if any([x for x in lst if x in range(881-5, 881+5)]) else self.ui3.close()
        self.mask4() if any([x for x in lst if x in range(1082-5, 1082+5)]) else self.ui4.close()
        self.mask5() if any([x for x in lst if x in range(1283-5, 1283+5)]) else self.ui5.close()

    # Qt.Tool hides app from taskbar
    # https://www.geeksforgeeks.org/pyqt5-how-to-hide-app-from-taskbar/
    
    def mask1(self):
        self.ui1.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool) 
        self.ui1.setAttribute(Qt.WA_NoSystemBackground, True)
        self.ui1.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui1.show()

    def mask2(self):
        self.ui2.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.ui2.setAttribute(Qt.WA_NoSystemBackground, True)
        self.ui2.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui2.show()
    
    def mask3(self):
        self.ui3.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.ui3.setAttribute(Qt.WA_NoSystemBackground, True)
        self.ui3.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui3.show()
    
    def mask4(self):
        self.ui4.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.ui4.setAttribute(Qt.WA_NoSystemBackground, True)
        self.ui4.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui4.show()
                    
    def mask5(self):
        self.ui5.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.ui5.setAttribute(Qt.WA_NoSystemBackground, True)
        self.ui5.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui5.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())