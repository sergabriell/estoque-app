import customtkinter as ctk

from app.database.init_db import init_db
from app.ui.products_page import ProductsPage
from app.ui.suppliers_page import SuppliersPage
from app.ui.dashboard_page import DashboardPage
from app.ui.movements_page import MovementsPage


DASHBOARD_COLOR = "#1E3A8A"
PRODUCTS_COLOR = "#2563EB"
SUPPLIERS_COLOR = "#7C3AED"
MOVEMENTS_COLOR = "#166534"

DEFAULT_BUTTON = "#1E293B"
HOVER_BUTTON = "#334155"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_db()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Armazem 4 irmãos")
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.configure(fg_color="#020617")

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0F172A")
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(self, fg_color="#020617")
        self.content.pack(side="right", fill="both", expand=True)

        self.build_sidebar()
        self.show_dashboard()

    def build_sidebar(self):
        ctk.CTkLabel(
            self.sidebar,
            text="Armazem\n4 irmãos",
            font=("Inter", 28, "bold"),
            justify="left",
            text_color="#F8FAFC",
        ).pack(anchor="w", padx=24, pady=(32, 8))

        ctk.CTkLabel(
            self.sidebar,
            text="Controle de estoque",
            font=("Inter", 13),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=24, pady=(0, 28))

        self.dashboard_button = self.sidebar_button(
            "📊 Dashboard",
            self.show_dashboard
        )

        self.products_button = self.sidebar_button(
            "📦 Produtos",
            self.show_products
        )

        self.suppliers_button = self.sidebar_button(
            "🏢 Fornecedores",
            self.show_suppliers
        )

        self.movements_button = self.sidebar_button(
            "🔁 Movimentações",
            self.show_movements
        )

        ctk.CTkLabel(
            self.sidebar,
            text="SQLite • SQLAlchemy • CustomTkinter",
            text_color="#64748B",
            font=("Inter", 12),
        ).pack(side="bottom", padx=20, pady=22)

    def sidebar_button(self, text, command):
        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            height=44,
            anchor="w",
            corner_radius=12,
            fg_color=DEFAULT_BUTTON,
            hover_color=HOVER_BUTTON,
            command=command,
        )
        button.pack(fill="x", padx=18, pady=6)
        return button

    def reset_sidebar_buttons(self):
        self.dashboard_button.configure(fg_color=DEFAULT_BUTTON)
        self.products_button.configure(fg_color=DEFAULT_BUTTON)
        self.suppliers_button.configure(fg_color=DEFAULT_BUTTON)
        self.movements_button.configure(fg_color=DEFAULT_BUTTON)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.reset_sidebar_buttons()
        self.dashboard_button.configure(fg_color=DASHBOARD_COLOR)
        self.clear_content()
        DashboardPage(self.content)

    def show_products(self):
        self.reset_sidebar_buttons()
        self.products_button.configure(fg_color=PRODUCTS_COLOR)
        self.clear_content()
        ProductsPage(self.content)

    def show_suppliers(self):
        self.reset_sidebar_buttons()
        self.suppliers_button.configure(fg_color=SUPPLIERS_COLOR)
        self.clear_content()
        SuppliersPage(self.content)

    def show_movements(self):
        self.reset_sidebar_buttons()
        self.movements_button.configure(fg_color=MOVEMENTS_COLOR)
        self.clear_content()
        MovementsPage(self.content)

if __name__ == "__main__":
    App().mainloop()