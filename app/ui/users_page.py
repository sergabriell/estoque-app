import re
import customtkinter as ctk
from app.repositories.user_repository import UserRepository

CARD_BG = "#0D1B2A"
BORDER = "#1E3A5F"
TEXT_MAIN = "#F0F6FF"
TEXT_MUTED = "#64748B"
INPUT_BG = "#060F1C"


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, on_confirm, on_cancel=None):
        super().__init__(master)
        self.title(title)
        self.geometry("420x200")
        self.configure(fg_color="#0D1B2A")
        self.resizable(False, False)

        # Faz o modal ficar no topo e travar a janela de trás
        self.transient(master)
        self.grab_set()

        # Centralizar na tela
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - 210
        y = master.winfo_y() + (master.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        ctk.CTkLabel(self, text=title, font=("Inter", 18, "bold"), text_color="#F0F6FF").pack(pady=(24, 10))
        ctk.CTkLabel(self, text=message, font=("Inter", 13), text_color="#64748B", wraplength=360).pack(pady=(0, 24))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=10)

        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#1E293B", hover_color="#334155", command=self.cancel).pack(
            side="left", expand=True, padx=10)
        ctk.CTkButton(btn_frame, text="Confirmar", fg_color="#2563EB", hover_color="#1D4ED8",
                      command=self.confirm).pack(side="right", expand=True, padx=10)

    def confirm(self):
        self.on_confirm()
        self.destroy()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()

