import os
import tomllib
from pathlib import Path


def read_pyproject_version(pyproject_path: Path) -> str:
    pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return pyproject_data["project"]["version"]


def normalize_tag(tag: str) -> str:
    return tag.removeprefix("v")


def main() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    pyproject_version = read_pyproject_version(repository_root / "pyproject.toml")

    tag = normalize_tag(os.environ.get("GITHUB_REF_NAME", ""))
    tag_version = normalize_tag(tag)

    if tag_version != pyproject_version:
        raise SystemExit(
            f"Tag version does not match pyproject.toml version: tag={tag!r} pyproject={pyproject_version!r}"
        )
    print(
        f"Tag version matches pyproject.toml version: tag={tag!r} pyproject={pyproject_version!r}"
    )


if __name__ == "__main__":
    main()
