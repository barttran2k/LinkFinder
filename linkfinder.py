import argparse
import requests
import random,time,sys
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from colorama import Fore, Style

USER_AGENTS_URL = "https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt"


def random_color_text(text):
    color_code = random.choice([30,31,32,33,34,35,36,37,38,39,90,91,92,93,94,95,96,97]) 
    return f"\033[{color_code}m{text}\033[0m"

def signURLCRAWLER():
    url_crawler_ascii = r"""

███    █▄     ▄████████  ▄█             ▄████████    ▄████████    ▄████████  ▄█     █▄   ▄█          ▄████████    ▄████████ 
███    ███   ███    ███ ███            ███    ███   ███    ███   ███    ███ ███     ███ ███         ███    ███   ███    ███ 
███    ███   ███    ███ ███            ███    █▀    ███    ███   ███    ███ ███     ███ ███         ███    █▀    ███    ███ 
███    ███  ▄███▄▄▄▄██▀ ███            ███         ▄███▄▄▄▄██▀   ███    ███ ███     ███ ███        ▄███▄▄▄      ▄███▄▄▄▄██▀ 
███    ███ ▀▀███▀▀▀▀▀   ███            ███        ▀▀███▀▀▀▀▀   ▀███████████ ███     ███ ███       ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   
███    ███ ▀███████████ ███            ███    █▄  ▀███████████   ███    ███ ███     ███ ███         ███    █▄  ▀███████████ 
███    ███   ███    ███ ███▌    ▄      ███    ███   ███    ███   ███    ███ ███ ▄█▄ ███ ███▌    ▄   ███    ███   ███    ███ 
████████▀    ███    ███ █████▄▄██      ████████▀    ███    ███   ███    █▀   ▀███▀███▀  █████▄▄██   ██████████   ███    ███ 
             ███    ███ ▀                           ███    ███                          ▀                        ███    ███ 
                                                                                                                                                                                                         
    """
    lines = url_crawler_ascii.split('\n')

    # Chuyển màu từ trên xuống dưới
    for line in lines:
        print(random_color_text(line))
        time.sleep(0.01) 
        
def get_user_agents(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_agents = response.text.split("\n")
            return [agent.strip() for agent in user_agents if agent.strip()]
        else:
            print(
                f"Failed to retrieve user agents. Status code: {response.status_code}"
            )
    except Exception as e:
        print(f"Error: {e}")
    return []


def extract_urls_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    # Thực hiện logic để trích xuất các URL từ HTML, ví dụ:
    a_tags = soup.find_all("a", href=True)
    script_tags = soup.find_all("script", src=True)
    # Thêm các thẻ khác nếu cần thiết
    extracted_urls = [tag["href"] for tag in a_tags] + [tag["src"] for tag in script_tags]
    return extracted_urls


def extract_urls_from_json(json_data):
    urls = []

    def process_data(data):
        if isinstance(data, dict):
            for key, value in data.items():
                process_data(value)
        elif isinstance(data, list):
            for item in data:
                process_data(item)
        elif isinstance(data, str) and urlparse(data).scheme in ["http", "https"]:
            urls.append(data)

    process_data(json_data)
    return urls


def crawl_url(url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers):
    if url in visited_urls:
        return

    try:
        count_all = len(same_domain_urls) + len(diff_domain_urls)
        # print(f"{Fore.YELLOW}\033[KFound: {str(count_all)} URLs",end='\n')
        # print(f"{Fore.GREEN}\033[KProcessing: {url}", end='\r')
        
        sys.stdout.write(f"\r\033[KFound: {Fore.LIGHTRED_EX}{str(count_all)} URLs | {Fore.GREEN}Processing: {url}")
        sys.stdout.flush()
        headers["User-Agent"] = random.choice(user_agents)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            visited_urls.add(url)

            # Kiểm tra nếu response là JSON
            if 'application/json' in response.headers.get('content-type', ''):
                # Xử lý dữ liệu JSON và trích xuất URL
                json_data = response.json()
                json_urls = extract_urls_from_json(json_data)
                for json_url in sorted(json_urls):
                    full_url = urljoin(url, json_url)
                    parsed_url = urlparse(full_url)

                    if parsed_url.netloc == urlparse(url).netloc:
                        same_domain_urls.add(full_url)
                        if full_url not in visited_urls:
                            crawl_url(full_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers)
                    else:
                        diff_domain_urls.add(full_url)

            else:
                # Xử lý dữ liệu HTML và trích xuất URL
                extracted_urls = extract_urls_from_html(response.text)
                for extracted_url in sorted(extracted_urls):
                    full_url = urljoin(url, extracted_url)
                    parsed_url = urlparse(full_url)

                    if parsed_url.netloc == urlparse(url).netloc:
                        same_domain_urls.add(full_url)
                        if full_url not in visited_urls:
                            crawl_url(full_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers)
                    else:
                        diff_domain_urls.add(full_url)

    except Exception as e:
        print(f"Error crawling {url}: {e}")


def main():
    signURLCRAWLER()
    parser = argparse.ArgumentParser(description="URL Crawler")
    parser.add_argument("-u", "--url", type=str, help="Initial URL")
    parser.add_argument("-H", "--header", action="append", metavar="KEY:VALUE", help="Custom headers")
    parser.add_argument("-o", "--output", type=str, help="Output file name")
    parser.add_argument("-t", "--type", type=str, help="Type of URLs to search (e.g., web, image, file)")
    parser.add_argument("-b", "--blacklist", type=str, help="Comma-separated list of blacklisted domains")
    parser.add_argument("-T", "--thread", type=str, help="Number of threads to use")
    args = parser.parse_args()

    if not args.url:
        print("Please provide an initial URL using -u or --url.")
        return

    user_agents = get_user_agents(USER_AGENTS_URL)
    initial_url = args.url
    visited_urls = set()
    same_domain_urls = set()
    diff_domain_urls = set()

    headers = {}
    if args.header:
        for header in args.header:
            key, value = header.split(":", 1)
            headers[key.strip()] = value.strip()

    try:
        while True:
            crawl_url(initial_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers)
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user.")

    print("\nResults:")
    print(f"{Fore.GREEN}Same Domain URLs:{Style.RESET_ALL}")
    for url in sorted(same_domain_urls):
        print(Fore.GREEN + url + Style.RESET_ALL)
        if args.output:
            with open(args.output, "a") as output_file:
                output_file.write(url + "\n")

    print(f"{Fore.YELLOW}Different Domain URLs:{Style.RESET_ALL}")
    for url in sorted(diff_domain_urls):
        print(Fore.YELLOW + url + Style.RESET_ALL)
        if args.output:
            with open(args.output, "a") as output_file:
                output_file.write(url + "\n")



if __name__ == "__main__":
    main()
