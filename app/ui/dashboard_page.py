import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from app.repositories.dashboard_repository import DashboardRepository
from app.ui.components import ModernCard, PageHeader, FONT_CARD_TITLE


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.repository = DashboardRepository()
        self.pack(fill="both", expand=True)
        self.build()

    def build(self):
        metrics = self.repository.get_metrics()
        df = metrics["df"]

        PageHeader(
            self,
            "Dashboard",
            "Visão geral do estoque e valores cadastrados."
        ).pack(fill="x", padx=24, pady=(24, 16))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(0, 16))

        self.metric_card(cards, "Produtos", metrics["total_products"], "#2563EB")
        self.metric_card(cards, "Itens em estoque", metrics["total_items"], "#16A34A")
        self.metric_card(
            cards,
            "Valor total em estoque",
            f"R$ {metrics['total_stock_value']:.2f}",
            "#7C3AED"
        )
        self.metric_card(cards, "Estoque baixo", metrics["low_stock_count"], "#DC2626")

        if df.empty:
            empty = ModernCard(self)
            empty.pack(fill="both", expand=True, padx=24, pady=(0, 24))

            ctk.CTkLabel(
                empty,
                text="Nenhum produto cadastrado ainda.",
                text_color="#9CA3AF",
                font=("Inter", 16),
            ).pack(pady=40)

            return

        self.build_chart(df)

    def metric_card(self, master, title, value, color):
        card = ModernCard(master)
        card.pack(side="left", fill="both", expand=True, padx=6)

        ctk.CTkLabel(
            card,
            text=title,
            text_color="#9CA3AF",
            font=("Inter", 13),
        ).pack(anchor="w", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            card,
            text=str(value),
            text_color=color,
            font=("Inter", 24, "bold"),
        ).pack(anchor="w", padx=18, pady=(0, 16))

    def build_chart(self, df):
        chart_card = ModernCard(self)
        chart_card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        ctk.CTkLabel(
            chart_card,
            text="Estoque por produto",
            font=FONT_CARD_TITLE,
            text_color="#F9FAFB",
        ).pack(anchor="w", padx=18, pady=(18, 8))

        top_df = df.sort_values("stock", ascending=False).head(8)

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.bar(top_df["name"], top_df["stock"])
        ax.set_ylabel("Quantidade")
        ax.set_title("Produtos com maior estoque")
        ax.tick_params(axis="x", rotation=30)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=18, pady=18)