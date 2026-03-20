from fpdf import FPDF
import io

def generate_formatted_pdf(start_date, end_date, df_vol, df_qual, df_live):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, f"Sparta Team Report: {start_date} to {end_date}", ln=True, align='C')
    pdf.ln(5)
    
    def draw_pdf_table(df, title):
        if df.empty: return
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 10, title, ln=True)
        
        df_reset = df.reset_index()
        if 'index' in df_reset.columns:
            df_reset.rename(columns={'index': 'Advisor'}, inplace=True)
            
        cols = df_reset.columns.tolist()
        page_width = pdf.w - 2 * pdf.l_margin
        col_width_advisor = 40
        rem_width = page_width - col_width_advisor
        col_width_other = rem_width / (len(cols) - 1) if len(cols) > 1 else 0
        row_height = 7
        
        # Header
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(220, 230, 245)
        for col in cols:
            w = col_width_advisor if col == cols[0] else col_width_other
            pdf.cell(w, row_height, str(col).replace('_', ' '), border=1, fill=True, align='C')
        pdf.ln(row_height)
        
        # Rows
        pdf.set_font("Arial", '', 9)
        fill = False
        for _, row in df_reset.iterrows():
            pdf.set_fill_color(248, 248, 248)
            for col in cols:
                w = col_width_advisor if col == cols[0] else col_width_other
                val = str(row[col])
                align = 'L' if col == cols[0] else 'R'
                if str(row[cols[0]]) == "GRAND TOTAL":
                    pdf.set_font("Arial", 'B', 9)
                else:
                    pdf.set_font("Arial", '', 9)
                pdf.cell(w, row_height, val, border=1, fill=fill, align=align)
            pdf.ln(row_height)
            fill = not fill
        pdf.ln(10)

    draw_pdf_table(df_vol, "1. Applications Volume")
    draw_pdf_table(df_qual, "2. Quality Audit Status")
    draw_pdf_table(df_live, "3. Live Status Pipeline")
    
    return pdf.output(dest='S').encode('latin-1')
