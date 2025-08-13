import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QPushButton, QMessageBox, QTextEdit, QHBoxLayout
from PyQt5.QtCore import QTimer

BASH_PATH = "src"  # cartella dove si trovano gli script bash


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager - GUI + Bash")
        self.setGeometry(200, 200, 800, 500)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["PID", "User", "CPU %", "Mem %", "Command"])

        # Pulsanti
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Aggiorna")
        self.kill_btn = QPushButton("Termina processo")
        self.tree_btn = QPushButton("Vista ad albero")

        self.refresh_btn.clicked.connect(self.load_processes)
        self.kill_btn.clicked.connect(self.kill_process)
        self.tree_btn.clicked.connect(self.show_tree)

        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.kill_btn)
        btn_layout.addWidget(self.tree_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer per aggiornare ogni 5 secondi
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_processes)
        self.timer.start(5000)

        self.load_processes()

    def run_bash(self, script, args=None):
        cmd = ["bash", f"{BASH_PATH}/{script}"]
        if args:
            cmd.extend(args)
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return output.decode().strip()
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.output.decode()}"

    def load_processes(self):
        output = self.run_bash("list_processes.sh")
        if output.startswith("ERROR"):
            QMessageBox.critical(self, "Errore", output)
            return

        rows = output.split("\n")
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            cols = row.split(",")
            for j, val in enumerate(cols):
                self.table.setItem(i, j, QTableWidgetItem(val))

    def kill_process(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Attenzione", "Seleziona un processo da terminare.")
            return

        pid = self.table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Conferma", f"Vuoi terminare il processo PID {pid}?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            result = self.run_bash("kill_process.sh", [pid])
            if "OK" in result:
                QMessageBox.information(self, "Successo", f"Processo {pid} terminato.")
                self.load_processes()
            else:
                QMessageBox.critical(self, "Errore", f"Impossibile terminare il processo {pid}.")

    def show_tree(self):
        output = self.run_bash("process_tree.sh")
        tree_window = QTextEdit()
        tree_window.setReadOnly(True)
        tree_window.setPlainText(output)

        msg_box = QMainWindow(self)
        msg_box.setWindowTitle("Vista ad albero")
        msg_box.setGeometry(250, 250, 600, 400)
        msg_box.setCentralWidget(tree_window)
        msg_box.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
