from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_launch_assets_exist_and_are_linked_from_readme():
    required = [
        ROOT / "RELEASE_NOTES.md",
        ROOT / "docs" / "github_about_pack.md",
        ROOT / "docs" / "public_launch_pack.md",
    ]

    for path in required:
        assert path.exists(), f"Missing launch asset: {path.relative_to(ROOT)}"
        assert _read(path).strip(), f"Empty launch asset: {path.relative_to(ROOT)}"

    readme = _read(ROOT / "README.md")
    assert "RELEASE_NOTES.md" in readme
    assert "docs/github_about_pack.md" in readme
    assert "docs/public_launch_pack.md" in readme


def test_launch_assets_preserve_honest_public_positioning():
    combined = "\n".join(
        [
            _read(ROOT / "RELEASE_NOTES.md").lower(),
            _read(ROOT / "docs" / "github_about_pack.md").lower(),
            _read(ROOT / "docs" / "public_launch_pack.md").lower(),
        ]
    )

    assert "open-source" in combined
    assert "rc/mvp" in combined
    assert "validated core" in combined
    assert "product shell" in combined
    assert "advisory-only" in combined
    assert "baseline integration" in combined or "baseline integrations" in combined
    assert "security/control layer for ai agents" in combined
    assert "not a production-ready enterprise platform" in combined
    assert "enterprise-ready" not in combined


def test_launch_assets_link_only_to_existing_local_files():
    files = [
        ROOT / "README.md",
        ROOT / "RELEASE_NOTES.md",
        ROOT / "docs" / "github_about_pack.md",
        ROOT / "docs" / "public_launch_pack.md",
        ROOT / "docs" / "release.md",
        ROOT / "docs" / "open_source_release_pack_m2.md",
    ]
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    missing: list[tuple[str, str]] = []
    for path in files:
        for target in pattern.findall(_read(path)):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative_target = target.split("#", 1)[0]
            if not relative_target:
                continue
            resolved = (path.parent / relative_target).resolve()
            if not resolved.exists():
                missing.append((str(path.relative_to(ROOT)), target))

    assert not missing, f"Broken markdown links: {missing}"
