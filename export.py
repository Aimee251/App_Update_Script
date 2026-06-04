import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def export_to_excel(df, filename="app_updates.xlsx"):
    
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Version History")
        
        ws = writer.sheets["Version History"]
        
        # Thin border style
        thin_border = Border(
            left   = Side(style="thin", color="BFBFBF"),
            right  = Side(style="thin", color="BFBFBF"),
            top    = Side(style="thin", color="BFBFBF"),
            bottom = Side(style="thin", color="BFBFBF"),
        )
        
        # Header row 
        header_fill = PatternFill("solid", start_color="2C2C2C")  # near black
        header_font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
        
        for cell in ws[1]:
            cell.fill      = header_fill
            cell.font      = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border    = thin_border
        
        # Data rows
        # iOS  = dark gray   #4A4A4A text on #D9D9D9 background
        # Android = lighter gray #F2F2F2 background
        ios_fill     = PatternFill("solid", start_color="D9D9D9")  # medium gray
        android_fill = PatternFill("solid", start_color="F2F2F2")  # light gray
        
        ios_font     = Font(name="Arial", size=9, color="1A1A1A")  # dark text
        android_font = Font(name="Arial", size=9, color="1A1A1A")  # dark text
        
        for row in ws.iter_rows(min_row=2):
            platform_cell = row[1]  # column B = platform
            
            is_ios = platform_cell.value == "iOS"
            fill   = ios_fill     if is_ios else android_fill
            font   = ios_font     if is_ios else android_font
            
            for cell in row:
                cell.fill      = fill
                cell.font      = font
                cell.border    = thin_border
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        
        # Bold the app name column (A)
            for cell in row:
                cell.font = Font(name="Arial", size=9, bold=True, color="1A1A1A")
        
        #Column widths
        column_widths = {
            "A": 15,  # app_name
            "B": 10,  # platform
            "C": 25,  # developer
            "D": 15,  # category
            "E": 15,  # version
            "F": 15,  # release_date
            "G": 12,  # is_current
            "H": 18,  # initial_release_date
            "I": 50,  # release_notes
            "J": 40,  # update_categories
            "K": 50,  # standardized_summary
            "L": 40,  # source_url
            "M": 40,  # data_quality_notes
        }
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width
        
        # Row height for readability
        ws.row_dimensions[1].height = 20  # header row taller
        for row_num in range(2, ws.max_row + 1):
            ws.row_dimensions[row_num].height = 40
        
        # Freeze header row 
        ws.freeze_panes = "A2"
        
        # Auto filter
        ws.auto_filter.ref = ws.dimensions
    
    print(f"\nSaved to {filename}")