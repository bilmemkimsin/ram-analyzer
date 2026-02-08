import os
import struct
import tkinter as tk
from tkinter import messagebox, ttk

import psutil


class RamAnalyzerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("RAM Analyzer")
        self.geometry("920x600")
        self.configure(padx=16, pady=16)

        self.processes = []
        self.selected_pid = None

        header = ttk.Label(
            self,
            text=(
                "RAM Analyzer - Süreç belleği inceleme ve okuma/yazma (yönetici izni gerekir)."
            ),
            font=("TkDefaultFont", 12, "bold"),
        )
        header.pack(anchor="w", pady=(0, 12))

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=False)

        self._build_process_list(left_frame)
        self._build_memory_tools(right_frame)

        self.refresh_processes()

    def _build_process_list(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 8))

        refresh_button = ttk.Button(
            toolbar, text="Süreçleri Yenile", command=self.refresh_processes
        )
        refresh_button.pack(side="left")

        search_label = ttk.Label(toolbar, text="Ara:")
        search_label.pack(side="left", padx=(12, 4))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_processes())
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=24)
        search_entry.pack(side="left")

        columns = ("pid", "name", "memory")
        self.tree = ttk.Treeview(
            parent, columns=columns, show="headings", height=20, selectmode="browse"
        )
        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="Süreç Adı")
        self.tree.heading("memory", text="Kullanılan RAM (MB)")
        self.tree.column("pid", width=80, anchor="center")
        self.tree.column("name", width=280)
        self.tree.column("memory", width=160, anchor="e")
        self.tree.bind("<<TreeviewSelect>>", self.on_select_process)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_memory_tools(self, parent: ttk.Frame) -> None:
        section = ttk.LabelFrame(parent, text="Bellek Okuma/Yazma")
        section.pack(fill="x", pady=(0, 12))

        pid_label = ttk.Label(section, text="Seçili PID:")
        pid_label.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))

        self.pid_value = ttk.Label(section, text="-")
        self.pid_value.grid(row=0, column=1, sticky="w", pady=(8, 4))

        addr_label = ttk.Label(section, text="Adres (hex):")
        addr_label.grid(row=1, column=0, sticky="w", padx=8, pady=4)

        self.address_var = tk.StringVar()
        addr_entry = ttk.Entry(section, textvariable=self.address_var, width=16)
        addr_entry.grid(row=1, column=1, sticky="w", pady=4)

        type_label = ttk.Label(section, text="Veri Tipi:")
        type_label.grid(row=2, column=0, sticky="w", padx=8, pady=4)

        self.type_var = tk.StringVar(value="int32")
        type_combo = ttk.Combobox(
            section,
            textvariable=self.type_var,
            values=["int32", "int64", "float", "double", "bytes"],
            state="readonly",
            width=10,
        )
        type_combo.grid(row=2, column=1, sticky="w", pady=4)

        size_label = ttk.Label(section, text="Boyut (bytes):")
        size_label.grid(row=3, column=0, sticky="w", padx=8, pady=4)

        self.size_var = tk.StringVar(value="4")
        size_entry = ttk.Entry(section, textvariable=self.size_var, width=10)
        size_entry.grid(row=3, column=1, sticky="w", pady=4)

        read_button = ttk.Button(section, text="Oku", command=self.read_memory)
        read_button.grid(row=4, column=0, padx=8, pady=8, sticky="w")

        write_button = ttk.Button(section, text="Yaz", command=self.write_memory)
        write_button.grid(row=4, column=1, padx=8, pady=8, sticky="w")

        value_label = ttk.Label(section, text="Değer:")
        value_label.grid(row=5, column=0, sticky="w", padx=8, pady=(4, 8))

        self.value_var = tk.StringVar()
        value_entry = ttk.Entry(section, textvariable=self.value_var, width=24)
        value_entry.grid(row=5, column=1, sticky="w", pady=(4, 8))

        note = ttk.Label(
            parent,
            text=(
                "Not: /proc/<pid>/mem erişimi için root izni gerekir. "
                "Oyunun/sürenin belleğine müdahale etmek sistem kararlılığını bozabilir."
            ),
            wraplength=240,
            foreground="#555",
        )
        note.pack(anchor="w", padx=4)

    def refresh_processes(self) -> None:
        search = self.search_var.get().lower().strip()
        self.tree.delete(*self.tree.get_children())
        self.processes = []
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                name = proc.info["name"] or ""
                if search and search not in name.lower():
                    continue
                memory_mb = proc.info["memory_info"].rss / (1024 * 1024)
                self.processes.append((proc.info["pid"], name, memory_mb))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        for pid, name, memory_mb in sorted(self.processes, key=lambda item: item[2], reverse=True):
            self.tree.insert("", "end", values=(pid, name, f"{memory_mb:,.2f}"))

    def on_select_process(self, event: tk.Event) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        pid = item["values"][0]
        self.selected_pid = int(pid)
        self.pid_value.config(text=str(pid))

    def _resolve_address(self) -> int:
        address_text = self.address_var.get().strip()
        if not address_text:
            raise ValueError("Adres girmelisiniz.")
        if address_text.startswith("0x"):
            address_text = address_text[2:]
        return int(address_text, 16)

    def _open_mem(self, pid: int, mode: str):
        path = f"/proc/{pid}/mem"
        if not os.path.exists(path):
            raise FileNotFoundError("PID bellek yolu bulunamadı.")
        return open(path, mode)

    def read_memory(self) -> None:
        if self.selected_pid is None:
            messagebox.showwarning("Uyarı", "Önce bir süreç seçmelisiniz.")
            return
        try:
            address = self._resolve_address()
            data_type = self.type_var.get()
            size = int(self.size_var.get())
            with self._open_mem(self.selected_pid, "rb") as mem:
                mem.seek(address)
                raw = mem.read(size)
            value = self._unpack_value(data_type, raw)
            self.value_var.set(value)
        except Exception as exc:  # noqa: BLE001 - UI level reporting
            messagebox.showerror("Hata", f"Okuma başarısız: {exc}")

    def write_memory(self) -> None:
        if self.selected_pid is None:
            messagebox.showwarning("Uyarı", "Önce bir süreç seçmelisiniz.")
            return
        try:
            address = self._resolve_address()
            data_type = self.type_var.get()
            size = int(self.size_var.get())
            value = self.value_var.get().strip()
            raw = self._pack_value(data_type, size, value)
            with self._open_mem(self.selected_pid, "r+b") as mem:
                mem.seek(address)
                mem.write(raw)
            messagebox.showinfo("Başarılı", "Bellek yazma işlemi tamamlandı.")
        except Exception as exc:  # noqa: BLE001 - UI level reporting
            messagebox.showerror("Hata", f"Yazma başarısız: {exc}")

    def _unpack_value(self, data_type: str, raw: bytes) -> str:
        if data_type == "int32":
            return str(struct.unpack("<i", raw[:4])[0])
        if data_type == "int64":
            return str(struct.unpack("<q", raw[:8])[0])
        if data_type == "float":
            return f"{struct.unpack('<f', raw[:4])[0]:.6f}"
        if data_type == "double":
            return f"{struct.unpack('<d', raw[:8])[0]:.6f}"
        return raw.hex()

    def _pack_value(self, data_type: str, size: int, value: str) -> bytes:
        if data_type == "int32":
            return struct.pack("<i", int(value))
        if data_type == "int64":
            return struct.pack("<q", int(value))
        if data_type == "float":
            return struct.pack("<f", float(value))
        if data_type == "double":
            return struct.pack("<d", float(value))
        raw = bytes.fromhex(value)
        if len(raw) != size:
            raise ValueError("Girilen hex değeri boyutla eşleşmiyor.")
        return raw


if __name__ == "__main__":
    app = RamAnalyzerApp()
    app.mainloop()
