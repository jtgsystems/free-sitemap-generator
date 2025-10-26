# CLAUDE.md - Free Sitemap Generator

## Project Overview

**Free Sitemap Generator** is a Python-based desktop application with a PyQt6 GUI that crawls websites and generates comprehensive sitemaps. The tool recursively discovers all pages within a specified domain, providing a clear overview of website structure for SEO, analytics, and documentation purposes.

**Repository**: https://github.com/jtgsystems/free-sitemap-generator
**License**: MIT
**Maintained By**: JTGSYSTEMS

---

## Key Features

- **PyQt6 GUI**: Modern, user-friendly graphical interface
- **Recursive Web Crawling**: Discovers all pages within the same domain
- **Real-time Progress Tracking**: Visual progress bar and live URL display
- **Robust Error Handling**: Handles network issues, invalid URLs, and HTTP errors gracefully
- **Multithreaded Architecture**: Non-blocking UI during crawl operations
- **Domain-Scoped Crawling**: Only crawls pages within the exact same domain (subdomains excluded)
- **Content-Type Filtering**: Skips non-HTML content (PDFs, images, etc.)
- **URL Normalization**: Handles fragments and query parameters intelligently
- **Configurable Depth**: Customizable maximum crawl depth (default: 3 levels from GUI, 5 programmatically)

---

## Directory Structure

```
free-sitemap-generator/
├── .github/                      # GitHub issue/PR templates
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── .gitignore                    # Python/IDE/OS ignores
├── banner.png                    # Project banner image (541KB)
├── CLAUDE.md                     # This file - project documentation
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # MIT License
├── main.py                       # Main application (GUI + Crawler)
├── README.md                     # User-facing documentation
├── requirements.txt              # Python dependencies
├── setup.py                      # PyInstaller build script
└── test_main.py                  # Comprehensive unit tests
```

---

## Technology Stack

### Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| **PyQt6** | >=6.4.0 | GUI framework (widgets, threading, signals) |
| **requests** | >=2.28.0 | HTTP requests for web crawling |
| **beautifulsoup4** | >=4.11.0 | HTML parsing and link extraction |
| **lxml** | >=4.9.0 | Fast XML/HTML parsing backend for BS4 |

### Development Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| **PyInstaller** | >=5.0 | Standalone executable builds |
| **unittest** | Built-in | Testing framework |

### Python Requirements

- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11)
- Cross-platform: Windows, macOS, Linux

---

## Architecture

### Component Design

#### 1. **SiteMapGeneratorApp** (QWidget)
- **Purpose**: Main GUI application window
- **Responsibilities**:
  - URL input validation
  - Button/progress bar management
  - Thread lifecycle management
  - Signal/slot connections for UI updates

**Key Methods**:
- `initUI()`: Builds GUI layout (input, button, progress, text area)
- `start_crawl_process()`: Validates URL, spawns CrawlerWorker thread
- `append_url_to_results(url)`: Appends discovered URLs to text area (real-time)
- `crawl_is_finished(sitemap)`: Displays completion summary
- `handle_crawl_error(error_msg)`: Shows error messages in GUI

#### 2. **Crawler** (Core Logic)
- **Purpose**: Recursive web crawling engine
- **Responsibilities**:
  - HTTP requests with timeout (5s) and User-Agent headers
  - HTML parsing and link extraction
  - Domain filtering (same netloc only)
  - URL normalization (fragments/query params)
  - Content-Type validation (HTML only)
  - Depth limiting

**Key Attributes**:
- `base_url`: Starting URL for crawl
- `domain`: Extracted netloc for same-domain checks
- `max_depth`: Maximum recursion depth (default: 5)
- `visited_urls`: Set of normalized URLs already crawled
- `sitemap`: Set of discovered URLs (includes query params, excludes fragments)
- `url_callback`: Optional callback for real-time URL reporting

