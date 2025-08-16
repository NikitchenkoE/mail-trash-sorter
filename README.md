# Mail Trash Sorter 📧🤖

An intelligent mail sorting application that uses machine learning to automatically classify and organize your emails. This project serves as a learning platform for exploring modern Python development practices, ML/AI integration, and email processing.

## 🏗️ Project Structure

```
mail-trash-sorter/
├── mailbot/                    # Main application package
│   ├── app/                   # Application logic and entry points
│   ├── config/                # Configuration files and settings
│   ├── data/                  # Data storage (emails, models, etc.)
│   └── tests/                 # Test suite
├── pyproject.toml             # Project configuration and dependencies
├── .editorconfig              # Editor configuration
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd mail-trash-sorter
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

### Development Setup

1. **Install pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

2. **Verify installation**
   ```bash
   # Run tests
   pytest
   
   # Check code quality
   ruff check .
   ruff format .
   
   # Type checking
   mypy mailbot/
   ```

## 🛠️ Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write code with tests**
   - Use type hints consistently

3. **Check code quality**
   ```bash
   ruff check . && ruff format . && mypy mailbot/ && pytest
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

## 📚 Learning Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
- [Modern Python Packaging](https://packaging.python.org/tutorials/packaging-projects/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.