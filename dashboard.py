import json
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

def load_grades():
    with open("grades.json", "r") as f:
        return json.load(f)

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maplewood Grade Dashboard")
        self.setMinimumSize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📚 Maplewood Grade Dashboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 16px;
                margin-right: 4px;
                border-radius: 4px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #2980b9;
                color: white;
            }
        """)

        grades = load_grades()
        for class_name, rows in grades.items():
            tab = self.make_tab(rows)
            short_name = class_name.split(" - ")[1] if " - " in class_name else class_name
            tabs.addTab(tab, short_name)

        layout.addWidget(tabs)

        self.setStyleSheet("background-color: #f5f5f5;")

    def make_tab(self, rows):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Item", "Mark", "Date", "Weight", "Out of"])
        table.setRowCount(len(rows))
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #ddd;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #2980b9;
                color: white;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)

        for i, row in enumerate(rows):
            items = [row["item"], row["mark"], row["date"], row["weight"], row["out_of"]]
            for j, value in enumerate(items):
                cell = QTableWidgetItem(value)
                cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                if row["item"].lower().startswith("term") or row["item"].lower().startswith("unit"):
                    cell.setBackground(QColor("#eaf4ff"))
                    cell.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                table.setItem(i, j, cell)

        layout.addWidget(table)
        return widget

app = QApplication(sys.argv)
window = Dashboard()
window.show()
sys.exit(app.exec())