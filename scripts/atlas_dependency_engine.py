from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent

INVENTORY_PATH = ROOT / "ATLAS_INVENTORY.json"
DEPENDENCY_GRAPH_PATH = ROOT / "DEPENDENCY_GRAPH.md"
CHANGE_IMPACT_PATH = ROOT / "CHANGE_IMPACT_REPORT.md"

IGNORED_CHANGED_FILES = {
    "ATLAS_INDEX.md",
    "ATLAS_INVENTORY.md",
    "ATLAS_INVENTORY.json",
    "ATLAS_VALIDATION_REPORT.md",
    "DEPENDENCY_GRAPH.md",
    "CHANGE_IMPACT_REPORT.md",
}

AUTHORITATIVE_PREFIXES = (
    "00_FOUNDATION/",
    "01_FRAMEWORK_EDI/",
    "02_EIOS/",
    "ADR/",
    "DECISIONS/",
)

DERIVED_PREFIXES = (
    "07_KNOWLEDGE/",
    "09_COLLECTION/",
    "11_PUBLISHER/",
)

ARCHITECTURE_RELATIONS: dict[str, list[str]] = {
    "00_FOUNDATION": [
        "01_FRAMEWORK_EDI",
        "02_EIOS",
        "07_KNOWLEDGE",
        "09_COLLECTION",
        "11_PUBLISHER",
    ],
    "01_FRAMEWORK_EDI": [
        "02_EIOS",
        "07_KNOWLEDGE",
        "09_COLLECTION",
        "11_PUBLISHER",
    ],
    "02_EIOS": [
        "07_KNOWLEDGE",
        "09_COLLECTION",
        "11_PUBLISHER",
    ],
    "ADR": [
        "02_EIOS",
        "07_KNOWLEDGE",
        "09_COLLECTION",
        "11_PUBLISHER",
    ],
    "DECISIONS": [
        "00_FOUNDATION",
        "01_FRAMEWORK_EDI",
        "02_EIOS",
        "07_KNOWLEDGE",
        "09_COLLECTION",
        "11_PUBLISHER",
    ],
    "07_KNOWLEDGE": [
        "09_COLLECTION",
        "11_PUBLISHER",
    ],
    "09_COLLECTION": [
        "11_PUBLISHER",
    ],
}


@dataclass(frozen=True)
class Document:
    path: str
    title: str
    document_id: str | None
    document_type: str | None
    status: str | None
    dependencies: tuple[str, ...]
    internal_links: tuple[str, ...]


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    relation: str
    origin: str


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )


def normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return re.sub(
        r"[^A-Z0-9]+",
        "_",
        without_accents.upper(),
    ).strip("_")


def top_directory(path: str) -> str:
    return path.split("/", maxsplit=1)[0]


def is_authoritative(path: str) -> bool:
    return path.startswith(AUTHORITATIVE_PREFIXES)


def is_derived(path: str) -> bool:
    return path.startswith(DERIVED_PREFIXES)


def read_inventory() -> list[Document]:
    if not INVENTORY_PATH.exists():
        raise FileNotFoundError(
            "ATLAS_INVENTORY.json não encontrado. "
            "Execute scripts/atlas_parser.py antes."
        )

    payload = json.loads(
        INVENTORY_PATH.read_text(encoding="utf-8")
    )

    documents: list[Document] = []

    for item in payload.get("documents", []):
        metadata = item.get("metadata") or {}

        documents.append(
            Document(
                path=str(item.get("path", "")).strip(),
                title=str(
                    metadata.get("title")
                    or item.get("filename")
                    or "Documento sem título"
                ).strip(),
                document_id=clean_optional(
                    metadata.get("document_id")
                ),
                document_type=clean_optional(
                    metadata.get("document_type")
                ),
                status=clean_optional(
                    metadata.get("status")
                ),
                dependencies=tuple(
                    clean_list(metadata.get("dependencies"))
                ),
                internal_links=tuple(
                    clean_list(item.get("internal_links"))
                ),
            )
        )

    return [
        document
        for document in documents
        if document.path
    ]


