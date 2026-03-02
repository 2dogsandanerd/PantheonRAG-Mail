# Contributing to PantheonRAG-Mail

Thank you for your interest in contributing to PantheonRAG-Mail!

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/PantheonRAG-Mail.git
   cd PantheonRAG-Mail
   ```
3. **Set up the Backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Set up the Frontend:**
   ```bash
   cd frontend
   npm install
   ```
5. **Configure your environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Generate a secure JWT key:
   echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> backend/.env
   ```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-awesome-feature`
2. Make your changes
3. **Run the backend tests:**
   ```bash
   cd backend
   source venv/bin/activate
   pytest test/ -v
   ```
4. **Lint your Python code:**
   ```bash
   ruff check backend/src/
   ```
5. **Lint your JavaScript code:**
   ```bash
   cd frontend && npm run lint
   ```
6. Commit with a clear message (see convention below)
7. Push to your fork: `git push origin feature/my-awesome-feature`
8. Open a **Pull Request** against `main`

## Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only changes |
| `refactor:` | Code change without feature/fix |
| `test:` | Adding or fixing tests |
| `chore:` | Build process, tooling |
| `security:` | Security-related fix |

**Examples:**
```
feat: add support for Anthropic Claude as LLM provider
fix: prevent temp file leak on upload error
security: implement admin role check for cache clear endpoint
docs: add QUICKSTART guide
```

## Code Standards

### Python (Backend)
- Follow **PEP 8** (enforced by `ruff`)
- All functions must have type hints
- **No mock/fake code in production paths** — Six Sigma quality standard
- All new features require tests

### JavaScript/React (Frontend)
- Follow ESLint rules (`.eslintrc`)
- Use functional components with hooks
- No inline styles — use Material-UI `sx` prop or theme

### Six Sigma Principle
This project enforces a "no fake code" policy:
- No `# TODO: replace with real implementation later`
- No placeholder return values (`return {"status": "ok"}` without real logic)
- No swallowed exceptions (`except: pass`)

## Testing

```bash
# Unit tests
cd backend && pytest test/unit/ -v

# Integration tests (requires Docker)
docker-compose -f docker-compose.test.yml up -d
cd backend && pytest test/integration/ -v
docker-compose -f docker-compose.test.yml down
```

## Reporting Issues

Please use the GitHub Issue templates:
- **Bug report:** Use the "Bug Report" template
- **Feature request:** Use the "Feature Request" template

## Questions?

Open a [GitHub Discussion](https://github.com/2dogsandanerd/PantheonRAG-Mail/discussions) — we're happy to help!

---

*By contributing, you agree that your contributions will be licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*
