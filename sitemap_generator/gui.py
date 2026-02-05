"""
Enhanced PyQt6 GUI for the Sitemap Generator.
SOTA 2026 Edition with modern UI and export options.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QTextEdit,
    QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QFileDialog, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QStatusBar, QToolBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QFont

from .crawler import AsyncCrawler, PageInfo
from .exporter import SitemapExporter

logger = logging.getLogger(__name__)


class CrawlerWorker(QThread):
    """Background worker for crawling."""
    
    url_found = pyqtSignal(object)  # PageInfo
    progress_update = pyqtSignal(int, int)  # current, max
    finished_signal = pyqtSignal(list)  # List[PageInfo]
    error_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    
    def __init__(
        self,
        url: str,
        max_depth: int = 5,
        max_urls: int = 50000,
        concurrency: int = 10,
        crawl_delay: float = 0.1,
        respect_robots: bool = True,
        include_images: bool = False
    ):
        super().__init__()
        self.url = url
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.concurrency = concurrency
        self.crawl_delay = crawl_delay
        self.respect_robots = respect_robots
        self.include_images = include_images
        self._is_running = True
    
    def stop(self):
        """Stop the crawler."""
        self._is_running = False
    
    def run(self):
        """Run the crawler."""
        try:
            import asyncio
            
            crawler = AsyncCrawler(
                base_url=self.url,
                max_depth=self.max_depth,
                max_urls=self.max_urls,
                concurrency=self.concurrency,
                crawl_delay=self.crawl_delay,
                respect_robots_txt=self.respect_robots,
                include_images=self.include_images
            )
            
            crawler.url_callback = self._on_url_found
            crawler.progress_callback = self._on_progress
            
            # Run async crawl
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            pages = loop.run_until_complete(crawler.crawl())
            loop.close()
            
            if self._is_running:
                self.finished_signal.emit(pages)
                
        except Exception as e:
            logger.exception("Crawl failed")
            self.error_signal.emit(str(e))
    
    def _on_url_found(self, page: PageInfo):
        """Handle found URL."""
        if self._is_running:
            self.url_found.emit(page)
    
    def _on_progress(self, current: int, max_urls: int):
        """Handle progress update."""
        if self._is_running:
            self.progress_update.emit(current, max_urls)


class SitemapGeneratorGUI(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Free Sitemap Generator - SOTA 2026 Edition")
        self.setGeometry(100, 100, 1200, 800)
        
        self.worker: Optional[CrawlerWorker] = None
        self.pages: List[PageInfo] = []
        
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_label = QLabel("🗺️ Free Sitemap Generator - SOTA 2026 Edition")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self._create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self._create_results_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
    
    def _create_control_panel(self) -> QWidget:
        """Create the control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # URL Input
        url_group = QGroupBox("🌐 Target Website")
        url_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.returnPressed.connect(self.start_crawl)
        url_layout.addWidget(self.url_input)
        
        layout.addWidget(url_group)
        
        # Crawl Settings
        settings_group = QGroupBox("⚙️ Crawl Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Max Depth
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Max Depth:"))
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 10)
        self.depth_spin.setValue(5)
        depth_layout.addWidget(self.depth_spin)
        settings_layout.addLayout(depth_layout)
        
        # Max URLs
        max_urls_layout = QHBoxLayout()
        max_urls_layout.addWidget(QLabel("Max URLs:"))
        self.max_urls_spin = QSpinBox()
        self.max_urls_spin.setRange(100, 50000)
        self.max_urls_spin.setValue(5000)
        self.max_urls_spin.setSingleStep(100)
        max_urls_layout.addWidget(self.max_urls_spin)
        settings_layout.addLayout(max_urls_layout)
        
        # Concurrency
        concurrency_layout = QHBoxLayout()
        concurrency_layout.addWidget(QLabel("Concurrency:"))
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 50)
        self.concurrency_spin.setValue(10)
        concurrency_layout.addWidget(self.concurrency_spin)
        settings_layout.addLayout(concurrency_layout)
        
        # Crawl Delay
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay (sec):"))
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0, 5)
        self.delay_spin.setValue(0.1)
        self.delay_spin.setSingleStep(0.1)
        delay_layout.addWidget(self.delay_spin)
        settings_layout.addLayout(delay_layout)
        
        # Checkboxes
        self.respect_robots_check = QCheckBox("Respect robots.txt")
        self.respect_robots_check.setChecked(True)
        settings_layout.addWidget(self.respect_robots_check)
        
        self.include_images_check = QCheckBox("Include images")
        self.include_images_check.setChecked(False)
        settings_layout.addWidget(self.include_images_check)
        
        layout.addWidget(settings_group)
        
        # Export Options
        export_group = QGroupBox("📁 Export Options")
        export_layout = QVBoxLayout(export_group)
        
        self.export_format = QComboBox()
        self.export_format.addItems([
            "XML Sitemap",
            "XML Sitemap (GZipped)",
            "Text File (.txt)",
            "CSV File",
            "JSON File"
        ])
        export_layout.addWidget(self.export_format)
        
        self.gzip_check = QCheckBox("Compress with GZip")
        self.gzip_check.setChecked(False)
        export_layout.addWidget(self.gzip_check)
        
        export_btn = QPushButton("💾 Export Sitemap")
        export_btn.clicked.connect(self.export_sitemap)
        export_layout.addWidget(export_btn)
        
        layout.addWidget(export_group)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Start Crawl")
        self.start_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        self.start_btn.clicked.connect(self.start_crawl)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_crawl)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return panel
    
    def _create_results_panel(self) -> QWidget:
        """Create the results panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # URLs Tab
        urls_tab = QWidget()
        urls_layout = QVBoxLayout(urls_tab)
        
        self.urls_table = QTableWidget()
        self.urls_table.setColumnCount(5)
        self.urls_table.setHorizontalHeaderLabels([
            "URL", "Title", "Priority", "ChangeFreq", "Images"
        ])
        self.urls_table.horizontalHeader().setStretchSection(0)
        self.urls_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        urls_layout.addWidget(self.urls_table)
        
        tabs.addTab(urls_tab, "URLs")
        
        # Log Tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        tabs.addTab(log_tab, "Log")
        
        # Stats Tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        tabs.addTab(stats_tab, "Statistics")
        
        return panel
    
    def _setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Sitemap...", self)
        export_action.triggered.connect(self.export_sitemap)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        start_action = QAction("Start", self)
        start_action.triggered.connect(self.start_crawl)
        toolbar.addAction(start_action)
        
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.stop_crawl)
        toolbar.addAction(stop_action)
    
    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
    
    def start_crawl(self):
        """Start the crawling process."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Error", "URL must start with http:// or https://")
            return
        
        # Reset UI
        self.pages = []
        self.urls_table.setRowCount(0)
        self.log_text.clear()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setRange(0, self.max_urls_spin.value())
        self.progress_bar.setValue(0)
        self.status_label.setText("Crawling...")
        
        # Create worker
        self.worker = CrawlerWorker(
            url=url,
            max_depth=self.depth_spin.value(),
            max_urls=self.max_urls_spin.value(),
            concurrency=self.concurrency_spin.value(),
            crawl_delay=self.delay_spin.value(),
            respect_robots=self.respect_robots_check.isChecked(),
            include_images=self.include_images_check.isChecked()
        )
        
        self.worker.url_found.connect(self.on_url_found)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.error_signal.connect(self.on_error)
        
        self.worker.start()
        
        self.log(f"Started crawling: {url}")
    
    def stop_crawl(self):
        """Stop the crawling process."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)
            self.log("Crawl stopped by user")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Stopped")
    
    def on_url_found(self, page: PageInfo):
        """Handle found URL."""
        self.pages.append(page)
        
        # Add to table
        row = self.urls_table.rowCount()
        self.urls_table.insertRow(row)
        
        self.urls_table.setItem(row, 0, QTableWidgetItem(page.url))
        self.urls_table.setItem(row, 1, QTableWidgetItem(page.title or ""))
        self.urls_table.setItem(row, 2, QTableWidgetItem(f"{page.priority:.1f}"))
        self.urls_table.setItem(row, 3, QTableWidgetItem(page.changefreq))
        self.urls_table.setItem(row, 4, QTableWidgetItem(str(len(page.images))))
        
        self.log(f"Found: {page.url}")
    
    def on_progress(self, current: int, max_urls: int):
        """Handle progress update."""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Crawled: {current} URLs")
    
    def on_finished(self, pages: List[PageInfo]):
        """Handle crawl completion."""
        self.pages = pages
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(len(pages))
        self.status_label.setText(f"Complete: {len(pages)} URLs found")
        
        self.log(f"\nCrawl complete! Found {len(pages)} URLs")
        
        # Update stats
        self.update_stats()
        
        # Auto-export suggestion
        QMessageBox.information(
            self,
            "Crawl Complete",
            f"Found {len(pages)} URLs.\n\nWould you like to export the sitemap?",
        )
    
    def on_error(self, error_msg: str):
        """Handle crawl error."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"Error: {error_msg}")
        
        QMessageBox.critical(self, "Error", f"Crawl failed:\n{error_msg}")
        self.log(f"ERROR: {error_msg}")
    
    def export_sitemap(self):
        """Export the sitemap."""
        if not self.pages:
            QMessageBox.warning(self, "Error", "No URLs to export. Please crawl a website first.")
            return
        
        format_idx = self.export_format.currentIndex()
        
        exporter = SitemapExporter(self.pages, self.url_input.text())
        
        if format_idx == 0:  # XML
            path, _ = QFileDialog.getSaveFileName(self, "Save Sitemap", "sitemap.xml", "XML files (*.xml)")
            if path:
                exporter.export_xml(path, include_images=self.include_images_check.isChecked())
                QMessageBox.information(self, "Success", f"Sitemap saved to:\n{path}")
        
        elif format_idx == 1:  # XML GZipped
            path, _ = QFileDialog.getSaveFileName(self, "Save Sitemap", "sitemap.xml.gz", "GZipped XML (*.xml.gz)")
            if path:
                exporter.export_xml(path, gzip_compress=True)
                QMessageBox.information(self, "Success", f"Sitemap saved to:\n{path}")
        
        elif format_idx == 2:  # TXT
            path, _ = QFileDialog.getSaveFileName(self, "Save Sitemap", "sitemap.txt", "Text files (*.txt)")
            if path:
                exporter.export_txt(path)
                QMessageBox.information(self, "Success", f"Sitemap saved to:\n{path}")
        
        elif format_idx == 3:  # CSV
            path, _ = QFileDialog.getSaveFileName(self, "Save Sitemap", "sitemap.csv", "CSV files (*.csv)")
            if path:
                exporter.export_csv(path)
                QMessageBox.information(self, "Success", f"Sitemap saved to:\n{path}")
        
        elif format_idx == 4:  # JSON
            path, _ = QFileDialog.getSaveFileName(self, "Save Sitemap", "sitemap.json", "JSON files (*.json)")
            if path:
                exporter.export_json(path)
                QMessageBox.information(self, "Success", f"Sitemap saved to:\n{path}")
    
    def update_stats(self):
        """Update statistics display."""
        if not self.pages:
            return
        
        exporter = SitemapExporter(self.pages, "")
        stats = exporter.get_stats()
        
        text = f"""
Sitemap Statistics
==================

Total URLs: {stats['total_urls']}
Total Images: {stats['total_images']}
Average Priority: {stats['avg_priority']:.2f}

Priority Distribution:
  High (0.8-1.0): {stats['priority_distribution']['high (0.8-1.0)']}
  Medium (0.4-0.7): {stats['priority_distribution']['medium (0.4-0.7)']}
  Low (0.0-0.3): {stats['priority_distribution']['low (0.0-0.3)']}
"""
        self.stats_text.setText(text)
    
    def log(self, message: str):
        """Add log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Free Sitemap Generator",
            """<h2>Free Sitemap Generator - SOTA 2026 Edition</h2>
            <p>Version 3.0</p>
            <p>A professional-grade sitemap generator with async crawling, 
            XML export, and modern GUI.</p>
            <p><a href="https://github.com/jtgsystems/free-sitemap-generator">
            GitHub Repository</a></p>
            <p>License: MIT</p>
            """
        )


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Free Sitemap Generator")
    app.setApplicationVersion("3.0-SOTA2026")
    
    window = SitemapGeneratorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
