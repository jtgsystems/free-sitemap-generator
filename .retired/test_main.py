"""Unit tests for the Free Sitemap Generator crawler functionality.

Tests the Crawler class in isolation with mocked PyQt6 and HTTP requests.
"""

import sys
import unittest
from unittest.mock import patch, Mock

# --- Start of PyQt6 Mocks ---
# Mock the PyQt6 modules before importing 'main' to prevent ModuleNotFoundError
# This is for testing the Crawler class in isolation from the GUI.
mock_qapplication = Mock()
mock_qwidget = Mock()
mock_qvboxlayout = Mock()
mock_qhboxlayout = Mock()
mock_qlabel = Mock()
mock_qlineedit = Mock()
mock_qpushbutton = Mock()
mock_qprogressbar = Mock()
mock_qtextedit = Mock()
mock_qthread = Mock()
mock_pyqtsignal = Mock() # This is actually a class/factory for signals

# Create a mock for the entire PyQt6.QtWidgets module
mock_qtwidgets_module = Mock()
mock_qtwidgets_module.QApplication = mock_qapplication
mock_qtwidgets_module.QWidget = mock_qwidget
mock_qtwidgets_module.QVBoxLayout = mock_qvboxlayout
mock_qtwidgets_module.QHBoxLayout = mock_qhboxlayout
mock_qtwidgets_module.QLabel = mock_qlabel
mock_qtwidgets_module.QLineEdit = mock_qlineedit
mock_qtwidgets_module.QPushButton = mock_qpushbutton
mock_qtwidgets_module.QProgressBar = mock_qprogressbar
mock_qtwidgets_module.QTextEdit = mock_qtextedit

# Create a mock for the entire PyQt6.QtCore module
mock_qtcore_module = Mock()
mock_qtcore_module.QThread = mock_qthread
mock_qtcore_module.pyqtSignal = mock_pyqtsignal

# Add these mocks to sys.modules
sys.modules['PyQt6.QtWidgets'] = mock_qtwidgets_module
sys.modules['PyQt6.QtCore'] = mock_qtcore_module
# --- End of PyQt6 Mocks ---

from main import Crawler # Now this import should work without PyQt6 installed
import requests # For requests.exceptions.HTTPError
from urllib.parse import urlparse # Added for domain checking in tests