def clean_optional(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    return text or None


def clean_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str) and value.strip():
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return []


def build_indexes(
    documents: list[Document],
) -> tuple[
    dict[str, Document],
    dict[str, Document],
    dict[str, list[Document]],
]:
    by_path = {
        document.path: document
        for document in documents
    }

    by_id = {
        normalize(document.document_id): document
        for document in documents
        if document.document_id
    }

    by_directory: dict[str, list[Document]] = defaultdict(list)

    for document in documents:
        by_directory[top_directory(document.path)].append(
            document
        )

    return by_path, by_id, by_directory


def resolve_internal_link(
    source_path: str,
    link: str,
    by_path: dict[str, Document],
) -> str | None:
    clean_link = link.split("#", maxsplit=1)[0].strip()

    if not clean_link:
        return None

    source_directory = Path(source_path).parent
    candidate = (
        source_directory / clean_link
    ).as_posix()

    normalized_candidate = Path(candidate).as_posix()

    if normalized_candidate.startswith("./"):
        normalized_candidate = normalized_candidate[2:]

    parts: list[str] = []

    for part in normalized_candidate.split("/"):
        if part in {"", "."}:
            continue

        if part == "..":
            if parts:
                parts.pop()
            continue

        parts.append(part)

    resolved = "/".join(parts)

    if resolved in by_path:
        return resolved

    if clean_link in by_path:
        return clean_link

    return None


def resolve_dependency_reference(
    reference: str,
    by_path: dict[str, Document],
    by_id: dict[str, Document],
    documents: list[Document],
) -> str | None:
    normalized_reference = normalize(reference)

    if normalized_reference in by_id:
        return by_id[normalized_reference].path

    if reference in by_path:
        return reference

    candidates = [
        document
        for document in documents
        if normalize(document.title) == normalized_reference
        or normalize(document.path) == normalized_reference
        or normalize(Path(document.path).stem)
        == normalized_reference
    ]

    if len(candidates) == 1:
        return candidates[0].path

    return None


def build_edges(
    documents: list[Document],
) -> tuple[list[Edge], list[str]]:
    by_path, by_id, by_directory = build_indexes(
        documents
    )

    edges: set[Edge] = set()
    unresolved: list[str] = []

    for document in documents:
        for dependency in document.dependencies:
            target = resolve_dependency_reference(
                dependency,
                by_path,
                by_id,
                documents,
            )

            if target:
                edges.add(
                    Edge(
                        source=target,
                        target=document.path,
                        relation="dependência declarada",
                        origin="frontmatter",
                    )
                )
            else:
                unresolved.append(
                    f"{document.path}: dependência não resolvida "
                    f"`{dependency}`"
                )

        for link in document.internal_links:
            target = resolve_internal_link(
                document.path,
                link,
                by_path,
            )

            if target:
                edges.add(
                    Edge(
                        source=target,
                        target=document.path,
                        relation="referência interna",
                        origin="markdown",
                    )
                )

    for source_directory, targets in (
        ARCHITECTURE_RELATIONS.items()
    ):
        source_documents = by_directory.get(
            source_directory,
            [],
        )

        for target_directory in targets:
            target_documents = by_directory.get(
                target_directory,
                [],
            )

            for source_document in source_documents:
                for target_document in target_documents:
                    edges.add(
                        Edge(
                            source=source_document.path,
                            target=target_document.path,
                            relation="relação arquitetural",
                            origin="arquitetura oficial",
                        )
                    )

    return sorted(
        edges,
        key=lambda edge: (
            edge.source.lower(),
            edge.target.lower(),
            edge.relation.lower(),
        ),
    ), sorted(set(unresolved))


