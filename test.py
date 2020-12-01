import os
import re
import json
import sys
import time
import re
import openpyxl

from datetime import datetime
from urllib.parse import quote
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QThread, QDate, QObject, pyqtSignal, pyqtSlot
from datetime import datetime, timedelta
from openpyxl.styles import PatternFill, Alignment, Side, Border
from requests import get, Session
from bs4 import BeautifulSoup as BS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