class TestCrawler(unittest.TestCase):

    def _create_mock_response(self, text, status_code=200, content_type='text/html', url=""):
        mock_resp = Mock()
        mock_resp.text = text
        mock_resp.status_code = status_code
        mock_resp.headers = {'Content-Type': content_type}
        mock_resp.url = url # Useful for debugging the mock

        def raise_for_status():
            if status_code >= 400:
                http_error = requests.exceptions.HTTPError(f"Mock HTTP Error {status_code} for url {url}")
                http_error.response = mock_resp # Attach the response to the error object
                raise http_error
        
        mock_resp.raise_for_status = Mock(side_effect=raise_for_status)
        return mock_resp

    @patch('main.requests.get')
    def test_basic_crawl_single_page(self, mock_get):
        # Define what mock_get should return for specific URLs
        mock_responses = {
            "http://example.com": self._create_mock_response('<html><a href="/page1">Page 1</a><a href="page2">Page 2</a></html>', url="http://example.com"),
            "http://example.com/page1": self._create_mock_response('<html><a href="http://example.com/page3">Page 3</a></html>', url="http://example.com/page1"),
            "http://example.com/page2": self._create_mock_response('<html>No more links here.</html>', url="http://example.com/page2"),
            "http://example.com/page3": self._create_mock_response('<html>Final page.</html>', url="http://example.com/page3")
        }
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses.get(url, self._create_mock_response("Not Found by Mock", 404, url=url))

        crawler = Crawler("http://example.com", max_depth=2, crawl_delay=0)
        sitemap = crawler.get_sitemap()
        
        expected_urls = {
            "http://example.com", 
            "http://example.com/page1", 
            "http://example.com/page2",
            "http://example.com/page3" # page3 is at depth 2 (base=0, page1=1, page3=2)
        }
        self.assertEqual(set(sitemap), expected_urls)
        # Check calls if necessary, e.g. mock_get.call_count

    @patch('main.requests.get')
    def test_same_domain_filter(self, mock_get):
        mock_responses = {
            "http://example.com": self._create_mock_response(
                '<html><a href="/page1">Internal</a><a href="http://othersite.com/pageO">External</a><a href="//sub.example.com/pageS">Subdomain Same Scheme</a><a href="http://sub.example.com/pageS2">Subdomain HTTP</a></html>', 
                url="http://example.com"),
            "http://example.com/page1": self._create_mock_response('<html>Internal Page 1</html>', url="http://example.com/page1"),
            # sub.example.com is treated as external by current crawler logic (netloc must match exactly)
            "http://sub.example.com/pageS": self._create_mock_response('<html>Subdomain Page S (should not be crawled if netloc must match exactly)</html>', url="http://sub.example.com/pageS"),
            "http://sub.example.com/pageS2": self._create_mock_response('<html>Subdomain Page S2 (should not be crawled)</html>', url="http://sub.example.com/pageS2"),
            "http://othersite.com/pageO": self._create_mock_response('<html>External Page O (should not be crawled)</html>', url="http://othersite.com/pageO")
        }
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses.get(url, self._create_mock_response("Not Found by Mock", 404, url=url))

        crawler = Crawler("http://example.com", max_depth=1, crawl_delay=0)
        sitemap = crawler.get_sitemap()

        expected_urls = {"http://example.com", "http://example.com/page1"}
        self.assertEqual(set(sitemap), expected_urls)
        
        # Verify that external/subdomain URLs were not attempted to be fetched by our main crawler logic
        # (though mock_get might have been called if the test structure is complex,
        # the key is they are not in the sitemap and not *crawled* further)
        
        # Check that any URL for which requests.get was called is within the same domain.
        # The crawler's internal logic should prevent it from trying to fetch external domains.
        for call_args_tuple in mock_get.call_args_list:
            actual_url_fetched = call_args_tuple[0][0] # url is the first positional argument
            # Ensure urlparse is imported: from urllib.parse import urlparse
            self.assertEqual(urlparse(actual_url_fetched).netloc, crawler.domain,
                             f"Crawler attempted to fetch a URL from an external domain: {actual_url_fetched}")


    @patch('main.requests.get')
    def test_depth_limit(self, mock_get):
        mock_responses = {
            "http://example.com": self._create_mock_response('<html><a href="/depth1">Depth 1</a></html>', url="http://example.com"),
            "http://example.com/depth1": self._create_mock_response('<html><a href="/depth2">Depth 2</a></html>', url="http://example.com/depth1"),
            "http://example.com/depth2": self._create_mock_response('<html><a href="/depth3">Depth 3</a></html>', url="http://example.com/depth2"),
            "http://example.com/depth3": self._create_mock_response('<html>Depth 3 Content</html>', url="http://example.com/depth3")
        }
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses.get(url, self._create_mock_response("Not Found by Mock", 404, url=url))

        # Max depth 0: only base_url
        crawler0 = Crawler("http://example.com", max_depth=0, crawl_delay=0)
        sitemap0 = crawler0.get_sitemap()
        self.assertEqual(set(sitemap0), {"http://example.com"})

        # Max depth 1: base_url and its direct links
        crawler1 = Crawler("http://example.com", max_depth=1, crawl_delay=0)
        sitemap1 = crawler1.get_sitemap()
        self.assertEqual(set(sitemap1), {"http://example.com", "http://example.com/depth1"})

        # Max depth 2: base_url, its links, and links from those pages
        crawler2 = Crawler("http://example.com", max_depth=2, crawl_delay=0)
        sitemap2 = crawler2.get_sitemap()
        self.assertEqual(set(sitemap2), {"http://example.com", "http://example.com/depth1", "http://example.com/depth2"})
        
        # Check that depth3 was not called for max_depth=2
        # Reset mock for this specific check if it's sensitive to prior calls in the same test method
        # (Not strictly necessary here as crawler2 creates new instance of Crawler and calls mock_get freshly)
        
        # Get all URLs called during crawler2's execution.
        # This is tricky if mock_get is shared across crawler0, crawler1, crawler2.
        # Let's re-run for crawler2 with a fresh mock or analyze calls more carefully.

        # For simplicity, let's assume mock_get calls are distinct per crawler run or analyze based on expected calls.
        # The mock_get is reset for each test method, but not between instantiations of Crawler within a method.
        # However, crawler.get_sitemap() re-initializes visited_urls.
        
        # Test that "http://example.com/depth3" was not part of the URLs *attempted to be fetched*
        # when max_depth was 2. The sitemap check already confirms it's not *in the sitemap*.
        # This ensures we didn't even try to request it.
        
        # Re-running crawler2.get_sitemap() to isolate its calls (if needed, but current structure is likely okay
        # because the mock_get is defined once for the whole test method).
        # Let's verify that depth3 was not requested by mock_get.
        
        # Get all unique URLs passed to mock_get during the entire test_depth_limit by crawler2
        # We need to isolate calls made by crawler2.
        # One way: reset mock before crawler2 runs and then collect calls.
        mock_get.reset_mock() # Reset calls from crawler0 and crawler1

        # Re-run for crawler2 to get its specific calls
        crawler2_rerun = Crawler("http://example.com", max_depth=2, crawl_delay=0)
        # The mock_responses and side_effect are already set for the whole test method.
        sitemap2_rerun = crawler2_rerun.get_sitemap() 
        self.assertEqual(set(sitemap2_rerun), {"http://example.com", "http://example.com/depth1", "http://example.com/depth2"})


        urls_called_by_crawler2 = {args[0][0] for args in mock_get.call_args_list}
        
        self.assertIn("http://example.com/depth2", urls_called_by_crawler2) 
        self.assertNotIn("http://example.com/depth3", urls_called_by_crawler2, 
                         "Crawler with max_depth=2 should not have attempted to fetch URLs at depth 3.")


    @patch('main.requests.get')
    def test_url_normalization_and_visited_set(self, mock_get):
        mock_responses = {
            "http://example.com/page": self._create_mock_response(
                '<html><a href="page#section1">Link to Section</a> <a href="page?param=1">Link to Param</a> <a href="/other">Other</a></html>', 
                url="http://example.com/page"),
            "http://example.com/page#section1": self._create_mock_response("Should not be called directly if normalized", url="http://example.com/page#section1"), # Normalized away
            "http://example.com/page?param=1": self._create_mock_response("Should not be called directly if normalized", url="http://example.com/page?param=1"), # Normalized away
            "http://example.com/other": self._create_mock_response('<html>Other page content</html>', url="http://example.com/other")
        }
        # The crawler normalizes before adding to visited and before crawling,
        # so 'page#section' and 'page?param=1' become 'page'.
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses.get(url, self._create_mock_response("Not Found by Mock for " + url, 404, url=url))
        
        crawler = Crawler("http://example.com/page", max_depth=1, crawl_delay=0)
        sitemap = crawler.get_sitemap()

        # The sitemap should contain the URL as it was found (before normalization for sitemap addition)
        # but the visited check should use normalized URLs.
        # Current crawler adds URL to sitemap *after* successful crawl.
        # And normalization `url_to_visit = parsed_absolute_url._replace(fragment="", query="").geturl()` is for `visited_urls` check
        # The actual URL crawled is `absolute_url` (which can have query params).
        # The sitemap should store the version of the URL that was actually crawled.
        # Let's refine mock_responses and expectations.

        mock_responses_refined = {
            "http://example.com/page": self._create_mock_response(
                '<html><a href="page#section1">Link to Section</a> <a href="page?param=val">Link to Param</a> <a href="/otherpage">Other</a></html>', 
                url="http://example.com/page"),
            "http://example.com/page?param=val": self._create_mock_response( # This will be crawled if different from base 'page'
                '<html>Param page. <a href="http://example.com/page">Back to page</a></html>', 
                url="http://example.com/page?param=val"),
            "http://example.com/otherpage": self._create_mock_response('<html>Other page content</html>', url="http://example.com/otherpage")
        }
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses_refined.get(url, self._create_mock_response("Not Found: " + url, 404, url=url))

        crawler_norm = Crawler("http://example.com/page", max_depth=1, crawl_delay=0)
        sitemap_norm = crawler_norm.get_sitemap()
        
        # URLs added to sitemap are the ones successfully crawled.
        # Normalization for visited: http://example.com/page (from page, page#section1, page?param=val)
        # If page?param=val is encountered, it's normalized to 'page' for visited check.
        # If 'page' is already visited (e.g. base_url), then page?param=val won't be crawled.
        # The current code:
        #   absolute_url = urljoin(url, href) -> this has params/fragments
        #   url_to_visit = parsed_absolute_url._replace(fragment="", query="").geturl() -> for visited_urls check
        #   self.crawl(url_to_visit, ...) -> THIS IS THE PROBLEM. It should crawl `absolute_url` but check `url_to_visit` in visited.
        # Let's assume the current crawler implementation is what we test.
        # If base is "http://example.com/page", then:
        # 1. Crawl "http://example.com/page". Add to visited. Add to sitemap.
        # 2. Find "page#section1". abs="http://example.com/page#section1". url_to_visit="http://example.com/page". Already visited. Skip.
        # 3. Find "page?param=val". abs="http://example.com/page?param=val". url_to_visit="http://example.com/page". Already visited. Skip.
        # 4. Find "/otherpage". abs="http://example.com/otherpage". url_to_visit="http://example.com/otherpage". Not visited. Crawl. Add to sitemap.
        
        expected_urls_norm = {"http://example.com/page", "http://example.com/otherpage"}
        self.assertEqual(set(sitemap_norm), expected_urls_norm)
        
        # Check that mock_get for "http://example.com/page?param=val" was NOT called
        # because its normalized form "http://example.com/page" was already visited (as the base URL).
        
        # Get all unique URLs passed to mock_get by crawler_norm
        # Similar to test_depth_limit, reset mock if checking specific calls for crawler_norm
        mock_get.reset_mock()
        crawler_norm_rerun = Crawler("http://example.com/page", max_depth=1, crawl_delay=0)
        # mock_get.side_effect is already set to mock_responses_refined
        sitemap_norm_rerun = crawler_norm_rerun.get_sitemap()
        self.assertEqual(set(sitemap_norm_rerun), expected_urls_norm) # Verify sitemap is still correct

        all_urls_requested_by_crawler_norm = {args[0][0] for args in mock_get.call_args_list}
        
        self.assertIn("http://example.com/page", all_urls_requested_by_crawler_norm)
        self.assertIn("http://example.com/otherpage", all_urls_requested_by_crawler_norm)
        
        # Key check: The normalized forms (which for "page?param=val" and "page#section1" is "page")
        # should not lead to new fetches of "page?param=val" or "page#section1" if "page" was already fetched.
        # The current crawler calls `self.crawl(url_to_visit, ...)` where url_to_visit is normalized.
        # So, if base_url is "http://example.com/page", it's fetched.
        # Then links like "page?param=val" are normalized to "http://example.com/page", which is already visited.
        # Thus, "http://example.com/page?param=val" itself should not be passed to requests.get().
        self.assertNotIn("http://example.com/page?param=val", all_urls_requested_by_crawler_norm,
                         "URL with query param (e.g. http://example.com/page?param=val) should not be fetched if its normalized form was already visited.")
        # "http://example.com/page#section1" would be resolved by urljoin to "http://example.com/page" 
        # (if current page is http://example.com/page), and then normalized again to "http://example.com/page".
        # So it should not appear as a separate call.
        self.assertNotIn("http://example.com/page#section1", all_urls_requested_by_crawler_norm,
                         "URL with fragment (e.g. http://example.com/page#section1) should not be fetched as a distinct URL if its base was visited.")


    @patch('main.requests.get')
    def test_content_type_filter(self, mock_get):
        mock_responses = {
            "http://example.com": self._create_mock_response(
                '<html><a href="/page.html">HTML Page</a><a href="/document.pdf">PDF Document</a><a href="/image.png">PNG Image</a></html>',
                url="http://example.com"),
            "http://example.com/page.html": self._create_mock_response('<html>HTML content</html>', url="http://example.com/page.html"),
            "http://example.com/document.pdf": self._create_mock_response('PDF binary data', content_type='application/pdf', url="http://example.com/document.pdf"),
            "http://example.com/image.png": self._create_mock_response('PNG binary data', content_type='image/png', url="http://example.com/image.png")
        }
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses.get(url, self._create_mock_response("Not Found by Mock", 404, url=url))

        crawler = Crawler("http://example.com", max_depth=1, crawl_delay=0)
        sitemap = crawler.get_sitemap()

        expected_urls = {"http://example.com", "http://example.com/page.html"}
        self.assertEqual(set(sitemap), expected_urls)
        
        # Verify that requests.get was called for PDF/image (to check content type) but they are not in sitemap
        pdf_url_requested = any(call_args[0][0] == "http://example.com/document.pdf" for call_args in mock_get.call_args_list)
        png_url_requested = any(call_args[0][0] == "http://example.com/image.png" for call_args in mock_get.call_args_list)
        self.assertTrue(pdf_url_requested, "Request for PDF URL was not made to check its content type")
        self.assertTrue(png_url_requested, "Request for PNG URL was not made to check its content type")


    @patch('main.requests.get')
    @patch('main.logger') # Patch logger instead of print
    def test_http_error_handling_for_single_url(self, mock_logger, mock_get):
        mock_responses = {
            "http://example.com": self._create_mock_response('<html><a href="/goodpage">Good Page</a><a href="/brokenpage">Broken Page</a><a href="/anothergood">Another Good</a></html>', url="http://example.com"),
            "http://example.com/goodpage": self._create_mock_response('<html>Good content</html>', url="http://example.com/goodpage"),
            "http://example.com/brokenpage": self._create_mock_response('Error', status_code=404, url="http://example.com/brokenpage"),
            "http://example.com/anothergood": self._create_mock_response('<html>More good content</html>', url="http://example.com/anothergood")
        }
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses.get(url, self._create_mock_response("Default Mock 404", 404, url=url))

        crawler = Crawler("http://example.com", max_depth=1, crawl_delay=0)
        sitemap = crawler.get_sitemap()

        expected_urls = {"http://example.com", "http://example.com/goodpage", "http://example.com/anothergood"}
        self.assertEqual(set(sitemap), expected_urls)

        # Verify error was logged (mock_logger.warning was called) for the broken page
        error_logged = False
        for call in mock_logger.warning.call_args_list:
            args, _ = call
            if args and "404" in str(args[0]) and "brokenpage" in str(args[0]):
                error_logged = True
                break
        self.assertTrue(error_logged, "Error message for 404 page was not logged.")


    @patch('main.requests.get')
    def test_url_resolution_relative_and_absolute(self, mock_get):
        # Base URL: http://example.com/folder1/
        base_url = "http://example.com/folder1/"
        page_content = """
        <html>
            <a href="page1.html">Relative to current folder</a>
            <a href="/page2.html">Relative to root</a>
            <a href="../page3.html">Relative to parent folder</a>
            <a href="http://example.com/page4.html">Absolute on same domain</a>
            <a href="https://othersite.com/page5.html">Absolute on other domain</a>
        </html>
        """
        mock_responses = {
            base_url: self._create_mock_response(page_content, url=base_url),
            "http://example.com/folder1/page1.html": self._create_mock_response("Page 1", url="http://example.com/folder1/page1.html"),
            "http://example.com/page2.html": self._create_mock_response("Page 2", url="http://example.com/page2.html"),
            "http://example.com/page3.html": self._create_mock_response("Page 3", url="http://example.com/page3.html"), # ../ from /folder1/ goes to /
            "http://example.com/page4.html": self._create_mock_response("Page 4", url="http://example.com/page4.html"),
            "https://othersite.com/page5.html": self._create_mock_response("Page 5 (External)", url="https://othersite.com/page5.html"),
        }
        mock_get.side_effect = lambda url, timeout=None, headers=None: mock_responses.get(url, self._create_mock_response("Not Found by Mock: " + url, 404, url=url))

        crawler = Crawler(base_url, max_depth=1, crawl_delay=0)
        sitemap = crawler.get_sitemap()

        expected_urls = {
            base_url,
            "http://example.com/folder1/page1.html",
            "http://example.com/page2.html",
            "http://example.com/page3.html",
            "http://example.com/page4.html",
        }
        self.assertEqual(set(sitemap), expected_urls)

if __name__ == '__main__':
    unittest.main()
