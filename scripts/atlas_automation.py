from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

README_PATH = ROOT / "README.md"
STATUS_PATH = ROOT / "STATUS_OFICIAL.md"
INDEX_PATH = ROOT / "ATLAS_INDEX.md"
REPORT_PATH = ROOT / "ATLAS_VALIDATION_REPORT.md"

STATUS_START = "<!-- EDI_ATLAS_STATUS_START -->"
STATUS_END = "<!-- EDI_ATLAS_STATUS_END -->"

GENERATED_NOTICE = (
    "> Este arquivo é gerado automaticamente pelo GitHub Actions. "
    "Não edite manualmente as seções automáticas."
)

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "scripts",
}

IGNORED_FILES = {
    "ATLAS_INDEX.md",
    "ATLAS_VALIDATION_REPORT.md",
}


@dataclass(frozen=True)
class AtlasSection:
    identifier: str
    title: str
    aliases: tuple[str, ...]
    required: bool = True


SECTIONS: tuple[AtlasSection, ...] = (
    AtlasSection(
        identifier="foundation",
        title="Fundação",
        aliases=(
            "00_FUNDAÇÃO",
            "00_FUNDACAO",
            "00_FOUNDATION",
        ),
    ),
    AtlasSection(
        identifier="framework",
        title="Framework EDI",
        aliases=(
            "01_FRAMEWORK_EDI",
            "01_FRAMEWORK-EDI",
        ),
    ),
    AtlasSection(
        identifier="eios",
        title="EIOS",
        aliases=(
            "02_EIOS",
        ),
    ),
    AtlasSection(
        identifier="knowledge",
        title="Conhecimento",
        aliases=(
            "07_CONHECIMENTO",
            "07_KNOWLEDGE",
        ),
    ),
    AtlasSection(
        identifier="collection",
        title="Coleção",
        aliases=(
            "09_COLEÇÃO",
            "09_COLECAO",
            "09_COLLECTION",
        ),
    ),
    AtlasSection(
        identifier="publisher",
        title="Editor e Publisher",
        aliases=(
            "11_EDITOR",
            "11_PUBLISHER",
        ),
    ),
    AtlasSection(
        identifier="adr",
        title="Registros de Decisão Arquitetural",
        aliases=(
            "ADR",
        ),
    ),
    AtlasSection(
        identifier="decisions",
        title="Decisões",
        aliases=(
            "DECISÕES",
            "DECISOES",
            "DECISIONS",
        ),
    ),
    AtlasSection(
        identifier="diagrams",
        title="Diagramas",
        aliases=(
            "DIAGRAMAS",
            "DIAGRAMS",
        ),
    ),
)


def normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"[^A-Z0-9]+", "_", without_accents.upper()).strip("_")


def relative_link(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def markdown_title(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.stem.replace("_", " ").replace("-", " — ")

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("# "):
            return stripped[2:].strip()

    return path.stem.replace("_", " ").replace("-", " — ")


def list_root_directories() -> list[Path]:
    return sorted(
        (
            path
            for path in ROOT.iterdir()
            if path.is_dir() and path.name not in IGNORED_DIRECTORIES
        ),
        key=lambda path: normalize(path.name),
    )


def find_section_directory(section: AtlasSection) -> Path | None:
    root_directories = list_root_directories()

    normalized_aliases = {
        normalize(alias)
        for alias in section.aliases
    }

    for directory in root_directories:
        if normalize(directory.name) in normalized_aliases:
            return directory

    return None


def markdown_files(directory: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in directory.rglob("*.md")
            if path.is_file()
            and path.name not in IGNORED_FILES
            and not any(
                part in IGNORED_DIRECTORIES
                for part in path.relative_to(ROOT).parts
            )
        ),
        key=lambda path: normalize(relative_link(path)),
    )


def all_markdown_files() -> list[Path]:
    return sorted(
        (
            path
            for path in ROOT.rglob("*.md")
            if path.is_file()
            and path.name not in IGNORED_FILES
            and not any(
                part in IGNORED_DIRECTORIES
                for part in path.relative_to(ROOT).parts
            )
        ),
        key=lambda path: normalize(relative_link(path)),
    )


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%d/%m/%Y às %H:%M UTC")


def build_index() -> tuple[str, dict[str, int]]:
    lines = [
        "# Índice Oficial do EDI Atlas",
        "",
        GENERATED_NOTICE,
        "",
        f"**Última atualização automática:** {utc_timestamp()}",
        "",
        "## Arquitetura oficial",
        "",
        "```text",
        "Framework EDI",
        "        ↓",
        "EIOS — Educational Intelligence Operating System",
        "        ↓",
        "Core Compartilhado",
        "        ↓",
        "Produtos Especializados",
        "```",
        "",
    ]

    statistics: dict[str, int] = {}
    indexed_paths: set[Path] = set()

    for section in SECTIONS:
        directory = find_section_directory(section)

        lines.extend(
            [
                f"## {section.title}",
                "",
            ]
        )

        if directory is None:
            statistics[section.identifier] = 0
            lines.extend(
                [
                    f"> Diretório não encontrado. Nomes aceitos: "
                    f"`{'`, `'.join(section.aliases)}`.",
                    "",
                ]
            )
            continue

        files = markdown_files(directory)
        statistics[section.identifier] = len(files)
        indexed_paths.update(files)

        lines.append(f"**Diretório:** `{relative_link(directory)}`")
        lines.append("")

        if not files:
            lines.extend(
                [
                    "_Nenhum documento Markdown encontrado._",
                    "",
                ]
            )
            continue

        for file_path in files:
            title = markdown_title(file_path)
            link = relative_link(file_path)
            lines.append(f"- [{title}]({link})")

        lines.append("")

    additional_files = [
        path
        for path in all_markdown_files()
        if path not in indexed_paths
        and path not in {
            README_PATH,
            STATUS_PATH,
            INDEX_PATH,
            REPORT_PATH,
        }
    ]

    if additional_files:
        lines.extend(
            [
                "## Outros documentos",
                "",
            ]
        )

        for file_path in additional_files:
            lines.append(
                f"- [{markdown_title(file_path)}]"
                f"({relative_link(file_path)})"
            )

        lines.append("")

    total_documents = sum(statistics.values()) + len(additional_files)

    lines.extend(
        [
            "## Resumo quantitativo",
            "",
            f"- Seções oficiais previstas: **{len(SECTIONS)}**",
            f"- Documentos indexados: **{total_documents}**",
            f"- Documentos adicionais: **{len(additional_files)}**",
            "",
        ]
    )

    return "\n".join(lines), statistics


def default_status_content() -> str:
    return """# Status Oficial da EduData IA

A EduData IA é uma **Plataforma Operacional de Inteligência Educacional**.

## Arquitetura oficial

```text
Framework EDI
        ↓
EIOS — Educational Intelligence Operating System
        ↓
Core Compartilhado
        ↓
Produtos Especializados
