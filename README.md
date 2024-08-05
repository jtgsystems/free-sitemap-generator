# Site Map Generator

## Overview
The Site Map Generator is a Python-based application with a graphical user interface (GUI) that allows users to generate a site map for a given website. It crawls through all pages within the specified domain and creates a comprehensive list of URLs, providing a clear overview of the website's structure.

## Features
- User-friendly PyQt6-based GUI
- Recursive crawling of websites within the same domain
- Progress bar to show crawling status
- Error handling for invalid URLs and network issues
- Multithreaded design for responsive UI during crawling
- Results displayed in an easy-to-read format

## Requirements
- Python 3.6 or higher
- PyQt6
- Requests
- BeautifulSoup4

## Installation
1. Ensure you have Python installed on your system.
2. Install the required packages:
   ```
   pip install PyQt6 requests beautifulsoup4
   ```
3. Download the `SiteMapGenerator.exe` file from the latest release.

## Usage
1. Run the `SiteMapGenerator.exe` file.
2. Enter the URL of the website you want to generate a site map for in the input field.
3. Click the "Generate Site Map" button.
4. Wait for the crawling process to complete. You can monitor the progress in the progress bar and the text area below.
5. Once completed, the site map will be displayed in the text area.

## Building from Source
If you want to build the executable from source:
1. Clone this repository or download the source files.
2. Install PyInstaller:
   ```
   pip install pyinstaller
   ```
3. Run the setup script:
   ```
   python setup.py
   ```
4. The executable will be created in the `dist` folder.

## Limitations
- The crawler is set to a maximum depth of 5 levels to prevent excessive crawling.
- Only pages within the same domain as the initial URL are crawled.
- The application may take a while to complete for large websites.

## Troubleshooting
- If you encounter any issues with crawling, ensure that you have a stable internet connection.
- Some websites may block automated crawling. In such cases, you may see error messages in the results.
- If the application freezes or becomes unresponsive, try closing and reopening it.

## Contributing
Contributions to improve the Site Map Generator are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License
This project is open-source and available under the MIT License.