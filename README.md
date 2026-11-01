# Tilecraft 

Rewrite of an old project started in 2021, a 2D recreation of minecraft.

## Installation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then open a terminal in the cloned repository. The project requires Python 3.10 or newer; CI currently tests Python 3.10 and 3.13.

For a full development setup, use Python 3.13 and install the locked dependencies:

```powershell
uv sync --locked --python 3.13
```

The default `dev` dependency group installs pytest, pytest-cov, and mypy alongside the game dependencies. uv creates `.venv` automatically; manual activation is not required.

Run the game from the repository root:

```powershell
uv run --locked python -m tilecraft
```

To install and run only the game dependencies:

```powershell
uv sync --locked --python 3.13 --no-dev
uv run --locked --no-dev python -m tilecraft
```

This runs the Python application but does not build a standalone executable.

## Development

To run tests (including the configured coverage report):

```powershell
uv run --locked python -m pytest
```

To run type checking:

```powershell
uv run --locked mypy tilecraft
```
