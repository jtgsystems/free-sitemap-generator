# Contributing to Site Map Generator

First off, thank you for considering contributing to Site Map Generator! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by a respectful and inclusive environment. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible using the bug report template.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please use the feature request template and include:

* A clear and descriptive title
* A detailed description of the proposed feature
* Why this enhancement would be useful
* Possible implementation approach (optional)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Make your changes** following the coding standards below
4. **Test your changes**: Run existing tests and add new ones if needed
5. **Update documentation**: Update README.md if needed
6. **Commit your changes**: Use clear and descriptive commit messages
7. **Push to your fork** and submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/free-sitemap-generator.git
cd free-sitemap-generator

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run tests
python -m unittest test_main.py
```

## Coding Standards

### Python Style Guide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
* Use meaningful variable and function names
* Add docstrings to functions and classes
* Keep functions focused and concise
* Use type hints where appropriate

### Code Organization

* **main.py**: GUI application and main entry point
* **Crawler class**: Web crawling logic
* **test_main.py**: Unit tests

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add support for custom crawl depth configuration

- Add max_depth parameter to GUI
- Update CrawlerWorker to accept user-defined depth
- Add validation for depth input

Fixes #123
```

## Testing

* Write unit tests for new features
* Ensure all tests pass before submitting PR
* Test on multiple operating systems if possible (Windows, macOS, Linux)
* Test with different Python versions (3.8+)

## Documentation

* Update README.md for user-facing changes
* Add docstrings to new functions and classes
* Update code comments for complex logic
* Keep the documentation clear and concise

## Project Structure

```
free-sitemap-generator/
├── .github/              # GitHub templates and workflows
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
├── main.py              # Main application code
├── setup.py             # PyInstaller build script
└── test_main.py         # Unit tests
```

## Questions?

Feel free to open an issue with the label "question" if you have any questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