**Key Methods**:
- `crawl(url, current_depth)`: Recursive crawl function
  - Fetches URL with requests
  - Parses HTML with BeautifulSoup
  - Extracts and resolves links with urljoin
  - Filters by domain, scheme (http/https), content-type
  - Normalizes URLs for visited tracking
  - Recursively crawls child pages
- `get_sitemap()`: Entry point - returns sorted list of URLs

**Error Handling**:
- HTTP errors (403, 404, 5xx): Logged to console, crawl continues
- Timeouts: 5-second timeout per request
- Connection errors: Graceful skip, logged
- Non-HTML content: Skipped after Content-Type check

#### 3. **CrawlerWorker** (QThread)
- **Purpose**: Background thread for non-blocking crawls
- **Responsibilities**:
  - Runs Crawler.get_sitemap() in separate thread
  - Emits signals for GUI updates

**Signals**:
- `url_found_signal(str)`: Emitted when each URL is discovered
- `finished_signal(list)`: Emitted with final sitemap list
- `error_signal(str)`: Emitted on unexpected exceptions

---

## Development Workflow

### Installation

```bash
# Clone repository
git clone https://github.com/jtgsystems/free-sitemap-generator.git
cd free-sitemap-generator

# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install PyQt6>=6.4.0 requests>=2.28.0 beautifulsoup4>=4.11.0 lxml>=4.9.0
```

### Running the Application

```bash
# Run from source
python main.py

# The GUI will launch with:
# - URL input field
# - "Generate Site Map" button
# - Progress bar
# - Results text area
```

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Run build script
python setup.py

# Executable created in dist/ folder
# - Windows: dist/SiteMapGenerator.exe
# - macOS/Linux: dist/SiteMapGenerator
```

**Build Configuration** (setup.py):
- `--onefile`: Single executable
- `--windowed`: No console window (GUI only)
- `--name=SiteMapGenerator`: Executable name

### Testing

```bash
# Run all unit tests
python -m unittest test_main.py

# Run specific test
python -m unittest test_main.TestCrawler.test_basic_crawl_single_page
```

**Test Coverage** (test_main.py):
- ✅ Basic crawling with multiple pages
- ✅ Same-domain filtering (excludes subdomains)
- ✅ Depth limiting (max_depth enforcement)
- ✅ URL normalization (fragments, query params)
- ✅ Content-Type filtering (HTML vs PDF/images)
- ✅ HTTP error handling (404, 403, 5xx)
- ✅ Relative/absolute URL resolution
- ✅ PyQt6 mocking for isolated testing

**Test Strategy**:
- Mocks PyQt6 modules (no GUI required for tests)
- Mocks requests.get() for controlled responses
- Tests Crawler class in isolation
- Validates visited_urls tracking, sitemap accuracy

---

## Configuration

### URL Validation

**Requirements**:
- Must include `http://` or `https://` scheme
- Must have valid domain (netloc)
- Example: `http://example.com` ✅
- Example: `example.com` ❌ (missing scheme)

### Crawl Depth

**Default Settings**:
- **GUI Mode**: `max_depth=3` (hardcoded in main.py line 62)
- **Programmatic Mode**: `max_depth=5` (Crawler class default)

**Depth Levels**:
- Depth 0: Base URL only
- Depth 1: Base URL + direct links
- Depth 2: Base URL + direct links + links from those pages
- Depth 3+: Continues recursively

**To Change GUI Depth**:
Edit `main.py` line 62:
```python
self.thread = CrawlerWorker(url, max_depth=5)  # Change 3 to desired depth
```

### Domain Filtering

**Behavior**:
- Only crawls URLs with exact same `netloc` as base URL
- `http://example.com` will crawl `http://example.com/page`
- `http://example.com` will NOT crawl `http://sub.example.com` (subdomain)
- `http://example.com` will NOT crawl `http://othersite.com` (external)

**Code Reference** (main.py lines 156-157):
```python
if parsed_absolute_url.netloc != self.domain:
    continue  # Skip external/subdomain URLs
```

### HTTP Configuration

**Request Headers**:
```python
headers = {'User-Agent': 'SiteMapGeneratorBot/1.0'}
```

