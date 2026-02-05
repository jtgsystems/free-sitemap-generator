"""
XML Sitemap exporter with support for standard, image, and index sitemaps.
SOTA 2026 Edition - Fully sitemaps.org compliant.
"""

import gzip
import os
from datetime import datetime
from pathlib import Path
from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from .crawler import PageInfo


class SitemapExporter:
    """Export crawled pages to various sitemap formats."""
    
    # Sitemaps.org limits
    MAX_URLS_PER_SITEMAP = 50000
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB uncompressed
    
    # XML Namespaces
    NS_SITEMAP = "http://www.sitemaps.org/schemas/sitemap/0.9"
    NS_IMAGE = "http://www.google.com/schemas/sitemap-image/1.1"
    NS_VIDEO = "http://www.google.com/schemas/sitemap-video/1.1"
    NS_NEWS = "http://www.google.com/schemas/sitemap-news/0.9"
    
    def __init__(self, pages: List[PageInfo], base_url: str):
        self.pages = sorted(pages, key=lambda p: p.url)
        self.base_url = base_url.rstrip('/')
    
    def _prettify_xml(self, elem: Element) -> str:
        """Return pretty-printed XML string."""
        rough_string = tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")
        # Remove empty lines
        lines = [line for line in pretty.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def export_xml(
        self,
        output_path: str,
        include_images: bool = False,
        gzip_compress: bool = False
    ) -> str:
        """
        Export standard XML sitemap.
        
        Args:
            output_path: Path to save the sitemap
            include_images: Include image sitemap entries
            gzip_compress: Compress with gzip
            
        Returns:
            Path to the saved file
        """
        urlset = Element('urlset')
        urlset.set('xmlns', self.NS_SITEMAP)
        
        if include_images:
            urlset.set('xmlns:image', self.NS_IMAGE)
        
        for page in self.pages:
            url_elem = SubElement(urlset, 'url')
            
            # Required: loc
            loc = SubElement(url_elem, 'loc')
            loc.text = self._escape_xml(page.url)
            
            # Optional: lastmod
            if page.lastmod:
                lastmod = SubElement(url_elem, 'lastmod')
                lastmod.text = page.lastmod
            
            # Optional: changefreq
            changefreq = SubElement(url_elem, 'changefreq')
            changefreq.text = page.changefreq
            
            # Optional: priority
            priority = SubElement(url_elem, 'priority')
            priority.text = f"{page.priority:.1f}"
            
            # Image entries
            if include_images and page.images:
                for img_url in page.images[:1000]:  # Google limit
                    image_elem = SubElement(url_elem, '{%s}image' % self.NS_IMAGE)
                    image_loc = SubElement(image_elem, '{%s}loc' % self.NS_IMAGE)
                    image_loc.text = self._escape_xml(img_url)
        
        xml_content = self._prettify_xml(urlset)
        
        # Write file
        if gzip_compress:
            output_path = output_path + '.gz' if not output_path.endswith('.gz') else output_path
            with gzip.open(output_path, 'wt', encoding='utf-8') as f:
                f.write(xml_content)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
        
        return output_path
    
    def export_sitemap_index(
        self,
        output_dir: str,
        base_filename: str = "sitemap",
        urls_per_file: int = 50000,
        gzip_compress: bool = True
    ) -> List[str]:
        """
        Export sitemap index with multiple sitemap files.
        For large sites exceeding 50,000 URLs or 50MB.
        
        Args:
            output_dir: Directory to save sitemaps
            base_filename: Base name for sitemap files
            urls_per_file: Maximum URLs per sitemap file
            gzip_compress: Compress individual sitemaps
            
        Returns:
            List of generated file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        sitemap_files = []
        
        # Split pages into chunks
        for i in range(0, len(self.pages), urls_per_file):
            chunk = self.pages[i:i + urls_per_file]
            chunk_num = (i // urls_per_file) + 1
            
            # Create sitemap for this chunk
            sitemap_filename = f"{base_filename}_{chunk_num}.xml"
            if gzip_compress:
                sitemap_filename += '.gz'
            
            sitemap_path = output_dir / sitemap_filename
            
            # Create temporary exporter for chunk
            chunk_exporter = SitemapExporter(chunk, self.base_url)
            chunk_exporter.export_xml(
                str(sitemap_path),
                include_images=False,
                gzip_compress=gzip_compress
            )
            
            generated_files.append(str(sitemap_path))
            sitemap_files.append((sitemap_filename, datetime.now().isoformat()))
        
        # Create sitemap index
        index_path = output_dir / f"{base_filename}_index.xml"
        self._create_sitemap_index(sitemap_files, str(index_path))
        generated_files.insert(0, str(index_path))
        
        return generated_files
    
    def _create_sitemap_index(self, sitemaps: List[tuple], output_path: str) -> None:
        """Create sitemap index file."""
        sitemapindex = Element('sitemapindex')
        sitemapindex.set('xmlns', self.NS_SITEMAP)
        
        for filename, lastmod in sitemaps:
            sitemap_elem = SubElement(sitemapindex, 'sitemap')
            
            loc = SubElement(sitemap_elem, 'loc')
            loc.text = f"{self.base_url}/{filename}"
            
            if lastmod:
                lastmod_elem = SubElement(sitemap_elem, 'lastmod')
                lastmod_elem.text = lastmod
        
        xml_content = self._prettify_xml(sitemapindex)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    
    def export_txt(self, output_path: str) -> str:
        """Export simple text file with one URL per line."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for page in self.pages:
                f.write(f"{page.url}\n")
        return output_path
    
    def export_csv(self, output_path: str) -> str:
        """Export CSV with URL details."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Priority', 'ChangeFreq', 'LastMod', 'Images'])
            
            for page in self.pages:
                writer.writerow([
                    page.url,
                    page.title or '',
                    page.priority,
                    page.changefreq,
                    page.lastmod or '',
                    len(page.images)
                ])
        
        return output_path
    
    def export_json(self, output_path: str) -> str:
        """Export JSON format."""
        import json
        
        data = {
            'base_url': self.base_url,
            'generated_at': datetime.now().isoformat(),
            'total_urls': len(self.pages),
            'urls': [
                {
                    'url': p.url,
                    'title': p.title,
                    'priority': p.priority,
                    'changefreq': p.changefreq,
                    'lastmod': p.lastmod,
                    'images': p.images
                }
                for p in self.pages
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def get_stats(self) -> dict:
        """Get statistics about the sitemap."""
        priorities = [p.priority for p in self.pages]
        images_count = sum(len(p.images) for p in self.pages)
        
        return {
            'total_urls': len(self.pages),
            'total_images': images_count,
            'avg_priority': sum(priorities) / len(priorities) if priorities else 0,
            'priority_distribution': {
                'high (0.8-1.0)': len([p for p in priorities if p >= 0.8]),
                'medium (0.4-0.7)': len([p for p in priorities if 0.4 <= p < 0.8]),
                'low (0.0-0.3)': len([p for p in priorities if p < 0.4])
            }
        }
    
    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))
