import warnings

# Suppress the specific DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning, message="sipPyTypeDict() is deprecated")

import sys
import requests
import os
import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar, QFileDialog, QMenuBar, QMenu, QDialog, QSpinBox, QCheckBox, QGroupBox, QRadioButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QPalette, QColor
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import webbrowser

import warnings

# Suppress the specific DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning, message="sipPyTypeDict() is deprecated")

class SiteMapGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Site Map Generator")
        self.setFixedSize(600, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.url_input = QLineEdit()
        self.result_text = QTextEdit()
        self.progress_bar = QProgressBar()
        self.depth_spinbox = QSpinBox()
        self.timeout_spinbox = QSpinBox()
        self.sitemap_xml_paths = {}

        self.create_layout()
        self.create_buttons()
        self.create_menu_bar()
        self.apply_styles()

        self.crawler_thread = None

    def create_layout(self):
        url_layout = QHBoxLayout()
        url_label = QLabel("Enter URL:")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        self.generate_button = QPushButton("Generate Site Map")
        self.generate_button.clicked.connect(self.generate_site_map)

        self.progress_bar.setVisible(False)
        self.result_text.setReadOnly(True)

        self.layout.addLayout(url_layout)
        self.layout.addWidget(self.generate_button)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.result_text)

    def create_buttons(self):
        button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_results)
        self.view_xml_button = QPushButton("View Sitemap XML")
        self.view_xml_button.clicked.connect(self.view_sitemap_xml)
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.view_xml_button)
        self.layout.addLayout(button_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QMenuBar {
                background-color: #333333;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #4CAF50;
            }
            QMenu {
                background-color: #333333;
                color: white;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
            }
        """)

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")
        save_action = QAction("Save Results", self)
        save_action.triggered.connect(self.save_results)
        file_menu.addAction(save_action)

        view_menu = menu_bar.addMenu("View")
        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        settings_menu = menu_bar.addMenu("Settings")
        crawl_settings_action = QAction("Crawl Settings", self)
        crawl_settings_action.triggered.connect(self.show_crawl_settings)
        settings_menu.addAction(crawl_settings_action)

    def save_results(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.result_text.toPlainText())

    def toggle_dark_mode(self):
        if self.dark_mode_action.isChecked():
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit, QTextEdit {
                    background-color: #3c3f41;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
                QProgressBar {
                    border: 1px solid #555555;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
                QMenuBar, QMenu {
                    background-color: #1e1e1e;
                    color: white;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #4CAF50;
                }
            """)
        else:
            self.apply_styles()

    def show_crawl_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Crawl Settings")
        layout = QVBoxLayout(dialog)

        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Max Crawl Depth:"))
        self.depth_spinbox.setRange(1, 10)
        self.depth_spinbox.setValue(5)
        depth_layout.addWidget(self.depth_spinbox)
        layout.addLayout(depth_layout)

        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Request Timeout (seconds):"))
        self.timeout_spinbox.setRange(1, 60)
        self.timeout_spinbox.setValue(10)
        timeout_layout.addWidget(self.timeout_spinbox)
        layout.addLayout(timeout_layout)

        sitemap_group = QGroupBox("Sitemap Formats")
        sitemap_layout = QVBoxLayout()
        self.standard_sitemap_cb = QCheckBox("Standard Sitemap")
        self.standard_sitemap_cb.setChecked(True)
        self.image_sitemap_cb = QCheckBox("Image Sitemap")
        self.video_sitemap_cb = QCheckBox("Video Sitemap")
        self.news_sitemap_cb = QCheckBox("News Sitemap")
        sitemap_layout.addWidget(self.standard_sitemap_cb)
        sitemap_layout.addWidget(self.image_sitemap_cb)
        sitemap_layout.addWidget(self.video_sitemap_cb)
        sitemap_layout.addWidget(self.news_sitemap_cb)
        sitemap_group.setLayout(sitemap_layout)
        layout.addWidget(sitemap_group)

        dialog.setLayout(layout)
        dialog.exec()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_text.toPlainText())

    def clear_results(self):
        self.url_input.clear()
        self.result_text.clear()
        self.progress_bar.setValue(0)

    def view_sitemap_xml(self):
        if hasattr(self, 'sitemap_xml_paths'):
            for path in self.sitemap_xml_paths.values():
                webbrowser.open(path)
        else:
            self.result_text.append("No sitemap XML files have been generated yet.")

    def generate_site_map(self):
        url = self.url_input.text().strip()
        if not url:
            self.result_text.setText("Please enter a valid URL.")
            return

        self.result_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_button.setEnabled(False)

        max_depth = self.depth_spinbox.value()
        timeout = self.timeout_spinbox.value()
        sitemap_formats = []
        if self.standard_sitemap_cb.isChecked():
            sitemap_formats.append('standard')
        if self.image_sitemap_cb.isChecked():
            sitemap_formats.append('image')
        if self.video_sitemap_cb.isChecked():
            sitemap_formats.append('video')
        if self.news_sitemap_cb.isChecked():
            sitemap_formats.append('news')

        self.crawler_thread = CrawlerThread(url, max_depth, timeout, sitemap_formats)
        self.crawler_thread.update_progress.connect(self.update_progress)
        self.crawler_thread.crawl_complete.connect(self.crawl_complete)
        self.crawler_thread.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.result_text.append(message)

    def crawl_complete(self, site_map, xml_paths):
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.result_text.append("\nSite Map:")
        self.result_text.append(site_map)
        self.sitemap_xml_paths = xml_paths
        for sitemap_type, path in xml_paths.items():
            self.result_text.append(f"\n{sitemap_type.capitalize()} Sitemap exported to: {path}")

