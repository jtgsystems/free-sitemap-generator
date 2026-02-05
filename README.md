![Banner](banner.png)

# 🗺️ Free Sitemap Generator - SOTA 2026 Edition

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-orange.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)
![GitHub Issues](https://img.shields.io/github/issues/jtgsystems/free-sitemap-generator)
![GitHub Stars](https://img.shields.io/github/stars/jtgsystems/free-sitemap-generator)

> 🚀 **The most advanced free sitemap generator** - Now with async crawling, XML export, and professional SEO features!

---

## ✨ What's New in SOTA 2026 Edition

### 🏎️ Performance
- **Async Concurrent Crawling** - Crawl up to 50 pages simultaneously
- **Connection Pooling** - Reuse connections for faster crawling
- **Smart Rate Limiting** - Respects server resources while maximizing speed

### 📄 Export Formats
- **XML Sitemap** - Full sitemaps.org compliance
- **XML Sitemap Index** - For large sites (50,000+ URLs)
- **GZip Compression** - Reduce file sizes by 80%+
- **Text, CSV, JSON** - Multiple export options

### 🎯 SEO Features
- **Automatic Priority Calculation** - Based on page depth and importance
- **Change Frequency Detection** - Smart changefreq assignment
- **Last Modified Extraction** - From HTTP headers
- **Image Sitemap Support** - Include page images
- **Robots.txt Compliance** - Optional respect for crawl rules

---

## 📋 Overview

The **Free Sitemap Generator** is a professional-grade desktop application for creating XML sitemaps. It crawls your website, discovers all pages, and generates standards-compliant sitemaps for search engine submission.

### Perfect For:
- 🌐 **Website Owners** - Improve SEO and search indexing
- 🏢 **SEO Professionals** - Client site audits and optimization
- 👨‍💻 **Developers** - Automated sitemap generation
- 🎨 **Agencies** - Batch site processing

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jtgsystems/free-sitemap-generator.git
cd free-sitemap-generator

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Usage

1. **Enter your website URL** (e.g., `https://example.com`)
2. **Configure crawl settings** (optional)
3. **Click "Start Crawl"**
4. **Export your sitemap** in your preferred format

---

## 📦 Features

### 🔍 Crawling
| Feature | Description |
|---------|-------------|
| **Async Concurrent** | Crawl up to 50 pages simultaneously |
| **Depth Control** | Limit crawl depth (1-10 levels) |
| **URL Limits** | Configurable max URLs (100-50,000) |
| **Smart Filtering** | Excludes non-HTML, external links |
| **Robots.txt** | Optional compliance with crawl rules |
| **Rate Limiting** | Configurable delay between requests |

### 📤 Export Options
| Format | Description | Best For |
|--------|-------------|----------|
| **XML Sitemap** | Standard sitemaps.org format | Google, Bing submission |
| **XML + GZip** | Compressed XML | Large sites, bandwidth saving |
| **Sitemap Index** | Multiple sitemap files | 50,000+ URLs |
| **Text** | One URL per line | Quick reviews |
| **CSV** | Spreadsheet format | Analysis in Excel |
| **JSON** | Structured data | API integration |

### 🎛️ Configuration
- **Max Depth** - How many link levels to follow
- **Max URLs** - Limit total discovered URLs
- **Concurrency** - Number of simultaneous requests
- **Crawl Delay** - Seconds between requests
- **Respect robots.txt** - Follow crawl rules
- **Include Images** - Add image sitemap entries

---

## 📊 Sitemap Features

### Automatic SEO Optimization
```xml
<url>
  <loc>https://example.com/</loc>
  <lastmod>2026-02-05T10:30:00+00:00</lastmod>
  <changefreq>daily</changefreq>
  <priority>1.0</priority>
</url>
```

- **Priority Calculation** - Homepage gets 1.0, deeper pages get lower priority
- **Change Frequency** - Detected from URL patterns (blog=weekly, about=monthly)
- **Last Modified** - Extracted from HTTP Last-Modified headers

### Image Sitemaps
```xml
<url>
  <loc>https://example.com/gallery</loc>
  <image:image>
    <image:loc>https://example.com/photo1.jpg</image:loc>
  </image:image>
</url>
```

---

## 🏗️ Building from Source

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build
python setup.py

# Find executable in dist/ folder
```

---

## 📁 Project Structure

```
free-sitemap-generator/
├── sitemap_generator/      # Main package
│   ├── __init__.py
│   ├── crawler.py          # Async web crawler
│   ├── exporter.py         # XML/export formats
│   └── gui.py              # PyQt6 interface
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── setup.py               # Build script
├── README.md              # This file
├── LICENSE                # MIT License
└── .github/               # GitHub templates
```

---

## ⚙️ Technical Specifications

### Sitemap Compliance
- ✅ sitemaps.org protocol
- ✅ Google Search Console compatible
- ✅ Bing Webmaster Tools compatible
- ✅ 50,000 URL limit per file
- ✅ 50MB file size limit
- ✅ UTF-8 encoding
- ✅ Proper XML escaping

### Performance
- **Crawling**: Up to 500 pages/minute (depending on site)
- **Memory**: Efficient streaming for large sites
- **CPU**: Multi-threaded processing
- **Network**: Connection pooling, keep-alive

---

## 🐛 Troubleshooting

### Common Issues

**"Timeout fetching URL"**
- Check your internet connection
- Increase timeout in settings
- Website may be blocking crawlers

**"No URLs found"**
- Ensure URL includes http:// or https://
- Check that website has crawlable links
- Verify robots.txt allows crawling

**"Application freezes"**
- Reduce concurrency setting
- Increase crawl delay
- Check system resources

### Error Codes
| Code | Meaning | Solution |
|------|---------|----------|
| 403 | Access Forbidden | Check robots.txt, add User-Agent |
| 404 | Page Not Found | Check URL spelling |
| 500 | Server Error | Try again later |
| Timeout | Request Timeout | Increase timeout setting |

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Clone repo
git clone https://github.com/jtgsystems/free-sitemap-generator.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black sitemap_generator/
```

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI
- Async crawling powered by [aiohttp](https://docs.aiohttp.org/)
- HTML parsing by [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

---

## 🔗 Links

- 🌐 **Website**: https://jtgsystems.com
- 💻 **GitHub**: https://github.com/jtgsystems/free-sitemap-generator
- 🐛 **Issues**: https://github.com/jtgsystems/free-sitemap-generator/issues
- 📖 **Wiki**: https://github.com/jtgsystems/free-sitemap-generator/wiki

---

Made with ❤️ by [JTGSYSTEMS](https://jtgsystems.com)

### SEO Keyword Cloud
`sitemap` `generator` `crawler` `python` `pyqt6` `gui` `web` `seo` `indexing` `discovery` `urls` `links` `analytics` `architecture` `structure` `navigation` `automation` `crawling` `spider` `performance` `lxml` `requests` `beautifulsoup` `multithreading` `progress` `reporting` `visualization` `export` `xml` `website` `audit` `diagnostics` `optimization` `accessibility` `compliance` `marketing` `content` `developers` `agencies` `freelancers` `startup` `enterprise` `batch` `queue` `resilience` `reliability` `uptime` `monitoring` `insights` `roadmap` `async` `concurrent` `gzip` `sitemap-index` `image-sitemap` `google` `bing` `search-console`
