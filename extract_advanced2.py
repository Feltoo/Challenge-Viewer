import PyPDF2

def extract_text(pdf_path, txt_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        with open(txt_path, 'w', encoding='utf-8') as out_f:
            for i, page in enumerate(reader.pages):
                out_f.write(f"\n--- Page {i + 1} ---\n")
                out_f.write(page.extract_text() or '')

if __name__ == "__main__":
    extract_text(r"c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\public\notes\advanced_2.pdf", r"c:\Users\Felto\.gemini\antigravity\scratch\challenge-viewer\advanced2_notes.txt")