class UsersPage(ctk.CTkFrame):
    def __init__(self, master, current_user_id):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.repository = UserRepository()
        self.current_user_id = current_user_id

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=24)

        self.build_header()
        self.build_form()

        # Container para a lista ser atualizada dinamicamente
        self.list_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.list_container.pack(fill="x", pady=(20, 0))

        self.load_users()

    def build_header(self):
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Gestão de Usuários", font=("Inter", 24, "bold"), text_color=TEXT_MAIN).pack(
            anchor="w")
        ctk.CTkLabel(header, text="Cadastre e gerencie o acesso ao sistema.", font=("Inter", 13),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(4, 0))

    def build_form(self):
        card = ctk.CTkFrame(self.scroll, fg_color=CARD_BG, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card, text="Novo Usuário", font=("Inter", 16, "bold"), text_color=TEXT_MAIN).pack(anchor="w",
                                                                                                       padx=20,
                                                                                                       pady=(16, 10))

        # Linha 1: Nome e Email
        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_name = ctk.CTkEntry(row1, placeholder_text="Nome Completo", height=38, fg_color=INPUT_BG,
                                       border_color=BORDER)
        self.entry_name.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.entry_email = ctk.CTkEntry(row1, placeholder_text="E-mail", height=38, fg_color=INPUT_BG,
                                        border_color=BORDER)
        self.entry_email.pack(side="left", fill="x", expand=True)

        # Linha 2: Username, Senha e Role
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        self.entry_user = ctk.CTkEntry(row2, placeholder_text="Nome de Usuário (Login)", height=38, fg_color=INPUT_BG,
                                       border_color=BORDER)
        self.entry_user.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.entry_pass = ctk.CTkEntry(row2, placeholder_text="Senha", show="*", height=38, fg_color=INPUT_BG,
                                       border_color=BORDER)
        self.entry_pass.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.opt_role = ctk.CTkOptionMenu(row2, values=["ESTOQUISTA", "GERENTE"], height=38, fg_color=INPUT_BG,
                                          button_color=BORDER, button_hover_color="#2563EB")
        self.opt_role.pack(side="left", fill="x", expand=True)

        # Linha 3: Botão e Mensagens de Erro
        row3 = ctk.CTkFrame(card, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(0, 20))

        self.lbl_msg = ctk.CTkLabel(row3, text="", font=("Inter", 12))
        self.lbl_msg.pack(side="left")

        ctk.CTkButton(row3, text="Cadastrar Usuário", height=38, fg_color="#10B981", hover_color="#059669",
                      font=("Inter", 13, "bold"), command=self.handle_save).pack(side="right")

    def handle_save(self):
        name = self.entry_name.get()
        email = self.entry_email.get()
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        role = self.opt_role.get()

        if not all([name, email, user, pwd]):
            self.lbl_msg.configure(text="Preencha todos os campos.", text_color="#EF4444")
            return

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            self.lbl_msg.configure(text="Formato de e-mail inválido.", text_color="#EF4444")
            return

        if len(pwd) < 6:
            self.lbl_msg.configure(text="A senha deve ter no mínimo 6 caracteres.", text_color="#EF4444")
            return

        try:
            self.repository.create(name, email, user, pwd, role)
            self.lbl_msg.configure(text="Usuário cadastrado com sucesso!", text_color="#10B981")

            # Limpa os campos
            for entry in [self.entry_name, self.entry_email, self.entry_user, self.entry_pass]:
                entry.delete(0, 'end')

            self.load_users()  # Recarrega a lista
        except ValueError as e:
            self.lbl_msg.configure(text=str(e), text_color="#EF4444")
        except Exception:
            self.lbl_msg.configure(text="Erro ao salvar no banco de dados.", text_color="#EF4444")

    def load_users(self):
        # Limpa a lista atual
        for widget in self.list_container.winfo_children():
            widget.destroy()

        users = self.repository.list_all()

        for user in users:
            row = ctk.CTkFrame(self.list_container, fg_color=CARD_BG, corner_radius=10, border_width=1,
                               border_color=BORDER)
            row.pack(fill="x", pady=4)

            # Verifica se essa linha é do usuário que está logado
            is_me = (user.id == self.current_user_id)

            opt_role = ctk.CTkOptionMenu(
                row, values=["ESTOQUISTA", "GERENTE"], width=120, height=28,
                fg_color=INPUT_BG, button_color=BORDER, button_hover_color="#2563EB"
            )
            opt_role.set(user.role)

            # Se for o próprio usuário, desabilita a edição de cargo
            if is_me:
                opt_role.configure(state="disabled", button_color="#0D1B2A")
            else:
                opt_role.configure(
                    command=lambda new_role, uid=user.id, old_role=user.role, opt=opt_role: self.confirm_role_change(
                        uid, new_role, old_role, opt))

            opt_role.pack(side="left", padx=14, pady=12)

            ctk.CTkLabel(row, text=user.full_name, font=("Inter", 14, "bold"), text_color=TEXT_MAIN).pack(side="left",
                                                                                                          padx=(0, 10))
            ctk.CTkLabel(row, text=f"@{user.username}", font=("Inter", 12), text_color=TEXT_MUTED).pack(side="left")

            # Se for o próprio usuário, mostra "Você" no lugar do botão Excluir
            if is_me:
                ctk.CTkLabel(row, text="(Você)", font=("Inter", 12, "bold"), text_color="#10B981").pack(side="right",
                                                                                                        padx=30)
            else:
                btn_delete = ctk.CTkButton(
                    row, text="Excluir", width=70, height=28,
                    fg_color="#3B1212", hover_color="#7F1D1D", text_color="#EF4444",
                    command=lambda uid=user.id: self.confirm_delete(uid)
                )
                btn_delete.pack(side="right", padx=14)

            ctk.CTkLabel(row, text=user.email, font=("Inter", 12), text_color=TEXT_MUTED).pack(side="right", padx=16)
    # --- FLUXO DE CONFIRMAÇÃO DE CARGO ---
    def confirm_role_change(self, user_id, new_role, old_role, opt_widget):
        if new_role == old_role:
            return

        def on_yes():
            self.handle_role_change(user_id, new_role)
            # Atualiza o "old_role" no comando do botão para o novo valor
            opt_widget.configure(
                command=lambda n_role, uid=user_id, o_role=new_role, opt=opt_widget: self.confirm_role_change(uid,
                                                                                                              n_role,
                                                                                                              o_role,
                                                                                                              opt))

        def on_no():
            opt_widget.set(old_role)  # Reverte visualmente para o valor anterior se o usuário cancelar

        ConfirmDialog(
            master=self,
            title="Alterar Cargo",
            message=f"Tem certeza que deseja alterar as permissões para {new_role}?",
            on_confirm=on_yes,
            on_cancel=on_no
        )

    def handle_role_change(self, user_id: int, new_role: str):
        try:
            self.repository.update_role(user_id, new_role)
            self.lbl_msg.configure(text="Cargo atualizado com sucesso!", text_color="#10B981")
        except Exception:
            self.lbl_msg.configure(text="Erro ao atualizar o cargo.", text_color="#EF4444")

    # --- FLUXO DE CONFIRMAÇÃO DE EXCLUSÃO ---
    def confirm_delete(self, user_id):
        def on_yes():
            self.handle_delete(user_id)

        ConfirmDialog(
            master=self,
            title="Excluir Usuário",
            message="Tem certeza que deseja excluir este usuário? Esta ação não pode ser desfeita.",
            on_confirm=on_yes
        )

    def handle_delete(self, user_id: int):
        try:
            self.repository.delete(user_id)
            self.lbl_msg.configure(text="Usuário removido com sucesso!", text_color="#10B981")
            self.load_users()
        except Exception:
            self.lbl_msg.configure(text="Erro ao excluir usuário.", text_color="#EF4444")

    def handle_role_change(self, user_id: int, new_role: str):
        try:
            self.repository.update_role(user_id, new_role)
            self.lbl_msg.configure(text="Cargo atualizado com sucesso!", text_color="#10B981")
        except Exception:
            self.lbl_msg.configure(text="Erro ao atualizar o cargo.", text_color="#EF4444")

    def handle_delete(self, user_id: int):
        try:
            self.repository.delete(user_id)
            self.lbl_msg.configure(text="Usuário removido com sucesso!", text_color="#10B981")
            self.load_users()  # Recarrega a lista para o usuário sumir da tela
        except Exception:
            self.lbl_msg.configure(text="Erro ao excluir usuário.", text_color="#EF4444")