import os
import pandas as pd
from fpdf import FPDF
from fpdf.fonts import FontFace
from bidi.algorithm import get_display

def create_schedule_pdf(df, year_str, output_path):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    font_path = "Heebo-Regular.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("Hebrew font not found.")
    
    pdf.add_font("NotoHebrew", "", font_path)
    pdf.set_font("NotoHebrew", size=18)
    
    title = f"לוח שבתות וחגים לשנת {year_str}"
    pdf.cell(0, 10, text=get_display(title), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    pdf.set_font("NotoHebrew", size=10)
    
    cols = ["פרשה/מועד", "תאריך עברי", "תאריך לועזי", "כניסת שבת/חג", "צאת שבת/חג", "ליל שבת", "שבת שחרית", "סעודה שלישית", "הערות"]
    
    with pdf.table(
        borders_layout="ALL",
        cell_fill_color=(250, 249, 246),
        cell_fill_mode="ROWS",
        col_widths=(30, 25, 25, 15, 15, 25, 25, 25, 40),
        text_align="CENTER",
        headings_style=FontFace(color=(212, 175, 55), fill_color=(0, 43, 91), emphasis="")
    ) as table:
        header_row = table.row()
        for col in reversed(cols):
            header_row.cell(get_display(col))
        
        for _, row in df.iterrows():
            data_row = table.row()
            for col in reversed(cols):
                val = str(row[col]) if pd.notna(row[col]) else ""
                # Do not use style="B" since we don't have a bold font loaded
                data_row.cell(get_display(val))
                
    pdf.output(output_path)
    return output_path
