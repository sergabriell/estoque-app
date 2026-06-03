import csv
import pandas as pd
from tkinter import filedialog, messagebox


def export_list_to_csv(default_filename: str, headers: list, rows: list):
    """Para persistir listas de objetos tratados (Produtos e Movimentações)"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv")],
        title="Salvar Relatório",
        initialfile=default_filename
    )
    if not file_path:
        return False

    try:
        with open(file_path, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(headers)
            writer.writerows(rows)

        messagebox.showinfo("Sucesso", "Arquivo exportado com sucesso!")
        return True
    except Exception as error:
        messagebox.showerror("Erro", f"Falha ao exportar CSV: {str(error)}")
        return False


def export_df_to_csv(df: pd.DataFrame, default_filename: str):
    """Para persistir DataFrames do Pandas direto (Dashboard / Alertas)"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv")],
        title="Salvar Relatório",
        initialfile=default_filename
    )
    if not file_path:
        return False

    try:
        df.to_csv(file_path, sep=";", index=False, encoding="utf-8-sig")
        messagebox.showinfo("Sucesso", "Relatório exportado com sucesso!")
        return True
    except Exception as error:
        messagebox.showerror("Erro", f"Falha ao exportar CSV: {str(error)}")
        return False