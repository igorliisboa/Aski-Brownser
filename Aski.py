# Imports
import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

# Janela principal
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Elementos da janela
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.setCentralWidget(self.tabs)

        # Nova aba
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        # Fechar a aba
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        # Mudar a aba
        self.tabs.currentChanged.connect(self.current_tab_changed)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        # Página anterior
        back_btn = QAction(QIcon(os.path.join('icons', 'cil-arrow-circle-left.png')), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        navtb.addAction(back_btn)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())

        # Página posterior
        next_btn = QAction(QIcon(os.path.join('icons', 'cil-arrow-circle-right.png')), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        navtb.addAction(next_btn)
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())

        # Atualizar
        reload_btn = QAction(QIcon(os.path.join('icons', 'cil-reload.png')), "Reload", self)
        reload_btn.setStatusTip("Reload page")
        navtb.addAction(reload_btn)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())

        # Home
        home_btn = QAction(QIcon(os.path.join('icons', 'cil-home.png')), "Home", self)
        home_btn.setStatusTip("Go home")
        navtb.addAction(home_btn)
        home_btn.triggered.connect(self.navigate_home)

        navtb.addSeparator()
        self.httpsicon = QLabel()  
        self.httpsicon.setPixmap(QPixmap(os.path.join('icons', 'cil-lock-unlocked.png')))
        navtb.addWidget(self.httpsicon)
        self.urlbar = QLineEdit()
        navtb.addWidget(self.urlbar)

        # Enter para carregar a página
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        # Stop para parar o carregamento
        stop_btn = QAction(QIcon(os.path.join('icons', 'cil-media-stop.png')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        navtb.addAction(stop_btn)
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())

        # File menu
        file_menu = self.menuBar().addMenu("&File")
        new_tab_action = QAction(QIcon(os.path.join('icons', 'cil-library-add.png')), "New Tab", self)
        new_tab_action.setStatusTip("Open a new tab")
        file_menu.addAction(new_tab_action)
        # Criar nova guia
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        navigate_home_action = QAction(QIcon(os.path.join('icons', 'cil-exit-to-app.png')),
                                            "Homepage", self)
        navigate_home_action.setStatusTip("Go to Homepage")
        help_menu.addAction(navigate_home_action)
        # Developer tools
        navigate_home_action.triggered.connect(self.navigate_home)

        self.setWindowTitle("Aski Browser")
        self.setWindowIcon(QIcon(os.path.join('icons', 'cil-screen-desktop.png')))
        self.setStyleSheet("""QWidget{
           background-color: rgb(48, 48, 48);
           color: rgb(255, 255, 255);
        }
        QTabWidget::pane {
            border-top: 2px solid rgb(90, 90, 90);
            position: absolute;
            top: -0.5em;
            color: rgb(255, 255, 255);
            padding: 5px;
        }

        QTabWidget::tab-bar {
            alignment: left;
        }

        QLabel, QToolButton, QTabBar::tab {
            background: rgb(90, 90, 90);
            border: 2px solid rgb(90, 90, 90);
            border-bottom-color: #C2C7CB;
            border-radius: 10px;
            min-width: 8ex;
            padding: 5px;
            margin-right: 2px;
            color: rgb(255, 255, 255);
        }

        QLabel:hover, QToolButton::hover, QTabBar::tab:selected, QTabBar::tab:hover {
            background: rgb(210, 210, 150);
            margin-top: 5px;
            margin-left: 3px;
            border: 2px black;
            background-color: black;
        }

        QLineEdit {
            border: 2px rgb(200, 200, 200);
            border-radius: 10px;
            padding: 5px;
            background-color: black;
            color: black;
        }
        QLineEdit:hover {
            border: 2px solid rgb(0, 66, 124);
        }
        QLineEdit:focus{
            border: 2px solid rgb(0, 136, 255);
            color: green;
        }
        QPushButton{
            background: rgb(200, 200, 200);
            border: 2px solid black;
            background-color: black;
            padding: 5px;
            border-radius: 10px;
        }""")

        # Homepage (Google)
        self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')
        self.show()

    # Nova aba
    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl('')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    # Criar uma nova guia com Double-click
    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    # Fechar guias 
    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        if q.scheme() == 'https':
            self.httpsicon.setPixmap(QPixmap(os.path.join('icons', 'cil-lock-locked.png')))

        else:
            self.httpsicon.setPixmap(QPixmap(os.path.join('icons', 'cil-lock-unlocked.png')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(title)

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com.br"))

app = QApplication(sys.argv)
# Nome do navegador
app.setApplicationName("Aski Browser")
window = MainWindow()
app.exec_()
