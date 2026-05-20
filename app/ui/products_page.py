import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError
from app.repositories.product_repository import ProductRepository
from app.ui.components import ModernCard, PageHeader, input_field, FONT_CARD_TITLE

class ProductsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.repository = ProductRepository()
        self.pack(fill="both", expand=True)
        self.build()
        self.refresh_list()

    def build(self):
        PageHeader(self, "Produtos", "Cadastre produtos, SKU, preço e estoque.").pack(fill="x", padx=24, pady=(24, 16))

        form = ModernCard(self)
        form.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(form, text="Novo produto", font=FONT_CARD_TITLE).grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(18, 10))

        self.name = input_field(form, "Nome do produto")
        self.sku = input_field(form, "SKU")
        self.price = input_field(form, "Preço")
        self.stock = input_field(form, "Estoque")

        self.name.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        self.sku.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        self.price.grid(row=1, column=2, padx=12, pady=8, sticky="ew")
        self.stock.grid(row=1, column=3, padx=12, pady=8, sticky="ew")

        for i in range(4):
            form.grid_columnconfigure(i, weight=1)

        ctk.CTkButton(
            form,
            text="Salvar produto",
            height=42,
            corner_radius=12,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.save,
        ).grid(row=2, column=3, padx=12, pady=(8, 18), sticky="ew")

        self.list_container = ModernCard(self)
        self.list_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        ctk.CTkLabel(self.list_container, text="Produtos cadastrados", font=FONT_CARD_TITLE).pack(anchor="w", padx=18, pady=(18, 8))
        self.list_frame = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def save(self):
        try:
            name = self.name.get().strip()
            sku = self.sku.get().strip()
            price = float(self.price.get().replace(",", "."))
            stock = int(self.stock.get())
            if not name or not sku:
                raise ValueError("Nome e SKU são obrigatórios.")
            self.repository.create(name, sku, price, stock)
            self.clear_form()
            self.refresh_list()
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
        except IntegrityError:
            messagebox.showerror("Erro", "Já existe um produto com este SKU.")
        except ValueError as error:
            messagebox.showerror("Erro", str(error))
        except Exception as error:
            messagebox.showerror("Erro inesperado", str(error))

    def clear_form(self):
        for field in [self.name, self.sku, self.price, self.stock]:
            field.delete(0, "end")

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        products = self.repository.list_all()
        if not products:
            ctk.CTkLabel(self.list_frame, text="Nenhum produto cadastrado ainda.", text_color="#9CA3AF").pack(pady=20)
            return
        for product in products:
            row = ctk.CTkFrame(self.list_frame, corner_radius=14, fg_color="#0B1220")
            row.pack(fill="x", padx=6, pady=6)
            ctk.CTkLabel(row, text=f"{product.name}  •  SKU: {product.sku}", font=("Inter", 14, "bold")).pack(side="left", padx=14, pady=12)
            ctk.CTkLabel(row, text=f"R$ {product.price:.2f} | Estoque: {product.stock}", text_color="#9CA3AF").pack(side="left", padx=10)
            ctk.CTkButton(row, text="Excluir", width=80, fg_color="#DC2626", hover_color="#B91C1C", command=lambda pid=product.id: self.delete(pid)).pack(side="right", padx=12)

    def delete(self, product_id: int):
        self.repository.delete(product_id)
        self.refresh_list()
