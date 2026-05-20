import customtkinter as ctk
from tkinter import messagebox

from app.repositories.product_repository import ProductRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.ui.components import ModernCard, PageHeader, input_field, FONT_CARD_TITLE
from app.utils.validators import parse_int


class MovementsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.product_repository = ProductRepository()
        self.movement_repository = StockMovementRepository()

        self.products = []

        self.pack(fill="both", expand=True)

        self.build()
        self.refresh_history()

    def build(self):
        PageHeader(
            self,
            "Movimentações",
            "Registre entradas e saídas de produtos do estoque."
        ).pack(fill="x", padx=24, pady=(24, 16))

        form = ModernCard(self)
        form.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkLabel(
            form,
            text="Nova movimentação",
            font=FONT_CARD_TITLE,
            text_color="#F9FAFB",
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(18, 10))

        self.products = self.product_repository.list_all()

        product_names = [
            f"{product.id} - {product.name} | Estoque: {product.stock}"
            for product in self.products
        ]

        self.product_combo = ctk.CTkComboBox(
            form,
            values=product_names if product_names else ["Cadastre um produto primeiro"],
            height=42,
            corner_radius=12,
            fg_color="#0B1220",
            border_color="#334155",
            state="readonly",
            command=self.on_product_change,
        )
        self.product_combo.set(
            product_names[0] if product_names else "Cadastre um produto primeiro"
        )

        self.type_combo = ctk.CTkComboBox(
            form,
            values=["ENTRADA", "SAIDA"],
            height=42,
            corner_radius=12,
            fg_color="#0B1220",
            border_color="#334155",
            state="readonly",
            command=self.on_type_change,
        )
        self.type_combo.set("ENTRADA")

        self.quantity = input_field(form, "Quantidade")
        self.quantity.configure(
            validate="key",
            validatecommand=(self.register(self.validate_integer_input), "%P")
        )

        self.stock_info = ctk.CTkLabel(
            form,
            text="",
            text_color="#9CA3AF",
            font=("Inter", 13),
        )

        self.product_combo.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        self.type_combo.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        self.quantity.grid(row=1, column=2, padx=12, pady=8, sticky="ew")

        self.save_button = ctk.CTkButton(
            form,
            text="Registrar movimentação",
            height=42,
            corner_radius=12,
            fg_color="#166534",
            hover_color="#14532D",
            command=self.save,
        )
        self.save_button.grid(row=1, column=3, padx=12, pady=8, sticky="ew")

        self.stock_info.grid(row=2, column=0, columnspan=4, padx=12, pady=(0, 18), sticky="w")

        for i in range(4):
            form.grid_columnconfigure(i, weight=1)

        self.history_container = ModernCard(self)
        self.history_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        ctk.CTkLabel(
            self.history_container,
            text="Histórico de movimentações",
            font=FONT_CARD_TITLE,
            text_color="#F9FAFB",
        ).pack(anchor="w", padx=18, pady=(18, 8))

        self.history_frame = ctk.CTkScrollableFrame(
            self.history_container,
            fg_color="transparent"
        )
        self.history_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.update_stock_info()

    def validate_integer_input(self, value):
        return value.isdigit() or value == ""

    def on_product_change(self, value=None):
        self.update_stock_info()

    def on_type_change(self, value=None):
        movement_type = self.type_combo.get()

        if movement_type == "ENTRADA":
            self.save_button.configure(
                fg_color="#166534",
                hover_color="#14532D",
                text="Registrar entrada"
            )
        else:
            self.save_button.configure(
                fg_color="#DC2626",
                hover_color="#B91C1C",
                text="Registrar saída"
            )

        self.update_stock_info()

    def get_selected_product_id(self):
        product_text = self.product_combo.get()

        if " - " not in product_text:
            raise ValueError("Selecione um produto válido.")

        return int(product_text.split(" - ")[0])

    def get_selected_product(self):
        product_id = self.get_selected_product_id()

        for product in self.products:
            if product.id == product_id:
                return product

        raise ValueError("Produto não encontrado.")

    def update_stock_info(self):
        if not self.products:
            self.stock_info.configure(text="Cadastre um produto antes de registrar movimentações.")
            return

        try:
            product = self.get_selected_product()
            movement_type = self.type_combo.get()

            if movement_type == "SAIDA":
                text = f"Estoque atual de {product.name}: {product.stock}. A saída não pode ser maior que esse valor."
                color = "#FBBF24"
            else:
                text = f"Estoque atual de {product.name}: {product.stock}. A entrada vai somar ao estoque atual."
                color = "#9CA3AF"

            self.stock_info.configure(text=text, text_color=color)

        except Exception:
            self.stock_info.configure(text="Selecione um produto válido.", text_color="#F87171")

    def reload_products(self):
        self.products = self.product_repository.list_all()

        product_names = [
            f"{product.id} - {product.name} | Estoque: {product.stock}"
            for product in self.products
        ]

        self.product_combo.configure(
            values=product_names if product_names else ["Cadastre um produto primeiro"]
        )
        self.product_combo.set(
            product_names[0] if product_names else "Cadastre um produto primeiro"
        )

        self.update_stock_info()

    def save(self):
        try:
            if not self.products:
                raise ValueError("Cadastre um produto antes de registrar movimentações.")

            product_id = self.get_selected_product_id()
            movement_type = self.type_combo.get()
            quantity = parse_int(self.quantity.get())

            if quantity <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")

            selected_product = self.get_selected_product()

            if movement_type == "SAIDA" and quantity > selected_product.stock:
                raise ValueError(
                    f"Estoque insuficiente. Estoque atual: {selected_product.stock}."
                )

            self.movement_repository.create(
                product_id=product_id,
                movement_type=movement_type,
                quantity=quantity
            )

            self.quantity.delete(0, "end")
            self.reload_products()
            self.refresh_history()

            if movement_type == "ENTRADA":
                messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
            else:
                messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")

        except ValueError as error:
            messagebox.showerror("Erro", str(error))
        except Exception as error:
            messagebox.showerror("Erro inesperado", str(error))

    def refresh_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        movements = self.movement_repository.list_all()

        if not movements:
            ctk.CTkLabel(
                self.history_frame,
                text="Nenhuma movimentação registrada ainda.",
                text_color="#9CA3AF"
            ).pack(pady=20)
            return

        for movement in movements:
            row = ctk.CTkFrame(
                self.history_frame,
                corner_radius=14,
                fg_color="#0B1220"
            )
            row.pack(fill="x", padx=6, pady=6)

            is_entry = movement.movement_type == "ENTRADA"

            color = "#22C55E" if is_entry else "#EF4444"
            symbol = "+" if is_entry else "-"
            type_label = "Entrada" if is_entry else "Saída"

            product_name = movement.product.name if movement.product else "Produto removido"

            ctk.CTkLabel(
                row,
                text=f"{type_label}  •  {product_name}",
                font=("Inter", 14, "bold"),
                text_color=color
            ).pack(side="left", padx=14, pady=12)

            ctk.CTkLabel(
                row,
                text=f"{symbol}{movement.quantity} unidade(s)",
                text_color="#F9FAFB",
                font=("Inter", 13, "bold")
            ).pack(side="left", padx=10)

            created_at = movement.created_at.strftime("%d/%m/%Y %H:%M")

            ctk.CTkLabel(
                row,
                text=created_at,
                text_color="#9CA3AF"
            ).pack(side="right", padx=14)