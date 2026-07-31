from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent

INVENTORY_PATH = ROOT / "ATLAS_INVENTORY.json"
VALIDATION_REPORT_PATH = ROOT / "ATLAS_VALIDATION_REPORT.md"
HEALTH_REPORT_PATH = ROOT / "ATLAS_HEALTH.md"
METADATA_REPORT_PATH = ROOT / "METADATA_REPORT.md"
BROKEN_LINKS_PATH = ROOT / "BROKEN_LINKS.md"
DUPLICATED_IDS_PATH = ROOT / "DUPLICATED_IDS.md"

REQUIRED_DIRECTORIES = {
    "00_FOUNDATION",
    "01_FRAMEWORK_EDI",
    "02_EIOS",
    "07_KNOWLEDGE",
    "09_COLLECTION",
    "11_PUBLISHER",
    "ADR",
    "DECISIONS",
    "DIAGRAMS",
}

REQUIRED_FILES = {
    "README.md",
    "STATUS_OFICIAL.md",
    "ATLAS_INDEX.md",
    "ATLAS_INVENTORY.md",
    "ATLAS_INVENTORY.json",
    "DEPENDENCY_GRAPH.md",
    "CHANGE_IMPACT_REPORT.md",
    "ATLAS_SYNC_REPORT.md",
}

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
    "ATLAS_HEALTH.md",
    "METADATA_REPORT.md",
    "BROKEN_LINKS.md",
    "DUPLICATED_IDS.md",
    "DEPENDENCY_GRAPH.md",
    "CHANGE_IMPACT_REPORT.md",
    "ATLAS_SYNC_REPORT.md",
    "AUTO_INDEX.md",
}

AUTHORITATIVE_PREFIXES = (
    "00_FOUNDATION/",
    "01_FRAMEWORK_EDI/",
    "02_EIOS/",
    "ADR/",
    "DECISIONS/",
)

REQUIRED_METADATA_FIELDS = (
    "document_id",
    "title",
    "status",
    "version",
    "author",
    "reviewed",
    "document_type",
    "tags",
)

ALLOWED_STATUS_VALUES = {
    "draft",
    "review",
    "approved",
    "official",
    "accepted",
    "deprecated",
    "archived",
    "active",
    "inactive",
    "proposed",
    "superseded",
}

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_PATTERN = re.compile(r"^(?:v)?\d+(?:\.\d+){0,2}(?:[-+][A-Za-z0-9.-]+)?$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class Document:
    path: str
    title: str
    document_id: str | None
    status: str | None
    version: str | None
    author: str | None
    reviewed: str | None
    document_type: str | None
    tags: tuple[str, ...]
    dependencies: tuple[str, ...]
    internal_links: tuple[str, ...]
    line_count: int
    size_bytes: int


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    category: str
    path: str
    message: str


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def clean_optional(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def clean_list(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(
            str(item).strip()
            for item in value
            if str(item).strip()
        )

    if isinstance(value, str) and value.strip():
        return tuple(
            item.strip()
            for item in value.split(",")
            if item.strip()
        )

    return ()


def normalize_status(value: str | None) -> str | None:
    if value is None:
        return None

    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def is_authoritative(path: str) -> bool:
    return path.startswith(AUTHORITATIVE_PREFIXES)


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
        path = str(item.get("path", "")).strip()

        if not path:
            continue

        documents.append(
            Document(
                path=path,
                title=str(
                    metadata.get("title")
                    or item.get("filename")
                    or Path(path).stem
                ).strip(),
                document_id=clean_optional(
                    metadata.get("document_id")
                ),
                status=clean_optional(
                    metadata.get("status")
                ),
                version=clean_optional(
                    metadata.get("version")
                ),
                author=clean_optional(
                    metadata.get("author")
                ),
                reviewed=clean_optional(
                    metadata.get("reviewed")
                ),
                document_type=clean_optional(
                    metadata.get("document_type")
                ),
                tags=clean_list(
                    metadata.get("tags")
                ),
                dependencies=clean_list(
                    metadata.get("dependencies")
                ),
                internal_links=clean_list(
                    item.get("internal_links")
                ),
                line_count=int(item.get("line_count") or 0),
                size_bytes=int(item.get("size_bytes") or 0),
            )
        )

    return sorted(
        documents,
        key=lambda document: document.path.lower(),
    )


def validate_required_structure() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for directory in sorted(REQUIRED_DIRECTORIES):
        path = ROOT / directory

        if not path.is_dir():
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="estrutura",
                    path=directory,
                    message="Diretório obrigatório ausente.",
                )
            )

    for filename in sorted(REQUIRED_FILES):
        path = ROOT / filename

        if not path.is_file():
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="estrutura",
                    path=filename,
                    message="Arquivo obrigatório ausente.",
                )
            )

    return issues


