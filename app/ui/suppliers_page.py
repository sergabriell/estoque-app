import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError
from app.repositories.supplier_repository import SupplierRepository
from app.ui.components import ModernCard, PageHeader, input_field, FONT_CARD_TITLE

class SuppliersPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.repository = SupplierRepository()
        self.pack(fill="both", expand=True)
        self.build()
        self.refresh_list()

    def build(self):
        PageHeader(self, "Fornecedores", "Gerencie dados de fornecedores e contatos.").pack(fill="x", padx=24, pady=(24, 16))

        form = ModernCard(self)
        form.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(form, text="Novo fornecedor", font=FONT_CARD_TITLE).grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(18, 10))

        self.name = input_field(form, "Nome / Razão social")
        self.document = input_field(form, "CNPJ / CPF")
        self.email = input_field(form, "E-mail")
        self.phone = input_field(form, "Telefone")

        self.name.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        self.document.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        self.email.grid(row=1, column=2, padx=12, pady=8, sticky="ew")
        self.phone.grid(row=1, column=3, padx=12, pady=8, sticky="ew")

        for i in range(4):
            form.grid_columnconfigure(i, weight=1)

        ctk.CTkButton(
            form,
            text="Salvar fornecedor",
            height=42,
            corner_radius=12,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=self.save,
        ).grid(row=2, column=3, padx=12, pady=(8, 18), sticky="ew")

        self.list_container = ModernCard(self)
        self.list_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        ctk.CTkLabel(self.list_container, text="Fornecedores cadastrados", font=FONT_CARD_TITLE).pack(anchor="w", padx=18, pady=(18, 8))
        self.list_frame = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def save(self):
        try:
            name = self.name.get().strip()
            document = self.document.get().strip()
            email = self.email.get().strip()
            phone = self.phone.get().strip()
            if not all([name, document, email, phone]):
                raise ValueError("Todos os campos são obrigatórios.")
            self.repository.create(name, document, email, phone)
            self.clear_form()
            self.refresh_list()
            messagebox.showinfo("Sucesso", "Fornecedor cadastrado com sucesso!")
        except IntegrityError:
            messagebox.showerror("Erro", "Já existe um fornecedor com este documento.")
        except ValueError as error:
            messagebox.showerror("Erro", str(error))
        except Exception as error:
            messagebox.showerror("Erro inesperado", str(error))

    def clear_form(self):
        for field in [self.name, self.document, self.email, self.phone]:
            field.delete(0, "end")

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        suppliers = self.repository.list_all()
        if not suppliers:
            ctk.CTkLabel(self.list_frame, text="Nenhum fornecedor cadastrado ainda.", text_color="#9CA3AF").pack(pady=20)
            return
        for supplier in suppliers:
            row = ctk.CTkFrame(self.list_frame, corner_radius=14, fg_color="#0B1220")
            row.pack(fill="x", padx=6, pady=6)
            ctk.CTkLabel(row, text=f"{supplier.name}  •  {supplier.document}", font=("Inter", 14, "bold")).pack(side="left", padx=14, pady=12)
            ctk.CTkLabel(row, text=f"{supplier.email} | {supplier.phone}", text_color="#9CA3AF").pack(side="left", padx=10)
            ctk.CTkButton(row, text="Excluir", width=80, fg_color="#DC2626", hover_color="#B91C1C", command=lambda sid=supplier.id: self.delete(sid)).pack(side="right", padx=12)

    def delete(self, supplier_id: int):
        self.repository.delete(supplier_id)
        self.refresh_list()
