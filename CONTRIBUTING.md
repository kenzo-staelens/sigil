# Contributing to Sigil

Thanks for your interest! This guide outlines how to set up the development environment, run tests, and submit changes.

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/kenzo-staelens/sigil.git
   cd sigil
   ```

2. **Create a virtual environment** (optional but recommended)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\Scripts\activate
   ```

3. **Install in editable mode with development dependencies**

   ```bash
   pip install -e .[completion,dev]
   ```

## Running Tests

Run the full test suite with coverage:

```bash
pytest --cov=sigil
```

If you renamed the import package (e.g., to `sigil_cli`), adjust the `--cov` argument accordingly.

## Code Style

We use **Ruff** for linting and formatting. (You can replace with Black/Flake8 if you prefer.)

Install Ruff:

```bash
pip install ruff
```

Check and format:

```bash
ruff check .      # lint
ruff format .     # auto‑format
```

## Submitting Changes

1. **Fork** the repository and create a **feature branch**.
2. **Write clear commit messages** (preferably imperative, concise).
3. **Add or update tests** for any new functionality or bug fixes.
4. **Ensure all tests pass** locally.
5. **Open a pull request** against the `main` branch.

Pull requests should include a description of the change, the motivation behind it, and any relevant issue numbers.

## Reporting Issues

Use the [GitHub issue tracker](https://github.com/kenzo-staelens/sigil/issues). Please include:

- A clear description of the problem
- Steps to reproduce
- Expected and actual behavior
- Python version and OS

## Licensing

By contributing, you agree that your contributions will be licensed under the same [license](LICENSE) as the project.

---

Thanks again for contributing!
