import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT

# ---------- TEXT CLEANING ----------
def get_text_without_links(el):
    return ' '.join(
        part.strip()
        for part in el.strings
        if not (hasattr(part.parent, 'name') and part.parent.name == 'a')
    )

def collect_text_set(container):
    texts = set()
    if not container:
        return texts
    elements = container.find_all(['h1','h2','h3','h4','h5','p','li'])
    for el in elements:
        text = get_text_without_links(el)
        if text:
            texts.add(text)
    return texts

# ---------- TXT EXPORT ----------
def save_as_txt(filename, soup, scrape_header, scrape_body, scrape_footer):
    output_lines = []
    header = soup.find('header')
    footer = soup.find('footer')
    body = soup.find('body')

    header_texts = set()
    footer_texts = set()

    if scrape_header and header:
        output_lines.append("HEADER:")
        header_texts = collect_text_set(header)
        extract_with_nesting_txt("HEADER", header, output_lines)
    else:
        if header:
            header.extract()

    if scrape_body and body:
        output_lines.append("BODY:")
        extract_with_nesting_txt_skip_set("BODY", body, output_lines, header_texts, footer_texts)

    if scrape_footer and footer:
        output_lines.append("FOOTER:")
        footer_texts = collect_text_set(footer)
        extract_with_nesting_txt("FOOTER", footer, output_lines)

    with open(f"{filename}.txt", "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")
    print(f"✅ Saved as {filename}.txt")
    return output_lines

def extract_with_nesting_txt(container_name, container, output_lines, level=0):
    if not container:
        return
    elements = container.find_all(['h1','h2','h3','h4','h5','p','ul','ol'])
    for el in elements:
        tag = el.name.upper()
        text = get_text_without_links(el)
        indent = '  ' * level
        if not text:
            continue
        if tag.startswith('H'):
            heading_level = int(tag[1])
            output_lines.append(f"{indent}{container_name} | {tag} (level {heading_level}): {text}")
        elif tag == 'P':
            output_lines.append(f"{indent}{container_name} | P: {text}")
        elif tag in ['UL', 'OL']:
            output_lines.append(f"{indent}{container_name} | {tag}:")
            process_list_items_txt(container_name, el, level + 1, output_lines)

def extract_with_nesting_txt_skip_set(container_name, container, output_lines, skip_header, skip_footer, level=0):
    if not container:
        return
    elements = container.find_all(['h1','h2','h3','h4','h5','p','ul','ol'])
    for el in elements:
        tag = el.name.upper()
        text = get_text_without_links(el)
        indent = '  ' * level
        if not text or text in skip_header or text in skip_footer:
            continue
        if tag.startswith('H'):
            heading_level = int(tag[1])
            output_lines.append(f"{indent}{container_name} | {tag} (level {heading_level}): {text}")
        elif tag == 'P':
            output_lines.append(f"{indent}{container_name} | P: {text}")
        elif tag in ['UL', 'OL']:
            output_lines.append(f"{indent}{container_name} | {tag}:")
            process_list_items_txt(container_name, el, level + 1, output_lines)

def process_list_items_txt(container_name, element, level, output_lines):
    lis = element.find_all('li')
    for li in lis:
        text = get_text_without_links(li)
        indent = '  ' * level
        if text:
            output_lines.append(f"{indent}{container_name} | LI (level {level}): {text}")
        for sublist in li.find_all(['ul', 'ol']):
            output_lines.append(f"{indent}{container_name} | {sublist.name.upper()}:")
            process_list_items_txt(container_name, sublist, level + 1, output_lines)

# ---------- DOCX EXPORT ----------
def add_runs_from_element(el, para):
    added = False
    for part in el.strings:
        if hasattr(part.parent, 'name') and part.parent.name == 'a':
            continue
        text = part.strip()
        if text:
            para.add_run(text)
            added = True
    return added

def process_list_items_docx(element, level, doc):
    lis = element.find_all('li')
    for li in lis:
        para = doc.add_paragraph()
        para.style = 'List Paragraph'
        para.paragraph_format.left_indent = level * 300
        added = add_runs_from_element(li, para)
        if not added:
            doc._body._element.remove(para._element)
        for sublist in li.find_all(['ul','ol']):
            process_list_items_docx(sublist, level + 1, doc)