**Timeout**: 5 seconds per request

**Retry Logic**: None (single attempt per URL)

---

## Performance Considerations

### Optimization Strategies

1. **Visited URL Tracking**: Set-based deduplication prevents redundant requests
2. **URL Normalization**: Removes fragments/query params before visited check
   - `http://example.com/page?param=1` → normalized to `http://example.com/page` for tracking
   - Prevents duplicate fetches of same logical page
3. **Content-Type Pre-Check**: Skips parsing non-HTML content (saves CPU)
4. **Multithreading**: GUI remains responsive during long crawls
5. **Depth Limiting**: Prevents infinite recursion on large sites

### Resource Usage

**Memory**:
- Visited URLs stored in set: ~50 bytes per URL
- Sitemap stored in set: ~50 bytes per URL
- Example: 10,000 URLs ≈ 1MB memory

**Network**:
- Sequential requests (no parallel crawling)
- 5-second timeout per request
- Rate: ~1-5 pages/second (depends on server response time)

**CPU**:
- BeautifulSoup parsing: ~10-50ms per page
- lxml backend: Faster than html.parser

### Performance Limits

**Large Websites**:
- 10,000 pages: ~30-60 minutes (at 3 pages/sec)
- 100,000 pages: 5-10 hours
- Recommendation: Use depth limiting for very large sites

**Memory Safety**:
- Sets prevent memory bloat from duplicates
- No disk caching (all in-memory)

---

## Known Issues & Troubleshooting

### Common Issues

#### 1. Invalid URL Error
**Symptoms**: "Error: Invalid URL. Please enter a full URL..."

**Causes**:
- Missing `http://` or `https://`
- Malformed domain

**Solutions**:
- Use full URL: `http://example.com` not `example.com`
- Verify domain exists and is reachable

#### 2. No Site Map Generated
**Symptoms**: Crawl completes with 0 or very few URLs

**Causes**:
- Website blocks crawlers (403 Forbidden)
- Single-page application (SPA) with JavaScript-rendered content
- No internal links on homepage

**Solutions**:
- Check console for 403 errors (if running from source)
- SPAs require JavaScript execution (not supported by this tool)
- Verify homepage has `<a href="...">` links

#### 3. Slow Crawling
**Symptoms**: Progress bar stuck for long periods

**Causes**:
- High network latency
- Server slow to respond
- Depth too high for large site

**Solutions**:
- Reduce `max_depth` in code
- Check internet connection
- Wait patiently (no timeout on overall crawl)

#### 4. Application Freezes (Unlikely)
**Symptoms**: GUI becomes unresponsive

**Causes**:
- Rare threading issue
- System resource exhaustion

**Solutions**:
- Force quit and restart
- Check system RAM/CPU usage
- Report as bug if reproducible

#### 5. Build Failures (PyInstaller)
**Symptoms**: `setup.py` errors during executable build

**Causes**:
- PyInstaller version incompatibility
- Missing dependencies
- OS-specific issues

**Solutions**:
```bash
# Update PyInstaller
pip install --upgrade pyinstaller

# Verify all deps installed
pip install -r requirements.txt

# Check setup.py output for specific errors
python setup.py
```

---

## Testing Approach

### Unit Test Philosophy

**Test Scope**:
- Isolated testing of `Crawler` class logic
- No GUI testing (PyQt6 mocked)
- Network requests mocked for deterministic results

**Mocking Strategy**:
```python
# PyQt6 modules mocked in test_main.py (lines 6-39)
sys.modules['PyQt6.QtWidgets'] = mock_qtwidgets_module
sys.modules['PyQt6.QtCore'] = mock_qtcore_module

# requests.get mocked per test
@patch('main.requests.get')
def test_basic_crawl_single_page(self, mock_get):
    mock_responses = {...}
    mock_get.side_effect = lambda url, **kwargs: mock_responses.get(url)
```

### Test Cases

