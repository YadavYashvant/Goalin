# Contributing to Goalin

Thank you for your interest in contributing to Goalin! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/YadavYashvant/Goalin/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System information (distro, DE/WM, X11/Wayland)
   - Relevant logs from `journalctl --user -u goalin.service`

### Suggesting Features

1. Check existing [Issues](https://github.com/YadavYashvant/Goalin/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following the coding standards below
4. Test your changes thoroughly
5. Commit with clear, descriptive messages
6. Push to your fork
7. Create a Pull Request with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Goalin.git
cd Goalin

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests (if available)
pytest
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Maximum line length: 100 characters

### Code Organization

- Keep related functionality together
- Use appropriate module structure
- Avoid circular imports
- Use type hints where appropriate

### Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Comment complex logic
- Update CHANGELOG.md

### Testing

- Test on both X11 and Wayland (if applicable)
- Test on different desktop environments
- Ensure backward compatibility
- Check for memory leaks in long-running processes

## Project Structure

```
src/goalin/
├── __init__.py       # Package initialization
├── config.py         # Configuration management
├── database.py       # Database operations
├── tracker.py        # Activity tracking
├── daemon.py         # Background service
├── report.py         # Report generation
└── gui.py           # GTK GUI
```

## Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line: brief summary (50 chars or less)
- Detailed description after blank line (if needed)
- Reference issues: "Fixes #123" or "Relates to #456"

Examples:
```
Add Wayland support for KDE Plasma

- Implement KWin window tracking
- Add detection for Plasma compositor
- Update documentation

Fixes #42
```

## Release Process

1. Update version in:
   - `setup.py`
   - `src/goalin/__init__.py`
   - `PKGBUILD`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. Create GitHub release
6. Update AUR package

## Questions?

Feel free to open an issue or reach out to the maintainers if you have any questions!
