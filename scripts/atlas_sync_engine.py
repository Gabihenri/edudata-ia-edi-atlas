from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent

INVENTORY_PATH = ROOT / "ATLAS_INVENTORY.json"
IMPACT_PATH = ROOT / "CHANGE_IMPACT_REPORT.md"
SYNC_REPORT_PATH = ROOT / "ATLAS_SYNC_REPORT.md"

AUTO_INDEX_FILENAME = "AUTO_INDEX.md"

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
    "ATLAS_SYNC_REPORT.md",
    "CHANGE_IMPACT_REPORT.md",
    "DEPENDENCY_GRAPH.md",
    AUTO_INDEX_FILENAME,
}

SYNCABLE_ROOT_DIRECTORIES = {
    "07_KNOWLEDGE",
    "09_COLLECTION",
    "11_PUBLISHER",
}


@dataclass(frozen=True)
class InventoryDocument:
    path: str
    title: str
    document_id: str | None
    document_type: str | None
    status: str | None
    version: str | None
    dependencies: tuple[str, ...]
    tags: tuple[str, ...]
    products: tuple[str, ...]
    line_count: int
    size_bytes: int


@dataclass(frozen=True)
class SyncAction:
    action: str
    path: str
    reason: str
    applied: bool


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


def read_inventory() -> list[InventoryDocument]:
    if not INVENTORY_PATH.exists():
        raise FileNotFoundError(
            "ATLAS_INVENTORY.json não encontrado. "
            "Execute scripts/atlas_parser.py antes do Sync Engine."
        )

    payload = json.loads(
        INVENTORY_PATH.read_text(encoding="utf-8")
    )

    documents: list[InventoryDocument] = []

    for item in payload.get("documents", []):
        metadata = item.get("metadata") or {}
        path = str(item.get("path", "")).strip()

        if not path:
            continue

        documents.append(
            InventoryDocument(
                path=path,
                title=str(
                    metadata.get("title")
                    or item.get("filename")
                    or Path(path).stem
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
                version=clean_optional(
                    metadata.get("version")
                ),
                dependencies=clean_list(
                    metadata.get("dependencies")
                ),
                tags=clean_list(
                    metadata.get("tags")
                ),
                products=clean_list(
                    metadata.get("products")
                ),
                line_count=int(item.get("line_count") or 0),
                size_bytes=int(item.get("size_bytes") or 0),
            )
        )

    return sorted(
        documents,
        key=lambda document: document.path.lower(),
    )


def should_manage_directory(directory: Path) -> bool:
    try:
        relative = directory.relative_to(ROOT)
    except ValueError:
        return False

    if not relative.parts:
        return False

    if any(part in IGNORED_DIRECTORIES for part in relative.parts):
        return False

    return relative.parts[0] in SYNCABLE_ROOT_DIRECTORIES


def group_documents_by_directory(
    documents: list[InventoryDocument],
) -> dict[str, list[InventoryDocument]]:
    grouped: dict[str, list[InventoryDocument]] = defaultdict(list)

    for document in documents:
        path = Path(document.path)

        if path.name in IGNORED_FILES:
            continue

        directory = path.parent.as_posix()

        if directory == ".":
            continue

        directory_path = ROOT / directory

        if should_manage_directory(directory_path):
            grouped[directory].append(document)

    for directory, items in grouped.items():
        grouped[directory] = sorted(
            items,
            key=lambda document: document.title.lower(),
        )

    return dict(
        sorted(
            grouped.items(),
            key=lambda item: item[0].lower(),
        )
    )


def directory_title(directory: str) -> str:
    return Path(directory).name.replace("_", " ").replace("-", " — ")


def document_summary(document: InventoryDocument) -> list[str]:
    lines = [
        f"- [{document.title}]({Path(document.path).name})",
    ]

    details: list[str] = []

    if document.document_id:
        details.append(f"ID: `{document.document_id}`")

    if document.status:
        details.append(f"status: `{document.status}`")

    if document.version:
        details.append(f"versão: `{document.version}`")

    if document.document_type:
        details.append(f"tipo: `{document.document_type}`")

    if details:
        lines.append(f"  - {' · '.join(details)}")

    if document.dependencies:
        lines.append(
            "  - Dependências declaradas: "
            + ", ".join(f"`{item}`" for item in document.dependencies)
        )

    if document.products:
        lines.append(
            "  - Produtos relacionados: "
            + ", ".join(document.products)
        )

    return lines


def build_auto_index_content(
    directory: str,
    documents: list[InventoryDocument],
) -> str:
    lines = [
        f"# Índice automático — {directory_title(directory)}",
        "",
        "> Arquivo gerado automaticamente pelo EDI Atlas Sync Engine.",
        "",
        f"**Última sincronização:** {utc_timestamp()}",
        "",
        f"**Documentos nesta pasta:** {len(documents)}",
        "",
        "## Documentos",
        "",
    ]

    if not documents:
        lines.append("_Nenhum documento indexável encontrado._")
    else:
        for document in documents:
            lines.extend(document_summary(document))

    lines.extend(
        [
            "",
            "## Governança",
            "",
            "- Este índice é derivado e pode ser atualizado automaticamente.",
            "- Documentos autoritativos não são reescritos pelo Sync Engine.",
            "- Alterações de conteúdo estratégico exigem revisão humana.",
            "",
        ]
    )

    return "\n".join(lines)


def write_if_changed(
    path: Path,
    content: str,
    apply_changes: bool,
    reason: str,
) -> SyncAction:
    normalized = content.rstrip() + "\n"

    current = (
        path.read_text(encoding="utf-8")
        if path.exists()
        else None
    )

    if current == normalized:
        return SyncAction(
            action="sem alteração",
            path=path.relative_to(ROOT).as_posix(),
            reason="conteúdo já sincronizado",
            applied=False,
        )

    if apply_changes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(normalized, encoding="utf-8")

    return SyncAction(
        action="criar" if current is None else "atualizar",
        path=path.relative_to(ROOT).as_posix(),
        reason=reason,
        applied=apply_changes,
    )


def discover_existing_auto_indexes() -> set[Path]:
    return {
        path
        for path in ROOT.rglob(AUTO_INDEX_FILENAME)
        if path.is_file()
        and not any(
            part in IGNORED_DIRECTORIES
            for part in path.relative_to(ROOT).parts
        )
    }


def sync_directory_indexes(
    documents: list[InventoryDocument],
    apply_changes: bool,
) -> list[SyncAction]:
    grouped = group_documents_by_directory(documents)
    actions: list[SyncAction] = []
    expected_indexes: set[Path] = set()

    for directory, items in grouped.items():
        output_path = ROOT / directory / AUTO_INDEX_FILENAME
        expected_indexes.add(output_path)

        actions.append(
            write_if_changed(
                output_path,
                build_auto_index_content(directory, items),
                apply_changes,
                "sincronizar índice da pasta derivada",
            )
        )

    existing_indexes = discover_existing_auto_indexes()

    for obsolete in sorted(
        existing_indexes - expected_indexes,
        key=lambda path: path.as_posix().lower(),
    ):
        relative = obsolete.relative_to(ROOT).as_posix()

        if apply_changes:
            obsolete.unlink()

        actions.append(
            SyncAction(
                action="remover",
                path=relative,
                reason="índice automático sem pasta documental correspondente",
                applied=apply_changes,
            )
        )

    return actions


def read_impact_summary() -> list[str]:
    if not IMPACT_PATH.exists():
        return [
            "CHANGE_IMPACT_REPORT.md ainda não foi gerado."
        ]

    content = IMPACT_PATH.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lines: list[str] = []

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("- Total de documentos impactados:"):
            lines.append(stripped)
        elif stripped.startswith("- Exigem revisão humana:"):
            lines.append(stripped)
        elif stripped.startswith("- Podem ser sincronizados:"):
            lines.append(stripped)

    return lines or [
        "O relatório de impacto não contém resumo reconhecível."
    ]


def build_sync_report(
    actions: list[SyncAction],
    apply_changes: bool,
    documents: list[InventoryDocument],
) -> str:
    actionable = [
        action
        for action in actions
        if action.action != "sem alteração"
    ]

    lines = [
        "# Relatório de Sincronização do EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo EDI Atlas Sync Engine.",
        "",
        f"**Executado em:** {utc_timestamp()}",
        "",
        f"**Modo:** `{'APPLY' if apply_changes else 'DRY-RUN'}`",
        "",
        f"**Documentos analisados:** {len(documents)}",
        "",
        f"**Ações identificadas:** {len(actionable)}",
        "",
        "## Resumo do impacto",
        "",
    ]

    lines.extend(read_impact_summary())

    lines.extend(
        [
            "",
            "## Ações",
            "",
        ]
    )

    if actionable:
        for action in actionable:
            status = "aplicada" if action.applied else "simulada"
            lines.append(
                f"- **{action.action}** `{action.path}` "
                f"— {action.reason} — {status}"
            )
    else:
        lines.append(
            "- Nenhuma alteração de sincronização foi necessária."
        )

    lines.extend(
        [
            "",
            "## Limites de segurança",
            "",
            "- O Sync Engine não reescreve documentos autoritativos.",
            "- O Sync Engine cria e atualiza apenas arquivos derivados controlados.",
            "- Conteúdo estratégico exige revisão humana.",
            "- Os arquivos `AUTO_INDEX.md` podem ser recriados a qualquer momento.",
            "",
        ]
    )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sincroniza índices derivados das subpastas "
            "do EDI Atlas."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as alterações. Sem esta opção, executa dry-run.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Força o modo de simulação.",
    )

    return parser.parse_args()


