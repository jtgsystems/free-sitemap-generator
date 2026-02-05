"""
Advanced async web crawler for sitemap generation.
SOTA 2026 Edition with concurrent crawling and smart URL discovery.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Set, List, Optional, Dict, Callable
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = 'FreeSitemapGenerator/3.0 (+https://github.com/jtgsystems/free-sitemap-generator)'


@dataclass
class PageInfo:
    """Information about a crawled page."""
    url: str
    depth: int = 0
    lastmod: Optional[str] = None
    priority: float = 0.5
    changefreq: str = "monthly"
    title: Optional[str] = None
    images: List[str] = field(default_factory=list)
    
    def to_xml(self) -> str:
        """Generate XML sitemap entry."""
        xml = f"  <url>\n    <loc>{self._escape_xml(self.url)}</loc>\n"
        if self.lastmod:
            xml += f"    <lastmod>{self.lastmod}</lastmod>\n"
        xml += f"    <changefreq>{self.changefreq}</changefreq>\n"
        xml += f"    <priority>{self.priority:.1f}</priority>\n"
        
        # Add image sitemap entries
        for img_url in self.images[:1000]:  # Limit images per URL
            xml += f"    <image:image>\n      <image:loc>{self._escape_xml(img_url)}</image:loc>\n    </image:image>\n"
        
        xml += "  </url>"
        return xml
    
    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))


class AsyncCrawler:
    """High-performance async web crawler."""
    
    def __init__(
        self,
        base_url: str,
        max_depth: int = 5,
        max_urls: int = 50000,
        concurrency: int = 10,
        crawl_delay: float = 0.1,
        respect_robots_txt: bool = True,
        include_images: bool = False,
        follow_redirects: bool = True,
        timeout: int = 30
    ):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.concurrency = concurrency
        self.crawl_delay = crawl_delay
        self.respect_robots_txt = respect_robots_txt
        self.include_images = include_images
        self.follow_redirects = follow_redirects
        self.timeout = timeout
        
        self.visited_urls: Set[str] = set()
        self.pages: Dict[str, PageInfo] = {}
        self.robot_parser: Optional[RobotFileParser] = None
        self.url_callback: Optional[Callable[[PageInfo], None]] = None
        self.progress_callback: Optional[Callable[[int, int], None]] = None
        
        # Statistics
        self.stats = {
            'urls_crawled': 0,
            'urls_failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def _init_robots_txt(self, session: aiohttp.ClientSession) -> None:
        """Initialize robots.txt parser."""
        if not self.respect_robots_txt:
            return
        
        try:
            robots_url = f"{urlparse(self.base_url).scheme}://{self.domain}/robots.txt"
            self.robot_parser = RobotFileParser()
            self.robot_parser.set_url(robots_url)
            
            async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    self.robot_parser.parse(content.split('\n'))
                    logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Could not load robots.txt: {e}")
            self.robot_parser = None
    
    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        if not self.respect_robots_txt or not self.robot_parser:
            return True
        return self.robot_parser.can_fetch(USER_AGENT, url)
    
    def _calculate_priority(self, depth: int, url: str) -> float:
        """Calculate page priority based on depth and URL characteristics."""
        # Base priority decreases with depth
        priority = max(0.1, 1.0 - (depth * 0.2))
        
        # Boost homepage
        if url == self.base_url or url.rstrip('/') == self.base_url.rstrip('/'):
            priority = 1.0
        
        # Boost important pages
        path = urlparse(url).path.lower()
        if any(x in path for x in ['contact', 'about', 'product', 'service']):
            priority = min(1.0, priority + 0.1)
        
        return round(priority, 1)
    
    def _calculate_changefreq(self, url: str) -> str:
        """Estimate change frequency based on URL patterns."""
        path = urlparse(url).path.lower()
        
        if path in ['', '/']:
            return "daily"
        elif any(x in path for x in ['blog', 'news', 'article']):
            return "weekly"
        elif any(x in path for x in ['product', 'category']):
            return "weekly"
        elif any(x in path for x in ['about', 'contact', 'faq']):
            return "monthly"
        else:
            return "monthly"
    
    async def _fetch_page(
        self,
        session: aiohttp.ClientSession,
        url: str,
        depth: int
    ) -> Optional[PageInfo]:
        """Fetch and parse a single page."""
        if url in self.visited_urls or len(self.pages) >= self.max_urls:
            return None
        
        if not self._can_fetch(url):
            logger.debug(f"Skipping {url} (robots.txt)")
            return None
        
        self.visited_urls.add(url)
        
        try:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
            
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                allow_redirects=self.follow_redirects
            ) as resp:
                
                if resp.status != 200:
                    logger.debug(f"HTTP {resp.status} for {url}")
                    self.stats['urls_failed'] += 1
                    return None
                
                content_type = resp.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    logger.debug(f"Skipping non-HTML {url} ({content_type})")
                    return None
                
                text = await resp.text()
                
                # Parse page
                soup = BeautifulSoup(text, 'lxml')
                
                # Extract lastmod from header if available
                lastmod = None
                if 'Last-Modified' in resp.headers:
                    try:
                        from email.utils import parsedate_to_datetime
                        dt = parsedate_to_datetime(resp.headers['Last-Modified'])
                        lastmod = dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
                    except:
                        pass
                
                # Extract title
                title = None
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                
                # Extract images if enabled
                images = []
                if self.include_images:
                    for img in soup.find_all('img', src=True):
                        img_url = urljoin(url, img['src'])
                        if urlparse(img_url).netloc == self.domain:
                            images.append(img_url)
                
                page_info = PageInfo(
                    url=url,
                    depth=depth,
                    lastmod=lastmod,
                    priority=self._calculate_priority(depth, url),
                    changefreq=self._calculate_changefreq(url),
                    title=title,
                    images=images[:10]  # Limit images per page
                )
                
                self.pages[url] = page_info
                self.stats['urls_crawled'] += 1
                
                if self.url_callback:
                    self.url_callback(page_info)
                
                if self.progress_callback:
                    self.progress_callback(len(self.pages), self.max_urls)
                
                return page_info
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url}")
            self.stats['urls_failed'] += 1
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            self.stats['urls_failed'] += 1
        
        return None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract valid links from parsed HTML."""
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip anchors and javascript
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            
            # Remove fragment
            absolute_url, _ = urldefrag(absolute_url)
            
            parsed = urlparse(absolute_url)
            
            # Check scheme
            if parsed.scheme not in ('http', 'https'):
                continue
            
            # Check same domain
            if parsed.netloc != self.domain:
                continue
            
            # Normalize URL
            normalized = parsed._replace(fragment="").geturl()
            
            if normalized not in self.visited_urls:
                links.add(normalized)
        
        return links
    
    async def crawl(self) -> List[PageInfo]:
        """Start the crawl and return discovered pages."""
        self.stats['start_time'] = time.time()
        
        connector = aiohttp.TCPConnector(
            limit=self.concurrency,
            limit_per_host=self.concurrency,
            enable_cleanup_closed=True,
            force_close=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            # Initialize robots.txt
            await self._init_robots_txt(session)
            
            # Start with base URL
            queue = asyncio.Queue()
            await queue.put((self.base_url, 0))
            
            semaphore = asyncio.Semaphore(self.concurrency)
            
            async def process_url(url: str, depth: int):
                """Process a single URL."""
                async with semaphore:
                    page_info = await self._fetch_page(session, url, depth)
                    
                    if page_info and depth < self.max_depth:
                        # Extract and queue new links
                        try:
                            async with session.get(url, headers={'User-Agent': USER_AGENT}) as resp:
                                text = await resp.text()
                                soup = BeautifulSoup(text, 'lxml')
                                links = self._extract_links(soup, url)
                                
                                for link in links:
                                    if link not in self.visited_urls and len(self.pages) < self.max_urls:
                                        await queue.put((link, depth + 1))
                        except:
                            pass
                    
                    # Rate limiting
                    if self.crawl_delay > 0:
                        await asyncio.sleep(self.crawl_delay)
            
            # Process queue
            tasks = set()
            
            while True:
                # Get next URL from queue
                try:
                    url, depth = await asyncio.wait_for(queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    # No more URLs in queue
                    if not tasks:
                        break
                    # Wait for some tasks to complete
                    done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                    for task in done:
                        try:
                            await task
                        except Exception:
                            pass
                    continue
                
                # Start new task
                task = asyncio.create_task(process_url(url, depth))
                tasks.add(task)
                
                # Clean up completed tasks
                if len(tasks) >= self.concurrency:
                    done, tasks = await asyncio.wait(
                        tasks,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in done:
                        try:
                            await task
                        except Exception:
                            pass
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        self.stats['end_time'] = time.time()
        logger.info(f"Crawl completed: {len(self.pages)} URLs in {self.stats['end_time'] - self.stats['start_time']:.1f}s")
        
        return list(self.pages.values())
