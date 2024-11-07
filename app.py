import os
import fitz
import pandas as pd
import io
from tkinter import Tk, Label, Button, filedialog, StringVar, messagebox, Canvas, Frame
from tkinter import ttk
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as reportlab_canvas
from reportlab.lib.pagesizes import A1

# Function to create a gradient background using a canvas
def create_gradient(canvas, width, height, color1, color2):
    for i in range(height):
        r, g, b = [
            int(color1[j] + (color2[j] - color1[j]) * (i / height)) for j in range(3)
        ]
        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=hex_color)

# Convert color from hex to RGB tuple
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Function to automatically find default input files in the current directory
def find_default_files():
    current_dir = os.getcwd()
    bestellingen_path = os.path.join(current_dir, "bol.com - Bestellingen.pdf")
    verzendzegels_path = None

    # Search for the verzendzegels PDF file with a date suffix
    for file in os.listdir(current_dir):
        if file.startswith("verzendzegels") and file.endswith(".pdf"):
            verzendzegels_path = os.path.join(current_dir, file)
            break
    
    return bestellingen_path if os.path.isfile(bestellingen_path) else "", verzendzegels_path or ""

# Main GUI class
class PDFMergerApp:
    def __init__(self, root, window_title="Bol Splines", window_size="600x400"):
        self.root = root
        self.root.title(window_title)
        self.root.geometry(window_size)
        self.root.resizable(False, False)
        
        # Create the gradient background
        canvas = Canvas(self.root, width=600, height=400)
        canvas.pack(fill="both", expand=True)
        create_gradient(
            canvas,
            600,
            400,
            hex_to_rgb("#D0E1F9"),  # Light color
            hex_to_rgb("#4D648D")   # Darker color
        )
        
        # Create a frame for content
        self.frame = Frame(canvas, bg="#F7FBFF", bd=2, relief="ridge")
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=540, height=340)

        # Initialize StringVars
        self.doc_path_var = StringVar()
        self.input_pdf_path_var = StringVar()
        self.output_pdf_path_var = StringVar(value=os.path.join(os.getcwd(), "output.pdf"))

        # Auto-populate paths if possible
        default_doc_path, default_input_path = find_default_files()
        if default_doc_path:
            self.doc_path_var.set(default_doc_path)
        if default_input_path:
            self.input_pdf_path_var.set(default_input_path)

        # Build the UI
        self.create_ui()

    def create_ui(self):
        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TLabel", background="#F7FBFF", font=("Helvetica", 10))

        # UI elements
        ttk.Label(self.frame, text="Select Bestellingen PDF:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Button(self.frame, text="Browse...", command=self.select_doc_pdf).grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(self.frame, textvariable=self.doc_path_var, wraplength=400).grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        ttk.Label(self.frame, text="Select Verzendzegels PDF:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Button(self.frame, text="Browse...", command=self.select_input_pdf).grid(row=2, column=1, padx=10, pady=5)
        ttk.Label(self.frame, textvariable=self.input_pdf_path_var, wraplength=400).grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        ttk.Label(self.frame, text="Select Output PDF Path:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ttk.Button(self.frame, text="Browse...", command=self.select_output_pdf).grid(row=4, column=1, padx=10, pady=5)
        ttk.Label(self.frame, textvariable=self.output_pdf_path_var, wraplength=400).grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        ttk.Button(self.frame, text="Run", command=self.run_processing, style="TButton").grid(row=6, column=0, columnspan=2, pady=15)

    def select_doc_pdf(self):
        path = filedialog.askopenfilename(title="Select Bestellingen PDF", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.doc_path_var.set(path)

    def select_input_pdf(self):
        path = filedialog.askopenfilename(title="Select Verzendzegels PDF", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.input_pdf_path_var.set(path)

    def select_output_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", title="Save output as", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.output_pdf_path_var.set(path)

    def run_processing(self):
        doc_path = self.doc_path_var.get()
        input_pdf_path = self.input_pdf_path_var.get()
        output_pdf_path = self.output_pdf_path_var.get()

        if not doc_path or not input_pdf_path or not output_pdf_path:
            messagebox.showerror("Error", "Please select all file paths before running.")
            return

        try:
            # Main processing logic
            doc = fitz.open(doc_path)
            df_list = []
            for page in doc:
                tabs = page.find_tables()
                if tabs.tables:
                    df = pd.DataFrame(tabs[0].extract())
                    df.columns = df.iloc[0]
                    df = df[1:].reset_index(drop=True)
                    df = df.dropna(axis=1, how='all')
                    df_list.append(df)

            df = pd.concat(df_list, axis=0).fillna("")
            order_df = df["Bestelnr."].replace(r'^\s*$', pd.NA, regex=True).dropna()
            df['EAN'] = df['EAN'].replace('', pd.NA).ffill()
            df['Bestelnr.'] = df['Bestelnr.'].replace('', pd.NA).ffill()

            grouped_df = df.groupby(["Bestelnr.", 'EAN']).agg({
                'Klantnaam': 'first',
                'Referentie': ''.join,
                'Product': ''.join,
                'Aant.': 'first'
            }).reset_index()
            # "EAN: " + grouped_df["EAN"] + "\n" +
            grouped_df["Ref"] =  grouped_df["Referentie"] + "\n" + "Aantal: " + grouped_df["Aant."]

            df = grouped_df.groupby(["Bestelnr."]).agg({
                'Klantnaam': 'first',
                'Ref': '\n'.join,
                'Product': '\n'.join
            }).reset_index().set_index("Bestelnr.")

            df = df.loc[order_df.values]
            selected_strings = df["Ref"].tolist()

            input_reader = PdfReader(input_pdf_path)
            output_writer = PdfWriter()

            for i, text in enumerate(selected_strings):
                if i < len(input_reader.pages):
                    packet = io.BytesIO()
                    c = reportlab_canvas.Canvas(packet, pagesize=A1)
                    c.setFont("Helvetica", 6)
                    text_obj = c.beginText(5, 150)
                    text_obj.setFont("Helvetica", 6)

                    for line in text.split('\n'):
                        text_obj.textLine(line)

                    c.drawText(text_obj)
                    c.save()
                    packet.seek(0)
                    new_pdf = PdfReader(packet)
                    page = input_reader.pages[i]
                    page.merge_page(new_pdf.pages[0])
                    output_writer.add_page(page)

            with open(output_pdf_path, 'wb') as output_file:
                output_writer.write(output_file)

            messagebox.showinfo("Success", f"PDF created successfully: {output_pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

root = Tk()
app = PDFMergerApp(root)
root.mainloop()
