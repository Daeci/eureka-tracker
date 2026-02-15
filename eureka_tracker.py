"""Eureka Moment Tracker - Track proc rates for Solid Reason / Ageless Words in FFXIV.

Connects to IINACT's OverlayPlugin WebSocket for real-time game event data.
Requires: IINACT Dalamud plugin running with WebSocket server enabled.
"""

import json
import threading
import tkinter as tk
from tkinter import ttk

import websocket

# --- Constants ---
IINACT_WS_URL = "ws://127.0.0.1:10501/ws"

# LogLine types (decimal strings as they appear in the line array)
TYPE_ABILITY = "21"   # NetworkAbility: line[3]=source, line[5]=ability name
TYPE_BUFF_GAIN = "26" # StatusAdd: line[3]=status name, line[6]=source name

TRACKED_ABILITIES = {"Solid Reason", "Ageless Words"}
TRACKED_BUFF = "Eureka Moment"


# --- IINACT WebSocket Listener ---

class IINACTListener:
    """Connects to IINACT WebSocket and dispatches relevant game events."""

    def __init__(self, on_ability, on_buff, on_status):
        """
        Args:
            on_ability: Called with (ability_name, timestamp_str) on tracked ability use.
            on_buff: Called with (buff_name, timestamp_str) on tracked buff gain.
            on_status: Called with (status_text,) for connection state changes.
        """
        self.on_ability = on_ability
        self.on_buff = on_buff
        self.on_status = on_status
        self._ws = None
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._ws:
            self._ws.close()
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.on_status("Connecting to IINACT...")
                self._ws = websocket.create_connection(
                    IINACT_WS_URL, timeout=5
                )
                self._ws.send(json.dumps({
                    "call": "subscribe",
                    "events": ["LogLine"],
                }))
                self.on_status("Connected — listening for ability uses")
                self._listen()
            except (ConnectionRefusedError, OSError, websocket.WebSocketException):
                if not self._stop_event.is_set():
                    self.on_status("Connection lost — retrying in 3s...")
                    self._stop_event.wait(3)
            finally:
                if self._ws:
                    try:
                        self._ws.close()
                    except Exception:
                        pass
                    self._ws = None

    def _listen(self):
        while not self._stop_event.is_set():
            try:
                raw = self._ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            except (websocket.WebSocketConnectionClosedException, OSError):
                break

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("type") != "LogLine":
                continue

            line = msg.get("line", [])
            if not line:
                continue

            line_type = line[0]
            timestamp = line[1] if len(line) > 1 else ""

            if line_type == TYPE_ABILITY and len(line) > 5:
                ability_name = line[5]
                if ability_name in TRACKED_ABILITIES:
                    self.on_ability(ability_name, timestamp)

            elif line_type == TYPE_BUFF_GAIN and len(line) > 3:
                buff_name = line[3]
                if buff_name == TRACKED_BUFF:
                    self.on_buff(buff_name, timestamp)


# --- GUI ---

