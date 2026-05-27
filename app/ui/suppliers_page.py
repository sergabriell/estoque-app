import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError

from app.repositories.supplier_repository import SupplierRepository
from app.repositories.product_repository import ProductRepository
from app.ui.components import ModernCard, PageHeader, input_field, FONT_CARD_TITLE
from app.utils.validators import (
    format_cpf_cnpj,
    format_phone,
    is_valid_email,
    is_valid_cpf_cnpj,
    is_valid_phone,
    format_money,
    parse_money,
    parse_int,
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
                self.cancel_edit()
                self.refresh_list()
            else:
                new_supplier = self.repository.create(name, document, email, phone)
                self.cancel_edit()
                self.refresh_list()
                self.show_supplier_products(new_supplier)

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

        self.save_button.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=12,
            pady=(8, 18),
            sticky="ew"
        )

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
        self.save_button.grid(
            row=2,
            column=0,
            columnspan=4,
            padx=12,
            pady=(8, 18),
            sticky="ew"
        )
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

            ctk.CTkButton(
                row,
                text="📦 Produtos",
                width=110,
                fg_color="#0F766E",
                hover_color="#0D6B63",
                command=lambda s=supplier: self.show_supplier_products(s)
            ).pack(side="right", padx=8)

    def show_supplier_products(self, supplier):
        product_repo = ProductRepository()

        popup = ctk.CTkToplevel(self)
        popup.title(f"Produtos — {supplier.name}")
        popup.geometry("900x820")
        popup.configure(fg_color="#020617")
        popup.grab_set()

        # ── cabeçalho ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            popup,
            text=f"📦  {supplier.name}",
            font=("Inter", 16, "bold"),
            text_color="#F8FAFC",
        ).pack(padx=24, pady=(24, 4), anchor="w")

        ctk.CTkLabel(
            popup,
            text=f"{supplier.document}  •  {supplier.email}  •  {supplier.phone}",
            font=("Inter", 12),
            text_color="#94A3B8",
        ).pack(padx=24, pady=(0, 14), anchor="w")

        # ── formulário de novo produto ─────────────────────────────────────────
        form_card = ModernCard(popup)
        form_card.pack(fill="x", padx=24, pady=(0, 6))

        ctk.CTkLabel(
            form_card,
            text="Adicionar novo produto",
            font=FONT_CARD_TITLE,
            text_color="#F8FAFC",
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(18, 8))

        p_name     = input_field(form_card, "Nome do produto")
        p_sku      = input_field(form_card, "SKU")
        p_category = input_field(form_card, "Categoria")
        p_cost     = input_field(form_card, "Preço de custo")
        p_sale     = input_field(form_card, "Preço de venda")
        p_stock    = input_field(form_card, "Estoque inicial")
        p_min      = input_field(form_card, "Estoque mínimo")

        def apply_money(field):
            v = format_money(field.get())
            field.delete(0, "end")
            field.insert(0, v)

        p_cost.bind("<KeyRelease>", lambda e: apply_money(p_cost))
        p_sale.bind("<KeyRelease>", lambda e: apply_money(p_sale))

        def validate_int(v):
            return v.isdigit() or v == ""

        p_stock.configure(validate="key", validatecommand=(popup.register(validate_int), "%P"))
        p_min.configure(validate="key",   validatecommand=(popup.register(validate_int), "%P"))

        p_name.grid    (row=1, column=0, padx=12, pady=6, sticky="ew")
        p_sku.grid     (row=1, column=1, padx=12, pady=6, sticky="ew")
        p_category.grid(row=1, column=2, padx=12, pady=6, sticky="ew")
        p_cost.grid    (row=2, column=0, padx=12, pady=6, sticky="ew")
        p_sale.grid    (row=2, column=1, padx=12, pady=6, sticky="ew")
        p_stock.grid   (row=2, column=2, padx=12, pady=6, sticky="ew")
        p_min.grid     (row=3, column=0, padx=12, pady=(0, 6), sticky="ew")

        for i in range(3):
            form_card.grid_columnconfigure(i, weight=1)

        status_label = ctk.CTkLabel(
            form_card,
            text="",
            font=("Inter", 12),
            text_color="#F87171",
        )
        status_label.grid(row=4, column=0, columnspan=3, padx=18, pady=(0, 4), sticky="w")

        products_list_ref = [None]

        def refresh_products_list():
            if products_list_ref[0] is None:
                return
            for w in products_list_ref[0].winfo_children():
                w.destroy()
            supplier_data = self.repository.get_with_products(supplier.id)
            _build_products_list(products_list_ref[0], supplier_data.products if supplier_data else [])

        def save_product():
            try:
                name     = p_name.get().strip()
                sku      = p_sku.get().strip() or None
                category = p_category.get().strip()

                if not name:
                    raise ValueError("Nome do produto é obrigatório.")
                if not category:
                    raise ValueError("Categoria é obrigatória.")

                cost_price = parse_money(p_cost.get()) if p_cost.get().strip() else 0.0
                sale_price = parse_money(p_sale.get()) if p_sale.get().strip() else 0.0
                stock      = parse_int(p_stock.get()) if p_stock.get().strip() else 0
                min_stock  = parse_int(p_min.get())   if p_min.get().strip()   else 0

                if cost_price < 0 or sale_price < 0:
                    raise ValueError("Preços não podem ser negativos.")
                if sale_price < cost_price:
                    raise ValueError("Preço de venda não pode ser menor que o custo.")

                product_repo.create(
                    name=name, sku=sku, category=category,
                    cost_price=cost_price, sale_price=sale_price,
                    stock=stock, min_stock=min_stock,
                    supplier_id=supplier.id,
                )

                for field in [p_name, p_sku, p_category, p_cost, p_sale, p_stock, p_min]:
                    field.configure(validate="none")
                    field.delete(0, "end")
                    activate = getattr(field, "_activate_placeholder", None)
                    if activate:
                        activate()
                p_stock.configure(validate="key", validatecommand=(popup.register(validate_int), "%P"))
                p_min.configure(validate="key",   validatecommand=(popup.register(validate_int), "%P"))

                status_label.configure(
                    text=f"✅  Produto '{name}' cadastrado com sucesso!",
                    text_color="#22C55E",
                )
                refresh_products_list()

            except IntegrityError:
                status_label.configure(text="❌  Já existe um produto com este SKU.", text_color="#F87171")
            except ValueError as error:
                status_label.configure(text=f"❌  {error}", text_color="#F87171")
            except Exception as error:
                status_label.configure(text=f"❌  Erro inesperado: {error}", text_color="#F87171")

        btn_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=3, padx=12, pady=(0, 18), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Salvar produto",
            height=40,
            corner_radius=12,
            fg_color="#0F766E",
            hover_color="#0D6B63",
            command=save_product,
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="Fechar",
            height=40,
            corner_radius=12,
            fg_color="#475569",
            hover_color="#334155",
            command=popup.destroy,
        ).pack(side="left", expand=True, fill="x")

        # ── lista de produtos cadastrados ──────────────────────────────────────
        ctk.CTkLabel(
            popup,
            text="Produtos cadastrados deste fornecedor",
            font=FONT_CARD_TITLE,
            text_color="#F8FAFC",
        ).pack(padx=24, pady=(12, 6), anchor="w")

        scroll = ctk.CTkScrollableFrame(popup, fg_color="#0B1220", corner_radius=12)
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        products_list_ref[0] = scroll

        supplier_data = self.repository.get_with_products(supplier.id)
        products = supplier_data.products if supplier_data else []

        def _build_products_list(container, product_list):
            if not product_list:
                ctk.CTkLabel(
                    container,
                    text="Nenhum produto cadastrado para este fornecedor.",
                    text_color="#9CA3AF",
                    font=("Inter", 13),
                ).pack(pady=20)
                return

            for product in product_list:
                row = ctk.CTkFrame(container, corner_radius=10, fg_color="#0F172A")
                row.pack(fill="x", padx=8, pady=5)

                name_color = "#F8FAFC"
                status_suffix = ""
                if product.stock <= product.min_stock:
                    name_color = "#F87171"
                    status_suffix = "  •  ESTOQUE BAIXO"

                ctk.CTkLabel(
                    row,
                    text=f"{product.name}  •  {product.category or 'Sem categoria'}{status_suffix}",
                    font=("Inter", 13, "bold"),
                    text_color=name_color,
                ).pack(side="left", padx=14, pady=10)

                sku_text = f"SKU: {product.sku}" if product.sku else "SKU: —"
                ctk.CTkLabel(
                    row,
                    text=(
                        f"{sku_text}  |  "
                        f"Custo: R$ {product.cost_price:.2f}  |  "
                        f"Venda: R$ {product.sale_price:.2f}  |  "
                        f"Estoque: {product.stock}"
                    ),
                    text_color="#9CA3AF",
                    font=("Inter", 12),
                ).pack(side="left", padx=10)

        _build_products_list(scroll, products)

    def delete(self, supplier_id: int):
        if messagebox.askyesno("Confirmar", "Deseja excluir este fornecedor?"):
            self.repository.delete(supplier_id)
            self.refresh_list()
