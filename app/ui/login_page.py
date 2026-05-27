import customtkinter as ctk
from app.repositories.auth_repository import AuthRepository


class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color="#020617")
        self.pack(fill="both", expand=True)
        self.on_success = on_success
        self.repo = AuthRepository()

        self.build()

    def build(self):
        # Card centralizado
        card = ctk.CTkFrame(self, fg_color="#0D1B2A", corner_radius=16, border_width=1, border_color="#1E3A5F")
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="Armazém 4 irmãos", font=("Inter", 24, "bold"), text_color="#F8FAFC").pack(
            pady=(30, 10), padx=40)
        ctk.CTkLabel(card, text="Faça login para continuar", font=("Inter", 12), text_color="#64748B").pack(
            pady=(0, 20))

        self.user_entry = ctk.CTkEntry(card, placeholder_text="Usuário", width=250, height=40, fg_color="#060F1C",
                                       border_color="#1E3A5F")
        self.user_entry.pack(pady=(0, 15), padx=30)

        self.pass_entry = ctk.CTkEntry(card, placeholder_text="Senha", show="*", width=250, height=40,
                                       fg_color="#060F1C", border_color="#1E3A5F")
        self.pass_entry.pack(pady=(0, 20), padx=30)

        self.error_label = ctk.CTkLabel(card, text="", text_color="#EF4444", font=("Inter", 11))
        self.error_label.pack(pady=(0, 10))

        ctk.CTkButton(card, text="Entrar", height=40, font=("Inter", 14, "bold"), fg_color="#2563EB",
                      hover_color="#1D4ED8", command=self.handle_login).pack(pady=(0, 30), padx=30, fill="x")

    def handle_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        user = self.repo.authenticate(username, password)
        if user:
            self.on_success(user)
        else:
            self.error_label.configure(text="Usuário ou senha inválidos.")