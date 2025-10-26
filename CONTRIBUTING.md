# Contributing to Git2Art

Thank you for your interest in contributing to Git2Art! We welcome contributions from everyone. This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We're building a welcoming community for artists, developers, and enthusiasts.

## Ways to Contribute

### 1. Report Bugs
Found a bug? Help us fix it!

- **Check existing issues** first to avoid duplicates
- **Provide detailed information**:
  - What you were trying to do
  - What happened (the bug)
  - What you expected to happen
  - Steps to reproduce
  - Your environment (OS, Python version, etc.)
- **Include error messages** and screenshots if relevant

### 2. Suggest Features
Have an idea for improvement?

- **Check existing issues** to see if it's already been suggested
- **Describe the feature** clearly with use cases
- **Explain the benefit** - how would this improve Git2Art?
- **Provide examples** if possible

### 3. Improve Documentation
Documentation is crucial for any project.

- Fix typos or unclear explanations
- Add examples or tutorials
- Improve README or API documentation
- Translate documentation to other languages
- Create art style guides or gallery showcases

### 4. Submit Code Changes

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- pip

### Clone and Setup
```bash
# Clone the repository
git clone https://github.com/RobertSvebeck/Git2Art.git
cd Git2Art

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your local database settings (optional for CLI testing)
```

### Test Your Changes

#### For CLI changes
```bash
# Test the art generation directly
python git2art.py --repo /path/to/test/repo
python git2art.py --repo /path/to/test/repo --aspect 16:9 --contrast high
```

#### For Flask app changes
```bash
# Run the web application
python app.py
# Visit http://localhost:5000
```

#### For specific features
```bash
# Test automatic aspect ratio detection
python git2art.py --repo /path/to/test/repo --aspect auto

# Test different contrasts
python git2art.py --contrast low
python git2art.py --contrast medium
python git2art.py --contrast high
```

## Submitting Changes

### Before You Start
1. **Fork the repository** on GitHub
2. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes:
   git checkout -b fix/bug-description
   ```
3. **Make your changes** - keep them focused and atomic
4. **Test thoroughly** - ensure your changes don't break existing functionality

### Commit Messages
Write clear, descriptive commit messages:

```bash
# Good commit message format:
git commit -m "Brief description of change

More detailed explanation if needed. Explain the 'why' not just the 'what'.

- Bullet point for specific changes if multiple
- Another detail about the implementation
"
```

### Submit a Pull Request
1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues (e.g., "Fixes #123")
   - Screenshots for UI changes
   - Test results or reproduction steps for bug fixes

3. **Respond to feedback** - maintainers may suggest changes

### Pull Request Guidelines
- Keep PRs focused - don't mix multiple features
- Include tests if applicable
- Update documentation if you change functionality
- Follow the existing code style
- Keep commits clean and descriptive

## Areas for Contribution

### High Priority
- **Bug fixes** - always welcome!
- **Performance improvements** - optimize art generation
- **Documentation improvements** - READMEs, comments, guides
- **Test coverage** - unit and integration tests
- **Accessibility** - make the web app more accessible

### Medium Priority
- **New color palettes** - add support for more languages/frameworks
- **Art style variations** - different composition algorithms
- **Feature enhancements** - improve existing functionality
- **Code quality** - refactoring, type hints, better organization

### Nice to Have
- **Translations** - support for multiple languages
- **Docker support** - containerized deployment
- **CI/CD improvements** - automated testing and deployment
- **Gallery features** - better curation and discovery

## Code Style

### Python
- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and testable
- Use type hints where helpful

### HTML/CSS/JavaScript
- Keep markup semantic
- Use consistent indentation (2 or 4 spaces)
- Comment complex selectors or logic
- Keep CSS modular and maintainable

## Key Files

- `git2art.py` - Main art generation engine
- `app.py` - Flask application entry point
- `services/art_service.py` - Art generation service
- `services/git_service.py` - Git repository operations
- `routes/main_routes.py` - Web application routes
- `models/` - Database models
- `templates/` - HTML templates
- `static/css/` - Stylesheets
- `static/js/` - Client-side JavaScript

## Testing

### Manual Testing
Test on various repository types:
- Python projects
- JavaScript/Node.js projects
- Java projects
- Ruby projects
- Go/Rust projects
- Mobile projects (Swift, Kotlin, Flutter)
- HTML/CSS projects
- Mixed-language projects

### Edge Cases to Test
- Empty repositories
- Very large repositories (100+ files)
- Repositories with unusual file types
- Monorepos with multiple languages
- Repositories with no commits

## Questions?

- **Check the README** for usage instructions
- **Read CLAUDE.md** for development history and architecture
- **Look at existing issues** for similar questions
- **Start a discussion** if you need clarification

## Recognition

Contributors will be recognized in:
- Pull request comments
- Release notes for significant contributions
- Contributors section (when created)

## License

By contributing to Git2Art, you agree that your contributions will be licensed under the GPL-3.0 License (same as the project).

---

Thank you for contributing to Git2Art! We're excited to see what you create. 🎨

