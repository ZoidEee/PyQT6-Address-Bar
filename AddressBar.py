import sys

from PyQt6.QtCore import QDir, QSize, Qt, QFile, QPoint, pyqtSignal
from PyQt6.QtGui import QFileSystemModel, QGuiApplication, QFont, QFontMetrics, QFontDatabase, QAction
from PyQt6.QtWidgets import QMainWindow, QApplication, QListView, QHBoxLayout, QWidget, QLabel, QFrame, \
    QToolBar, QPushButton, QMenu


class AddressBarLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, txt, font):
        super().__init__(txt)
        self.fontMetrics = QFontMetrics(font)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(font)
        self.setStyleSheet("""
            QLabel{ border-radius: 5px; }
            QLabel:hover{ background-color: #ededed; }
        """)
        self.setFixedWidth(self.fontMetrics.horizontalAdvance(txt) + 15)
        self.setFixedHeight(25)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.text())


class AddressBar(QFrame):
    directoryClicked = pyqtSignal(str)  # New signal

    def __init__(self, menu, menu_btn):
        super().__init__()
        self.actions()
        self.menu_btn = menu_btn

        # Set the font for the address bar
        font_family = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
        self.font = QFont(font_family, 11)

        self.fontMetrics = QFontMetrics(self.font)

        # Set the size and margins for the address bar
        self.setFixedSize(QSize(600, 35))
        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("main_frame")
        self.setStyleSheet("""
            QFrame#main_frame { border: 1px solid black;
                                border-radius: 2px;}
        """)

        # Create the layout and subframe for the address bar
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.sub_frame = QFrame()

        # Create the sub-layout for the address bar
        self.sub_layout = QHBoxLayout()
        self.sub_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.sub_layout.setContentsMargins(0, 0, 0, 0)

        # Set the sub-layout for the subframe
        self.sub_frame.setLayout(self.sub_layout)
        self.layout.addWidget(self.sub_frame)
        self.setLayout(self.layout)

        # Store the menu object as an instance variable
        self.menu = menu

    def stripAddressBar(self):
        # Remove all widgets and spacer items from the sub-layout
        for i in reversed(range(self.sub_layout.count())):
            item = self.sub_layout.itemAt(i)
            if item.widget():
                self.sub_layout.removeWidget(item.widget())
            else:
                pass

    def updateAddressBar(self, path):
        # Remove any existing content from the address bar
        self.stripAddressBar()

        if path.startswith("/"):
            path = path[1:]
        # Split the path into subdirectories
        self.sub_path = path.split("/")

        total_width = 0
        self.sub_dirs = []

        # Add a QLabel widget for each subdirectory and a separator after each one
        for i1, sub_dir in enumerate(self.sub_path):
            sub_dir_l = AddressBarLabel(sub_dir, self.font)
            sub_dir_width = self.fontMetrics.horizontalAdvance(sub_dir) + 15
            total_width += sub_dir_width + 8  # Eight compensates for the /

            if total_width > 600:
                # Remove the first subdirectory and separator until the total width is less than or equal to 600
                while total_width > 600 and self.sub_layout.count() > 1:
                    item = self.sub_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        spacer = item.spacerItem()
                        if spacer is not None:
                            spacer.deleteLater()
                    self.sub_layout.takeAt(
                        0).widget().deleteLater()  # This deletes the "/" form the beginning of the path
                    total_width -= sub_dir_width + 10

            self.sub_dirs.append(sub_dir_l)
            sub_dir_l.clicked.connect(self.onSubDirectoryClicked)  # Connect the label's clicked signal
            self.sub_layout.addWidget(sub_dir_l)

            if i1 < len(self.sub_path) - 1:
                sep = QLabel("/")
                sep.setFixedWidth(self.fontMetrics.horizontalAdvance("/"))
                # self.sub_dirs.append(sep)
                self.sub_layout.addWidget(sep)

            # Enable context menus for each QLabel that is not a separator
            sub_dir_l.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            sub_dir_l.customContextMenuRequested.connect(lambda pos, i=i1: self.showContextMenu(pos, i))

        # Set the font weight of the last subdirectory to bold and adjust its width to fit the text
        self.sub_dirs[-1].setStyleSheet("font-weight: bold")
        w = self.fontMetrics.horizontalAdvance(
            self.sub_dirs[-1].text()) + 10  # +10 adds 10 pixels to the bolded directory
        self.sub_dirs[-1].setFixedWidth(w)

        # Set the spacing and width for the sub-layout and subframe
        self.sub_layout.setSpacing(0)
        self.sub_frame.setFixedWidth(total_width)

    def onSubDirectoryClicked(self, index):
        # Emit the directoryClicked signal with the directory name and path at the clicked index
        clicked_directory_path = None
        for i, directory in enumerate(self.sub_path):
            if directory.endswith(index):
                clicked_directory_path = '/'.join(self.sub_path[:i + 1])
                break
        if clicked_directory_path is not None:
            self.directoryClicked.emit("/" + clicked_directory_path)

    def showContextMenu(self, pos, index):  # Do I need pos? ---- Create a QMenu object and add actions to it
        menu = self.menu
        menu.addAction(self.new_folder_act)
        menu.addAction(self.open_new_tab_act)
        menu.addAction(self.properties_act)
        if index == len(self.sub_dirs) - 1:
            # If the last directory in the path --> display on QPushButton
            # Calculate the position of the context menu based on the position of the QPushButton
            btn_pos = self.menu_btn.mapToGlobal(QPoint(0, 0))
            btn_width = self.menu_btn.width()
            btn_height = self.menu_btn.height()
            menu_width = menu.sizeHint().width()
            menu_height = menu.sizeHint().height()
            x = int(btn_pos.x() + (btn_width / 2) - (menu_width / 2))
            y = int(btn_pos.y() + btn_height)
            action = menu.exec(QPoint(x, y))
        else:
            # else display on the QLabel
            # Calculates the position of the context menu based on the position of the QLabel
            label_pos = self.sub_dirs[index].mapToGlobal(QPoint(0, 0))
            label_width = self.sub_dirs[index].width()
            label_height = self.sub_dirs[index].height()
            menu_width = menu.sizeHint().width()
            menu_height = menu.sizeHint().height()
            x = int(label_pos.x() + (label_width / 2) - (menu_width / 2))
            y = int(label_pos.y() + label_height)
            action = menu.exec(QPoint(x, y))
        # Handle the selected action (currently, just print)
        if action == self.new_folder_act:
            print("New Folder selected")
        elif action == self.open_new_tab_act:
            print("Open in New Tab selected")
        elif action == self.properties_act:
            print("Properties selected")

    def actions(self):
        # Create Actions
        self.new_folder_act = QAction("New Folder")
        self.open_new_tab_act = QAction("Open in New Tab")
        self.properties_act = QAction("Properties")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.clipboard = QGuiApplication.clipboard()
        self.homePath = QDir.homePath()

        self.initUI()

    def initUI(self):

        self.setWindowTitle("Tanz")
        self.setFixedSize(800, 500)

        self.setupActions()
        self.setupMainWindow()
        self.adr_bar.directoryClicked.connect(self.updateFileView)

        self.show()

    def setupMainWindow(self):
        """ Toolbar """
        self.core_toolbar = QToolBar()
        self.core_toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.core_toolbar.setParent(self)
        self.core_toolbar.setFixedSize(800, 45)
        self.core_toolbar.setMovable(False)
        self.core_toolbar.toggleViewAction().setEnabled(False)
        self.core_toolbar.setIconSize(QSize(25, 25))
        self.core_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        back = QPushButton("<")
        back.setFixedSize(25, 25)
        forward = QPushButton(">")
        forward.setFixedSize(25, 25)

        self.core_toolbar.addWidget(back)
        self.core_toolbar.addWidget(forward)

        # Create a QMenu object for the address bar context menu
        self.address_bar_menu = QMenu()
        # Create the menu QPushButton for the QToolbar
        menu = QPushButton("Menu")
        menu.setFixedSize(50, 25)

        # Pass the menu object to the AddressBar constructor
        self.adr_bar = AddressBar(self.address_bar_menu, menu)
        self.core_toolbar.addWidget(self.adr_bar)
        self.adr_bar.new_folder_act.triggered.connect(self.newDirectory)

        search = QPushButton("Srch")
        search.setFixedSize(75, 25)
        self.core_toolbar.addWidget(menu)
        self.core_toolbar.addWidget(search)
        self.addToolBar(self.core_toolbar)
        self.addToolBarBreak()

        self.core_file_model = QFileSystemModel()
        self.core_file_model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)
        self.core_file_model.sort(0, Qt.SortOrder.AscendingOrder)
        self.core_file_model.setRootPath(self.homePath)

        self.core_f_list_view = QListView()
        self.core_f_list_view.setModel(self.core_file_model)
        self.core_f_list_view.setRootIndex(self.core_file_model.index(self.homePath))
        self.core_f_list_view.setViewMode(QListView.ViewMode.IconMode)
        self.core_f_list_view.setIconSize(QSize(60, 60))
        self.core_f_list_view.setSpacing(5)
        self.core_f_list_view.setWordWrap(True)
        self.core_f_list_view.setFrameStyle(QListView.Shape.NoFrame)
        self.core_f_list_view.setGridSize(QSize(100, 100))
        self.core_f_list_view.doubleClicked.connect(self.load)

        layout = QHBoxLayout()
        layout.addWidget(self.core_f_list_view)

        wid = QWidget()
        wid.setLayout(layout)
        self.setCentralWidget(wid)

    def updateFileView(self, directory_path):
        index = self.core_file_model.index(directory_path)
        self.adr_bar.updateAddressBar(directory_path)
        self.core_f_list_view.setRootIndex(index)
        self.core_file_model.setRootPath(directory_path)

    def setupActions(self):
        pass

    def newDirectory(self):
        curr_path = self.core_file_model.filePath(self.core_f_list_view.rootIndex())
        new_direc_path = curr_path + "/New Folder"
        QDir(curr_path).mkdir(new_direc_path)

    def load(self):
        cur_ind = self.core_f_list_view.currentIndex()
        cur_ind_path = self.core_file_model.filePath(cur_ind)
        if QDir(cur_ind_path).exists():
            self.adr_bar.updateAddressBar(cur_ind_path)
            self.core_f_list_view.setRootIndex(self.core_file_model.index(cur_ind_path))
            self.core_file_model.setRootPath(cur_ind_path)
        elif QFile(cur_ind_path).exists():
            # Open the file.
            pass
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
