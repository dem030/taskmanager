import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit,
    QMessageBox, QLabel, QHeaderView, QInputDialog  
)
from PyQt5.QtCore import QTimer

SRC_DIR = "src/"

def run_script(script, args=[]):
    try:
        result = subprocess.run(
            ["bash", SRC_DIR + script] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stderr:
            print("Errore:", result.stderr)
        return result.stdout.strip().splitlines()
    except Exception as e:
        print("Errore esecuzione script:", e)
        return []

class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager - PyQt5")
        self.resize(900, 500)

        layout = QVBoxLayout()

        # filtro
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtra per nome processo...")
        filter_btn = QPushButton("Applica filtro")
        filter_btn.clicked.connect(self.update_table)
        filter_layout.addWidget(QLabel("Filtro:"))
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(filter_btn)
        layout.addLayout(filter_layout)

        # tabella processi
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["PID", "USER", "CPU%", "MEM%", "COMMAND"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # pulsanti azioni
        btn_layout = QHBoxLayout()
        kill_btn = QPushButton("Kill (SIGTERM)")
        kill_btn.clicked.connect(self.kill_process)
        stop_btn = QPushButton("Stop (SIGSTOP)")
        stop_btn.clicked.connect(self.stop_process)
        cont_btn = QPushButton("Continue (SIGCONT)")
        cont_btn.clicked.connect(self.cont_process)
        renice_btn = QPushButton("Renice")
        renice_btn.clicked.connect(self.renice_process)

        btn_layout.addWidget(kill_btn)
        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(cont_btn)
        btn_layout.addWidget(renice_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # timer refresh ogni 2 sec
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(2000)

        self.update_table()

    def update_table(self):
        processes = run_script("list.sh")
        filter_text = self.filter_input.text().lower()

        rows = []
        for line in processes:
            parts = line.split(None, 4)
            if len(parts) < 5:
                continue
            pid, user, cpu, mem, cmd = parts
            if filter_text and filter_text not in cmd.lower():
                continue
            rows.append((pid, user, cpu, mem, cmd))

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(val))

    def get_selected_pid(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Errore", "Seleziona un processo dalla tabella")
            return None
        pid = self.table.item(selected, 0).text()
        return pid

    def kill_process(self):
        pid = self.get_selected_pid()
        if pid:
            run_script("kill.sh", [pid])
            self.update_table()

    def stop_process(self):
        pid = self.get_selected_pid()
        if pid:
            run_script("stop.sh", [pid])
            self.update_table()

    def cont_process(self):
        pid = self.get_selected_pid()
        if pid:
            run_script("cont.sh", [pid])
            self.update_table()

    def renice_process(self):
        pid = self.get_selected_pid()
        if pid:
            val, ok = QInputDialog.getInt(self, "Renice", f"Nuovo nice per PID {pid}", 0, -20, 19, 1)
            if ok:
                run_script("renice.sh", [pid, str(val)])
                self.update_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    