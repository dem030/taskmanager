import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import subprocess
import os
import pwd
import time

REFRESH_MS = 3000
LOG_FILE = "logs/events.log"

# ---------------------------
# Utils
# ---------------------------

def current_user():
    return pwd.getpwuid(os.getuid()).pw_name

def is_root():
    return os.geteuid() == 0

def run_action(script, args):
    try:
        subprocess.run(["bash", script] + args,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=False)
    except Exception:
        pass

def read_logs():
    try:
        with open(LOG_FILE) as f:
            return f.read()
    except FileNotFoundError:
        return ""

def fetch_processes():
    """
    Legge processi direttamente con ps
    Include TEMPO ATTIVO REALE (etimes)
    """
    cmd = [
        "ps",
        "-eo", "pid,user,pcpu,pmem,etimes,etime,comm",
        "--no-headers"
    ]
    out = subprocess.check_output(cmd, text=True)

    procs = []
    for line in out.splitlines():
        parts = line.split(None, 6)
        if len(parts) == 7:
            pid, user, cpu, mem, etimes, etime, cmd = parts
            try:
                procs.append({
                    "PID": int(pid),
                    "USER": user,
                    "CPU": float(cpu),
                    "MEM": float(mem),
                    "ETIMES": int(etimes),  # secondi
                    "TIME": etime,
                    "CMD": cmd
                })
            except ValueError:
                continue
    return procs

# ---------------------------
# GUI
# ---------------------------

class TaskManagerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")

        self.me = current_user()
        self.root_mode = is_root()

        self.sort_mode = "CPU"  # CPU | MEM | TIME
        self.processes = []

        self.build_gui()
        self.refresh()

    def build_gui(self):
        # --- Top bar ---
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(top, text="Utente:").pack(side=tk.LEFT)
        self.user_filter = tk.Entry(top, width=15)
        self.user_filter.pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="Sort CPU", command=lambda: self.set_sort("CPU")).pack(side=tk.LEFT)
        tk.Button(top, text="Sort MEM", command=lambda: self.set_sort("MEM")).pack(side=tk.LEFT)
        tk.Button(top, text="Sort TIME", command=lambda: self.set_sort("TIME")).pack(side=tk.LEFT)

        # Scenario multiutente
        if not self.root_mode:
            self.user_filter.insert(0, self.me)
            self.user_filter.config(state="disabled")

        # --- Tabella ---
        cols = ("PID", "USER", "CPU", "MEM", "TIME", "CMD")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=15)

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5)

        # --- Pulsanti ---
        btn = tk.Frame(self.root)
        btn.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(btn, text="KILL", command=self.kill).pack(side=tk.LEFT)
        tk.Button(btn, text="STOP", command=self.stop).pack(side=tk.LEFT)
        tk.Button(btn, text="CONT", command=self.cont).pack(side=tk.LEFT)
        tk.Button(btn, text="RENICE", command=self.renice).pack(side=tk.LEFT)
        tk.Button(btn, text="PSTREE", command=self.show_tree).pack(side=tk.LEFT)

        # --- Log ---
        tk.Label(self.root, text="Event log:").pack(anchor="w", padx=5)
        self.log_box = tk.Text(self.root, height=6, bg="#111", fg="#0f0")
        self.log_box.pack(fill=tk.X, padx=5, pady=5)

    # ---------------------------
    # Core
    # ---------------------------

    def refresh(self):
        self.processes = fetch_processes()
        self.apply_filter_and_sort()
        self.update_table()
        self.update_log()
        self.root.after(REFRESH_MS, self.refresh)

    def apply_filter_and_sort(self):
        # filtro utente
        user = self.user_filter.get()
        if user:
            self.processes = [p for p in self.processes if p["USER"] == user]

        # sort
        if self.sort_mode == "CPU":
            self.processes.sort(key=lambda p: p["CPU"], reverse=True)
        elif self.sort_mode == "MEM":
            self.processes.sort(key=lambda p: p["MEM"], reverse=True)
        elif self.sort_mode == "TIME":
            self.processes.sort(key=lambda p: p["ETIMES"], reverse=True)

    def update_table(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        for p in self.processes:
            self.tree.insert(
                "",
                tk.END,
                values=(p["PID"], p["USER"], p["CPU"], p["MEM"], p["TIME"], p["CMD"])
            )

    def update_log(self):
        self.log_box.delete(1.0, tk.END)
        self.log_box.insert(tk.END, read_logs())

    def set_sort(self, mode):
        self.sort_mode = mode
        self.apply_filter_and_sort()
        self.update_table()

    def selected_pid(self):
        sel = self.tree.focus()
        if not sel:
            return None
        return self.tree.item(sel)["values"][0]

    # ---------------------------
    # Azioni
    # ---------------------------

    def kill(self):
        pid = self.selected_pid()
        if pid:
            run_action("kill.sh", [str(pid)])

    def stop(self):
        pid = self.selected_pid()
        if pid:
            run_action("stop.sh", [str(pid)])

    def cont(self):
        pid = self.selected_pid()
        if pid:
            run_action("cont.sh", [str(pid)])

    def renice(self):
        pid = self.selected_pid()
        if not pid:
            return
        val = simpledialog.askstring("Renice", "Valore nice (-20..19):")
        if val:
            run_action("renice.sh", [str(pid), val])

    def show_tree(self):
        try:
            output = subprocess.check_output(
            ["bash", "pstree.sh"],
            text=True
        )
        except subprocess.CalledProcessError:
            output = "Errore nella visualizzazione dell'albero processi"

        win.title("Process Tree (pstree)")
        txt = tk.Text(win)
        win = tk.Toplevel(self.root)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, output)


# ---------------------------
# Avvio
# ---------------------------

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x650")
    TaskManagerGUI(root)
    root.mainloop()
