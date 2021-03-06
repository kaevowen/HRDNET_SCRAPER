from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QThread, QDate, pyqtSignal, pyqtSlot
from PyQt5 import uic
from datetime import datetime, timedelta
import sys
import time
import re
import getCBValue
import HrdNetAPI

main_class = uic.loadUiType("main_gui.ui")[0]
login_class = uic.loadUiType("login_gui.ui")[0]


class LoginWindow(QMainWindow, login_class):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setupUi(self)
        self.loginBtn.clicked.connect(self.login)
        self.PWbox.returnPressed.connect(self.login)
        self.setWindowFlags(Qt.WindowMaximizeButtonHint)
        self.MainWindow = object()

    def login(self):
        ID = self.IDbox.text()
        PW = self.PWbox.text()
        checkLogin = HrdNetAPI.checkLogin(ID, PW)
        if checkLogin == "Fail_Login":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("아이디 또는 패스워드가 맞지 않습니다!")
            msg.exec_()

        if checkLogin == "Fail_Authkey":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("api키를 불러올 수 없습니다. 마이 페이지에서 발급받아주세요.")
            msg.exec_()
            
        else:
            self.MainWindow = MainWindow(checkLogin)
            self.MainWindow.show()
            self.hide()

class MainWindow(QMainWindow, main_class):
    def __init__(self, session):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.cb = getCBValue.getCB_Value()
        self.area_json = self.cb.get_area_json()
        self.ncs_json = self.cb.get_ncs_json()
        self.session = session
        self.NcsCode = [None, None, None]
        self.AreaCode = [None, None]
        self.radioValue = 60
        self.startDate.setDate(QDate.currentDate())
        self.endDate.setDate(QDate.currentDate().addDays(7))
        self.Worker = QThread()

        for key in self.area_json.keys():
            self.upperAreaCd.addItem(key)

        for key in self.ncs_json.keys():
            self.upperNcsCd.addItem(key)

        self.upperAreaCd.currentTextChanged.connect(self.upperAreaCdChanged)
        self.areaCd.currentTextChanged.connect(self.AreaCdChanged)
        self.upperNcsCd.currentTextChanged.connect(self.upperNcsCdChanged)
        self.middleNcsCd.currentTextChanged.connect(self.middleNcsCdChanged)
        self.smallNcsCd.currentTextChanged.connect(self.smallNcsCdChanged)

        self.optA.clicked.connect(self.radioSelected)
        self.optB.clicked.connect(self.radioSelected)
        self.optC.clicked.connect(self.radioSelected)
        self.optD.clicked.connect(self.radioSelected)

        self.execBtn.clicked.connect(self.ExecuteScript)
        self.cancelBtn.clicked.connect(self.DestroyScript)

    def radioSelected(self):
        if self.optA.isChecked():
            self.radioValue = 60
        elif self.optB.isChecked():
            self.radioValue = 61
        elif self.optC.isChecked():
            self.radioValue = 62
        elif self.optD.isChecked():
            self.radioValue = 64
        # print(self.radioValue)

    def upperAreaCdChanged(self):
        uppertxt = self.upperAreaCd.currentText()
        self.areaCd.clear()
        self.areaCd.addItems([key for key in self.area_json[uppertxt]])

        try:
            if uppertxt == '전체':
                self.AreaCode = [None, None]
                self.areaCd.setEnabled(False)

            else:
                self.AreaCode[0] = self.area_json[uppertxt]['전체']
                self.areaCd.setEnabled(True)
        except KeyError:
            pass

    def AreaCdChanged(self):
        try:
            uppertxt = self.upperAreaCd.currentText()
            lowertxt = self.areaCd.currentText()

            if lowertxt == '전체':
                self.AreaCode[1] = None
            else:
                self.AreaCode[1] = self.area_json[uppertxt][lowertxt]

            print(self.AreaCode)
        except KeyError:
            pass

    def upperNcsCdChanged(self):
        upperTxt = self.upperNcsCd.currentText()
        self.middleNcsCd.clear()
        if upperTxt == '전체':
            self.middleNcsCd.setEnabled(False)
            self.smallNcsCd.setEnabled(False)
            self.NcsCode = [None, None, None]
            print(self.NcsCode)

        else:
            self.middleNcsCd.setEnabled(True)
            self.smallNcsCd.setEnabled(True)
            self.middleNcsCd.addItem('전체')
            self.middleNcsCd.addItems([key for key in self.ncs_json[upperTxt]])
            self.NcsCode[0] = re.findall('\\d{2}', upperTxt)[0]

    def middleNcsCdChanged(self):
        upperTxt = self.upperNcsCd.currentText()
        middleTxt = self.middleNcsCd.currentText()
        self.smallNcsCd.clear()
        try:
            if middleTxt == '전체':
                self.smallNcsCd.setEnabled(False)
                self.NcsCode[1] = None

            else:
                self.smallNcsCd.setEnabled(True)
                self.smallNcsCd.addItems([key for key in self.ncs_json[upperTxt][middleTxt]])
                self.NcsCode[1] = self.ncs_json[upperTxt][middleTxt]['전체']
        except KeyError:
            pass

    def smallNcsCdChanged(self):
        upperTxt = self.upperNcsCd.currentText()
        middleTxt = self.middleNcsCd.currentText()
        smallTxt = self.smallNcsCd.currentText()

        try:
            if smallTxt == '전체':
                self.NcsCode[2] = None
                print(self.NcsCode)

            else:
                self.NcsCode[2] = self.ncs_json[upperTxt][middleTxt][smallTxt]['전체']
                print(self.NcsCode)
        except KeyError:
            pass

    def ExecuteScript(self):
        keyword = None if self.lineEdit_2.text() == '' else self.lineEdit_2.text()
        self.Worker = Worker(
            self.session,
            self.startDate.date().toString('yyyyMMdd'),
            self.endDate.date().toString('yyyyMMdd'),
            self.radioValue,
            self.NcsCode,
            self.AreaCode,
            keyword=keyword
        )
        self.Worker.start()

    def DestroyScript(self):
        print("cancel...")
        self.Worker.terminate()


class Worker(QThread):
    def __init__(self, session, startDate, endDate, radioValue, NcsCode, AreaCode, keyword, parent=None):
        QThread.__init__(self, parent)
        self.session = session
        self.startDate = startDate
        self.endDate = endDate
        self.radioValue = radioValue
        self.NcsCode = NcsCode
        self.AreaCode = AreaCode
        self.keyword = keyword

    def run(self):
        hrdnet = HrdNetAPI.HrdNetAPI(
            self.session,
            self.startDate,
            self.endDate,
            self.radioValue,
            self.NcsCode,
            self.AreaCode,
            keyword=self.keyword
        )
        hrdnet.getPagination()
        hrdnet.getAPI()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    LW = LoginWindow()
    # LW = MainWindow()
    LW.show()
    app.exec_()