1. **test_basic_crawl_single_page**: Validates recursive crawling across 4 pages
2. **test_same_domain_filter**: Ensures subdomains/external sites excluded
3. **test_depth_limit**: Verifies max_depth enforcement at depths 0, 1, 2
4. **test_url_normalization_and_visited_set**: Confirms fragments/params handled correctly
5. **test_content_type_filter**: Checks HTML-only crawling (skips PDF/images)
6. **test_http_error_handling_for_single_url**: Validates 404/403 error resilience
7. **test_url_resolution_relative_and_absolute**: Tests urljoin for relative/absolute links

**Running Tests**:
```bash
# All tests
python -m unittest test_main.py -v

# Specific test
python -m unittest test_main.TestCrawler.test_depth_limit -v
```

---

## Contributing

### Code Standards

- **Style**: PEP 8 compliant
- **Docstrings**: Required for all functions/classes
- **Type Hints**: Recommended but not enforced
- **Commit Messages**: Imperative mood, 72 chars max

### Pull Request Workflow

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Install deps: `pip install -r requirements.txt`
4. Make changes and test: `python -m unittest test_main.py`
5. Update docs (README.md, CLAUDE.md if needed)
6. Commit: `git commit -m "Add feature X"`
7. Push and open PR: Use `.github/PULL_REQUEST_TEMPLATE.md`

**See**: `CONTRIBUTING.md` for full guidelines

---

## Roadmap & Next Steps

### Potential Enhancements

#### Short-Term (Easy Wins)
- [ ] **Configurable Depth in GUI**: Add spinbox for user-defined max_depth
- [ ] **Export Sitemap**: Save results to .txt or .xml file
- [ ] **Duplicate URL Counter**: Show if duplicates were filtered
- [ ] **Pause/Resume Crawling**: Stop and restart crawl mid-process

#### Medium-Term (Moderate Effort)
- [ ] **Parallel Crawling**: Thread pool for faster multi-page crawls
- [ ] **Subdomain Support**: Option to include subdomains
- [ ] **Robots.txt Compliance**: Respect robots.txt rules
- [ ] **Sitemap.xml Export**: Generate XML sitemap format
- [ ] **Custom Headers**: User-defined User-Agent, cookies, etc.

#### Long-Term (Advanced Features)
- [ ] **JavaScript Rendering**: Selenium/Playwright for SPAs
- [ ] **Sitemap Visualization**: Graph/tree view of site structure
- [ ] **Broken Link Detection**: Flag 404s and unreachable pages
- [ ] **SEO Metrics**: Page titles, meta descriptions, word counts
- [ ] **Scheduled Crawls**: Cron-like scheduling for recurring audits

### Performance Improvements
- [ ] **Async I/O**: Use aiohttp for concurrent requests
- [ ] **Disk Caching**: SQLite for large sitemaps (reduce memory)
- [ ] **Progress Estimation**: % complete based on discovered queue size

### UI/UX Enhancements
- [ ] **Dark Mode**: Theme support
- [ ] **URL History**: Dropdown of recently crawled sites
- [ ] **Filter/Search Results**: Find URLs in sitemap text area
- [ ] **Copy to Clipboard**: One-click copy sitemap

---

## Usage Examples

### Basic Usage (GUI)

1. Launch application: `python main.py`
2. Enter URL: `http://example.com`
3. Click "Generate Site Map"
4. Wait for progress bar to complete
5. Review sitemap in text area

### Programmatic Usage

```python
from main import Crawler

# Create crawler instance
crawler = Crawler("http://example.com", max_depth=5)

# Generate sitemap
sitemap = crawler.get_sitemap()

# Print results
for url in sitemap:
    print(url)

# Access visited URLs
print(f"Visited {len(crawler.visited_urls)} unique pages")
```

### Custom Callback Example

```python
from main import Crawler

def log_url(url):
    print(f"Discovered: {url}")

crawler = Crawler("http://example.com", max_depth=3)
crawler.url_callback = log_url
sitemap = crawler.get_sitemap()
```

---

## Maintenance Notes

### Dependencies Update Strategy

