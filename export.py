import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def export_to_excel(df, filename="app_updates.xlsx"):
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Version History")
        ws = writer.sheets["Version History"]
        thin_border = Border(
            left=Side(style="thin", color="BFBFBF"),
            right=Side(style="thin", color="BFBFBF"),
            top=Side(style="thin", color="BFBFBF"),
            bottom=Side(style="thin", color="BFBFBF"),
        )
        header_fill = PatternFill("solid", start_color="2C2C2C")
        header_font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ios_fill = PatternFill("solid", start_color="D9D9D9")
        android_fill = PatternFill("solid", start_color="F2F2F2")
        ios_font = Font(name="Arial", size=9, color="1A1A1A")
        android_font = Font(name="Arial", size=9, color="1A1A1A")
        for row in ws.iter_rows(min_row=2):
            platform_cell = row[1]
            is_ios = platform_cell.value == "iOS"
            fill = ios_fill if is_ios else android_fill
            font = ios_font if is_ios else android_font
            for cell in row:
                cell.fill = fill
                cell.font = font
                cell.border = thin_border
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
            for cell in row:
                cell.font = Font(name="Arial", size=9, bold=True, color="1A1A1A")
        column_widths = {
            "A": 15, "B": 10, "C": 25, "D": 15,
            "E": 15, "F": 15, "G": 12, "H": 18,
            "I": 50, "J": 40, "K": 50, "L": 40, "M": 40,
        }
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width
        ws.row_dimensions[1].height = 20
        for row_num in range(2, ws.max_row + 1):
            ws.row_dimensions[row_num].height = 40
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
    print(f"\nSaved to {filename}")
