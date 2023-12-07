import argparse
import requests
import random
import time
import sys
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from colorama import Fore, Style

USER_AGENTS_URL = "https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt"


def random_color_text(text):
    color_code = random.choice([30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 90, 91, 92, 93, 94, 95, 96, 97])
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
    █████████    ███    ███ █████▄▄██      ████████▀    ███    ███   ███    █▀   ▀███▀███▀  █████▄▄██   ██████████   ███    ███ 
                 ███    ███ ▀                           ███    ███                          ▀                        ███    ███ 
    """
    for i in url_crawler_ascii.split("\n"):
        print(random_color_text(i))
        
def get_user_agents(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_agents = response.text.split("\n")
            return [agent.strip() for agent in user_agents if agent.strip()]
        else:
            print(f"Failed to retrieve user agents. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return []

def extract_urls_from_html(html_content, base_url):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        a_tags = soup.find_all("a", href=True)
        script_tags = soup.find_all("script", src=True)
        extracted_urls = [tag["href"] for tag in a_tags] + [tag["src"] for tag in script_tags]
        parsed_url = urlparse(base_url)
        if parsed_url.path.endswith("robots.txt"):
            # If the URL ends with robots.txt, get disallowed URIs from robots.txt
            disallowed_uris = get_disallowed_uris(full_url)
            for disallowed_uri in disallowed_uris:
                disallowed_url = urljoin(full_url, disallowed_uri)
            extracted_urls.append(disallowed_url)
            return extracted_urls 
        else:
            return extracted_urls

    except Exception as e:
        print(f"Error extracting URLs from HTML: {e}")
        pass  # Ignore the error and continue


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


def crawl_single_url(url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers, retry=3, timeout=30):
    for _ in range(retry):
        try:
            count_all = len(same_domain_urls) + len(diff_domain_urls)
            sys.stdout.write(f"\r\033[KFound: {Fore.LIGHTRED_EX}{str(count_all)} URLs | {Fore.GREEN}Processing: {url}")
            sys.stdout.flush()
            headers["User-Agent"] = random.choice(user_agents)
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                visited_urls.add(url)
                
                if 'application/json' in response.headers.get('content-type', ''):
                    json_data = response.json()
                    json_urls = extract_urls_from_json(json_data)
                    for json_url in sorted(json_urls):
                        full_url = urljoin(url, json_url)
                        parsed_url = urlparse(full_url)
                        if parsed_url.netloc == urlparse(url).netloc:
                            same_domain_urls.add(full_url)
                            if full_url not in visited_urls:
                                crawl_single_url(full_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers)
                        else:
                            diff_domain_urls.add(full_url)
                else:
                    extracted_urls = extract_urls_from_html(response.text, url)
                    for extracted_url in sorted(extracted_urls):
                        full_url = urljoin(url, extracted_url)
                        parsed_url = urlparse(full_url)
                        if parsed_url.netloc == urlparse(url).netloc:
                            same_domain_urls.add(full_url)
                            if full_url not in visited_urls:
                                crawl_single_url(full_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers)
                        else:
                            diff_domain_urls.add(full_url)
                break  # Stop retrying if successful
        except requests.RequestException as e:
            print(f"\nError crawling {url}: {e}")
            time.sleep(1)  # Sleep for a while before retrying


def crawl_with_threads(initial_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers, num_threads, retry=3, timeout=30):
    from concurrent.futures import ThreadPoolExecutor

    def crawl_url_wrapper(url):
        crawl_single_url(url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers, retry=retry, timeout=timeout)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(crawl_url_wrapper, url) for url in same_domain_urls | diff_domain_urls]

        for future in futures:
            future.result()

def print_results(same_domain_urls, diff_domain_urls, output_file=None):
    if output_file:
        with open(output_file, "w") as file:
            print(f"{Fore.GREEN}Same Domain URLs:{Style.RESET_ALL}", file=file)
            for url in sorted(same_domain_urls):
                print(url, file=file)

            print(f"{Fore.YELLOW}Different Domain URLs:{Style.RESET_ALL}", file=file)
            for url in sorted(diff_domain_urls):
                print(url, file=file)
    else:
        print("\nResults:")
        print(f"{Fore.GREEN}Same Domain URLs:{Style.RESET_ALL}")
        for url in sorted(same_domain_urls):
            print(Fore.GREEN + url + Style.RESET_ALL)

        print(f"{Fore.YELLOW}Different Domain URLs:{Style.RESET_ALL}")
        for url in sorted(diff_domain_urls):
            print(Fore.YELLOW + url + Style.RESET_ALL)


def main():
    signURLCRAWLER()
    parser = argparse.ArgumentParser(description="URL Crawler")
    parser.add_argument("-u", "--url", type=str, help="Initial URL")
    parser.add_argument("-H", "--header", action="append", metavar="KEY:VALUE", help="Custom headers")
    parser.add_argument("-o", "--output", type=str, help="Output file name")
    parser.add_argument("-t", "--type", type=str, help="Type of URLs to search (e.g., web, image, file)")
    parser.add_argument("-b", "--blacklist", type=str, help="Comma-separated list of blacklisted domains")
    parser.add_argument("-T", "--thread", type=str, help="Number of threads to use")
    parser.add_argument("--retry", type=int, default=3, help="Number of retries for a failed request")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout for each request in seconds")
    parser.add_argument("--show", choices=["same", "diff", "all"], default="same", help="Show URLs of the same domain, different domain, or both")
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
        crawl_single_url(initial_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers, retry=args.retry, timeout=args.timeout)
        if args.thread:
            num_threads = int(args.thread)
            crawl_with_threads(initial_url, visited_urls, same_domain_urls, diff_domain_urls, user_agents, headers, num_threads, retry=args.retry, timeout=args.timeout)
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user.")

    print("\nResults:")
    if args.show == "same":
        print_results(same_domain_urls, set(), args.output)
    elif args.show == "diff":
        print_results(set(), diff_domain_urls, args.output)
    else:
        print_results(same_domain_urls, diff_domain_urls, args.output)

if __name__ == "__main__":
    main()
