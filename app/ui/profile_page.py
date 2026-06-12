import re
import customtkinter as ctk
from app.repositories.user_repository import UserRepository

CARD_BG = "#0D1B2A"
BORDER = "#1E3A5F"
TEXT_MAIN = "#F0F6FF"
TEXT_MUTED = "#64748B"
INPUT_BG = "#060F1C"


class ProfilePage(ctk.CTkFrame):
    def __init__(self, master, current_user, on_update_callback):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.repository = UserRepository()
        self.current_user = current_user
        self.on_update_callback = on_update_callback  # Para atualizar o nome na sidebar se mudar

        self.build()

    def build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 20))
        ctk.CTkLabel(header, text="Meu Perfil", font=("Inter", 24, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(header, text="Atualize suas informações pessoais e credenciais.", font=("Inter", 13),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=24, pady=(0, 20))

        # Nome e Email
        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(20, 10))

        col_name = ctk.CTkFrame(row1, fg_color="transparent")
        col_name.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col_name, text="Nome Completo", font=("Inter", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.entry_name = ctk.CTkEntry(col_name, placeholder_text="Nome Completo", height=38, fg_color=INPUT_BG,
                                       border_color=BORDER)
        self.entry_name.pack(fill="x")
        self.entry_name.insert(0, self.current_user.full_name)

        col_email = ctk.CTkFrame(row1, fg_color="transparent")
        col_email.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(col_email, text="E-mail", font=("Inter", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.entry_email = ctk.CTkEntry(col_email, placeholder_text="E-mail", height=38, fg_color=INPUT_BG,
                                        border_color=BORDER)
        self.entry_email.pack(fill="x")
        self.entry_email.insert(0, self.current_user.email)

        # Username, Senha e Role
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        col_user = ctk.CTkFrame(row2, fg_color="transparent")
        col_user.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col_user, text="Nome de Usuário", font=("Inter", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.entry_user = ctk.CTkEntry(col_user, placeholder_text="Nome de Usuário", height=38, fg_color=INPUT_BG,
                                       border_color=BORDER)
        self.entry_user.pack(fill="x")
        self.entry_user.insert(0, self.current_user.username)

        col_pass = ctk.CTkFrame(row2, fg_color="transparent")
        col_pass.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col_pass, text="Nova Senha", font=("Inter", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.entry_pass = ctk.CTkEntry(col_pass, placeholder_text="Deixe em branco para manter", show="*",
                                       height=38, fg_color=INPUT_BG, border_color=BORDER)
        self.entry_pass.pack(fill="x")

        col_role = ctk.CTkFrame(row2, fg_color="transparent")
        col_role.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(col_role, text="Nível de Acesso", font=("Inter", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.opt_role = ctk.CTkOptionMenu(col_role, values=["ESTOQUISTA", "GERENTE"], height=38, fg_color=INPUT_BG,
                                          button_color=BORDER)
        self.opt_role.pack(fill="x")
        self.opt_role.set(self.current_user.role)

        # REGRA DE NEGÓCIO: Se não for gerente, desabilita a edição da Role
        if self.current_user.role != "GERENTE":
            self.opt_role.configure(state="disabled", button_color="#0D1B2A")

        # Botão Salvar
        row3 = ctk.CTkFrame(card, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(0, 20))

        self.lbl_msg = ctk.CTkLabel(row3, text="", font=("Inter", 12))
        self.lbl_msg.pack(side="left")

        ctk.CTkButton(row3, text="Salvar Alterações", height=38, fg_color="#2563EB", hover_color="#1D4ED8",
                      font=("Inter", 13, "bold"), command=self.handle_update).pack(side="right")

    def handle_update(self):
        name = self.entry_name.get()
        email = self.entry_email.get()
        user = self.entry_user.get()
        new_pwd = self.entry_pass.get()
        role = self.opt_role.get()

        if not all([name, email, user]):
            self.lbl_msg.configure(text="Nome, Email e Usuário são obrigatórios.", text_color="#EF4444")
            return

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            self.lbl_msg.configure(text="Formato de e-mail inválido.", text_color="#EF4444")
            return

        if new_pwd and len(new_pwd) < 6:
            self.lbl_msg.configure(text="A nova senha deve ter no mínimo 6 caracteres.", text_color="#EF4444")
            return

        try:
            updated_user = self.repository.update_profile(
                user_id=self.current_user.id,
                full_name=name,
                email=email,
                username=user,
                role=role,
                new_password=new_pwd if new_pwd else None
            )
            self.lbl_msg.configure(text="Perfil atualizado com sucesso!", text_color="#10B981")
            self.entry_pass.delete(0, 'end')

            # Avisa o main.py que o usuário mudou (para atualizar o nome na sidebar, por exemplo)
            self.on_update_callback(updated_user)

        except Exception as e:
            self.lbl_msg.configure(text=f"Erro ao salvar: {e}", text_color="#EF4444")