def metadata_dict(document: Document) -> dict[str, Any]:
    return {
        "document_id": document.document_id,
        "title": document.title,
        "status": document.status,
        "version": document.version,
        "author": document.author,
        "reviewed": document.reviewed,
        "document_type": document.document_type,
        "tags": document.tags,
    }


def validate_metadata(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for document in documents:
        if document.path in IGNORED_FILES:
            continue

        fields = metadata_dict(document)

        for field in REQUIRED_METADATA_FIELDS:
            value = fields[field]
            missing = value is None or value == "" or value == ()

            if missing:
                severity = (
                    "error"
                    if is_authoritative(document.path)
                    else "warning"
                )

                issues.append(
                    ValidationIssue(
                        severity=severity,
                        category="metadados",
                        path=document.path,
                        message=f"Metadado obrigatório ausente: `{field}`.",
                    )
                )

        normalized_status = normalize_status(document.status)

        if normalized_status and normalized_status not in ALLOWED_STATUS_VALUES:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="metadados",
                    path=document.path,
                    message=(
                        "Status fora da lista recomendada: "
                        f"`{document.status}`."
                    ),
                )
            )

        if document.reviewed and not DATE_PATTERN.match(document.reviewed):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="metadados",
                    path=document.path,
                    message=(
                        "Campo `reviewed` deve usar o formato "
                        "`YYYY-MM-DD`."
                    ),
                )
            )

        if document.version and not VERSION_PATTERN.match(document.version):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="metadados",
                    path=document.path,
                    message=(
                        "Versão fora do padrão recomendado "
                        "`1.0.0` ou `v1.0.0`."
                    ),
                )
            )

    return issues


def validate_empty_documents(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for document in documents:
        if document.path in IGNORED_FILES:
            continue

        if document.size_bytes == 0 or document.line_count == 0:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="conteúdo",
                    path=document.path,
                    message="Documento vazio.",
                )
            )
        elif document.line_count < 3:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="conteúdo",
                    path=document.path,
                    message="Documento possui menos de 3 linhas.",
                )
            )

    return issues


def validate_duplicate_ids(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_id: dict[str, list[Document]] = defaultdict(list)

    for document in documents:
        if document.document_id:
            by_id[document.document_id.strip().lower()].append(document)

    for document_id, items in sorted(by_id.items()):
        if len(items) < 2:
            continue

        paths = ", ".join(
            f"`{document.path}`"
            for document in items
        )

        for document in items:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="duplicidade",
                    path=document.path,
                    message=(
                        f"ID duplicado `{document_id}` também usado em "
                        f"{paths}."
                    ),
                )
            )

    return issues


def validate_duplicate_titles(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_title: dict[str, list[Document]] = defaultdict(list)

    for document in documents:
        normalized_title = re.sub(
            r"\s+",
            " ",
            document.title.strip().lower(),
        )

        if normalized_title:
            by_title[normalized_title].append(document)

    for title, items in sorted(by_title.items()):
        if len(items) < 2:
            continue

        unique_paths = {item.path for item in items}

        if len(unique_paths) < 2:
            continue

        for document in items:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="duplicidade",
                    path=document.path,
                    message=f"Título duplicado: `{title}`.",
                )
            )

    return issues


