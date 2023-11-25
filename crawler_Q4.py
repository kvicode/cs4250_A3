import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost")  # Replace with your MongoDB connection string
db = client["web_crawler"]
pages_collection = db["pages"]

class Frontier:
    def __init__(self, initial_url):
        self.queue = [initial_url]
        self.visited = set()

    def next_url(self):
        if not self.done():
            url = self.queue.pop(0)
            self.visited.add(url)
            return url
        return None

    def add_url(self, url):
        if url not in self.visited and url not in self.queue:
            self.queue.append(url)

    def done(self):
        return len(self.queue) == 0

def retrieve_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
            return html.decode("utf-8")
    except Exception as e:
        print(f"Error retrieving URL {url}: {e}")
        return None

def store_page(url, html):
    if html:
        page_data = {"url": url, "html": html}
        pages_collection.insert_one(page_data)

def target_page(html):
    soup = BeautifulSoup(html, "html.parser")
    headings = soup.find_all("h2")
    for heading in headings:
        if heading.text.strip().lower() == "permanent faculty":
            return True
    return False

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    return [link["href"] for link in links]

def clear_frontier():
    frontier.queue.clear()

def crawler_thread(frontier):
    while not frontier.done():
        url = frontier.next_url()
        html = retrieve_url(url)
        store_page(url, html)
        if target_page(html):
            print(f"Target page found: {url}")
            clear_frontier()
        else:
            for link in parse(html):
                frontier.add_url(link)

# Initial setup with the CS home page
initial_url = "https://www.cpp.edu/sci/computer-science/"
frontier = Frontier(initial_url)

# Run the crawler
crawler_thread(frontier)
