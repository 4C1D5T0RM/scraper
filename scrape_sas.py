import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        output_lines = []

        # Extract header content
        header = soup.find('header')
        if header:
            header_text = header.get_text(separator=' ', strip=True)
            if header_text:
                output_lines.append(f"HEADER: {header_text}")

        # Extract footer content
        footer = soup.find('footer')
        if footer:
            footer_text = footer.get_text(separator=' ', strip=True)
            if footer_text:
                output_lines.append(f"FOOTER: {footer_text}")

        # Extract headings and paragraphs
        elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
        for el in elements:
            tag = el.name.upper()
            text = el.get_text(separator=' ', strip=True)
            if text:
                output_lines.append(f"{tag}: {text}")

        # Show result
        if output_lines:
            print("\n📄 SCRAPED STRUCTURED TEXT:\n")
            for line in output_lines:
                print(line)

            # Ask if the user wants to save
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
            print("⚠ No main content found.")

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