def normalize_internal_target(
    source_path: str,
    link: str,
) -> str | None:
    clean_link = link.strip()

    if not clean_link:
        return None

    if clean_link.startswith(
        ("http://", "https://", "mailto:", "#")
    ):
        return None

    clean_link = clean_link.split("#", maxsplit=1)[0].strip()

    if not clean_link:
        return None

    source_directory = Path(source_path).parent
    candidate = (source_directory / clean_link).as_posix()

    parts: list[str] = []

    for part in candidate.split("/"):
        if part in {"", "."}:
            continue

        if part == "..":
            if parts:
                parts.pop()
            continue

        parts.append(part)

    return "/".join(parts)


def validate_broken_links(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    known_paths = {
        document.path
        for document in documents
    }

    for document in documents:
        for link in document.internal_links:
            target = normalize_internal_target(
                document.path,
                link,
            )

            if target is None:
                continue

            if target not in known_paths and not (ROOT / target).exists():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        category="links",
                        path=document.path,
                        message=f"Link interno quebrado: `{link}`.",
                    )
                )

    return issues


def validate_dependencies(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    known_ids = {
        document.document_id.strip().lower()
        for document in documents
        if document.document_id
    }

    known_paths = {
        document.path
        for document in documents
    }

    known_titles = {
        document.title.strip().lower()
        for document in documents
    }

    for document in documents:
        for dependency in document.dependencies:
            normalized = dependency.strip().lower()

            if (
                normalized not in known_ids
                and dependency not in known_paths
                and normalized not in known_titles
            ):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="dependências",
                        path=document.path,
                        message=(
                            "Dependência não resolvida: "
                            f"`{dependency}`."
                        ),
                    )
                )

    return issues


def build_dependency_graph(
    documents: list[Document],
) -> dict[str, set[str]]:
    by_id = {
        document.document_id.strip().lower(): document.path
        for document in documents
        if document.document_id
    }

    by_title = {
        document.title.strip().lower(): document.path
        for document in documents
    }

    by_path = {
        document.path: document.path
        for document in documents
    }

    graph: dict[str, set[str]] = defaultdict(set)

    for document in documents:
        for dependency in document.dependencies:
            normalized = dependency.strip().lower()
            target = (
                by_id.get(normalized)
                or by_title.get(normalized)
                or by_path.get(dependency)
            )

            if target:
                graph[document.path].add(target)

    return graph


def find_cycles(
    graph: dict[str, set[str]],
) -> list[list[str]]:
    cycles: list[list[str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return

        if node in visiting:
            try:
                index = stack.index(node)
            except ValueError:
                return

            cycle = stack[index:] + [node]

            if cycle not in cycles:
                cycles.append(cycle)

            return

        visiting.add(node)
        stack.append(node)

        for neighbor in graph.get(node, set()):
            visit(neighbor)

        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)

    return cycles


def validate_cycles(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    graph = build_dependency_graph(documents)
    cycles = find_cycles(graph)

    for cycle in cycles:
        cycle_text = " → ".join(cycle)

        for path in set(cycle[:-1]):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="dependências",
                    path=path,
                    message=f"Dependência circular detectada: {cycle_text}.",
                )
            )

    return issues


