import tkinter as tk


BG = "#080B12"
CARD = "#111827"
CYAN = "#00E5FF"
WHITE = "#F8FAFC"
GREY = "#94A3B8"
GREEN = "#22C55E"


class VoiceAuthUI:
    def __init__(self, root):
        self.root = root

        root.title("Jarvis • Voice Security")
        root.geometry("700x600")
        root.resizable(False, False)
        root.configure(bg=BG)

        # ---------- HEADER ----------
        tk.Label(
            root,
            text="JARVIS",
            font=("Helvetica", 30, "bold"),
            fg=CYAN,
            bg=BG
        ).pack(pady=(35, 0))

        tk.Label(
            root,
            text="VOICE SECURITY",
            font=("Helvetica", 12, "bold"),
            fg=GREY,
            bg=BG
        ).pack(pady=(3, 25))

        # ---------- MAIN CARD ----------
        card = tk.Frame(
            root,
            bg=CARD,
            width=580,
            height=380
        )
        card.pack()
        card.pack_propagate(False)

        # Voice icon
        tk.Label(
            card,
            text="🎙",
            font=("Helvetica", 55),
            fg=CYAN,
            bg=CARD
        ).pack(pady=(25, 5))

        tk.Label(
            card,
            text="VOICE LOCK",
            font=("Helvetica", 18, "bold"),
            fg=WHITE,
            bg=CARD
        ).pack()

        tk.Label(
            card,
            text="Your voice will be used to authenticate Jarvis",
            font=("Helvetica", 11),
            fg=GREY,
            bg=CARD
        ).pack(pady=(5, 25))

        # Status box
        status_frame = tk.Frame(card, bg="#0B1220")
        status_frame.pack(fill="x", padx=45)

        self.status = tk.Label(
            status_frame,
            text="●  VOICE NOT REGISTERED",
            font=("Helvetica", 12, "bold"),
            fg="#F59E0B",
            bg="#0B1220"
        )
        self.status.pack(pady=15)

        # Register button
        self.button = tk.Button(
            card,
            text="🎙  REGISTER MY VOICE",
            font=("Helvetica", 13, "bold"),
            fg=BG,
            bg=CYAN,
            activebackground="#67E8F9",
            activeforeground=BG,
            relief="flat",
            bd=0,
            padx=35,
            pady=13,
            cursor="hand2",
            command=self.register_voice
        )
        self.button.pack(pady=30)

        # ---------- SECURITY ----------
        tk.Label(
            root,
            text="🔒  VOICE AUTHENTICATION",
            font=("Helvetica", 11, "bold"),
            fg=GREY,
            bg=BG
        ).pack(pady=(25, 5))

        self.security = tk.Label(
            root,
            text="INACTIVE",
            font=("Helvetica", 12, "bold"),
            fg="#F59E0B",
            bg=BG
        )
        self.security.pack()

    def register_voice(self):
        self.status.config(
            text="●  LISTENING FOR YOUR VOICE",
            fg=CYAN
        )

        self.button.config(
            text="🎙  LISTENING...",
            state="disabled",
            bg="#334155",
            fg=WHITE
        )

        self.root.after(3000, self.register_complete)

    def register_complete(self):
        self.status.config(
            text="●  VOICE REGISTERED",
            fg=GREEN
        )

        self.security.config(
            text="ACTIVE ✓",
            fg=GREEN
        )

        self.button.config(
            text="✓  VOICE REGISTERED",
            state="normal",
            bg=GREEN,
            fg=BG
        )


if __name__ == "__main__":
    root = tk.Tk()
    VoiceAuthUI(root)
    root.mainloop()