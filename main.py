"""
Free Sitemap Generator - SOTA 2026 Edition
==========================================

A professional-grade sitemap generator with:
- Async concurrent crawling
- XML sitemap export (sitemaps.org compliant)
- Priority and changefreq calculation
- Image sitemap support
- GZip compression
- Modern PyQt6 GUI

Usage:
    python main.py              # Launch GUI
    python -m sitemap_generator # Alternative launch

For more information: https://github.com/jtgsystems/free-sitemap-generator
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point."""
    try:
        from sitemap_generator.gui import main as gui_main
        return gui_main()
    except ImportError as e:
        print(f"Error: Missing required dependencies. {e}")
        print("\nPlease install requirements:")
        print("  pip install -r requirements.txt")
        return 1
    except Exception as e:
        logging.exception("Application failed to start")
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
