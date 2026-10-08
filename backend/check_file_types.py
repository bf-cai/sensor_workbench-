"""Run additional file-type quality tools, visibly skipping absent file types."""

import os
import subprocess
from pathlib import Path

EXCLUDED_PARTS = frozenset({
    ".git", ".venv", "node_modules", "build", "dist", "static", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", "__pycache__",
})


def main() -> None:
    """Check maintained shell/YAML/Actions/C++/Rust files with real tools.

    Raises:
        RuntimeError: A new compiled language needs explicit build integration.
        OSError: An applicable required tool is missing.
        subprocess.CalledProcessError: Any applicable quality tool fails.
    """
    root = Path.cwd()
    files: list[Path] = []
    for directory, subdirectories, filenames in os.walk(root):
        subdirectories[:] = [name for name in subdirectories if name not in EXCLUDED_PARTS]
        files.extend(Path(directory) / name for name in filenames)
    shell = [str(path) for path in files if path.suffix == ".sh"]
    yaml = [str(path) for path in files if path.suffix in (".yml", ".yaml")]
    workflows = [str(path) for path in files if ".github/workflows" in str(path)]
    for label, selected, commands in (
        ("Shell", shell, (("shellcheck",), ("shfmt", "-d"))),
        ("YAML", yaml, (("yamllint",),)),
        ("GitHub Actions", workflows, (("actionlint",),)),
    ):
        if not selected:
            print(f"SKIP {label}: no applicable maintained files")
        for command in commands if selected else ():
            subprocess.run([*command, *selected], check=True)
    for label, extensions in (
        ("C/C++", {".c", ".cc", ".cpp", ".h", ".hpp"}),
        ("Rust", {".rs"}),
    ):
        if any(path.suffix in extensions for path in files):
            raise RuntimeError(f"Integrate {label} formatter, linter, compiler and tests")
        print(f"SKIP {label}: no applicable maintained files")


if __name__ == "__main__":
    main()
