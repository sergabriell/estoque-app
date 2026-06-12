import customtkinter as ctk

from app.database.init_db import init_db
from app.ui.products_page import ProductsPage
from app.ui.suppliers_page import SuppliersPage
from app.ui.dashboard_page import DashboardPage
from app.ui.movements_page import MovementsPage
from app.ui.login_page import LoginPage
from app.ui.users_page import UsersPage
from app.ui.profile_page import ProfilePage

DASHBOARD_COLOR = "#1E3A8A"
PRODUCTS_COLOR = "#2563EB"
SUPPLIERS_COLOR = "#7C3AED"
MOVEMENTS_COLOR = "#166534"

DEFAULT_BUTTON = "#1E293B"
HOVER_BUTTON = "#334155"
USERS_COLOR = "#EA580C"
PROFILE_COLOR = "#0891B2"


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

        self.current_user = None

        self.content = ctk.CTkFrame(self, fg_color="#020617")
        self.content.pack(side="right", fill="both", expand=True)


        self.show_login()

    def show_login(self):
        self.clear_content()
        LoginPage(self.content, on_success=self.process_login)

    def process_login(self, user):
        self.current_user = user
        self.clear_content()

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0F172A")
        self.sidebar.pack(side="left", fill="y", before=self.content)

        self.build_sidebar()

        # Redirecionamento inicial baseado na role
        if self.current_user.role == "GERENTE":
            self.show_dashboard()
        else:
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
            self.sidebar, text=f"Olá, {self.current_user.full_name}",
            font=("Inter", 14, "bold"), text_color="#F8FAFC"
        ).pack(anchor="w", padx=24, pady=(0, 2))

        role_name = "Gerente" if self.current_user.role == "GERENTE" else "Estoquista"
        ctk.CTkLabel(
            self.sidebar, text=f"Acesso: {role_name}",
            font=("Inter", 12), text_color="#10B981"
        ).pack(anchor="w", padx=24, pady=(0, 28))

        ctk.CTkLabel(
            self.sidebar,
            text="Controle de estoque",
            font=("Inter", 13),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=24, pady=(0, 28))

        # Lista para armazenar os botões criados
        self.buttons = []

        # --- CONTROLE DE ACESSO (RBAC) ---
        # Só cria e adiciona o botão de Dashboard se for Gerente
        if self.current_user.role == "GERENTE":
            self.dashboard_button = self.sidebar_button("📊 Dashboard", self.show_dashboard)
            self.buttons.append(self.dashboard_button)
            self.users_button = self.sidebar_button("👥 Usuários", self.show_users)
            self.buttons.append(self.users_button)

        self.products_button = self.sidebar_button("📦 Produtos", self.show_products)
        self.buttons.append(self.products_button)

        self.suppliers_button = self.sidebar_button("🏢 Fornecedores", self.show_suppliers)
        self.buttons.append(self.suppliers_button)

        self.movements_button = self.sidebar_button("🔁 Movimentações", self.show_movements)
        self.buttons.append(self.movements_button)

        self.profile_button = self.sidebar_button("👤 Meu Perfil", self.show_profile)
        self.buttons.append(self.profile_button)


        ctk.CTkButton(
            self.sidebar, text="Sair", fg_color="transparent", hover_color="#3B1212",
            text_color="#EF4444", command=self.logout
        ).pack(side="bottom", pady=20, padx=20, fill="x")

        ctk.CTkLabel(
            self.sidebar,
            text="SQLite • SQLAlchemy\nCustomTkinter",
            text_color="#64748B",
            font=("Inter", 10),
        ).pack(side="bottom", padx=20, pady=0)

    def sidebar_button(self, text, command):
        button = ctk.CTkButton(
            self.sidebar, text=text, height=44, anchor="w", corner_radius=12,
            fg_color=DEFAULT_BUTTON, hover_color=HOVER_BUTTON, command=command,
        )
        button.pack(fill="x", padx=18, pady=6)
        return button

    def reset_sidebar_buttons(self):
        for btn in self.buttons:
            btn.configure(fg_color=DEFAULT_BUTTON)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def logout(self):
        self.current_user = None
        self.sidebar.destroy() # Remove a barra lateral inteira
        self.show_login()

    def show_dashboard(self):
        self.reset_sidebar_buttons()
        # Garantia extra para evitar erro se o botão não existir (ex: Estoquista)
        if hasattr(self, 'dashboard_button'):
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

    def show_users(self):
        self.reset_sidebar_buttons()
        if hasattr(self, 'users_button'):
            self.users_button.configure(fg_color=USERS_COLOR)
        self.clear_content()
        UsersPage(self.content, current_user_id=self.current_user.id)

    def show_profile(self):
        self.reset_sidebar_buttons()
        self.profile_button.configure(fg_color=PROFILE_COLOR)
        self.clear_content()

        ProfilePage(self.content, current_user=self.current_user, on_update_callback=self.update_current_user)

    def update_current_user(self, updated_user):
        self.current_user = updated_user

if __name__ == "__main__":
    App().mainloop()