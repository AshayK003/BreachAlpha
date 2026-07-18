# Contributing to BreachAlpha

Thanks for your interest in contributing. This document covers the practical details.

## Getting Started

```bash
git clone https://github.com/AshayK003/BreachAlpha.git
cd BreachAlpha
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

Verify everything works:

```bash
pytest                        # 188 tests pass
cd frontend && npm run build  # builds clean
```

## Development Workflow

1. Create a branch from `main`: `git checkout -b feature/my-change`
2. Make your changes
3. Add or update tests
4. Run `pytest` — all tests must pass
5. Run `pytest --cov=breachalpha --cov-fail-under=60` — coverage must not drop
6. Commit and push
7. Open a pull request

## What to Work On

Check [open issues](https://github.com/AshayK003/BreachAlpha/issues) for planned work. Good first contributions:

- Add ticker mappings to `KNOWN_TICKERS` in `ticker_resolver.py`
- Improve error messages in `core/exceptions.py`
- Add test coverage for edge cases
- Fix frontend accessibility issues

## Code Conventions

### Python

- Follow existing style in the file you're editing
- Use domain exceptions (`core/exceptions.py`) instead of `HTTPException` in services
- Route modules are factory functions: `create_xxx_routes(limiter) -> APIRouter`
- Keep imports sorted: stdlib, third-party, local

### Frontend

- Plain JavaScript — no TypeScript
- Functional components with hooks
- Use shadcn/ui primitives from `components/ui/`
- Use `cn()` from `lib/utils.js` for conditional classes

### Testing

- Test files go in `tests/`
- Name tests `test_<module>.py`
- Use `httpx.AsyncClient` for API tests
- Write behavior-focused tests, not implementation tests

## Commit Messages

Use short imperative descriptions:

```
add SSRF validation for outbound URLs
fix CSV injection in batch export
remove unused _compute_pool from services/model.py
update README with deployment guide
```

## Pull Requests

- Keep PRs focused — one change per PR
- Include a description of what changed and why
- Add screenshots for UI changes
- Reference related issues

## Questions?

Open an issue or start a discussion on GitHub.
