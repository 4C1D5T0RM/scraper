import requests
from bs4 import BeautifulSoup

def process_list_items(container_name, element, level, output_lines):
    lis = element.find_all('li', recursive=False)
    for li in lis:
        text = li.get_text(separator=' ', strip=True)
        indent = '  ' * level
        if text:
            output_lines.append(f"{indent}{container_name} | LI (level {level}): {text}")
        for sublist in li.find_all(['ul', 'ol'], recursive=False):
            output_lines.append(f"{indent}{container_name} | {sublist.name.upper()}:")
            process_list_items(container_name, sublist, level + 1, output_lines)

def extract_with_nesting(container_name, container, output_lines, level=0):
    if not container:
        return
    elements = container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a', 'span', 'ul', 'ol'])
    for el in elements:
        tag = el.name.upper()
        indent = '  ' * level
        if tag in ['H1', 'H2', 'H3', 'H4', 'H5']:
            text = el.get_text(separator=' ', strip=True)
            if text:
                heading_level = int(tag[1])
                output_lines.append(f"{indent}{container_name} | {tag} (level {heading_level}): {text}")
        elif tag in ['UL', 'OL']:
            output_lines.append(f"{indent}{container_name} | {tag}:")
            process_list_items(container_name, el, level + 1, output_lines)
        else:
            text = el.get_text(separator=' ', strip=True)
            if text:
                output_lines.append(f"{indent}{container_name} | {tag}: {text}")

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        output_lines = []

        # Ask user what to scrape
        scrape_header = input("🔍 Do you want to scrape the HEADER content? (yes/no): ").strip().lower()
        scrape_body = input("🔍 Do you want to scrape the BODY content? (yes/no): ").strip().lower()
        scrape_footer = input("🔍 Do you want to scrape the FOOTER content? (yes/no): ").strip().lower()

        # HEADER
        if scrape_header in ['yes', 'y']:
            header = soup.find('header')
            extract_with_nesting("HEADER", header, output_lines)
        else:
            print("ℹ Skipping HEADER content.")

        # FOOTER (remove before body to avoid duplication)
        footer = soup.find('footer')

        # BODY
        if scrape_body in ['yes', 'y']:
            body = soup.find('body')
            if body:
                if scrape_header in ['yes', 'y'] and (header := soup.find('header')):
                    header.extract()
                if scrape_footer in ['yes', 'y'] and footer:
                    footer.extract()
                extract_with_nesting("BODY", body, output_lines)
        else:
            print("ℹ Skipping BODY content.")

        # FOOTER
        if scrape_footer in ['yes', 'y']:
            extract_with_nesting("FOOTER", footer, output_lines)
        else:
            print("ℹ Skipping FOOTER content.")

        if output_lines:
            print("\n📄 SCRAPED STRUCTURED TEXT:\n")
            for line in output_lines:
                print(line)

            save = input("\n💾 Do you want to save this content to a .txt file? (yes/no): ").strip().lower()
            if save in ['yes', 'y']:
                filename = input("📄 Enter a filename (without extension): ").strip()
                if not filename:
                    filename = "scraped_content"
                with open(f"{filename}.txt", "w", encoding="utf-8") as f:
                    for line in output_lines:
                        f.write(line + "\n")
                print(f"✅ Content saved as {filename}.txt")
            else:
                print("📝 Content not saved.")
        else:
            print("⚠ No relevant content found.")

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