class EurekaTrackerApp:
    """tkinter GUI for the Eureka Moment Tracker."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Eureka Moment Tracker")
        self.root.resizable(False, False)

        # Counters
        self.solid_reason_count = 0
        self.ageless_words_count = 0
        self.eureka_count = 0

        # Listener
        self.listener = None
        self.is_tracking = False

        self._build_gui()

    def _apply_dark_theme(self):
        BG = "#1e1e2e"
        FG = "#cdd6f4"
        BG_WIDGET = "#313244"
        BG_BUTTON = "#45475a"
        BORDER = "#585b70"

        self.root.configure(bg=BG)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=BG, foreground=FG, bordercolor=BORDER,
                         focuscolor=BG_BUTTON, fieldbackground=BG_WIDGET)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TFrame", background=BG)
        style.configure("TLabelframe", background=BG, foreground=FG,
                         bordercolor=BORDER, lightcolor=BG, darkcolor=BORDER)
        style.configure("TLabelframe.Label", background=BG, foreground=FG)
        style.configure("TButton", background=BG_BUTTON, foreground=FG,
                         bordercolor=BORDER, padding=(8, 4))
        style.map("TButton",
                   background=[("active", BORDER)],
                   foreground=[("active", FG)])
        style.configure("Status.TLabel", background=BG_WIDGET, foreground=FG,
                         bordercolor=BORDER, padding=(4, 2))

        # Store colors for dynamic use
        self._bg = BG
        self._fg_default = FG

    def _build_gui(self):
        root = self.root
        self._apply_dark_theme()
        root.configure(padx=12, pady=8)

        # --- Counters ---
        # Use tk.LabelFrame (not ttk) to get the label embedded in the border
        counter_frame = tk.LabelFrame(root, text="Counters", padx=10, pady=10,
                                      bg=self._bg, fg=self._fg_default,
                                      bd=2, relief="groove")
        counter_frame.pack(fill="x", pady=(0, 8))

        labels = [
            ("Solid Reason uses:", "sr_label"),
            ("Ageless Words uses:", "aw_label"),
            ("Total uses:", "total_label"),
            ("Eureka Moment procs:", "proc_label"),
            ("Proc rate:", "rate_label"),
        ]

        for i, (text, attr) in enumerate(labels):
            ttk.Label(counter_frame, text=text).grid(
                row=i, column=0, sticky="w", pady=2
            )
            lbl = ttk.Label(counter_frame, text="0", width=12, anchor="e")
            lbl.grid(row=i, column=1, sticky="e", padx=(12, 0), pady=2)
            setattr(self, attr, lbl)

        counter_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", pady=(0, 4))

        self.start_btn = ttk.Button(
            btn_frame, text="Start", command=self._toggle_tracking
        )
        self.start_btn.pack(side="left")

        self.reset_btn = ttk.Button(
            btn_frame, text="Reset", command=self._reset_counters
        )
        self.reset_btn.pack(side="left", padx=(6, 0))

        # --- Status bar ---
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(root, textvariable=self.status_var,
                           style="Status.TLabel", relief="sunken")
        status.pack(fill="x", pady=(4, 0))

    def _toggle_tracking(self):
        if self.is_tracking:
            self._stop_tracking()
        else:
            self._start_tracking()

    def _start_tracking(self):
        self.listener = IINACTListener(
            on_ability=self._on_ability,
            on_buff=self._on_buff,
            on_status=self._on_status,
        )
        self.listener.start()
        self.is_tracking = True
        self.start_btn.configure(text="Stop")

    def _stop_tracking(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.is_tracking = False
        self.start_btn.configure(text="Start")
        self.status_var.set("Stopped")

    def _reset_counters(self):
        self.solid_reason_count = 0
        self.ageless_words_count = 0
        self.eureka_count = 0
        self._update_display()

    def _on_ability(self, ability_name, timestamp):
        if ability_name == "Solid Reason":
            self.solid_reason_count += 1
        elif ability_name == "Ageless Words":
            self.ageless_words_count += 1
        self.root.after(0, self._update_display)
        ts_short = self._format_ts(timestamp)
        self.root.after(0, self._set_status, f"[{ts_short}] {ability_name}")

    def _on_buff(self, buff_name, timestamp):
        self.eureka_count += 1
        self.root.after(0, self._update_display)
        ts_short = self._format_ts(timestamp)
        self.root.after(0, self._set_status, f"[{ts_short}] Eureka Moment proc!")

    def _on_status(self, text):
        self.root.after(0, self._set_status, text)

    @staticmethod
    def _format_ts(timestamp):
        """Extract HH:MM:SS from IINACT's ISO timestamp."""
        try:
            return timestamp.split("T")[1].split(".")[0]
        except (IndexError, AttributeError):
            return "??:??:??"

    def _set_status(self, text):
        self.status_var.set(text)

    def _update_display(self):
        total = self.solid_reason_count + self.ageless_words_count

        self.sr_label.configure(text=str(self.solid_reason_count))
        self.aw_label.configure(text=str(self.ageless_words_count))
        self.total_label.configure(text=str(total))
        self.proc_label.configure(text=str(self.eureka_count))

        if total > 0:
            rate = self.eureka_count / total * 100
            self.rate_label.configure(
                text=f"{rate:.1f}%",
                foreground="#a6e3a1" if rate >= 50 else "#f38ba8",
            )
        else:
            self.rate_label.configure(text="—", foreground=self._fg_default)

    def run(self):
        self.root.mainloop()
        if self.listener:
            self.listener.stop()


if __name__ == "__main__":
    app = EurekaTrackerApp()
    app.run()