**Regular Updates** (quarterly):
```bash
pip install --upgrade PyQt6 requests beautifulsoup4 lxml
pip freeze > requirements.txt
```

**Test After Updates**:
- Run full test suite: `python -m unittest test_main.py`
- Manual GUI test: Launch app, crawl known site
- Build test: `python setup.py` and run executable

### Backward Compatibility

- Maintain Python 3.8+ support
- Avoid breaking changes to Crawler API
- Deprecate features with warnings before removal

### Issue Triage

**Bug Priority**:
1. Crashes/data loss (P0 - fix immediately)
2. Crawl failures (P1 - fix in days)
3. UI glitches (P2 - fix in weeks)
4. Enhancement requests (P3 - backlog)

**Use Labels**:
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `question`: Further information requested
- `good first issue`: Good for newcomers

---

## Security Considerations

### Crawler Safety

**User-Agent Identification**:
- Clearly identifies as bot: `SiteMapGeneratorBot/1.0`
- Websites can block in robots.txt if desired

**Rate Limiting**:
- Sequential requests (no flooding)
- 5-second timeout prevents hanging on slow servers
- No aggressive retry logic

**Content Validation**:
- Only parses HTML (skips executables, scripts)
- No code execution from crawled content
- BeautifulSoup escapes malicious HTML

### Privacy

**Data Handling**:
- No telemetry or analytics
- All crawling local (no data sent to external servers)
- Sitemap stored in memory only (not persisted unless exported)

**Credentials**:
- No authentication support (public pages only)
- No cookie handling
- No session management

---

## License

This project is licensed under the **MIT License**.

**Permissions**:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Limitations**:
- ❌ Liability
- ❌ Warranty

**Conditions**:
- Must include license and copyright notice

See `LICENSE` file for full text.

---

## Resources

### Documentation
- **README.md**: User-facing getting started guide
- **CONTRIBUTING.md**: Developer contribution guidelines
- **CLAUDE.md**: This file - comprehensive technical reference

### External Links
- **PyQt6 Docs**: https://doc.qt.io/qtforpython-6/
- **Requests Docs**: https://docs.python-requests.org/
- **BeautifulSoup Docs**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **PyInstaller Docs**: https://pyinstaller.org/

### Issue Tracker
- **GitHub Issues**: https://github.com/jtgsystems/free-sitemap-generator/issues

### Community
- **Pull Requests**: https://github.com/jtgsystems/free-sitemap-generator/pulls
- **Discussions**: Use GitHub Discussions (if enabled)

---

## FAQ

### Q: Can this crawl JavaScript-heavy sites (SPAs)?
**A**: No. This tool uses `requests` which fetches raw HTML. JavaScript-rendered content (React, Vue, Angular apps) won't be crawled. For SPAs, use Selenium or Playwright-based tools.

### Q: Does this respect robots.txt?
**A**: No. Currently, robots.txt is not parsed. This is a planned enhancement. Use responsibly on sites you own or have permission to crawl.

### Q: Can I crawl password-protected pages?
**A**: No. There's no authentication mechanism. Only public pages are accessible.

### Q: How do I crawl subdomains?
**A**: Not currently supported. The crawler filters by exact `netloc` match. Subdomain support is in the roadmap.

### Q: Why is the crawl so slow?
**A**: Requests are sequential with 5-second timeouts. For very large sites, reduce `max_depth` or wait patiently. Parallel crawling is a planned optimization.

### Q: Can I export the sitemap?
**A**: Not yet. Currently, results are displayed in the GUI text area. Copy-paste to save. Export features are planned.

### Q: What's the maximum site size this can handle?
**A**: Depends on available RAM. Each URL uses ~50 bytes. 10,000 URLs ≈ 1MB. Tested up to 10,000 pages. For larger sites, use depth limiting.

---

**Last Updated**: 2025-10-26
**Maintained By**: JTGSYSTEMS
**Contact**: https://github.com/jtgsystems/free-sitemap-generator/issues

## Framework Versions