def resolve_apply_mode(args: argparse.Namespace) -> bool:
    if args.dry_run:
        return False

    if args.apply:
        return True

    environment_value = os.getenv(
        "EDI_ATLAS_SYNC_APPLY",
        "",
    ).strip().lower()

    return environment_value in {
        "1",
        "true",
        "yes",
        "sim",
        "on",
    }


def main() -> int:
    try:
        args = parse_args()
        apply_changes = resolve_apply_mode(args)
        documents = read_inventory()

        actions = sync_directory_indexes(
            documents=documents,
            apply_changes=apply_changes,
        )

        SYNC_REPORT_PATH.write_text(
            build_sync_report(
                actions=actions,
                apply_changes=apply_changes,
                documents=documents,
            ).rstrip() + "\n",
            encoding="utf-8",
        )

        print("EDI Atlas Sync Engine concluído.")
        print(
            f"Modo: {'APPLY' if apply_changes else 'DRY-RUN'}"
        )
        print(f"Documentos analisados: {len(documents)}")
        print(
            "Ações identificadas: "
            f"{sum(1 for action in actions if action.action != 'sem alteração')}"
        )
        print(f"Relatório: {SYNC_REPORT_PATH.name}")

        return 0

    except Exception as error:
        print(
            f"Falha no Sync Engine do EDI Atlas: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
