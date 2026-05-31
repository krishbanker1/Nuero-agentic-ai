"""Packaging safety checks for fresh-machine installs."""

from pathlib import Path
import sys
import tomllib


PROJECT = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]


def _all_dependency_specs() -> list[str]:
    specs = list(PROJECT.get("dependencies", []))
    for extra_specs in PROJECT.get("optional-dependencies", {}).values():
        specs.extend(extra_specs)
    return specs


def test_core_install_has_no_heavy_or_invalid_optional_dependencies():
    core_dependencies = PROJECT["dependencies"]

    assert "sqlitevec>=0.0.0" not in core_dependencies
    assert all(not dependency.startswith("sqlitevec") for dependency in core_dependencies)
    assert all(not dependency.startswith("chromadb") for dependency in core_dependencies)
    assert all(not dependency.startswith("playwright") for dependency in core_dependencies)
    assert all(not dependency.startswith("opencv-python") for dependency in core_dependencies)


def test_memory_extra_uses_published_sqlite_vec_package_name():
    memory_dependencies = PROJECT["optional-dependencies"]["memory"]

    assert any(dependency.startswith("sqlite-vec") for dependency in memory_dependencies)
    assert not any(dependency.startswith("sqlitevec") for dependency in _all_dependency_specs())


def test_sqlite_vec_extra_is_skipped_on_unsupported_bleeding_edge_python():
    marker_specs = [dependency for dependency in PROJECT["optional-dependencies"]["memory"] if dependency.startswith("sqlite-vec")]

    assert marker_specs
    assert "python_version < '3.14'" in marker_specs[0]
    assert sys.version_info >= (3, 10)


def test_cli_supports_repo_typo_alias():
    scripts = PROJECT["scripts"]

    assert scripts["neuro"] == "neuro.__main__:main"
    assert scripts["nuero"] == "neuro.__main__:main"
