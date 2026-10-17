import math
import platform
import re
import shutil
import subprocess
import threading
import tkinter as tk
from datetime import datetime

import psutil

# J.A.R.V.I.S 2.0 — Siri-inspired interface
BG = "#070A12"
PANEL = "#101726"
PANEL_2 = "#151F31"
CYAN = "#55F4FF"
BLUE = "#638BFF"
PURPLE = "#B18CFF"
PINK = "#F38CFF"
GREEN = "#68F7B0"
WHITE = "#F3F7FF"
MUTED = "#91A0B8"
RED = "#FF718A"


class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S 2.0")
        self.root.geometry("1180x820")
        self.root.minsize(900, 740)
        self.root.configure(bg=BG)

        self._gpu_data = (0.0, "Waiting for GPU telemetry")
        self._gpu_check_running = False
        self._animation_step = 0
        self._listening = False
        self._history = {"cpu": [], "ram": [], "gpu": []}
        self._history_limit = 48

        # Header
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=26, pady=(15, 3))

        title_row = tk.Frame(header, bg=BG)
        title_row.pack(fill="x")
        tk.Label(
            title_row, text="J.A.R.V.I.S",
            font=("Helvetica", 25, "bold"), fg=CYAN, bg=BG
        ).pack(side="left")
        tk.Label(
            title_row, text="2.0  /  SYSTEM INTELLIGENCE",
            font=("Menlo", 9, "bold"), fg=MUTED, bg=BG
        ).pack(side="left", padx=(14, 0), pady=(10, 0))

        self.clock = tk.Label(
            title_row, text="", font=("Menlo", 10),
            fg=PURPLE, bg=BG
        )
        self.clock.pack(side="right", pady=(8, 0))

        tk.Label(
            header, text="YOUR PERSONAL AI • LIVE SYSTEM TELEMETRY",
            font=("Helvetica", 9, "bold"), fg=MUTED, bg=BG
        ).pack(anchor="w", pady=(5, 0))

        # Siri-like orb area
        self.hero = tk.Frame(root, bg=BG, height=220)
        self.hero.pack(fill="x", padx=20, pady=(0, 2))
        self.hero.pack_propagate(False)

        self.orb_canvas = tk.Canvas(
            self.hero, bg=BG, highlightthickness=0, height=190
        )
        self.orb_canvas.pack(fill="both", expand=True)

        self.orb_status = tk.Label(
            self.hero, text="READY WHEN YOU ARE",
            font=("Helvetica", 10, "bold"), fg=CYAN, bg=BG
        )
        self.orb_status.pack(pady=(0, 8))

        controls = tk.Frame(root, bg=BG)
        controls.pack(fill="x", padx=26, pady=(0, 8))

        # Use styled Labels as buttons: macOS Aqua can ignore Tk Button
        # background/foreground colours, which made white text disappear.
        self.listen_button = tk.Label(
            controls, text="◉  ACTIVATE LISTENING",
            bg="#0B5268", fg="#FFFFFF", padx=18, pady=10,
            highlightthickness=1, highlightbackground=CYAN,
            font=("Helvetica", 9, "bold"), cursor="hand2"
        )
        self.listen_button.pack(side="left")
        self.listen_button.bind("<Button-1>", lambda _event: self.toggle_listening())
        self.listen_button.bind("<Enter>", lambda _event: self.listen_button.config(bg="#117E96" if not self._listening else "#8056C4"))
        self.listen_button.bind("<Leave>", lambda _event: self.listen_button.config(bg="#65409B" if self._listening else "#0B5268"))

        refresh_button = tk.Label(
            controls, text="↻  REFRESH SYSTEM",
            bg="#39265F", fg="#FFFFFF", padx=18, pady=10,
            highlightthickness=1, highlightbackground=PURPLE,
            font=("Helvetica", 9, "bold"), cursor="hand2"
        )
        refresh_button.pack(side="right")
        refresh_button.bind("<Button-1>", lambda _event: self.refresh())
        refresh_button.bind("<Enter>", lambda _event: refresh_button.config(bg="#62409B"))
        refresh_button.bind("<Leave>", lambda _event: refresh_button.config(bg="#39265F"))

        # Modern message / command composer (UI only; does not run shell commands)
        composer = tk.Frame(root, bg="#0C1423", highlightbackground="#28415F", highlightthickness=1)
        composer.pack(fill="x", padx=24, pady=(0, 7))
        tk.Label(
            composer, text="JARVIS MESSAGE", font=("Helvetica", 8, "bold"),
            fg=CYAN, bg="#0C1423"
        ).pack(anchor="w", padx=12, pady=(8, 2))
        composer_row = tk.Frame(composer, bg="#0C1423")
        composer_row.pack(fill="x", padx=10, pady=(0, 9))
        self.message_input = tk.Entry(
            composer_row, bg="#111D30", fg=WHITE, insertbackground=CYAN,
            relief="flat", bd=0, font=("Helvetica", 11),
            highlightthickness=1, highlightbackground="#263A57",
            highlightcolor=CYAN
        )
        self.message_input.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self.message_input.insert(0, "Type a message to Jarvis…")
        self.message_input.config(fg=MUTED)
        self.message_input.bind("<FocusIn>", self._message_focus_in)
        self.message_input.bind("<Return>", self.send_message)
        self.send_button = tk.Label(
            composer_row, text="SEND  ↗", bg="#087F8C", fg="#FFFFFF",
            padx=20, pady=9, highlightthickness=1,
            highlightbackground=CYAN, font=("Helvetica", 9, "bold"), cursor="hand2"
        )
        self.send_button.pack(side="right")
        self.send_button.bind("<Button-1>", lambda _event: self.send_message())
        self.send_button.bind("<Enter>", lambda _event: self.send_button.config(bg="#0AA6B5"))
        self.send_button.bind("<Leave>", lambda _event: self.send_button.config(bg="#087F8C"))
        self.message_feedback = tk.Label(
            composer, text="Message UI ready • connect your existing Jarvis handler to enable replies",
            font=("Helvetica", 8), fg=MUTED, bg="#0C1423", anchor="w"
        )
        self.message_feedback.pack(fill="x", padx=12, pady=(0, 7))

        # Compact telemetry panels
        self.cards_frame = tk.Frame(root, bg=BG)
        self.cards_frame.pack(fill="x", expand=False, padx=22, pady=(0, 6))
        for col in range(3):
            self.cards_frame.grid_columnconfigure(col, weight=1, uniform="metric")
        for row in range(2):
            self.cards_frame.grid_rowconfigure(row, weight=0, minsize=105)

        self.metrics = {}
        cards = [
            ("CPU", "cpu", CYAN),
            ("MEMORY / RAM", "ram", PURPLE),
            ("BATTERY", "battery", GREEN),
            ("STORAGE", "disk", BLUE),
            ("GPU", "gpu", PINK),
        ]

        for index, (label, key, color) in enumerate(cards):
            card = tk.Frame(
                self.cards_frame, bg="#0E182A",
                highlightbackground="#2A4263", highlightthickness=1
            )
            card.grid(
                row=index // 3, column=index % 3,
                sticky="nsew", padx=4, pady=4
            )

            tk.Label(
                card, text=label, font=("Helvetica", 8, "bold"),
                fg=MUTED, bg="#0E182A"
            ).pack(anchor="w", padx=10, pady=(8, 2))

            value = tk.Label(
                card, text="--", font=("Helvetica", 19, "bold"),
                fg=color, bg="#0E182A"
            )
            value.pack(anchor="w", padx=10)

            bar = tk.Canvas(
                card, height=4, bg="#263149", highlightthickness=0
            )
            bar.pack(fill="x", padx=10, pady=(5, 5))

            detail = tk.Label(
                card, text="Collecting data…",
                font=("Helvetica", 7), fg=MUTED, bg="#0E182A",
                anchor="w", justify="left", wraplength=240
            )
            detail.pack(fill="x", padx=10, pady=(0, 8))

            self.metrics[key] = {
                "value": value, "bar": bar, "detail": detail, "color": color
            }

        # Integrated live performance trends (same dashboard, no separate window).
        trends = tk.Frame(root, bg=BG)
        trends.pack(fill="x", padx=22, pady=(0, 5))
        for col in range(3):
            trends.grid_columnconfigure(col, weight=1, uniform="trend")

        self.trend_canvases = {}
        for col, (key, title, accent) in enumerate([
            ("cpu", "CPU HISTORY", CYAN),
            ("gpu", "GPU HISTORY", PINK),
            ("ram", "MEMORY HISTORY", PURPLE),
        ]):
            panel = tk.Frame(
                trends, bg="#0C1423",
                highlightbackground="#253B58", highlightthickness=1
            )
            panel.grid(row=0, column=col, sticky="ew", padx=4)
            tk.Label(
                panel, text=title, bg="#0C1423", fg=accent,
                font=("Helvetica", 7, "bold")
            ).pack(anchor="w", padx=8, pady=(5, 1))
            chart = tk.Canvas(
                panel, height=46, bg="#0C1423", highlightthickness=0
            )
            chart.pack(fill="x", padx=7, pady=(0, 5))
            self.trend_canvases[key] = (chart, accent)

        footer = tk.Frame(root, bg=BG)
        footer.pack(fill="x", padx=26, pady=(0, 8))
        self.status = tk.Label(
            footer, text="● SYSTEM ONLINE  /  TELEMETRY ACTIVE",
            font=("Menlo", 8, "bold"), fg=GREEN, bg=BG
        )
        self.status.pack(side="left")
        tk.Label(
            footer, text=f"DEVICE  /  {platform.machine()}",
            font=("Menlo", 8), fg=MUTED, bg=BG
        ).pack(side="right")

        self.root.bind("<Configure>", self._resize_orb)
        self.refresh()
        self._animate_orb()

    def toggle_listening(self):
        # UI state only; this button does not start the separate voice engine.
        self._listening = not self._listening
        if self._listening:
            self.orb_status.config(text="LISTENING MODE • VOICE ENGINE NOT CONNECTED", fg=PURPLE)
            self.listen_button.config(text="◉  STOP LISTENING", fg="#FFFFFF", bg="#65409B")
        else:
            self.orb_status.config(text="READY WHEN YOU ARE", fg=CYAN)
            self.listen_button.config(text="◉  ACTIVATE LISTENING", fg="#FFFFFF", bg="#0B5268")

    def _message_focus_in(self, _event=None):
        if self.message_input.get() == "Type a message to Jarvis…":
            self.message_input.delete(0, "end")
            self.message_input.config(fg=WHITE)

    def send_message(self, _event=None):
        message = self.message_input.get().strip()
        if not message or message == "Type a message to Jarvis…":
            self.message_feedback.config(text="Pehle message type kar, bhai.", fg=RED)
            return
        self.message_feedback.config(
            text=f'Message entered: “{message[:100]}” • UI ready; command handler not connected',
            fg=GREEN
        )
        self.message_input.delete(0, "end")

    def _resize_orb(self, _event=None):
        # Redraw on resize without changing the window's other widgets.
        if hasattr(self, "orb_canvas"):
            self._draw_orb()

    def _draw_orb(self):
        canvas = self.orb_canvas
        canvas.delete("orb")
        width = max(canvas.winfo_width(), 300)
        height = max(canvas.winfo_height(), 200)
        cx, cy = width / 2, height / 2
        pulse = (math.sin(self._animation_step / 7) + 1) / 2
        listening_boost = 1.0 if self._listening else 0.0

        # Soft outer rings
        for i in range(5):
            radius = 49 + i * 13 + pulse * (4 + listening_boost * 5)
            color = ["#172844", "#1B2D4C", "#23335A", "#29305B", "#302A5A"][i]
            canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                outline=color, width=1 + (i == 0), tags="orb"
            )

        # Glowing orb made from layered ovals (Tkinter-compatible)
        base = 43 + pulse * 4 + listening_boost * 5
        layers = [
            (base + 18, "#182B4B"),
            (base + 12, "#243568"),
            (base + 6, "#315A91"),
            (base, "#4B78C7"),
            (base - 8, "#6B7FE3"),
            (base - 15, "#8E8DF2"),
            (base - 21, "#B6A6FF"),
        ]
        for radius, color in layers:
            canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=color, outline="", tags="orb"
            )

        # Iridescent highlights and floating signal dots
        canvas.create_oval(
            cx - base * 0.55, cy - base * 0.68,
            cx + base * 0.05, cy - base * 0.08,
            fill="#D9F8FF", outline="", tags="orb"
        )
        canvas.create_oval(
            cx + base * 0.05, cy + base * 0.02,
            cx + base * 0.58, cy + base * 0.53,
            fill="#E6B8FF", outline="", tags="orb"
        )
        for i in range(12):
            angle = (self._animation_step * 0.035) + (i * math.tau / 12)
            radius = 88 + 5 * math.sin(self._animation_step / 5 + i)
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius * 0.63
            dot_color = CYAN if i % 2 == 0 else PURPLE
            dot_size = 2 + (i % 3 == 0)
            canvas.create_oval(
                x - dot_size, y - dot_size, x + dot_size, y + dot_size,
                fill=dot_color, outline="", tags="orb"
            )

        canvas.create_text(
            cx, cy + base + 31, text="J.A.R.V.I.S",
            fill="#AAB8D8", font=("Menlo", 8, "bold"), tags="orb"
        )

    def _animate_orb(self):
        self._animation_step += 1
        self._draw_orb()
        self.root.after(45, self._animate_orb)

    def _update_trend(self, key, value):
        values = self._history[key]
        values.append(max(0.0, min(100.0, float(value))))
        del values[:-self._history_limit]
        canvas, color = self.trend_canvases[key]
        canvas.delete("trend")
        width = max(canvas.winfo_width(), 100)
        height = max(canvas.winfo_height(), 30)
        # faint horizontal guide lines
        for fraction in (0.25, 0.5, 0.75):
            y = height * fraction
            canvas.create_line(0, y, width, y, fill="#1B2B43", tags="trend")
        if len(values) < 2:
            return
        points = []
        for index, sample in enumerate(values):
            x = 3 + (width - 6) * index / max(1, len(values) - 1)
            y = height - 3 - (height - 6) * sample / 100.0
            points.extend((x, y))
        canvas.create_line(
            *points, fill=color, width=2, smooth=True, splinesteps=12, tags="trend"
        )

    def set_metric(self, key, percent, detail):
        metric = self.metrics[key]
        percent = max(0.0, min(100.0, float(percent)))
        metric["value"].config(text=f"{percent:.1f}%")
        metric["detail"].config(text=detail)

        bar = metric["bar"]
        bar.update_idletasks()
        bar.delete("all")
        width = max(bar.winfo_width(), 1)
        bar.create_rectangle(
            0, 0, width * percent / 100, 5,
            fill=metric["color"], outline=""
        )

    def _read_gpu(self):
        try:
            result = subprocess.run(
                [
                    "sudo", "-n", "/usr/bin/powermetrics",
                    "--samplers", "gpu_power", "-i", "1000", "-n", "1"
                ],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout + result.stderr

            if result.returncode != 0:
                error = result.stderr.strip()
                if "password" in error.lower() or "sudo" in error.lower():
                    detail = "GPU permission unavailable"
                else:
                    detail = error[:90] or "powermetrics failed"
                self._gpu_data = (0.0, detail)
                return

            usage = re.search(
                r"GPU HW active residency:\s*([\d.]+)%",
                output
            )
            power = re.search(r"GPU Power:\s*([\d.]+)\s*(mW|W)", output)

            if usage:
                percent = float(usage.group(1))
                power_text = (
                    f"{power.group(1)} {power.group(2)}" if power else "unavailable"
                )
                self._gpu_data = (percent, f"Apple GPU • {power_text}")
            else:
                self._gpu_data = (0.0, "GPU usage data not found")
        except (subprocess.TimeoutExpired, OSError) as error:
            self._gpu_data = (0.0, str(error)[:90])
        finally:
            self._gpu_check_running = False

    def refresh(self):
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            battery = psutil.sensors_battery()
            disk = shutil.disk_usage("/")

            if not self._gpu_check_running:
                self._gpu_check_running = True
                threading.Thread(target=self._read_gpu, daemon=True).start()

            gpu_usage, gpu_detail = self._gpu_data
            self.set_metric("gpu", gpu_usage, gpu_detail)
            self.set_metric("cpu", cpu, f"{psutil.cpu_count()} logical CPU cores")
            self._update_trend("cpu", cpu)
            self._update_trend("gpu", gpu_usage)
            self._update_trend("ram", memory.percent)
            self.set_metric(
                "ram", memory.percent,
                f"{memory.used / (1024**3):.1f} GB used • "
                f"{memory.available / (1024**3):.1f} GB available"
            )

            if battery is not None:
                charging = "Plugged in" if battery.power_plugged else "On battery"
                remaining = (
                    f"{battery.secsleft // 3600}h "
                    f"{(battery.secsleft % 3600) // 60}m remaining"
                    if battery.secsleft > 0 else "Time unavailable"
                )
                self.set_metric("battery", battery.percent, f"{charging} • {remaining}")
            else:
                self.set_metric("battery", 0, "Battery data unavailable")

            disk_percent = disk.used / disk.total * 100
            self.set_metric(
                "disk", disk_percent,
                f"{disk.free / (1024**3):.1f} GB free • Macintosh HD"
            )

            self.clock.config(text=datetime.now().strftime("%d %b  |  %I:%M:%S %p"))
            self.status.config(text="● SYSTEM ONLINE  /  TELEMETRY ACTIVE", fg=GREEN)
        except Exception as error:
            self.status.config(text=f"● MONITOR ERROR: {error}", fg=RED)

        self.root.after(2000, self.refresh)


def main():
    root = tk.Tk()
    SystemMonitor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