def validate_orphans(
    documents: list[Document],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    referenced_paths: set[str] = set()
    referenced_ids: set[str] = set()

    for document in documents:
        for link in document.internal_links:
            target = normalize_internal_target(
                document.path,
                link,
            )

            if target:
                referenced_paths.add(target)

        for dependency in document.dependencies:
            referenced_ids.add(dependency.strip().lower())

    for document in documents:
        if document.path in IGNORED_FILES:
            continue

        if is_authoritative(document.path):
            continue

        referenced = (
            document.path in referenced_paths
            or (
                document.document_id is not None
                and document.document_id.strip().lower()
                in referenced_ids
            )
        )

        if not referenced:
            issues.append(
                ValidationIssue(
                    severity="info",
                    category="órfãos",
                    path=document.path,
                    message=(
                        "Documento não é referenciado por links "
                        "ou dependências declaradas."
                    ),
                )
            )

    return issues


def collect_issues(
    documents: list[Document],
) -> list[ValidationIssue]:
    validators = (
        validate_required_structure,
        lambda: validate_metadata(documents),
        lambda: validate_empty_documents(documents),
        lambda: validate_duplicate_ids(documents),
        lambda: validate_duplicate_titles(documents),
        lambda: validate_broken_links(documents),
        lambda: validate_dependencies(documents),
        lambda: validate_cycles(documents),
        lambda: validate_orphans(documents),
    )

    issues: list[ValidationIssue] = []

    for validator in validators:
        issues.extend(validator())

    severity_order = {
        "error": 0,
        "warning": 1,
        "info": 2,
    }

    return sorted(
        issues,
        key=lambda issue: (
            severity_order.get(issue.severity, 99),
            issue.category,
            issue.path.lower(),
            issue.message.lower(),
        ),
    )


def issue_counts(
    issues: list[ValidationIssue],
) -> Counter[str]:
    return Counter(
        issue.severity
        for issue in issues
    )


def calculate_health_score(
    documents: list[Document],
    issues: list[ValidationIssue],
) -> int:
    if not documents:
        return 0

    counts = issue_counts(issues)

    penalty = (
        counts.get("error", 0) * 5
        + counts.get("warning", 0) * 2
        + counts.get("info", 0)
    )

    maximum = max(len(documents) * 8, 1)
    score = round(100 - min(100, penalty * 100 / maximum))

    return max(0, min(100, score))


def health_label(score: int) -> str:
    if score >= 90:
        return "Excelente"

    if score >= 75:
        return "Bom"

    if score >= 60:
        return "Atenção"

    if score >= 40:
        return "Crítico"

    return "Muito crítico"


def write_validation_report(
    documents: list[Document],
    issues: list[ValidationIssue],
) -> None:
    counts = issue_counts(issues)
    score = calculate_health_score(documents, issues)

    lines = [
        "# Relatório de Validação do EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo Validation Engine.",
        "",
        f"**Executado em:** {utc_timestamp()}",
        "",
        f"**Documentos analisados:** {len(documents)}",
        "",
        f"**Saúde do Atlas:** {score}/100 — **{health_label(score)}**",
        "",
        "## Resumo",
        "",
        f"- Erros: **{counts.get('error', 0)}**",
        f"- Avisos: **{counts.get('warning', 0)}**",
        f"- Informações: **{counts.get('info', 0)}**",
        "",
    ]

    for severity, title in (
        ("error", "Erros"),
        ("warning", "Avisos"),
        ("info", "Informações"),
    ):
        lines.extend(
            [
                f"## {title}",
                "",
            ]
        )

        filtered = [
            issue
            for issue in issues
            if issue.severity == severity
        ]

        if filtered:
            for issue in filtered:
                lines.append(
                    f"- `{issue.path}` — "
                    f"**{issue.category}** — "
                    f"{issue.message}"
                )
        else:
            lines.append(
                f"- Nenhum item classificado como {severity}."
            )

        lines.append("")

    VALIDATION_REPORT_PATH.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )


def write_health_report(
    documents: list[Document],
    issues: list[ValidationIssue],
) -> None:
    counts = issue_counts(issues)
    score = calculate_health_score(documents, issues)

    by_category = Counter(
        issue.category
        for issue in issues
    )

    lines = [
        "# Saúde do EDI Atlas",
        "",
        "> Indicador automático de qualidade documental.",
        "",
        f"**Atualizado em:** {utc_timestamp()}",
        "",
        f"## Pontuação: {score}/100",
        "",
        f"**Classificação:** {health_label(score)}",
        "",
        "## Indicadores",
        "",
        f"- Documentos analisados: **{len(documents)}**",
        f"- Erros: **{counts.get('error', 0)}**",
        f"- Avisos: **{counts.get('warning', 0)}**",
        f"- Informações: **{counts.get('info', 0)}**",
        "",
        "## Ocorrências por categoria",
        "",
    ]

    if by_category:
        for category, count in sorted(
            by_category.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            lines.append(
                f"- {category}: **{count}**"
            )
    else:
        lines.append(
            "- Nenhuma ocorrência encontrada."
        )

    lines.extend(
        [
            "",
            "## Critério",
            "",
            "- Erro: penalidade alta.",
            "- Aviso: penalidade média.",
            "- Informação: penalidade baixa.",
            "",
        ]
    )

    HEALTH_REPORT_PATH.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )


