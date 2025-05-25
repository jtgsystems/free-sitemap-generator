import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class SiteMapGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None # Initialize thread attribute
        self.initUI()

    def initUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout()

        # URL Input Layout
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter website URL")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        # Button
        self.generate_button = QPushButton("Generate Site Map")
        self.generate_button.clicked.connect(self.start_crawl_process) # Connect button
        main_layout.addWidget(self.generate_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Text Area for Site Map / Errors
        self.results_text_area = QTextEdit()
        self.results_text_area.setReadOnly(True) # Make it read-only for now
        main_layout.addWidget(self.results_text_area)

        self.setLayout(main_layout)
        self.setWindowTitle('Site Map Generator')
        self.setGeometry(300, 300, 600, 400) # x, y, width, height
        self.show()

    def start_crawl_process(self):
        url_text = self.url_input.text().strip()
        parsed_url = urlparse(url_text)

        if not parsed_url.scheme or parsed_url.scheme not in ['http', 'https'] or not parsed_url.netloc:
            self.results_text_area.setText("Error: Invalid URL. Please enter a full URL including http:// or https:// and a domain name (e.g., http://example.com).")
            return

        url = parsed_url.geturl() # Use the cleaned/re-assembled URL

        self.generate_button.setEnabled(False)
        self.results_text_area.clear()
        self.results_text_area.append(f"Starting crawl for: {url}\n")
        self.progress_bar.setRange(0, 0) # Indeterminate progress

        # Max depth can be made configurable later if needed
        self.thread = CrawlerWorker(url, max_depth=3) # Using max_depth=3 for now
        self.thread.url_found_signal.connect(self.append_url_to_results)
        self.thread.finished_signal.connect(self.crawl_is_finished)
        self.thread.error_signal.connect(self.handle_crawl_error)
        self.thread.start()

    def append_url_to_results(self, url_str):
        self.results_text_area.append(url_str)

    def crawl_is_finished(self, sitemap_list):
        self.results_text_area.append("\n--- Crawling Finished ---")
        self.results_text_area.append(f"Found {len(sitemap_list)} unique URLs.")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.generate_button.setEnabled(True)

    def handle_crawl_error(self, error_msg):
        self.results_text_area.append(f"\n--- CRAWLING ERROR ---")
        self.results_text_area.append(f"An error occurred: {error_msg}")
        self.results_text_area.append("Please check the URL or your network connection and try again.")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0) # Or some error indication
        self.generate_button.setEnabled(True)

class Crawler:
    def __init__(self, base_url, max_depth=5):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls = set()
        self.sitemap = set()
        self.url_callback = None # For emitting found URLs

    def crawl(self, url, current_depth):
        if url in self.visited_urls or current_depth > self.max_depth:
            return

        self.visited_urls.add(url)

        try:
            # Added timeout and User-Agent
            headers = {'User-Agent': 'SiteMapGeneratorBot/1.0'}
            response = requests.get(url, timeout=5, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_message = f"Error fetching {url}: HTTP {status_code} - {e.response.reason}."
            if status_code == 403:
                error_message += " Access forbidden. Website may block crawlers."
            elif status_code == 404:
                error_message += " Page not found."
            elif 400 <= status_code < 500:
                error_message += " Client error."
            elif 500 <= status_code < 600:
                error_message += " Server error."
            print(error_message) # Log to console
            # Optionally, emit a signal if this specific error should update the GUI directly
            return
        except requests.exceptions.Timeout:
            print(f"Error fetching {url}: Timeout after 5 seconds.")
            return
        except requests.exceptions.ConnectionError:
            print(f"Error fetching {url}: Connection error. Check network or domain name.")
            return
        except requests.RequestException as e: # Catch other request-related errors
            print(f"Error fetching {url}: {e}")
            return

        # Check if the response content is HTML
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            print(f"Skipping non-HTML content at {url} (Content-Type: {content_type})")
            return

        self.sitemap.add(url)
        if hasattr(self, 'url_callback') and self.url_callback:
            self.url_callback(url)
        # print(f"Crawled (depth {current_depth}): {url}") # For progress indication

        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Resolve relative URLs
            absolute_url = urljoin(url, href) # Use current page URL for resolving
            parsed_absolute_url = urlparse(absolute_url)

            # Basic validation and normalization
            # Ensure scheme is http or https
            if parsed_absolute_url.scheme not in ['http', 'https']:
                continue
            
            # Ensure it's within the same domain
            if parsed_absolute_url.netloc != self.domain:
                continue
            
            # Remove fragment and query parameters for visited check, but keep for sitemap
            url_to_visit = parsed_absolute_url._replace(fragment="", query="").geturl()
            
            # Add the clean URL (with query params, without fragment) to sitemap
            sitemap_url_to_add = parsed_absolute_url._replace(fragment="").geturl()


            if url_to_visit not in self.visited_urls:
                # Add to sitemap before crawling to handle cases where crawl might fail
                # but the link itself is valid and discovered.
                # However, only add if it's within domain and is HTML (checked later)
                # For now, we add to sitemap when successfully crawled.
                self.crawl(url_to_visit, current_depth + 1)
            
            # Ensure the sitemap also contains the version of the URL that was actually crawled
            # if it leads to a successful crawl later.
            # The current logic adds to sitemap at the beginning of a successful crawl.

    def get_sitemap(self):
        self.visited_urls.clear() # Ensure it's reusable
        self.sitemap.clear()      # Ensure it's reusable
        self.crawl(self.base_url, 0)
        return sorted(list(self.sitemap)) # Return a sorted list

class CrawlerWorker(QThread):
    url_found_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, start_url, max_depth=5):
        super().__init__()
        self.start_url = start_url
        self.max_depth = max_depth
        # It's generally safer to create the object that will be used in the thread
        # within the run method if it's not passed in, or ensure it's thread-safe.
        # For this case, Crawler is instantiated here but used only in run().
        self.crawler = Crawler(self.start_url, self.max_depth)

    def run(self):
        try:
            self.crawler.url_callback = self.url_found_signal.emit
            sitemap = self.crawler.get_sitemap()
            self.finished_signal.emit(sitemap)
        except Exception as e:
            # Provide a more generic message to the GUI, details are in console.
            self.error_signal.emit(f"An unexpected error occurred during the crawl. See console for details if any. Exception: {type(e).__name__}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SiteMapGeneratorApp()
    sys.exit(app.exec())
# Keep the original main execution for GUI
# No changes to the example usage block needed as it's commented out.