class CrawlerThread(QThread):
    update_progress = pyqtSignal(int, str)
    crawl_complete = pyqtSignal(str, dict)

    def __init__(self, url, max_depth=5, timeout=10, sitemap_formats=None):
        super().__init__()
        self.url = url
        self.visited = set()
        self.max_depth = max_depth
        self.timeout = timeout
        self.sitemap_formats = sitemap_formats or ['standard']

    def run(self):
        try:
            site_map = self.crawl(self.url)
            xml_paths = self.export_sitemaps(site_map)
            self.crawl_complete.emit("\n".join(site_map), xml_paths)
        except Exception as e:
            self.crawl_complete.emit(f"An error occurred: {str(e)}", {})

    def crawl(self, url, depth=0):
        if url in self.visited or depth > self.max_depth:
            return []

        self.visited.add(url)
        self.update_progress.emit(len(self.visited), f"Crawling: {url}")

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            self.update_progress.emit(len(self.visited), f"Error crawling {url}: {str(e)}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        site_map = [url]

        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if self.is_valid_url(full_url):
                site_map.extend(self.crawl(full_url, depth + 1))

        return site_map

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme) and parsed.netloc == urlparse(self.url).netloc

    def export_sitemaps(self, site_map):
        xml_paths = {}
        domain = urlparse(self.url).netloc
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{domain}-sitemap-{timestamp}"
        os.makedirs(folder_name, exist_ok=True)

        if 'standard' in self.sitemap_formats:
            xml_paths['standard'] = self.export_standard_sitemap(site_map, folder_name)
        if 'image' in self.sitemap_formats:
            xml_paths['image'] = self.export_image_sitemap(site_map, folder_name)
        if 'video' in self.sitemap_formats:
            xml_paths['video'] = self.export_video_sitemap(site_map, folder_name)
        if 'news' in self.sitemap_formats:
            xml_paths['news'] = self.export_news_sitemap(site_map, folder_name)

        return xml_paths

    def export_standard_sitemap(self, site_map, folder_name):
        root = Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        for url in site_map:
            url_element = SubElement(root, 'url')
            loc = SubElement(url_element, 'loc')
            loc.text = url
        
        return self.save_sitemap(root, folder_name, "sitemap.xml")

    def export_image_sitemap(self, site_map, folder_name):
        root = Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
        
        for url in site_map:
            url_element = SubElement(root, 'url')
            loc = SubElement(url_element, 'loc')
            loc.text = url
            # Here you would add logic to find and add image:image elements
        
        return self.save_sitemap(root, folder_name, "image-sitemap.xml")

    def export_video_sitemap(self, site_map, folder_name):
        root = Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')
        
        for url in site_map:
            url_element = SubElement(root, 'url')
            loc = SubElement(url_element, 'loc')
            loc.text = url
            # Here you would add logic to find and add video:video elements
        
        return self.save_sitemap(root, folder_name, "video-sitemap.xml")

    def export_news_sitemap(self, site_map, folder_name):
        root = Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
        
        for url in site_map:
            url_element = SubElement(root, 'url')
            loc = SubElement(url_element, 'loc')
            loc.text = url
            # Here you would add logic to find and add news:news elements
        
        return self.save_sitemap(root, folder_name, "news-sitemap.xml")

    def save_sitemap(self, root, folder_name, filename):
        xml_string = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        file_path = os.path.join(folder_name, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml_string)
        return file_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SiteMapGenerator()
    window.show()
    sys.exit(app.exec())