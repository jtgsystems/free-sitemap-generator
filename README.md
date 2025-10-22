![Banner](banner.png)

# 🗺️ Site Map Generator

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-orange.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)
![GitHub Issues](https://img.shields.io/github/issues/jtgsystems/free-sitemap-generator)
![GitHub Stars](https://img.shields.io/github/stars/jtgsystems/free-sitemap-generator)
![GitHub Forks](https://img.shields.io/github/forks/jtgsystems/free-sitemap-generator)

## 📋 Overview
The Site Map Generator is a Python-based application with a graphical user interface (GUI) that allows users to generate a site map for a given website. It crawls through all pages within the specified domain and creates a comprehensive list of URLs, providing a clear overview of the website's structure.

## ✨ Features
- 🖥️ User-friendly PyQt6-based GUI
- 🔄 Recursive crawling of websites within the same domain
- 📊 Progress bar to show crawling status
- ⚠️ Error handling for invalid URLs and network issues
- 🧵 Multithreaded design for responsive UI during crawling
- 📝 Results displayed in an easy-to-read format

## 📦 Requirements

**To run from source:**
- Python 3.8 or higher
- PyQt6 >= 6.4.0
- Requests >= 2.28.0
- BeautifulSoup4 >= 4.11.0
- lxml >= 4.9.0

**To build from source:**
- All of the above, plus:
- PyInstaller >= 5.0

## 🚀 Installation

1. Ensure you have Python 3.8 or higher installed on your system.
2. Install the required packages for running from source:
   ```bash
   pip install -r requirements.txt
   ```
   Or install packages individually:
   ```bash
   pip install PyQt6>=6.4.0 requests>=2.28.0 beautifulsoup4>=4.11.0 lxml>=4.9.0
   ```
3. To run the application, you can either run it directly from source (see Usage) or build an executable (see Building from Source).

## 💻 Usage

1. **To run from source:**
   Navigate to the project directory in your terminal and execute:
   ```bash
   python main.py
   ```
2. **Alternatively, after building the executable (see 'Building from Source' below):**
   Run the `SiteMapGenerator` executable (e.g., `SiteMapGenerator.exe` on Windows, `SiteMapGenerator` on macOS/Linux) from the `dist` folder.
3. Enter the full URL of the website (e.g., `http://example.com`) you want to generate a site map for in the input field.
4. Click the "Generate Site Map" button.
5. Wait for the crawling process to complete. You can monitor the progress in the progress bar and the text area below.
6. Once completed, the site map will be displayed in the text area.

## 🏗️ Building from Source

If you wish to build the executable from the source code:

1. Ensure you have Python 3.8+ and the required packages installed (see Installation section above).
2. Clone this repository or download and extract the source files.
3. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
4. Navigate to the root directory of the project in your terminal.
5. Run the setup script:
   ```bash
   python setup.py
   ```
6. The executable (e.g., `SiteMapGenerator.exe` on Windows) will be created in a `dist` subfolder.

## ⚠️ Limitations

- The crawler is currently set to a default maximum depth of 3 levels internally when run from the GUI (this is configurable in the `CrawlerWorker` instantiation in `main.py`). The `Crawler` class itself defaults to 5 if used programmatically.
- Only pages within the exact same domain (netloc) as the initial URL are crawled. Subdomains are treated as external.
- The application may take a while to complete for very large websites.
- Error messages for specific page fetch failures are printed to the console (if running from source) or logged by PyInstaller (if running as an executable and an issue occurs), while the GUI shows a general error if the crawl cannot proceed.

## 🐛 Troubleshooting

- **Invalid URL:** Ensure you are entering a full and valid URL, including `http://` or `https://`.
- **No Site Map Generated / Errors:**
    - Check your internet connection.
    - The website might be blocking automated crawlers (check for 403 errors in console if running from source).
    - The website might not have any crawlable internal links or might be a single-page application not easily navigable by this type of crawler.
- **Application Freezes (Unlikely):** The application uses multithreading to keep the GUI responsive. If it appears to freeze, check for system resource issues or very high network latency.
- **Building Executable Fails:**
    - Ensure PyInstaller is installed correctly and is the latest version (`pip install --upgrade pyinstaller`).
    - Verify all dependencies are installed: `pip install -r requirements.txt`
    - Consult the output from `setup.py` for specific error messages from PyInstaller.

## 🤝 Contributing

Contributions to improve the Site Map Generator are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

Before contributing, please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

### SEO Keyword Cloud

`sitemap` `generator` `crawler` `python` `pyqt6` `gui` `web` `seo` `indexing` `discovery` `urls` `links` `analytics` `architecture` `structure` `navigation` `automation` `crawling` `spider` `performance` `lxml` `requests` `beautifulsoup` `multithreading` `progress` `reporting` `visualization` `export` `xml` `website` `audit` `diagnostics` `optimization` `accessibility` `compliance` `marketing` `content` `developers` `agencies` `freelancers` `startup` `enterprise` `batch` `queue` `resilience` `reliability` `uptime` `monitoring` `insights` `roadmap`
