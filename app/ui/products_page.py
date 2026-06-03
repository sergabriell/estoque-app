import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError

from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_repository import SupplierRepository
from app.ui.components import ModernCard, PageHeader, input_field, FONT_CARD_TITLE
from app.utils.validators import format_money, parse_money, parse_int
from app.utils.csv_exporter import export_list_to_csv


class ProductsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.repository = ProductRepository()
        self.supplier_repository = SupplierRepository()

        self.suppliers = []
        self.editing_product_id = None

        self.pack(fill="both", expand=True)

        self.scroll_outer = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_outer.pack(fill="both", expand=True)

        self.build()
        self.refresh_list()
        self.refresh_supplier_products()

    def build(self):
        PageHeader(
            self.scroll_outer,
            "Produtos",
            "Cadastre produtos, fornecedor, preços e estoque."
        ).pack(fill="x", padx=24, pady=(24, 16))

        form = ModernCard(self.scroll_outer)
        form.pack(fill="x", padx=24, pady=(0, 16))

        self.form_title = ctk.CTkLabel(form, text="Novo produto", font=FONT_CARD_TITLE)
        self.form_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(18, 10))

        self.name = input_field(form, "Nome do produto")
        self.sku = input_field(form, "SKU")
        self.category = input_field(form, "Categoria")
        self.cost_price = input_field(form, "Preço de custo")
        self.sale_price = input_field(form, "Preço de venda")
        self.stock = input_field(form, "Estoque")
        self.min_stock = input_field(form, "Estoque mínimo")

        self.cost_price.bind("<KeyRelease>", lambda event: self.apply_money_mask(self.cost_price))
        self.sale_price.bind("<KeyRelease>", lambda event: self.apply_money_mask(self.sale_price))

        self.stock.configure(validate="key", validatecommand=(self.register(self.validate_integer_input), "%P"))
        self.min_stock.configure(validate="key", validatecommand=(self.register(self.validate_integer_input), "%P"))

        self.suppliers = self.supplier_repository.list_all()
        supplier_names = [f"{supplier.id} - {supplier.name}" for supplier in self.suppliers]

        self.supplier_combo = ctk.CTkComboBox(
            form,
            values=supplier_names if supplier_names else ["Cadastre um fornecedor primeiro"],
            height=42,
            corner_radius=12,
            fg_color="#0B1220",
            border_color="#334155",
            state="readonly",
            command=self.on_supplier_change,
        )
        self.supplier_combo.set(supplier_names[0] if supplier_names else "Cadastre um fornecedor primeiro")

        self.name.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        self.sku.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        self.category.grid(row=1, column=2, padx=12, pady=8, sticky="ew")
        self.supplier_combo.grid(row=1, column=3, padx=12, pady=8, sticky="ew")

        self.cost_price.grid(row=2, column=0, padx=12, pady=8, sticky="ew")
        self.sale_price.grid(row=2, column=1, padx=12, pady=8, sticky="ew")
        self.stock.grid(row=2, column=2, padx=12, pady=8, sticky="ew")
        self.min_stock.grid(row=2, column=3, padx=12, pady=8, sticky="ew")

        for i in range(4): form.grid_columnconfigure(i, weight=1)

        self.save_button = ctk.CTkButton(form, text="Salvar produto", height=42, corner_radius=12, fg_color="#2563EB",
                                         hover_color="#1D4ED8", command=self.save)
        self.save_button.grid(row=3, column=0, columnspan=4, padx=12, pady=(8, 18), sticky="ew")

        self.cancel_button = ctk.CTkButton(form, text="Cancelar edição", height=42, corner_radius=12,
                                           fg_color="#475569", hover_color="#334155", command=self.cancel_edit)

        self.supplier_info_frame = ctk.CTkFrame(self.scroll_outer, fg_color="transparent")
        self.supplier_info_frame.pack(fill="x", padx=24, pady=(0, 16))

        # ── REVISÃO DO CONTAINER DA LISTA DE PRODUTOS CADASTRADOS ─────────────
        self.list_container = ModernCard(self.scroll_outer)
        self.list_container.pack(fill="x", padx=24, pady=(0, 24))

        # O Frame de Alinhamento Horizontal solicitado (list_header_frame)
        list_header_frame = ctk.CTkFrame(self.list_container, fg_color="transparent")
        list_header_frame.pack(fill="x", padx=18, pady=(18, 8))

        ctk.CTkLabel(
            list_header_frame,
            text="Produtos cadastrados",
            font=FONT_CARD_TITLE
        ).pack(side="left")

        # Botão de Exportação posicionado perfeitamente à direita do título
        self.export_button = ctk.CTkButton(
            list_header_frame,
            text="📥 Exportar CSV",
            width=120,
            height=32,
            fg_color="#1E293B",
            border_width=1,
            border_color="#334155",
            hover_color="#334155",
            command=self.export_to_csv,
        )
        self.export_button.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent", height=280)
        self.list_frame.pack(fill="x", padx=12, pady=(0, 12))

    def validate_integer_input(self, value):
        return value.isdigit() or value == ""

    def apply_money_mask(self, field):
        value = format_money(field.get())
        field.delete(0, "end")
        field.insert(0, value)

    def get_supplier_id_from_combo(self):
        supplier_text = self.supplier_combo.get()
        if " - " not in supplier_text: raise ValueError("Selecione um fornecedor válido.")
        return int(supplier_text.split(" - ")[0])

    def save(self):
        try:
            if not self.suppliers: raise ValueError("Cadastre um fornecedor antes de cadastrar produtos.")
            name, sku, category = self.name.get().strip(), self.sku.get().strip(), self.category.get().strip()
            cost_price = parse_money(self.cost_price.get())
            sale_price = parse_money(self.sale_price.get())
            stock = parse_int(self.stock.get())
            min_stock = parse_int(self.min_stock.get())
            supplier_id = self.get_supplier_id_from_combo()

            if not name: raise ValueError("Nome do produto é obrigatório.")
            if not sku: raise ValueError("SKU é obrigatório.")
            if not category: raise ValueError("Categoria é obrigatória.")
            if cost_price < 0 or sale_price < 0: raise ValueError("Preços não podem ser negativos.")
            if stock < 0 or min_stock < 0: raise ValueError("Estoque e estoque mínimo não podem ser negativos.")
            if sale_price < cost_price: raise ValueError("Preço de venda não pode ser menor que o preço de custo.")

            if self.editing_product_id:
                self.repository.update(product_id=self.editing_product_id, name=name, sku=sku, category=category,
                                       cost_price=cost_price, sale_price=sale_price, stock=stock, min_stock=min_stock,
                                       supplier_id=supplier_id)
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            else:
                self.repository.create(name=name, sku=sku, category=category, cost_price=cost_price,
                                       sale_price=sale_price, stock=stock, min_stock=min_stock, supplier_id=supplier_id)
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")

            self.cancel_edit()
            self.refresh_list()
        except IntegrityError:
            messagebox.showerror("Erro", "Já existe um produto com este SKU.")
        except ValueError as error:
            messagebox.showerror("Erro", str(error))
        except Exception as error:
            messagebox.showerror("Erro inesperado", str(error))

    def start_edit(self, product):
        self.editing_product_id = product.id
        self.form_title.configure(text="Editar produto")
        self.save_button.configure(text="Atualizar produto")
        canvas = getattr(self.scroll_outer, "_parent_canvas", None)
        if canvas: canvas.yview_moveto(0)

        self.clear_form()
        if product.name: self.name.insert(0, product.name)
        if product.sku: self.sku.insert(0, product.sku)
        if product.category: self.category.insert(0, product.category)
        if product.cost_price: self.cost_price.insert(0, format_money(str(int(product.cost_price * 100))))
        if product.sale_price: self.sale_price.insert(0, format_money(str(int(product.sale_price * 100))))
        if product.stock: self.stock.insert(0, str(product.stock))
        if product.min_stock: self.min_stock.insert(0, str(product.min_stock))

        if product.supplier_id:
            supplier = next((s for s in self.suppliers if s.id == product.supplier_id), None)
            if supplier: self.supplier_combo.set(f"{supplier.id} - {supplier.name}")

        self.save_button.grid(row=3, column=0, columnspan=2, padx=12, pady=(8, 18), sticky="ew")
        self.cancel_button.grid(row=3, column=2, columnspan=2, padx=12, pady=(8, 18), sticky="ew")

    def cancel_edit(self):
        self.editing_product_id = None
        self.form_title.configure(text="Novo produto")
        self.save_button.configure(text="Salvar produto")
        self.clear_form()
        self.save_button.grid(row=3, column=0, columnspan=4, padx=12, pady=(8, 18), sticky="ew")
        self.cancel_button.grid_forget()

    def clear_form(self):
        for field in [self.name, self.sku, self.category, self.cost_price, self.sale_price, self.stock, self.min_stock]:
            field.configure(validate="none")
            field.delete(0, "end")
            activate = getattr(field, "_activate_placeholder", None)
            if activate: activate()
        self.stock.configure(validate="key", validatecommand=(self.register(self.validate_integer_input), "%P"))
        self.min_stock.configure(validate="key", validatecommand=(self.register(self.validate_integer_input), "%P"))

    def refresh_list(self):
        for widget in self.list_frame.winfo_children(): widget.destroy()
        products = self.repository.list_all()

        if not products:
            ctk.CTkLabel(self.list_frame, text="Nenhum produto cadastrado ainda.", text_color="#9CA3AF").pack(pady=20)
            return

        for product in products:
            row = ctk.CTkFrame(self.list_frame, corner_radius=14, fg_color="#0B1220")
            row.pack(fill="x", padx=6, pady=6)
            supplier_name = product.supplier.name if product.supplier else "Sem fornecedor"

            status_text, status_color = "", "#9CA3AF"
            if product.stock <= product.min_stock:
                status_text, status_color = "  •  ESTOQUE BAIXO", "#F87171"

            sku_display = f"SKU: {product.sku}" if product.sku else "SKU: —"
            ctk.CTkLabel(row, text=f"{product.name}  •  {sku_display}{status_text}", font=("Inter", 14, "bold"),
                         text_color=status_color if status_text else "#F9FAFB").pack(side="left", padx=14, pady=12)
            ctk.CTkLabel(row, text=(
                f"Custo: R$ {product.cost_price:.2f} | Venda: R$ {product.sale_price:.2f} | Estoque: {product.stock} | Mínimo: {product.min_stock} | Fornecedor: {supplier_name}"),
                         text_color="#9CA3AF").pack(side="left", padx=10)

            ctk.CTkButton(row, text="Excluir", width=80, fg_color="#DC2626", hover_color="#B91C1C",
                          command=lambda pid=product.id: self.delete(pid)).pack(side="right", padx=8)
            ctk.CTkButton(row, text="Editar", width=80, fg_color="#2563EB", hover_color="#1D4ED8",
                          command=lambda p=product: self.start_edit(p)).pack(side="right", padx=8)

    def on_supplier_change(self, value=None):
        self.refresh_supplier_products()

    def refresh_supplier_products(self):
        for widget in self.supplier_info_frame.winfo_children(): widget.destroy()
        supplier_text = self.supplier_combo.get()
        if " - " not in supplier_text: return
        try:
            supplier_id = int(supplier_text.split(" - ")[0])
        except (ValueError, IndexError):
            return

        supplier_data = self.supplier_repository.get_with_products(supplier_id)
        if not supplier_data or not supplier_data.products: return

        card = ModernCard(self.supplier_info_frame)
        card.pack(fill="x")
        ctk.CTkLabel(card, text=f"📦  Produtos de {supplier_data.name} — clique em um para preencher o formulário",
                     font=FONT_CARD_TITLE, text_color="#F8FAFC").pack(anchor="w", padx=18, pady=(18, 8))

        inner = ctk.CTkScrollableFrame(card, fg_color="transparent", height=160)
        inner.pack(fill="x", padx=12, pady=(0, 14))

        for product in supplier_data.products:
            row = ctk.CTkFrame(inner, corner_radius=10, fg_color="#0B1220")
            row.pack(fill="x", padx=6, pady=5)
            name_color, status_suffix = "#F9FAFB", ""
            if product.stock <= product.min_stock:
                status_suffix, name_color = "  •  ESTOQUE BAIXO", "#F87171"

            sku_display = f"SKU: {product.sku}" if product.sku else "SKU: —"
            ctk.CTkLabel(row, text=f"{product.name}  •  {product.category or '—'}  •  {sku_display}{status_suffix}",
                         font=("Inter", 13, "bold"), text_color=name_color).pack(side="left", padx=14, pady=10)
            ctk.CTkLabel(row, text=(
                f"Custo: R$ {product.cost_price:.2f}  |  Venda: R$ {product.sale_price:.2f}  |  Estoque: {product.stock}"),
                         text_color="#9CA3AF", font=("Inter", 12)).pack(side="left", padx=10)
            ctk.CTkButton(row, text="Editar", width=80, height=34, corner_radius=10, fg_color="#2563EB",
                          hover_color="#1D4ED8", command=lambda p=product: self.start_edit(p)).pack(side="right",
                                                                                                    padx=10)

    def delete(self, product_id: int):
        if messagebox.askyesno("Confirmar", "Deseja excluir este produto?"):
            self.repository.delete(product_id)
            self.refresh_list()

    # ── LOGICA COMPLETA DE MAPEAMENTO PARA O UTILITÁRIO DE CSV ──────────────────
    def export_to_csv(self):
        products = self.repository.list_all()
        if not products:
            messagebox.showwarning("Aviso", "Nenhum produto cadastrado para exportar.")
            return

        headers = ["ID", "Nome", "SKU", "Categoria", "Preço de Custo", "Preço de Venda", "Estoque Atual",
                   "Estoque Mínimo", "Fornecedor"]

        rows = []
        for p in products:
            supplier_name = p.supplier.name if p.supplier else "Sem fornecedor"
            rows.append([
                p.id, p.name, p.sku or "—", p.category or "—",
                f"{p.cost_price:.2f}", f"{p.sale_price:.2f}",
                p.stock, p.min_stock, supplier_name
            ])

        export_list_to_csv("produtos_estoque.csv", headers, rows)