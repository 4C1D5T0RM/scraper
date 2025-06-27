import requests
from bs4 import BeautifulSoup
from docx import Document

def process_list_items_docx(element, level, doc):
    lis = element.find_all('li')
    for li in lis:
        para = doc.add_paragraph()
        para.style = 'List Paragraph'
        para.paragraph_format.left_indent = level * 300
        add_runs_from_element(li, para)
        for sublist in li.find_all(['ul', 'ol']):
            process_list_items_docx(sublist, level + 1, doc)

def add_runs_from_element(el, para):
    for part in el.descendants:
        if part.name == 'a':
            continue  # Skip link text entirely
        elif part.name is None:
            text = part.strip()
            if text:
                para.add_run(text)

def extract_with_nesting_docx(container, doc, level=0):
    if not container:
        return
    elements = container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'ul', 'ol'])
    for el in elements:
        tag = el.name.upper()
        indent = level * 300
        if tag in ['H1', 'H2', 'H3', 'H4', 'H5']:
            heading_level = int(tag[1])
            para = doc.add_paragraph()
            para.style = f'Heading {heading_level}'
            para.paragraph_format.left_indent = indent
            add_runs_from_element(el, para)
        elif tag == 'P':
            para = doc.add_paragraph()
            para.style = 'Normal'
            para.paragraph_format.left_indent = indent
            add_runs_from_element(el, para)
        elif tag in ['UL', 'OL']:
            process_list_items_docx(el, level + 1, doc)

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

def extract_with_nesting_txt(container_name, container, output_lines, level=0):
    if not container:
        return
    elements = container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'ul', 'ol'])
    for el in elements:
        tag = el.name.upper()
        text = get_text_without_links(el)
        indent = '  ' * level
        if not text:
            continue
        if tag in ['H1', 'H2', 'H3', 'H4', 'H5']:
            heading_level = int(tag[1])
            output_lines.append(f"{indent}{container_name} | {tag} (level {heading_level}): {text}")
        elif tag == 'P':
            output_lines.append(f"{indent}{container_name} | {tag}: {text}")
        elif tag in ['UL', 'OL']:
            output_lines.append(f"{indent}{container_name} | {tag}:")
            process_list_items_txt(container_name, el, level + 1, output_lines)

def get_text_without_links(el):
    parts = []
    for part in el.descendants:
        if part.name == 'a':
            continue
        elif part.name is None:
            text = part.strip()
            if text:
                parts.append(text)
    return ' '.join(parts)

def save_as_docx(filename, soup, scrape_header, scrape_body, scrape_footer):
    doc = Document()
    header = soup.find('header')
    footer = soup.find('footer')
    body = soup.find('body')

    if scrape_header and header:
        doc.add_paragraph("HEADER:", style='Normal')
        extract_with_nesting_docx(header, doc)
    else:
        if header:
            header.extract()

    if not scrape_footer and footer:
        footer.extract()

    if scrape_body and body:
        doc.add_paragraph("BODY:", style='Normal')
        extract_with_nesting_docx(body, doc)

    if scrape_footer and footer:
        doc.add_paragraph("FOOTER:", style='Normal')
        extract_with_nesting_docx(footer, doc)

    doc.save(f"{filename}.docx")
    print(f"✅ Content saved as {filename}.docx")

def save_as_txt(filename, soup, scrape_header, scrape_body, scrape_footer):
    output_lines = []
    header = soup.find('header')
    footer = soup.find('footer')
    body = soup.find('body')

    if scrape_header and header:
        output_lines.append("HEADER:")
        extract_with_nesting_txt("HEADER", header, output_lines)
    else:
        if header:
            header.extract()

    if not scrape_footer and footer:
        footer.extract()

    if scrape_body and body:
        output_lines.append("BODY:")
        extract_with_nesting_txt("BODY", body, output_lines)

    if scrape_footer and footer:
        output_lines.append("FOOTER:")
        extract_with_nesting_txt("FOOTER", footer, output_lines)

    with open(f"{filename}.txt", "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")
    print(f"✅ Content saved as {filename}.txt")

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        scrape_header = input("🔍 Do you want to scrape the HEADER content? (yes/no): ").strip().lower() in ['yes', 'y']
        scrape_body = input("🔍 Do you want to scrape the BODY content? (yes/no): ").strip().lower() in ['yes', 'y']
        scrape_footer = input("🔍 Do you want to scrape the FOOTER content? (yes/no): ").strip().lower() in ['yes', 'y']

        filename = input("📄 Enter a filename (without extension): ").strip()
        if not filename:
            filename = "scraped_content"

        filetype = input("💾 What file type do you want to save as? (txt/docx): ").strip().lower()

        if filetype == 'docx':
            save_as_docx(filename, soup, scrape_header, scrape_body, scrape_footer)
        else:
            save_as_txt(filename, soup, scrape_header, scrape_body, scrape_footer)

        another = input("\n💾 Do you want to save this content in another format too? (yes/no): ").strip().lower()
        if another in ['yes', 'y']:
            alt_filetype = 'docx' if filetype == 'txt' else 'txt'
            alt_filename = input(f"📄 Enter a filename for the {alt_filetype} file (without extension): ").strip()
            if not alt_filename:
                alt_filename = f"{filename}_alt"
            if alt_filetype == 'docx':
                save_as_docx(alt_filename, soup, scrape_header, scrape_body, scrape_footer)
            else:
                save_as_txt(alt_filename, soup, scrape_header, scrape_body, scrape_footer)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching the page: {e}")

def main():
    while True:
        url = input("🌐 Enter the URL to scrape (or type 'exit' to quit): ").strip()
        if url.lower() == 'exit':
            print("👋 Goodbye!")
            break
        if not url.startswith('http'):
            print("⚠ Please enter a valid URL (including http/https).")
            continue
        scrape_website(url)

if __name__ == "__main__":
    main()
