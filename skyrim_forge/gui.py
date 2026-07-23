from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .config import load_config
from .service import ForgeService


class ForgeGui(tk.Tk):
    def __init__(self, config_path: str | None = None):
        super().__init__()
        self.title("Skyrim Forge 3.0 Automation Fabric")
        self.geometry("1050x720")
        self.service = ForgeService(load_config(config_path))
        self._build()

    def _build(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=8, pady=8)
        for label, command in [
            ("Doctor", lambda: self._run(self.service.doctor)),
            ("Discover tools", lambda: self._run(self.service.discover)),
            ("Framework lint", self._lint),
            ("Validate release", self._release),
            ("Run automation job", self._job),
        ]:
            ttk.Button(top, text=label, command=command).pack(side="left", padx=4)
        self.output = tk.Text(self, wrap="none", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(self, text="Forge never asks you to finish an xEdit or CK job manually. Unexpected dialogs block the job.").pack(anchor="w", padx=8, pady=4)

    def _run(self, func):
        def worker():
            try: value = func()
            except Exception as exc: value = {"result": "FAIL", "error": type(exc).__name__, "message": str(exc)}
            text = json.dumps(value, indent=2, ensure_ascii=False, default=str)
            self.after(0, lambda: (self.output.delete("1.0", "end"), self.output.insert("1.0", text)))
        threading.Thread(target=worker, daemon=True).start()

    def _lint(self):
        path = filedialog.askdirectory()
        if path: self._run(lambda: self.service.lint([path]))

    def _release(self):
        path = filedialog.askdirectory()
        if path: self._run(lambda: self.service.release_validate(path))

    def _job(self):
        path = filedialog.askopenfilename(filetypes=[("Forge JSON jobs", "*.json")])
        if not path: return
        approved = messagebox.askyesno("Forge approval", "Approve writes/external operations requested by this typed job?")
        self._run(lambda: self.service.automation_run(path, approved, True))


def run_gui(config_path: str | None = None) -> None:
    ForgeGui(config_path).mainloop()