def run_git_command(
    arguments: list[str],
) -> list[str]:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return []

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def changed_files() -> list[str]:
    changed = run_git_command(
        [
            "diff",
            "--name-only",
            "HEAD^",
            "HEAD",
        ]
    )

    if not changed:
        changed = run_git_command(
            [
                "diff",
                "--name-only",
                "HEAD",
            ]
        )

    filtered = [
        path
        for path in changed
        if path not in IGNORED_CHANGED_FILES
        and not path.startswith("scripts/__pycache__/")
        and not path.endswith(".pyc")
    ]

    return sorted(set(filtered))


def build_adjacency(
    edges: list[Edge],
) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)

    for edge in edges:
        adjacency[edge.source].add(edge.target)

    return adjacency


def calculate_impacts(
    changed: list[str],
    edges: list[Edge],
) -> dict[str, set[str]]:
    adjacency = build_adjacency(edges)
    impacts: dict[str, set[str]] = {}

    for changed_path in changed:
        discovered: set[str] = set()
        queue: deque[str] = deque(
            adjacency.get(changed_path, set())
        )

        while queue:
            current = queue.popleft()

            if current in discovered:
                continue

            discovered.add(current)

            for dependent in adjacency.get(current, set()):
                if dependent not in discovered:
                    queue.append(dependent)

        impacts[changed_path] = discovered

    return impacts


def escape_mermaid(value: str) -> str:
    return (
        value.replace('"', "'")
        .replace("[", "(")
        .replace("]", ")")
        .replace("\n", " ")
    )


def node_id(path: str) -> str:
    return "N_" + re.sub(
        r"[^A-Za-z0-9_]",
        "_",
        path,
    )


