# Twiggy 🌿

Real-time directory structure for Cursor AI. Your AI always knows your codebase's structure.

## Install

```bash
pip install -e .
```

## Use

```bash
twiggy init    # setup in any project
twiggy watch   # start watching for changes
```

Creates `.cursor/rules/file-structure.mdc` that auto-updates when you add/remove files.

Ignores the usual stuff: `node_modules`, `__pycache__`, `.git`, `dist`, etc.
