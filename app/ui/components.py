import customtkinter as ctk

FONT_TITLE = ("Inter", 26, "bold")
FONT_SUBTITLE = ("Inter", 15)
FONT_CARD_TITLE = ("Inter", 18, "bold")

class ModernCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=18,
            border_width=1,
            border_color="#243044",
            fg_color="#111827",
            **kwargs,
        )

class PageHeader(ctk.CTkFrame):
    def __init__(self, master, title: str, subtitle: str):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=title, font=FONT_TITLE, text_color="#F9FAFB").pack(anchor="w")
        ctk.CTkLabel(self, text=subtitle, font=FONT_SUBTITLE, text_color="#9CA3AF").pack(anchor="w", pady=(4, 0))

def input_field(master, placeholder: str):
    return ctk.CTkEntry(
        master,
        placeholder_text=placeholder,
        height=42,
        corner_radius=12,
        border_width=1,
        fg_color="#0B1220",
        border_color="#334155",
    )
