import customtkinter as ctk

from app.ui.components import ModernCard, PageHeader, FONT_CARD_TITLE


class MovementsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.build()

    def build(self):
        PageHeader(
            self,
            "Movimentações",
            "Registre entradas e saídas de produtos do estoque."
        ).pack(fill="x", padx=24, pady=(24, 16))

        card = ModernCard(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        ctk.CTkLabel(
            card,
            text="Página de movimentações",
            font=FONT_CARD_TITLE,
            text_color="#F9FAFB",
        ).pack(anchor="w", padx=18, pady=(18, 8))

        ctk.CTkLabel(
            card,
            text="Em breve aqui ficará o formulário de entrada e saída de produtos.",
            text_color="#9CA3AF",
            font=("Inter", 15),
        ).pack(anchor="w", padx=18, pady=8)