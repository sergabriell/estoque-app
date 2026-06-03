import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches
import pandas as pd
from tkinter import messagebox

from app.repositories.dashboard_repository import DashboardRepository
from app.ui.components import PageHeader, FONT_CARD_TITLE
from app.utils.csv_exporter import export_df_to_csv

BG = "#020617"
CARD_BG = "#0D1B2A"
ROW_BG = "#0B1220"
BORDER = "#1E3A5F"
TEXT_MAIN = "#F0F6FF"
TEXT_MUTED = "#64748B"

_ICON_BG = {
    "#3B82F6": "#112244",
    "#0EA5E9": "#0A2535",
    "#10B981": "#0A2520",
    "#8B5CF6": "#201440",
    "#EF4444": "#3B1212",
}
_BADGE_BG = {
    "#10B981": "#0A2520",
    "#EF4444": "#3B1212",
}


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.repository = DashboardRepository()
        self._anims = []
        self.pack(fill="both", expand=True)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self.build()

    def build(self):
        metrics = self.repository.get_metrics()
        df = metrics["df"]

        PageHeader(
            self.scroll, "Dashboard",
            "Visão geral do estoque e valores cadastrados."
        ).pack(fill="x", padx=24, pady=(24, 20))

        row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 20))

        cards_data = [
            ("📦", "Produtos", metrics["total_products"], "#3B82F6", True, False),
            ("🏢", "Fornecedores", metrics["total_suppliers"], "#0EA5E9", True, False),
            ("📦", "Itens em estoque", metrics["total_items"], "#10B981", True, False),
            ("💰", "Valor de custo", metrics["total_stock_value"], "#8B5CF6", False, True),
            ("⚠️", "Estoque baixo", metrics["low_stock_count"], "#EF4444", True, False),
        ]

        labels = []
        for icon, title, value, color, is_int, is_curr in cards_data:
            lbl = self._metric_card(row, icon, title, color)
            labels.append((lbl, value, is_int, is_curr, color))

        for i, (lbl, val, is_int, is_curr, color) in enumerate(labels):
            self._count_up(lbl, val, is_int=is_int, is_currency=is_curr,
                           delay=i * 100, color=color)

        if metrics["low_stock_count"] > 0:
            self._pulse(labels[4][0], "#EF4444", "#FF6B6B")

        if df.empty:
            self._empty_state()
            return

        mid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        mid.pack(fill="x", padx=24, pady=(0, 20))
        mid.grid_columnconfigure(0, weight=5)
        mid.grid_columnconfigure(1, weight=3)

        self._build_bar_chart(mid, df)
        self._build_low_stock(mid, metrics["low_stock_df"])

        self._build_movements()

    def _metric_card(self, master, icon, title, color):
        outer = ctk.CTkFrame(master, fg_color=CARD_BG,
                             corner_radius=16, border_width=2,
                             border_color=color)
        outer.pack(side="left", fill="both", expand=True, padx=6)

        header = ctk.CTkFrame(outer, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))

        icon_bg = ctk.CTkFrame(header, width=38, height=38,
                               fg_color=_ICON_BG.get(color, "#1A2A3A"), corner_radius=10)
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=icon, font=("Inter", 18)).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(header, text=title, text_color=TEXT_MUTED,
                     font=("Inter", 12)).pack(side="left", padx=(10, 0))

        val_lbl = ctk.CTkLabel(outer, text="0", text_color=color,
                               font=("Inter", 28, "bold"))
        val_lbl.pack(anchor="w", padx=18, pady=(2, 16))

        def _enter(_): outer.configure(fg_color="#152032", border_color=color)

        def _leave(_): outer.configure(fg_color=CARD_BG, border_color=BORDER)

        outer.bind("<Enter>", _enter)
        outer.bind("<Leave>", _leave)

        return val_lbl

    def _build_bar_chart(self, master, df):
        card = ctk.CTkFrame(master, fg_color=CARD_BG, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # ── HEADER HORIZONTAL DO GRÁFICO ──────────────────────────────────────
        chart_header = ctk.CTkFrame(card, fg_color="transparent")
        chart_header.pack(fill="x", padx=18, pady=(16, 4))

        ctk.CTkLabel(chart_header, text="📊  Estoque por produto",
                     font=FONT_CARD_TITLE, text_color=TEXT_MAIN,
                     ).pack(side="left")

        # Botão para exportar o inventário consolidado completo do Dashboard
        ctk.CTkButton(
            chart_header,
            text="📥 Relatório Geral",
            width=130,
            height=28,
            fg_color="#1E293B",      # Tom slate escuro combinando com o app
            border_width=1,
            border_color="#334155",
            hover_color="#334155",
            command=lambda: self.export_general_report(df)
        ).pack(side="right")
        # ──────────────────────────────────────────────────────────────────────

        top_df  = df.sort_values("stock", ascending=False).head(8).reset_index(drop=True)
        targets = top_df["stock"].values.tolist()
        colors  = ["#3B82F6" if not low else "#EF4444" for low in top_df["is_low_stock"]]

        fig = Figure(figsize=(6, 3.4), dpi=96)
        fig.patch.set_facecolor(CARD_BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor("#060F1C")

        bars = ax.bar(top_df["name"], [0]*len(top_df), color=colors,
                      width=0.55, zorder=3)

        labels = [
            ax.text(b.get_x() + b.get_width()/2, 0, "",
                    ha="center", va="bottom",
                    color=TEXT_MAIN, fontsize=9, fontweight="bold", alpha=0)
            for b in bars
        ]

        ax.set_ylim(0, max(targets) * 1.22 if targets else 1)
        ax.set_ylabel("Qtd", color=TEXT_MUTED, fontsize=9)
        ax.tick_params(axis="x", colors=TEXT_MUTED, rotation=28, labelsize=8)
        ax.tick_params(axis="y", colors=TEXT_MUTED, labelsize=8)
        for spine in ("top","right"): ax.spines[spine].set_visible(False)
        for spine in ("bottom","left"): ax.spines[spine].set_color(BORDER)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color="#0F2035", linewidth=0.8, linestyle="--")

        # tooltip
        annot = ax.annotate(
            "", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.7", fc="#0D1B2A", ec="#3B82F6", lw=1.5),
            arrowprops=dict(arrowstyle="->", color="#64748B"),
            color=TEXT_MAIN, fontsize=10,
            ha="center", va="bottom",
        )
        annot.set_visible(False)

        y_max = max(targets) * 1.22 if targets else 1

        def _hover(event):
            if event.inaxes != ax:
                if annot.get_visible():
                    annot.set_visible(False)
                    fig.canvas.draw_idle()
                return
            for i, bar in enumerate(bars):
                if bar.contains(event)[0]:
                    r   = top_df.iloc[i]
                    bx  = bar.get_x() + bar.get_width() / 2
                    bh  = bar.get_height()
                    if bh > y_max * 0.6: oy, va = -60, "top"
                    else: oy, va = 14, "bottom"
                    annot.xy = (bx, bh)
                    annot.set_position((0, oy))
                    annot.set_va(va)
                    annot.set_text(
                        f"{r['name']}\n"
                        f"Estoque: {int(r['stock'])}  •  Mínimo: {int(r['min_stock'])}\n"
                        f"Fornecedor: {r['supplier']}"
                    )
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
            annot.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", _hover)
        fig.tight_layout(pad=1.4)

        N = 40
        def _anim(frame):
            t = frame / N
            ease = 1 - (1-t)**3
            for bar, lbl, tgt in zip(bars, labels, targets):
                h = tgt * ease
                bar.set_height(h)
                lbl.set_position((bar.get_x() + bar.get_width()/2, h + 0.3))
                lbl.set_text(str(int(h)))
                lbl.set_alpha(ease)
            return bars

        cv = FigureCanvasTkAgg(fig, master=card)
        cv.draw()
        cv.get_tk_widget().configure(bg=CARD_BG, highlightthickness=0)
        cv.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0,12))

        anim = FuncAnimation(fig, _anim, frames=N+1, interval=16,
                             blit=False, repeat=False)
        self._anims.append(anim)
        cv.draw()

    def _build_low_stock(self, master, low_df):
        card = ctk.CTkFrame(master, fg_color=CARD_BG, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # ── HEADER HORIZONTAL DOS ALERTAS ─────────────────────────────────────
        header_alert = ctk.CTkFrame(card, fg_color="transparent")
        header_alert.pack(fill="x", padx=18, pady=(16, 8))

        ctk.CTkLabel(header_alert, text="⚠️  Alertas de estoque",
                     font=FONT_CARD_TITLE, text_color="#F87171",
                     ).pack(side="left")

        # Botão rápido para baixar os alertas urgentes em CSV
        if not low_df.empty:
            ctk.CTkButton(
                header_alert,
                text="📥 Baixar",
                width=75,
                height=26,
                fg_color="#2D1010",
                text_color="#F87171",
                border_width=1,
                border_color="#7F1D1D",
                hover_color="#451A1A",
                command=lambda: self.export_alerts(low_df)
            ).pack(side="right")

        if low_df.empty:
            ctk.CTkLabel(card, text="✅  Tudo em ordem!\nNenhum produto abaixo\ndo estoque mínimo.",
                         text_color="#10B981", font=("Inter", 13), justify="center",
                         ).pack(pady=30)
            return

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent", height=200)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        for _, r in low_df.iterrows():
            pct = int(r["stock"]) / max(int(r["min_stock"]), 1)
            item = ctk.CTkFrame(scroll, corner_radius=10,
                                fg_color="#1A0A0A", border_width=1,
                                border_color="#7F1D1D")
            item.pack(fill="x", padx=4, pady=5)

            ctk.CTkLabel(item, text=r["name"], font=("Inter", 12, "bold"),
                         text_color="#F87171").pack(anchor="w", padx=12, pady=(8, 2))
            ctk.CTkLabel(item,
                         text=f"Estoque: {int(r['stock'])}  •  Mín: {int(r['min_stock'])}  •  {r['supplier']}",
                         font=("Inter", 11), text_color=TEXT_MUTED,
                         ).pack(anchor="w", padx=12)

            prog = ctk.CTkProgressBar(item, height=6, corner_radius=3,
                                      fg_color="#2D1010",
                                      progress_color="#EF4444" if pct < 0.5 else "#F59E0B")
            prog.pack(fill="x", padx=12, pady=(4, 10))
            prog.set(0)
            self._animate_progress(prog, min(pct, 1.0))

    def _build_movements(self):
        movements = self.repository.get_recent_movements(limit=5)
        if not movements:
            return

        card = ctk.CTkFrame(self.scroll, fg_color=CARD_BG, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=24, pady=(0, 24))

        ctk.CTkLabel(card, text="🕐  Últimas movimentações",
                     font=FONT_CARD_TITLE, text_color=TEXT_MAIN,
                     ).pack(anchor="w", padx=18, pady=(16, 8))

        for idx, mov in enumerate(movements):
            is_entry = mov.movement_type == "ENTRADA"
            color = "#10B981" if is_entry else "#EF4444"
            symbol = f"+{mov.quantity}" if is_entry else f"-{mov.quantity}"
            badge = "ENTRADA" if is_entry else "SAÍDA"
            name = mov.product.name if mov.product else "Produto removido"
            date_str = mov.created_at.strftime("%d/%m/%Y  %H:%M")

            row = ctk.CTkFrame(card, corner_radius=10, fg_color="#060F1C",
                               border_width=1, border_color=BORDER)
            row.pack(fill="x", padx=14, pady=4)

            bdg = ctk.CTkFrame(row, width=68, fg_color=_BADGE_BG.get(color, "#1A2A3A"),
                               corner_radius=6)
            bdg.pack(side="left", padx=(12, 8), pady=10)
            bdg.pack_propagate(False)
            ctk.CTkLabel(bdg, text=badge, font=("Inter", 10, "bold"),
                         text_color=color).place(relx=.5, rely=.5, anchor="center")

            ctk.CTkLabel(row, text=name, font=("Inter", 13, "bold"),
                         text_color=TEXT_MAIN).pack(side="left", padx=4)

            ctk.CTkLabel(row, text=date_str, font=("Inter", 11),
                         text_color=TEXT_MUTED).pack(side="right", padx=14)

            ctk.CTkLabel(row, text=symbol + " unid.", font=("Inter", 13, "bold"),
                         text_color=color).pack(side="right", padx=8)

            def _slide(r=row, d=idx * 70):
                frames = ["#020617", "#040B16", "#060F1C"]

                def _t(s):
                    if s < len(frames):
                        r.configure(fg_color=frames[s])
                        r.after(25, _t, s + 1)

                r.after(d, lambda: _t(0))

            _slide()

        ctk.CTkFrame(card, height=8, fg_color="transparent").pack()

    def _empty_state(self):
        card = ctk.CTkFrame(self.scroll, fg_color=CARD_BG, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkLabel(card, text="📦\n\nNenhum produto cadastrado ainda.",
                     text_color=TEXT_MUTED, font=("Inter", 16),
                     justify="center").pack(pady=50)

    # ── LOGICA DE EXPORTAÇÃO DO DASHBOARD ─────────────────────────────────────
    def export_alerts(self, low_stock_df: pd.DataFrame):
        if low_stock_df.empty:
            messagebox.showwarning("Aviso", "Não há produtos com estoque baixo para baixar.")
            return

        df_readable = low_stock_df.copy()
        df_readable = df_readable.rename(columns={
            "id": "ID", "name": "Produto", "sku": "SKU", "category": "Categoria",
            "supplier": "Fornecedor", "cost_price": "Preço de Custo",
            "sale_price": "Preço de Venda", "stock": "Estoque Atual",
            "min_stock": "Estoque Mínimo", "stock_value": "Valor Total de Custo"
        })

        if "is_low_stock" in df_readable.columns:
            df_readable = df_readable.drop(columns=["is_low_stock"])

        export_df_to_csv(df_readable, "alertas_reposicao_estoque.csv")

    # ── HELPERS DE ANIMAÇÃO OMITIDOS PARA BREVIDADE (CONTINUAM IGUAIS NO SEU APP) ──
    def _count_up(self, label, target, is_int=False, is_currency=False, delay=0, steps=35, color="#F0F6FF"):
        def _fmt(v):
            if is_currency: return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return str(int(v))

        def _tick(s):
            if not label.winfo_exists(): return
            if s > steps:
                label.configure(text=_fmt(target))
                return
            t = s / steps
            ease = 1 - (1 - t) ** 3
            label.configure(text=_fmt(target * ease))
            label.after(18, _tick, s + 1)

        label.after(delay, lambda: _tick(0))

    def _animate_progress(self, bar, target, delay=0, steps=35):
        def _tick(s):
            if not bar.winfo_exists(): return
            if s > steps:
                bar.set(target)
                return
            t = s / steps
            ease = 1 - (1 - t) ** 3
            bar.set(target * ease)
            bar.after(18, _tick, s + 1)

        bar.after(delay + 300, lambda: _tick(0))

    def _pulse(self, label, color_a, color_b, toggle=False):
        if not label.winfo_exists(): return
        label.configure(text_color=color_b if toggle else color_a)
        label.after(600, self._pulse, label, color_a, color_b, not toggle)

    def export_general_report(self, df: pd.DataFrame):
        if df.empty:
            messagebox.showwarning("Aviso", "Nenhum dado disponível para gerar relatório.")
            return

        df_readable = df.copy()
        df_readable = df_readable.rename(columns={
            "id": "ID Produto",
            "name": "Produto",
            "sku": "SKU",
            "category": "Categoria",
            "supplier": "Fornecedor",
            "cost_price": "Preço de Custo (R$)",
            "sale_price": "Preço de Venda (R$)",
            "stock": "Qtd em Estoque",
            "min_stock": "Estoque Mínimo",
            "stock_value": "Valor Total em Estoque (Custo)",
            "is_low_stock": "Alerta Estoque Baixo"
        })

        # Mapeia True/False para Sim/Não para facilitar a leitura do usuário comum
        df_readable["Alerta Estoque Baixo"] = df_readable["Alerta Estoque Baixo"].map({True: "SIM", False: "NÃO"})

        # Dispara o salvamento usando o utilitário do pandas
        export_df_to_csv(df_readable, "inventario_geral_armazem.csv")