def extract_with_nesting_docx_collect(container, doc, level=0):
    lines = []
    if not container:
        return lines
    elements = container.find_all(['h1','h2','h3','h4','h5','p','ul','ol'])
    for el in elements:
        tag = el.name.upper()
        indent = level * 300
        line_text = get_text_without_links(el)
        if not line_text:
            continue
        lines.append(line_text)
        if tag.startswith('H'):
            heading_level = int(tag[1])
            para = doc.add_paragraph()
            para.style = f'Heading {heading_level}'
            para.paragraph_format.left_indent = indent
            added = add_runs_from_element(el, para)
            if not added:
                doc._body._element.remove(para._element)
        elif tag == 'P':
            para = doc.add_paragraph()
            para.style = 'Normal'
            para.paragraph_format.left_indent = indent
            added = add_runs_from_element(el, para)
            if not added:
                doc._body._element.remove(para._element)
        elif tag in ['UL', 'OL']:
            process_list_items_docx(el, level + 1, doc)
    return lines

def save_as_docx(filename, soup, scrape_header, scrape_body, scrape_footer):
    doc = Document()
    lines = []
    header = soup.find('header')
    footer = soup.find('footer')
    body = soup.find('body')

    if scrape_header and header:
        doc.add_paragraph("HEADER:")
        lines.append("HEADER:")
        lines += extract_with_nesting_docx_collect(header, doc)
    else:
        if header:
            header.extract()

    if scrape_body and body:
        doc.add_paragraph("BODY:")
        lines.append("BODY:")
        lines += extract_with_nesting_docx_collect(body, doc)

    if scrape_footer and footer:
        doc.add_paragraph("FOOTER:")
        lines.append("FOOTER:")
        lines += extract_with_nesting_docx_collect(footer, doc)

    doc.save(f"{filename}.docx")
    print(f"✅ Saved as {filename}.docx")
    return lines

# ---------- BILINGUAL TABLE ----------
def save_as_bilingual_table(filename, lines):
    doc = Document()
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'  # Ensure visible gridlines
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'SOURCE LANGUAGE'
    hdr_cells[1].text = 'TARGET LANGUAGE'

    for cell in hdr_cells:
        for p in cell.paragraphs:
            run = p.runs[0]
            run.font.bold = True
            run.font.size = Pt(10)

    for line in lines:
        if line.strip():
            row_cells = table.add_row().cells
            row_cells[0].text = line
            row_cells[1].text = ""

    bilingual_filename = input("📄 Enter filename for bilingual table (no extension): ").strip() or f"{filename}_bilingual"
    doc.save(f"{bilingual_filename}.docx")
    print(f"✅ Bilingual table saved as {bilingual_filename}.docx")

# ---------- MAIN ----------
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        scrape_header = input("🔍 Scrape HEADER? (yes/no): ").strip().lower() in ['yes', 'y']
        scrape_body = input("🔍 Scrape BODY? (yes/no): ").strip().lower() in ['yes', 'y']
        scrape_footer = input("🔍 Scrape FOOTER? (yes/no): ").strip().lower() in ['yes', 'y']

        filename = input("📄 Filename (no extension): ").strip() or "scraped_content"
        filetype = input("💾 Save as txt or docx? ").strip().lower()

        lines = []
        if filetype == 'txt':
            lines = save_as_txt(filename, soup, scrape_header, scrape_body, scrape_footer)
        else:
            lines = save_as_docx(filename, soup, scrape_header, scrape_body, scrape_footer)

        other_format = 'docx' if filetype == 'txt' else 'txt'
        if input(f"💾 Export to {other_format} too? (yes/no): ").strip().lower() in ['yes', 'y']:
            alt_filename = input(f"📄 {other_format} filename (no extension): ").strip() or f"{filename}_alt"
            if other_format == 'txt':
                save_as_txt(alt_filename, soup, scrape_header, scrape_body, scrape_footer)
            else:
                save_as_docx(alt_filename, soup, scrape_header, scrape_body, scrape_footer)

        if filetype == 'docx':
            if input("📝 Export as bilingual table for translation? (yes/no): ").strip().lower() in ['yes', 'y']:
                save_as_bilingual_table(filename, lines)
        else:
            print("⚠ Bilingual table export only available after DOCX export.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def main():
    while True:
        url = input("🌐 URL to scrape (or type 'exit'): ").strip()
        if url.lower() == 'exit':
            print("👋 Exiting.")
            break
        if not url.startswith('http'):
            print("⚠ Please include http/https in the URL.")
            continue
        scrape_website(url)

if __name__ == "__main__":
    main()
