import customtkinter as ctk
from app.database.init_db import init_db
from app.ui.products_page import ProductsPage
from app.ui.suppliers_page import SuppliersPage

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
        self.show_products()

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
            text="Produtos e fornecedores",
            font=("Inter", 13),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=24, pady=(0, 28))

        self.products_button = ctk.CTkButton(
            self.sidebar,
            text="📦 Produtos",
            height=44,
            anchor="w",
            corner_radius=12,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.show_products,
        )
        self.products_button.pack(fill="x", padx=18, pady=6)

        self.suppliers_button = ctk.CTkButton(
            self.sidebar,
            text="🏢 Fornecedores",
            height=44,
            anchor="w",
            corner_radius=12,
            fg_color="#1E293B",
            hover_color="#334155",
            command=self.show_suppliers,
        )
        self.suppliers_button.pack(fill="x", padx=18, pady=6)

        ctk.CTkLabel(
            self.sidebar,
            text="SQLite • SQLAlchemy • CustomTkinter",
            text_color="#64748B",
            font=("Inter", 12),
        ).pack(side="bottom", padx=20, pady=22)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_products(self):
        self.products_button.configure(fg_color="#2563EB")
        self.suppliers_button.configure(fg_color="#1E293B")
        self.clear_content()
        ProductsPage(self.content)

    def show_suppliers(self):
        self.products_button.configure(fg_color="#1E293B")
        self.suppliers_button.configure(fg_color="#7C3AED")
        self.clear_content()
        SuppliersPage(self.content)

if __name__ == "__main__":
    App().mainloop()
