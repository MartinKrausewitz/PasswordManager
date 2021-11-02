from encryptdecrypt import encstring, keyfrompas, writetofile, decryptfile
from safepass import safepas
import secrets
import string
import os
from shutil import copy2

import sys

from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QFormLayout, QGroupBox, QLabel, QScrollArea, QVBoxLayout, QMainWindow, QAction, QHBoxLayout, QLineEdit, QInputDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import *






def getlist(key, md , mf): #Mainfile lesen und in Liste teilen
    a = str(decryptfile(md, mf, key), "utf-8")
    a = a.split('#')
    #print("a")
    return a

def getfile(key, md, file): #beliebige Datei lesen
    dec = decryptfile(md, file, key)
    return dec

def bccmain(key, destdir, destfile, data): #Backup für die Mainfile
    genstrin = str(data[0])
    for i in range(1, len(data)):
        genstrin += "#" + data[i]
    mzw = encstring(genstrin, key)
    writetofile(destdir, destfile, mzw[0], mzw[1], mzw[2])


def writefile(key, md, mf, nam, det): #Mainfile erweitern und Datei schreiben
    a = str(decryptfile(md, mf, key), "utf-8")#liste holen
    a = a.split('#')
    fn = ranpath()
    zsp = safepas()
    #Liste erweitern
    a.append(str(nam))
    a.append(str(fn))
    a.append(str(zsp))
    ###!--- Mainfile generieren ---!###
    genstrin = str(a[0])
    for i in range(1, len(a)):
        genstrin += "#" + a[i]

    ###!--- Mainfile schreiben ---!###

    zw = encstring(det, keyfrompas(zsp))
    writetofile(md, str(fn), zw[0], zw[1], zw[2])

    mzw = encstring(genstrin, key)
    writetofile(md, mf, mzw[0], mzw[1], mzw[2])


def removefile(key, md, mf, ind): #Datei löschen und Mainfile bearbeiten
    a = str(decryptfile(md, mf, key), "utf-8")
    a = a.split('#')
    nam = a.pop(ind)
    fn = a.pop(ind)
    a.pop(ind)

    genstrin = str(a[0])
    for i in range(1, len(a)):
        genstrin += "#" + a[i]

    os.remove(os.path.join(md,fn))

    mzw = encstring(genstrin, key)
    writetofile(md, mf, mzw[0], mzw[1], mzw[2])
    return nam



def ranpath(n = 30): # Randompath
    chars = string.digits + string.ascii_letters
    return ''.join(secrets.choice(chars) for _ in range(n))



class PasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mainlayout = QFormLayout()
        self.vstat = -1 # -1 = unüberprüft || 0 = P überprüft || 1 = P benötigt || 2 = nicht initialisiert || 3 = Backup


        # Mainfiles
        self.maindir = 'data'
        self.mainfile = 'maintable'
        self.urmaindir = 'data'

        # Ordner erstellen
        if not os.path.exists(self.maindir):
            os.mkdir(self.maindir)

        if not os.path.exists("bacdir"):
            os.mkdir("bacdir")

        #Passwort Variablen
        self.p = ""
        self.pz = ""
        #Aktionsschritt
        self.step = 0
        #Statusvariablen
        self.vrem = False
        self.inbac = False
        #Mainlist
        self.mainlist = []

        #Label und Buttonlist
        self.paslabellist = []
        self.buttonshowlist = []

        #Initfunktionen
        self.initMess() #Init Messageboxen
        self.initme()   #Init anderes

        self.checkstatus()  #Status setzen
        self.aktion()       #Jeweilige Aktion ausführen
        #self.getpas()
        #self.dellall()
        self.show()         #Anzeigen


    def checkstatus(self):  #Status setzten
        if not os.path.isfile(os.path.join(self.maindir, self.mainfile)):
            self.vstat = 2
        elif self.p == "":
            self.vstat = 1
        elif not self.p == "":
            self.vstat = 0
        else:
            print("Error")

    def holmainlist(self):  #Mainlist holen und '#' austauschen
        if self.p == "":
            return
        self.mainlist = getlist(self.p, self.maindir, self.mainfile)
        if len(self.mainlist) == 1:
            return
        for l in range(0, int((len(self.mainlist)-1)/3)):
            i = l*3+1
            self.mainlist[i] = self.mainlist[i].replace('&?=)(','#')

    def aktion(self):       #Jeweilige Aktion ausführen
        if self.vstat == 0:     #Passwort da und Mainfile existiert hauptphase
            self.holmainlist()
            self.showlist()
        elif self.vstat == 1 and self.step == 0:    #Passwort eingeben Anmeldephase
            self.mainlayout.addRow(QLabel("Passwort eingeben: "))
            self.getpas()
            self.step = 1
        elif self.vstat == 1 and self.step == 1:    #Passwort eingegeben
            if not self.p == "":
                self.vstat = 0
                self.step = 0
            self.aktion()
        elif self.vstat == 2 and self.step == 0:    #Init Program step 0
            self.initpas(0)
        elif self.vstat == 2 and self.step == 1:    #Init Program step 1
            self.initpas(1)
        elif self.vstat == 2 and self.step == 2:    #Init Program step 2
            self.initpas(2)
        elif self.vstat == 3:   #Backupphase
            self.dobacstteo()
        else:
            return False

    def dellall(self):  #ALLe LAbels und BUttons löschen
        for i in reversed(range(self.mainlayout.rowCount())):
            #print(str(i))
            self.mainlayout.removeRow(i)

    def addFile(self):  #Datei hinzufügen
        if self.p == "":    #Anmeldeüberprüfung
            retval = self.mispas.exec_()
            return
        fname, ok = QInputDialog().getText(self, "Name", "Gib den Platform-/Webseitennamen ein: ")
        if not ok:
            return
        fdet, ok = QInputDialog().getMultiLineText(self, "Details", "Gib Details bzw. Sicherheitsinformationen ein: ")
        if not ok:
            return
        fname = str(fname).replace('#','&?=)(')
        fdet = str(fdet).replace('#','&?=)(')
        writefile(self.p,self.maindir, self.mainfile, fname, fdet)
        self.updall()

    def initMess(self):         #Messageboxen initiieren

        ###Passwort erst eingeben
        self.mispas = QMessageBox()
        self.mispas.setIcon(QMessageBox.Critical)
        self.mispas.setText("Zuerst Anmelden!")
        self.mispas.setWindowTitle("Anmeldefehler")
        self.mispas.setStandardButtons(QMessageBox.Ok)


        ###Details eines Eintrages anzeigen
        self.showdet = QMessageBox()
        self.showdet.setIcon(QMessageBox.Information)
        self.showdet.setWindowTitle("Informationen")
        self.showdet.setStandardButtons(QMessageBox.Ok)

        ###Sicherheits frage zum löschen
        self.remwar = QMessageBox()
        self.remwar.setIcon(QMessageBox.Critical)
        self.remwar.setWindowTitle("Löschabfrage")
        self.remwar.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        ###Beschtätigung einer Löschung
        self.delinf = QMessageBox()
        self.delinf.setIcon(QMessageBox.Information)
        self.delinf.setWindowTitle("Löschbestätigung")
        self.delinf.setInformativeText("Zum Verlassen des Löschmodus bitte erneut Remove in der Menübar oder der Toolbar drücken!")
        self.delinf.setStandardButtons(QMessageBox.Ok)

        ###Backupfrage für Zielordner
        self.bacqes = QMessageBox()
        self.bacqes.setIcon(QMessageBox.Information)
        self.bacqes.setWindowTitle("Backupabfrage")
        self.bacqes.setText("Standardbackupordner verwenden?")
        self.bacqes.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        ###Backupabfrage für adneres passwort
        self.bacpas = QMessageBox()
        self.bacpas.setIcon(QMessageBox.Information)
        self.bacpas.setWindowTitle("Backupabfrage")
        self.bacpas.setText("Backuppasswort verändern?")
        self.bacpas.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        ### Backup konnte erfolgreich erstellt werdem
        self.showsuc = QMessageBox()
        self.showsuc.setIcon(QMessageBox.Information)
        self.showsuc.setWindowTitle("Backupinformation")
        self.showsuc.setText("Backup erfolgreich erstellt.")
        self.showsuc.setStandardButtons(QMessageBox.Ok)

        ###Backup konnte nicht erstellt werden
        self.showden = QMessageBox()
        self.showden.setIcon(QMessageBox.Information)
        self.showden.setWindowTitle("Backupinformation")
        self.showden.setText("Backup konnte nicht erstellt werden. Versuchen Sie einen anderen Backupnamen")
        self.showden.setStandardButtons(QMessageBox.Ok)


    def initpas(self, stza): #Erstes Passwort festlegen
        #if os.path.isfile(os.path.join(maindir,mainfile)):
        #    return
        if stza == 0:
            self.mainlayout.addRow(QLabel("Passwort festlegen: "))
            self.getpas()
            self.step = 1

            self.update()
        elif stza == 1:
            self.mainlayout.addRow(QLabel("Passwort erneut eingeben: "))
            self.pz = self.p
            self.p  = ""
            self.getpas()
            self.step = 2
        elif stza == 2:
            if self.p == self.pz:
                genstrin = "CONTROL"
                mzw = encstring(genstrin, self.p)
                writetofile(self.maindir, self.mainfile, mzw[0], mzw[1], mzw[2])
                self.vstat = 0
                self.step = 0
                self.aktion()
            else:
                self.step = 0


    def getpas(self):   #Passwort anzeige
        trick = QHBoxLayout()
        self.passwidget = PwIn()
        self.passbutton = QPushButton("Submit")
        self.passbutton.clicked.connect(self.subpass)
        trick.addWidget(self.passwidget)
        trick.addWidget(self.passbutton)
        self.mainlayout.addRow(trick)
        #self.update()

    def subpass(self):  #Passwort funktion
        self.p = keyfrompas(self.passwidget.gettext())
        self.dellall()
        self.aktion()

        #print(self.p)

    def showlist(self): #Listeanzeigen incl. Passwort
        if self.mainlist == []:
            return
        va = "Öffnen"
        if self.vrem == True:
            va = "Löschen"
        for l in range(0,int((len(self.mainlist)-1)/3)):
            i = l*3+1
            self.paslabellist.append(QLabel(self.mainlist[i]))
            self.buttonshowlist.append(QPushButton(va))
            self.buttonshowlist[l].clicked.connect(self.click)
            trick = QHBoxLayout()
            trick.addWidget(self.buttonshowlist[l])
            self.mainlayout.addRow(self.paslabellist[l], trick)
        self.update()

    def initme(self):   #self init
        self.groupBox = QGroupBox("Alle")
        self.groupBox.setLayout(self.mainlayout)

        self.scrolling = QScrollArea()
        self.scrolling.setWidget(self.groupBox)
        self.scrolling.setWidgetResizable(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scrolling)

        self.setLayout(self.layout)

        #self.showlist(self.list)

        self.show()

    def remFile(self): #Datei löschen
        if self.p == "":
            retval = self.mispas.exec_()
            return
        if self.inbac == True:
            return
        if self.vrem == True:
            self.vrem = False
            for i in range(len(self.buttonshowlist)):
                self.buttonshowlist[i].setText("Öffnen")
        elif self.vrem == False:
            self.vrem = True
            for i in range(len(self.buttonshowlist)):
                self.buttonshowlist[i].setText("Löschen")


    def dobac(self): #Backup schreiben
        if self.p == "":
            retval = self.mispas.exec_()
            return

        retval = self.bacqes.exec_()
        if retval == 16384:
            destDir = "bacdir"
        else:
            startingDir = os.getcwd()
            destDir = QFileDialog.getExistingDirectory(None,
                                                       'Open working directory',
                                                       startingDir,
                                                       QFileDialog.ShowDirsOnly)
        bcname, ok = QInputDialog().getText(self, "Backupabfrage", "Gib einen Backupname ein: ")
        retval = self.bacpas.exec_()
        self.pz = self.p
        if retval == 16384:
            self.dellall()
            self.mainlayout.addRow(QLabel("Backuppasworteingeben  eingeben: "))
            self.getpas()
            stp = False
            self.pz = self.p
            self.vstat = 3
            self.stbacp = (destDir, bcname, stp)
        else:
            stp = True
            self.vstat = 3
            self.stbacp = (destDir, bcname, stp)
            self.dobacstteo()

    def dobacstteo(self): #backup step 2
        if self.vstat != 3:
            return
        try:
            z = os.path.join(self.stbacp[0], self.stbacp[1])
            os.mkdir(z)
        except FileExistsError as e:
            self.vstat = 0
            self.showden.exec_()
            return
        if self.stbacp[2] == False:
            zl = getlist(self.pz, self.urmaindir, self.mainfile)
            bccmain(self.p, z, self.mainfile, zl)
            zp = os.listdir(self.urmaindir)
            for x in zp:
                copy2(os.path.join(self.urmaindir, x), os.path.join(z, x))
        else:
            zp = os.listdir(self.urmaindir)
            for x in zp:
                copy2(os.path.join(self.urmaindir,x), os.path.join(z,x))
        self.vstat = 0
        self.showsuc.exec_()

    def readback(self): #Backuplesen
        if self.inbac == True:
            self.maindir = self.urmaindir
            self.inbac = False
            self.p = ""
            self.pz = ""
            self.buttonshowlist = []
            self.paslabellist = []
            self.dellall()
            self.vstat = -1
            self.step = 0
            self.checkstatus()
            self.aktion()
            return

        retval = self.bacqes.exec_()
        if retval == 16384:
            a = os.listdir('bacdir')
            item, ok = QInputDialog.getItem(self, "Backupdialog", "Backup auswählen:", a)
            if not ok:
                return
            zp = os.path.join('bacdir', item)
            self.maindir = zp
        else:
            startingDir = os.getcwd()
            destDir = QFileDialog.getExistingDirectory(None,
                                                      'Öffne Backupordner',
                                                      startingDir,
                                                      QFileDialog.ShowDirsOnly)
            za = os.listdir(destDir)
            ismain = False
            for x in za:
                if x == self.mainfile:
                    ismain = True
            if not ismain:
                item, ok = QInputDialog.getItem(self, "Backupdialog", "Backup auswählen:", za)
                if not ok:
                    return
                zp = os.path.join(destDir, item)
                self.maindir = zp
            else:
                self.maindir = destDir
        self.inbac = True
        self.p = ""
        self.pz = ""
        self.buttonshowlist = []
        self.paslabellist = []
        self.dellall()
        self.vstat = -1
        self.step = 0
        self.checkstatus()
        self.aktion()




    def updall(self):       #Liste aktualisieren
        if self.vstat != 0:
            return
        self.holmainlist()
        self.dellall()
        self.buttonshowlist = []
        self.paslabellist = []
        self.showlist()


    def click(self):        #Buttonclick
        send = self.sender()
        num = self.buttonshowlist.index(send)
        if self.vrem == True:
            nam = self.mainlist[num * 3 + 1]
            self.remwar.setText("Sind Sie sich sicher, dass Sie die Datei '"+nam+"' löschen möchten?")
            retval = self.remwar.exec_()
            if retval == 16384:
                retnam = removefile(self.p, self.maindir, self.mainfile, num*3+1)
                self.delinf.setText("'"+retnam+"' wurde erfolgreich gelöscht!")
                self.delinf.exec_()
                self.updall()
            else:
                return
        elif self.vrem == False:
            nam = self.mainlist[num*3+1]
            fn = self.mainlist[num*3+2]
            pas = self.mainlist[num*3+3]
            fil = str(getfile(keyfrompas(pas), self.maindir, fn),'utf-8').replace('&?=)(','#')
            self.showdet.setText("Informationen für '" + nam + "' werden angezeigt:")
            self.showdet.setInformativeText(fil)
            self.showdet.setDetailedText(fil)
            self.showdet.exec_()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initme()

        self.titlev = "Passwort Merker"

        self.leftv = 500
        self.topv = 200
        self.widthv = 700
        self.heightv = 500

        self.setWindowTitle(self.titlev)
        self.setGeometry(self.leftv,self.topv,self.widthv,self.heightv)

    def initme(self):
        #Passwidget
        self.widget = PasWidget()
        self.setCentralWidget(self.widget)

        #QActions definieren
        addPas = QAction(QIcon(''),'&Hinzufügen',self)
        addPas.setShortcut('Ctrl+H')
        addPas.triggered.connect(self.widget.addFile)

        self.remPas = QAction(QIcon(''), '&Löschen', self)
        self.remPas.setShortcut('Ctrl+L')
        self.remPas.triggered.connect(self.remf)

        bccPas = QAction(QIcon(''), 'Backup &erstellen', self)
        bccPas.setShortcut('Ctrl+E')
        bccPas.triggered.connect(self.widget.dobac)

        self.lodBcc = QAction(QIcon(''), '&Backup laden', self)
        self.lodBcc.setShortcut('Ctrl+B')
        self.lodBcc.triggered.connect(self.readb)


        men = self.menuBar()
        dat = men.addMenu('&Datei')
        dat.addAction(addPas)
        dat.addAction(self.remPas)
        dat.addAction(bccPas)
        dat.addAction(self.lodBcc)


        self.show()

    def remf(self):
        self.widget.remFile()
        if self.widget.vrem == True:
            self.remPas.setText('&Löschmodus beenden')
        else:
            self.remPas.setText('&Löschen')

    def readb(self):
        self.widget.readback()
        if self.widget.inbac == True:
            self.lodBcc.setText('&Backup lesen beenden')
        else:
            self.lodBcc.setText('&Backup lesen')




class PwIn(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.e1 = QLineEdit()
        self.e1.setEchoMode(QLineEdit.Password)

        flo = QFormLayout()

        flo.addRow("Passwort: ", self.e1)
        self.setLayout(flo)

    def gettext(self):
        return self.e1.text()


if __name__ == '__main__':
    #haupt()
    App = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(App.exec())
    ### ---Schema: Name#filename#Pass

    ###!--erster Eintrag - manuell--!###
    #zsp = safepas()
    #while True:
    #    rpath = ranpath()
    #    if not os.path.exists(os.path.join(maindir, rpath)):
    #        break
    #print(rpath)
    #inp = input('Passwort: ')
    #d = encstring("Posteo#"+rpath+"#"+zsp, keyfrompas(inp))
    #writetofile(maindir, mainfile, d[0], d[1], d[2])

    #inpos = "E-mail:m.krausewitz@posteo.de; Passwort:*****"
    #d = encstring(inpos, keyfrompas(zsp))
    #writetofile(maindir, rpath, d[0], d[1], d[2])

    #decyrpt erster eintrag
    #p = input("Passwort")
    #a = decryptfile(maindir, mainfile, keyfrompas(p))
    #print(a)