def write_dependency_graph(
    documents: list[Document],
    edges: list[Edge],
    unresolved: list[str],
) -> None:
    by_path = {
        document.path: document
        for document in documents
    }

    lines = [
        "# Grafo de Dependências do EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo "
        "EDI Knowledge Engine.",
        "",
        f"**Gerado em:** {timestamp()}",
        "",
        f"**Documentos analisados:** {len(documents)}",
        "",
        f"**Relações identificadas:** {len(edges)}",
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
        "## Grafo Mermaid",
        "",
        "```mermaid",
        "flowchart TD",
    ]

    connected_paths = {
        edge.source
        for edge in edges
    } | {
        edge.target
        for edge in edges
    }

    for path in sorted(connected_paths):
        document = by_path.get(path)

        label = (
            document.title
            if document
            else Path(path).stem
        )

        lines.append(
            f'    {node_id(path)}["{escape_mermaid(label)}"]'
        )

    for edge in edges:
        relation = escape_mermaid(edge.relation)

        lines.append(
            f"    {node_id(edge.source)} "
            f'-->|"{relation}"| '
            f"{node_id(edge.target)}"
        )

    lines.extend(
        [
            "```",
            "",
            "## Relações detalhadas",
            "",
        ]
    )

    if edges:
        for edge in edges:
            lines.append(
                f"- `{edge.source}` → `{edge.target}` "
                f"— **{edge.relation}** "
                f"({edge.origin})"
            )
    else:
        lines.append(
            "- Nenhuma relação foi identificada."
        )

    lines.extend(
        [
            "",
            "## Dependências não resolvidas",
            "",
        ]
    )

    if unresolved:
        lines.extend(
            f"- {item}"
            for item in unresolved
        )
    else:
        lines.append(
            "- Nenhuma dependência declarada ficou sem resolução."
        )

    lines.extend(
        [
            "",
            "## Regras de governança",
            "",
            "- Documentos autoritativos não são "
            "reescritos automaticamente.",
            "- Documentos derivados podem ser "
            "sincronizados automaticamente.",
            "- Alterações em ADRs e decisões devem "
            "gerar análise de impacto.",
            "",
        ]
    )

    DEPENDENCY_GRAPH_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_change_impact_report(
    changed: list[str],
    impacts: dict[str, set[str]],
    documents: list[Document],
) -> None:
    known_paths = {
        document.path
        for document in documents
    }

    lines = [
        "# Relatório de Impacto de Alterações",
        "",
        "> Arquivo gerado automaticamente pelo "
        "EDI Knowledge Engine.",
        "",
        f"**Gerado em:** {timestamp()}",
        "",
        f"**Arquivos alterados detectados:** {len(changed)}",
        "",
    ]

    if not changed:
        lines.extend(
            [
                "Nenhuma alteração documental foi "
                "detectada no commit analisado.",
                "",
            ]
        )
    else:
        for changed_path in changed:
            lines.extend(
                [
                    f"## `{changed_path}`",
                    "",
                ]
            )

            if changed_path not in known_paths:
                lines.append(
                    "> O arquivo alterado não está presente "
                    "no inventário documental atual."
                )
                lines.append("")
                continue

            if is_authoritative(changed_path):
                lines.append(
                    "**Classificação:** documento autoritativo."
                )
                lines.append("")
                lines.append(
                    "A automação não deve alterar este "
                    "documento sem revisão humana."
                )
                lines.append("")
            elif is_derived(changed_path):
                lines.append(
                    "**Classificação:** documento derivado."
                )
                lines.append("")
            else:
                lines.append(
                    "**Classificação:** documento de apoio."
                )
                lines.append("")

            affected = sorted(
                impacts.get(changed_path, set())
            )

            lines.append(
                f"**Documentos potencialmente impactados:** "
                f"{len(affected)}"
            )
            lines.append("")

            if affected:
                for affected_path in affected:
                    action = (
                        "revisão humana"
                        if is_authoritative(affected_path)
                        else "sincronização permitida"
                    )

                    lines.append(
                        f"- `{affected_path}` — {action}"
                    )
            else:
                lines.append(
                    "- Nenhum documento dependente foi identificado."
                )

            lines.append("")

    all_impacted = sorted(
        {
            impacted
            for values in impacts.values()
            for impacted in values
        }
    )

    authoritative_impacts = [
        path
        for path in all_impacted
        if is_authoritative(path)
    ]

    derived_impacts = [
        path
        for path in all_impacted
        if is_derived(path)
    ]

    lines.extend(
        [
            "## Resumo",
            "",
            f"- Total de documentos impactados: "
            f"**{len(all_impacted)}**",
            f"- Exigem revisão humana: "
            f"**{len(authoritative_impacts)}**",
            f"- Podem ser sincronizados: "
            f"**{len(derived_impacts)}**",
            "",
            "## Próxima ação recomendada",
            "",
        ]
    )

    if authoritative_impacts:
        lines.append(
            "Revisar manualmente os documentos "
            "autoritativos identificados antes de "
            "qualquer alteração."
        )
    elif derived_impacts:
        lines.append(
            "Executar o Sync Engine para atualizar "
            "os documentos derivados."
        )
    else:
        lines.append(
            "Nenhuma sincronização adicional é necessária."
        )

    lines.append("")

    CHANGE_IMPACT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> int:
    try:
        documents = read_inventory()
        edges, unresolved = build_edges(documents)

        changed = changed_files()
        impacts = calculate_impacts(
            changed,
            edges,
        )

        write_dependency_graph(
            documents,
            edges,
            unresolved,
        )

        write_change_impact_report(
            changed,
            impacts,
            documents,
        )

        print(
            "Análise de dependências do EDI Atlas concluída."
        )
        print(
            f"Documentos analisados: {len(documents)}"
        )
        print(
            f"Relações identificadas: {len(edges)}"
        )
        print(
            f"Arquivos alterados: {len(changed)}"
        )
        print(
            f"Arquivo gerado: {DEPENDENCY_GRAPH_PATH.name}"
        )
        print(
            f"Arquivo gerado: {CHANGE_IMPACT_PATH.name}"
        )

        return 0

    except Exception as error:
        print(
            "Falha no Dependency Engine do EDI Atlas: "
            f"{error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