def write_metadata_report(
    documents: list[Document],
) -> None:
    lines = [
        "# Relatório de Metadados do EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo Validation Engine.",
        "",
        f"**Atualizado em:** {utc_timestamp()}",
        "",
    ]

    incomplete = 0

    for document in documents:
        if document.path in IGNORED_FILES:
            continue

        fields = metadata_dict(document)

        missing = [
            field
            for field in REQUIRED_METADATA_FIELDS
            if fields[field] is None
            or fields[field] == ""
            or fields[field] == ()
        ]

        if missing:
            incomplete += 1

            lines.extend(
                [
                    f"## `{document.path}`",
                    "",
                    "Metadados ausentes:",
                    "",
                ]
            )

            lines.extend(
                f"- `{field}`"
                for field in missing
            )

            lines.append("")

    if incomplete == 0:
        lines.extend(
            [
                "Todos os documentos analisados possuem "
                "os metadados obrigatórios.",
                "",
            ]
        )

    lines.extend(
        [
            "## Resumo",
            "",
            f"- Documentos com metadados incompletos: **{incomplete}**",
            "",
        ]
    )

    METADATA_REPORT_PATH.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )


def write_broken_links_report(
    issues: list[ValidationIssue],
) -> None:
    broken = [
        issue
        for issue in issues
        if issue.category == "links"
    ]

    lines = [
        "# Links Internos Quebrados",
        "",
        "> Arquivo gerado automaticamente pelo Validation Engine.",
        "",
        f"**Atualizado em:** {utc_timestamp()}",
        "",
        f"**Total:** {len(broken)}",
        "",
    ]

    if broken:
        for issue in broken:
            lines.append(
                f"- `{issue.path}` — {issue.message}"
            )
    else:
        lines.append(
            "- Nenhum link interno quebrado foi encontrado."
        )

    lines.append("")

    BROKEN_LINKS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_duplicated_ids_report(
    documents: list[Document],
) -> None:
    by_id: dict[str, list[str]] = defaultdict(list)

    for document in documents:
        if document.document_id:
            by_id[document.document_id.strip().lower()].append(
                document.path
            )

    duplicates = {
        document_id: paths
        for document_id, paths in by_id.items()
        if len(paths) > 1
    }

    lines = [
        "# IDs Duplicados no EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo Validation Engine.",
        "",
        f"**Atualizado em:** {utc_timestamp()}",
        "",
        f"**IDs duplicados:** {len(duplicates)}",
        "",
    ]

    if duplicates:
        for document_id, paths in sorted(duplicates.items()):
            lines.extend(
                [
                    f"## `{document_id}`",
                    "",
                ]
            )

            lines.extend(
                f"- `{path}`"
                for path in sorted(paths)
            )

            lines.append("")
    else:
        lines.append(
            "- Nenhum ID duplicado foi encontrado."
        )
        lines.append("")

    DUPLICATED_IDS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> int:
    try:
        documents = read_inventory()
        issues = collect_issues(documents)

        write_validation_report(documents, issues)
        write_health_report(documents, issues)
        write_metadata_report(documents)
        write_broken_links_report(issues)
        write_duplicated_ids_report(documents)

        counts = issue_counts(issues)
        score = calculate_health_score(documents, issues)

        print("EDI Atlas Validation Engine concluído.")
        print(f"Documentos analisados: {len(documents)}")
        print(f"Erros: {counts.get('error', 0)}")
        print(f"Avisos: {counts.get('warning', 0)}")
        print(f"Informações: {counts.get('info', 0)}")
        print(f"Saúde do Atlas: {score}/100")

        return 0

    except Exception as error:
        print(
            f"Falha no Validation Engine do EDI Atlas: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
