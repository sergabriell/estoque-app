import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError

from app.repositories.supplier_repository import SupplierRepository
from app.ui.components import ModernCard, PageHeader, input_field, FONT_CARD_TITLE
from app.utils.validators import (
    format_cpf_cnpj,
    format_phone,
    is_valid_email,
    is_valid_cpf_cnpj,
    is_valid_phone,
)


class SuppliersPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.repository = SupplierRepository()
        self.editing_supplier_id = None

        self.pack(fill="both", expand=True)

        self.build()
        self.refresh_list()

    def build(self):
        PageHeader(
            self,
            "Fornecedores",
            "Gerencie dados de fornecedores e contatos."
        ).pack(fill="x", padx=24, pady=(24, 16))

        form = ModernCard(self)
        form.pack(fill="x", padx=24, pady=(0, 16))

        self.form_title = ctk.CTkLabel(
            form,
            text="Novo fornecedor",
            font=FONT_CARD_TITLE
        )
        self.form_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(18, 10))

        self.name = input_field(form, "Nome / Razão social")
        self.document = input_field(form, "CNPJ / CPF")
        self.email = input_field(form, "E-mail")
        self.phone = input_field(form, "Telefone")

        self.document.bind("<KeyRelease>", self.apply_document_mask)
        self.phone.bind("<KeyRelease>", self.apply_phone_mask)

        self.name.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        self.document.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        self.email.grid(row=1, column=2, padx=12, pady=8, sticky="ew")
        self.phone.grid(row=1, column=3, padx=12, pady=8, sticky="ew")

        for i in range(4):
            form.grid_columnconfigure(i, weight=1)

        self.save_button = ctk.CTkButton(
            form,
            text="Salvar fornecedor",
            height=42,
            corner_radius=12,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=self.save,
        )
        self.save_button.grid(
            row=2,
            column=0,
            columnspan=4,
            padx=12,
            pady=(8, 18),
            sticky="ew"
        )

        self.cancel_button = ctk.CTkButton(
            form,
            text="Cancelar edição",
            height=42,
            corner_radius=12,
            fg_color="#475569",
            hover_color="#334155",
            command=self.cancel_edit,
        )

        self.list_container = ModernCard(self)
        self.list_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        ctk.CTkLabel(
            self.list_container,
            text="Fornecedores cadastrados",
            font=FONT_CARD_TITLE
        ).pack(anchor="w", padx=18, pady=(18, 8))

        self.list_frame = ctk.CTkScrollableFrame(
            self.list_container,
            fg_color="transparent"
        )
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def apply_document_mask(self, event=None):
        value = format_cpf_cnpj(self.document.get())
        self.document.delete(0, "end")
        self.document.insert(0, value)

    def apply_phone_mask(self, event=None):
        value = format_phone(self.phone.get())
        self.phone.delete(0, "end")
        self.phone.insert(0, value)

    def save(self):
        try:
            name = self.name.get().strip()
            document = self.document.get().strip()
            email = self.email.get().strip()
            phone = self.phone.get().strip()

            if not all([name, document, email, phone]):
                raise ValueError("Todos os campos são obrigatórios.")

            if not is_valid_cpf_cnpj(document):
                raise ValueError("CPF/CNPJ inválido.")

            if not is_valid_email(email):
                raise ValueError("E-mail inválido.")

            if not is_valid_phone(phone):
                raise ValueError("Telefone inválido.")

            if self.editing_supplier_id:
                self.repository.update(
                    self.editing_supplier_id,
                    name,
                    document,
                    email,
                    phone
                )
                messagebox.showinfo("Sucesso", "Fornecedor atualizado com sucesso!")
            else:
                self.repository.create(name, document, email, phone)
                messagebox.showinfo("Sucesso", "Fornecedor cadastrado com sucesso!")

            self.cancel_edit()
            self.refresh_list()

        except IntegrityError:
            messagebox.showerror("Erro", "Já existe um fornecedor com este documento.")
        except ValueError as error:
            messagebox.showerror("Erro", str(error))
        except Exception as error:
            messagebox.showerror("Erro inesperado", str(error))

    def start_edit(self, supplier):
        self.editing_supplier_id = supplier.id

        self.form_title.configure(text="Editar fornecedor")
        self.save_button.configure(text="Atualizar fornecedor")

        self.name.delete(0, "end")
        self.document.delete(0, "end")
        self.email.delete(0, "end")
        self.phone.delete(0, "end")

        self.name.insert(0, supplier.name)
        self.document.insert(0, supplier.document)
        self.email.insert(0, supplier.email)
        self.phone.insert(0, supplier.phone)

        self.cancel_button.grid(
            row=2,
            column=2,
            columnspan=2,
            padx=12,
            pady=(8, 18),
            sticky="ew"
        )

    def cancel_edit(self):
        self.editing_supplier_id = None
        self.form_title.configure(text="Novo fornecedor")
        self.save_button.configure(text="Salvar fornecedor")
        self.cancel_button.grid_forget()
        self.clear_form()

    def clear_form(self):
        for field in [self.name, self.document, self.email, self.phone]:
            field.delete(0, "end")

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        suppliers = self.repository.list_all()

        if not suppliers:
            ctk.CTkLabel(
                self.list_frame,
                text="Nenhum fornecedor cadastrado ainda.",
                text_color="#9CA3AF"
            ).pack(pady=20)
            return

        for supplier in suppliers:
            row = ctk.CTkFrame(
                self.list_frame,
                corner_radius=14,
                fg_color="#0B1220"
            )
            row.pack(fill="x", padx=6, pady=6)

            ctk.CTkLabel(
                row,
                text=f"{supplier.name}  •  {supplier.document}",
                font=("Inter", 14, "bold")
            ).pack(side="left", padx=14, pady=12)

            ctk.CTkLabel(
                row,
                text=f"{supplier.email} | {supplier.phone}",
                text_color="#9CA3AF"
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                row,
                text="Excluir",
                width=80,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda sid=supplier.id: self.delete(sid)
            ).pack(side="right", padx=8)

            ctk.CTkButton(
                row,
                text="Editar",
                width=80,
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                command=lambda s=supplier: self.start_edit(s)
            ).pack(side="right", padx=8)

    def delete(self, supplier_id: int):
        if messagebox.askyesno("Confirmar", "Deseja excluir este fornecedor?"):
            self.repository.delete(supplier_id)
            self.refresh_list()