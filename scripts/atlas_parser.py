from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent

OUTPUT_JSON = ROOT / "ATLAS_INVENTORY.json"
OUTPUT_MD = ROOT / "ATLAS_INVENTORY.md"

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
    "ATLAS_INVENTORY.md",
    "ATLAS_INVENTORY.json",
    "ATLAS_VALIDATION_REPORT.md",
    "CHANGE_IMPACT_REPORT.md",
    "DEPENDENCY_GRAPH.md",
}

SUPPORTED_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".tex",
    ".bib",
    ".mmd",
    ".puml",
    ".mermaid",
}


@dataclass
class DocumentMetadata:
    document_id: str | None
    title: str
    status: str | None
    version: str | None
    author: str | None
    reviewed: str | None
    document_type: str | None
    tags: list[str]
    products: list[str]
    dependencies: list[str]


@dataclass
class AtlasDocument:
    path: str
    directory: str
    filename: str
    extension: str
    size_bytes: int
    line_count: int
    modified_at: str
    checksum_sha256: str
    metadata: DocumentMetadata
    headings: list[str]
    internal_links: list[str]
    external_links: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def should_ignore(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts

    if any(part in IGNORED_DIRECTORIES for part in relative_parts):
        return True

    if path.name in IGNORED_FILES:
        return True

    return False


def discover_files() -> list[Path]:
    files: list[Path] = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if should_ignore(path):
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        files.append(path)

    return sorted(
        files,
        key=lambda item: relative_path(item).lower(),
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            digest.update(block)

    return digest.hexdigest()


def parse_scalar(value: str) -> str | None:
    value = value.strip().strip("\"'")

    if not value:
        return None

    return value


def parse_inline_list(value: str) -> list[str]:
    value = value.strip()

    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]

    items = [
        item.strip().strip("\"'")
        for item in value.split(",")
    ]

    return [
        item
        for item in items
        if item
    ]


def parse_frontmatter(content: str) -> dict[str, Any]:
    lines = content.splitlines()

    if not lines or lines[0].strip() != "---":
        return {}

    end_index: int | None = None

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}

    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in lines[1:end_index]:
        line = raw_line.rstrip()

        if not line.strip() or line.lstrip().startswith("#"):
            continue

        list_match = re.match(r"^\s*-\s+(.+)$", line)

        if list_match and current_list_key:
            value = list_match.group(1).strip().strip("\"'")
            data.setdefault(current_list_key, []).append(value)
            continue

        key_match = re.match(
            r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$",
            line,
        )

        if not key_match:
            continue

        key = key_match.group(1).strip().lower()
        value = key_match.group(2).strip()

        if not value:
            data[key] = []
            current_list_key = key
            continue

        current_list_key = None

        if value.startswith("[") and value.endswith("]"):
            data[key] = parse_inline_list(value)
        else:
            data[key] = parse_scalar(value)

    return data


def first_heading(content: str, fallback: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("# "):
            return stripped[2:].strip()

    return fallback.replace("_", " ").replace("-", " — ")


def extract_headings(content: str) -> list[str]:
    headings: list[str] = []

    for line in content.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())

        if match:
            headings.append(match.group(2).strip())

    return headings


def extract_links(content: str) -> tuple[list[str], list[str]]:
    links = re.findall(
        r"\[[^\]]+\]\(([^)]+)\)",
        content,
    )

    internal: list[str] = []
    external: list[str] = []

    for link in links:
        link = link.strip()

        if link.startswith(("http://", "https://")):
            external.append(link)
        elif not link.startswith(("#", "mailto:")):
            internal.append(link)

    return sorted(set(internal)), sorted(set(external))


def list_value(
    metadata: dict[str, Any],
    *keys: str,
) -> list[str]:
    for key in keys:
        value = metadata.get(key)

        if isinstance(value, list):
            return [
                str(item)
                for item in value
                if str(item).strip()
            ]

        if isinstance(value, str):
            return parse_inline_list(value)

    return []


def scalar_value(
    metadata: dict[str, Any],
    *keys: str,
) -> str | None:
    for key in keys:
        value = metadata.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def build_document(path: Path) -> AtlasDocument:
    content = read_text(path)
    frontmatter = parse_frontmatter(content)

    fallback_title = path.stem
    title = (
        scalar_value(frontmatter, "title", "titulo")
        or first_heading(content, fallback_title)
    )

    internal_links, external_links = extract_links(content)

    stat = path.stat()

    metadata = DocumentMetadata(
        document_id=scalar_value(
            frontmatter,
            "id",
            "document_id",
            "document-id",
        ),
        title=title,
        status=scalar_value(
            frontmatter,
            "status",
        ),
        version=scalar_value(
            frontmatter,
            "version",
            "versao",
        ),
        author=scalar_value(
            frontmatter,
            "author",
            "autor",
        ),
        reviewed=scalar_value(
            frontmatter,
            "reviewed",
            "review_date",
            "revisado",
        ),
        document_type=scalar_value(
            frontmatter,
            "type",
            "document_type",
            "tipo",
        ),
        tags=list_value(
            frontmatter,
            "tags",
        ),
        products=list_value(
            frontmatter,
            "products",
            "produtos",
        ),
        dependencies=list_value(
            frontmatter,
            "dependencies",
            "depends_on",
            "dependencias",
        ),
    )

    return AtlasDocument(
        path=relative_path(path),
        directory=relative_path(path.parent),
        filename=path.name,
        extension=path.suffix.lower(),
        size_bytes=stat.st_size,
        line_count=len(content.splitlines()),
        modified_at=datetime.fromtimestamp(
            stat.st_mtime,
            timezone.utc,
        ).strftime("%Y-%m-%d %H:%M UTC"),
        checksum_sha256=sha256(path),
        metadata=metadata,
        headings=extract_headings(content),
        internal_links=internal_links,
        external_links=external_links,
    )


def build_inventory() -> list[AtlasDocument]:
    return [
        build_document(path)
        for path in discover_files()
    ]


def write_json(
    documents: list[AtlasDocument],
) -> None:
    payload = {
        "generated_at": utc_now(),
        "repository": ROOT.name,
        "document_count": len(documents),
        "documents": [
            asdict(document)
            for document in documents
        ],
    }

    OUTPUT_JSON.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_markdown(
    documents: list[AtlasDocument],
) -> None:
    grouped: dict[str, list[AtlasDocument]] = {}

    for document in documents:
        top_directory = document.path.split("/", maxsplit=1)[0]
        grouped.setdefault(top_directory, []).append(document)

    lines = [
        "# Inventário Oficial do EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo EDI Knowledge Engine.",
        "",
        f"**Gerado em:** {utc_now()}",
        "",
        f"**Total de documentos:** {len(documents)}",
        "",
    ]

    for directory in sorted(grouped):
        items = grouped[directory]

        lines.extend(
            [
                f"## {directory}",
                "",
                f"Documentos encontrados: **{len(items)}**",
                "",
            ]
        )

        for document in items:
            metadata = document.metadata

            lines.append(
                f"### [{metadata.title}]({document.path})"
            )
            lines.append("")
            lines.append(f"- Caminho: `{document.path}`")
            lines.append(f"- Tipo: `{metadata.document_type or 'não informado'}`")
            lines.append(f"- ID: `{metadata.document_id or 'não informado'}`")
            lines.append(f"- Status: `{metadata.status or 'não informado'}`")
            lines.append(f"- Versão: `{metadata.version or 'não informada'}`")
            lines.append(f"- Autor: `{metadata.author or 'não informado'}`")
            lines.append(f"- Revisado: `{metadata.reviewed or 'não informado'}`")
            lines.append(f"- Linhas: **{document.line_count}**")
            lines.append(f"- Tamanho: **{document.size_bytes} bytes**")

            if metadata.tags:
                lines.append(
                    f"- Tags: {', '.join(metadata.tags)}"
                )

            if metadata.products:
                lines.append(
                    f"- Produtos: {', '.join(metadata.products)}"
                )

            if metadata.dependencies:
                lines.append(
                    f"- Dependências: {', '.join(metadata.dependencies)}"
                )

            lines.append("")

    OUTPUT_MD.write_text(
        "\n".join(lines).strip() + "\n",
        encoding="utf-8",
    )


def main() -> int:
    try:
        documents = build_inventory()

        write_json(documents)
        write_markdown(documents)

        print("Varredura completa do EDI Atlas concluída.")
        print(f"Documentos encontrados: {len(documents)}")
        print(f"Inventário Markdown: {OUTPUT_MD.name}")
        print(f"Inventário JSON: {OUTPUT_JSON.name}")

        return 0

    except Exception as error:
        print(
            f"Falha ao processar o EDI Atlas: {error}",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
