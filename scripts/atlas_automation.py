from __future__ import annotations

import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

README_PATH = ROOT / "README.md"
STATUS_PATH = ROOT / "STATUS_OFICIAL.md"
INDEX_PATH = ROOT / "ATLAS_INDEX.md"
REPORT_PATH = ROOT / "ATLAS_VALIDATION_REPORT.md"

STATUS_START = "<!-- EDI_ATLAS_STATUS_START -->"
STATUS_END = "<!-- EDI_ATLAS_STATUS_END -->"

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

SECTIONS = [
    {
        "id": "foundation",
        "title": "Fundação",
        "aliases": ["00_FOUNDATION", "00_FUNDAÇÃO", "00_FUNDACAO"],
        "required": True,
    },
    {
        "id": "framework",
        "title": "Framework EDI",
        "aliases": ["01_FRAMEWORK_EDI", "01_FRAMEWORK-EDI"],
        "required": True,
    },
    {
        "id": "eios",
        "title": "EIOS",
        "aliases": ["02_EIOS"],
        "required": True,
    },
    {
        "id": "core",
        "title": "Core Compartilhado",
        "aliases": ["03_CORE", "03_CORE_COMPARTILHADO"],
        "required": False,
    },
    {
        "id": "products",
        "title": "Produtos",
        "aliases": ["04_PRODUTOS", "04_PRODUCTS"],
        "required": False,
    },
    {
        "id": "governance",
        "title": "Governança",
        "aliases": ["05_GOVERNANÇA", "05_GOVERNANCA", "05_GOVERNANCE"],
        "required": False,
    },
    {
        "id": "architecture",
        "title": "Arquitetura",
        "aliases": ["06_ARQUITETURA", "06_ARCHITECTURE"],
        "required": False,
    },
    {
        "id": "knowledge",
        "title": "Conhecimento",
        "aliases": ["07_KNOWLEDGE", "07_CONHECIMENTO"],
        "required": True,
    },
    {
        "id": "diagrams",
        "title": "Diagramas",
        "aliases": ["08_DIAGRAMS", "08_DIAGRAMAS", "DIAGRAMS", "DIAGRAMAS"],
        "required": False,
    },
    {
        "id": "collection",
        "title": "Coleção",
        "aliases": ["09_COLLECTION", "09_COLEÇÃO", "09_COLECAO"],
        "required": True,
    },
    {
        "id": "roadmap",
        "title": "Roadmap",
        "aliases": ["10_ROADMAP"],
        "required": False,
    },
    {
        "id": "publisher",
        "title": "Editor e Publisher",
        "aliases": ["11_EDITOR", "11_PUBLISHER"],
        "required": True,
    },
    {
        "id": "adr",
        "title": "ADRs",
        "aliases": ["ADR", "ADRS"],
        "required": True,
    },
    {
        "id": "decisions",
        "title": "Decisões",
        "aliases": ["DECISIONS", "DECISÕES", "DECISOES"],
        "required": True,
    },
]


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def root_directories() -> list[Path]:
    return sorted(
        [
            path
            for path in ROOT.iterdir()
            if path.is_dir() and path.name not in IGNORED_DIRECTORIES
        ],
        key=lambda item: normalize(item.name),
    )


def find_directory(aliases: list[str]) -> Path | None:
    normalized_aliases = {normalize(alias) for alias in aliases}

    for directory in root_directories():
        if normalize(directory.name) in normalized_aliases:
            return directory

    return None


def markdown_files(directory: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in directory.rglob("*.md")
            if path.is_file()
            and path.name not in IGNORED_FILES
            and not any(
                part in IGNORED_DIRECTORIES
                for part in path.relative_to(ROOT).parts
            )
        ],
        key=lambda item: normalize(relative(item)),
    )


def markdown_title(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.stem.replace("_", " ").replace("-", " — ")

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()

    return path.stem.replace("_", " ").replace("-", " — ")


def default_status_content() -> str:
    lines = [
        "# Status Oficial da EduData IA",
        "",
        "A EduData IA é uma **Plataforma Operacional de Inteligência Educacional**.",
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
        "## Estado atual",
        "",
        "- A plataforma já existe e está em evolução.",
        "- A Home Estratégica está implementada.",
        "- A infraestrutura utiliza GitHub, Vercel, Supabase, Next.js e FastAPI.",
        "- A EduData Academy possui estrutura e inscrição integradas ao Supabase.",
        "- A Agenda Inteligente EDI é a prioridade técnica atual.",
        "- O Professor Digital é a principal porta de entrada comercial e formativa.",
        "- O BackOffice único e o Experience Manager são diretrizes oficiais.",
        "- O EDI Atlas é a fonte oficial do patrimônio intelectual.",
        "- O EDI Publisher e a EduData Press integram a infraestrutura editorial.",
        "- O template LaTeX da EduData Press está em homologação.",
        "",
        "## Prioridade operacional",
        "",
        "```text",
        "Agenda Inteligente EDI",
        "        ↓",
        "Segurança e autenticação",
        "        ↓",
        "BackOffice unificado",
        "        ↓",
        "Núcleo operacional do EIOS",
        "        ↓",
        "Professor Digital",
        "        ↓",
        "EduData Academy",
        "        ↓",
        "EduData Analytics",
        "        ↓",
        "SGPA",
        "        ↓",
        "Observatório da Educação",
        "        ↓",
        "Comunidade EduData IA",
        "```",
        "",
        "## Regra de evolução",
        "",
        "```text",
        "Auditoria",
        "    ↓",
        "Mapeamento",
        "    ↓",
        "Integração",
        "    ↓",
        "Evolução",
        "    ↓",
        "Build",
        "    ↓",
        "Deploy",
        "    ↓",
        "Validação",
        "    ↓",
        "Documentação",
        "```",
        "",
        "Não reconstruir produtos existentes, não criar soluções paralelas e não alterar a arquitetura oficial sem decisão formal registrada no EDI Atlas.",
        "",
    ]

    return "\n".join(lines)


def ensure_status_file() -> None:
    if not STATUS_PATH.exists():
        STATUS_PATH.write_text(
            default_status_content(),
            encoding="utf-8",
        )


def build_index() -> tuple[str, dict[str, int], set[Path]]:
    lines = [
        "# Índice Oficial do EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo GitHub Actions.",
        "",
        f"**Última atualização automática:** {timestamp()}",
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
    indexed_files: set[Path] = set()

    for section in SECTIONS:
        lines.extend([f"## {section['title']}", ""])

        directory = find_directory(section["aliases"])

        if directory is None:
            statistics[section["id"]] = 0
            aliases = "`, `".join(section["aliases"])
            lines.extend([
                f"> Diretório não encontrado. Nomes aceitos: `{aliases}`.",
                "",
            ])
            continue

        files = markdown_files(directory)
        indexed_files.update(files)
        statistics[section["id"]] = len(files)

        lines.extend([
            f"**Diretório:** `{relative(directory)}`",
            "",
        ])

        if not files:
            lines.extend([
                "_Nenhum documento Markdown encontrado._",
                "",
            ])
            continue

        for file_path in files:
            lines.append(
                f"- [{markdown_title(file_path)}]({relative(file_path)})"
            )

        lines.append("")

    all_docs = {
        path
        for path in ROOT.rglob("*.md")
        if path.is_file()
        and path.name not in IGNORED_FILES
        and not any(
            part in IGNORED_DIRECTORIES
            for part in path.relative_to(ROOT).parts
        )
    }

    excluded = {
        README_PATH,
        STATUS_PATH,
        INDEX_PATH,
        REPORT_PATH,
    }

    additional = sorted(
        [
            path
            for path in all_docs
            if path not in indexed_files and path not in excluded
        ],
        key=lambda item: normalize(relative(item)),
    )

    if additional:
        lines.extend(["## Outros documentos", ""])

        for file_path in additional:
            lines.append(
                f"- [{markdown_title(file_path)}]({relative(file_path)})"
            )

        lines.append("")

    total_documents = len(indexed_files) + len(additional)

    lines.extend([
        "## Resumo quantitativo",
        "",
        f"- Seções oficiais previstas: **{len(SECTIONS)}**",
        f"- Documentos indexados: **{total_documents}**",
        f"- Documentos adicionais: **{len(additional)}**",
        "",
    ])

    return "\n".join(lines), statistics, indexed_files


def status_block() -> str:
    content = STATUS_PATH.read_text(encoding="utf-8").strip()

    if content.startswith("# "):
        content = "\n".join(content.splitlines()[1:]).strip()

    return "\n".join([
        STATUS_START,
        "",
        "## Status oficial da EduData IA",
        "",
        content,
        "",
        STATUS_END,
    ])


def update_readme() -> None:
    if README_PATH.exists():
        content = README_PATH.read_text(encoding="utf-8")
    else:
        content = (
            "# EDI Atlas\n\n"
            "Patrimônio intelectual oficial da EduData IA.\n"
        )

    block = status_block()

    pattern = re.compile(
        re.escape(STATUS_START)
        + r".*?"
        + re.escape(STATUS_END),
        re.DOTALL,
    )

    if pattern.search(content):
        updated = pattern.sub(block, content)
    else:
        updated = content.rstrip() + "\n\n" + block + "\n"

    README_PATH.write_text(updated, encoding="utf-8")


def validate_structure(
    statistics: dict[str, int],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for section in SECTIONS:
        directory = find_directory(section["aliases"])

        if directory is None:
            message = (
                f"Diretório da seção '{section['title']}' não encontrado. "
                f"Nomes aceitos: {', '.join(section['aliases'])}."
            )

            if section["required"]:
                errors.append(message)
            else:
                warnings.append(message)

            continue

        if statistics.get(section["id"], 0) == 0:
            warnings.append(
                f"A seção '{section['title']}' existe, mas não contém documentos Markdown."
            )

    return errors, warnings


def build_report(
    errors: list[str],
    warnings: list[str],
    statistics: dict[str, int],
) -> str:
    result = "APROVADO" if not errors else "REPROVADO"

    lines = [
        "# Relatório de Validação do EDI Atlas",
        "",
        "> Arquivo gerado automaticamente pelo GitHub Actions.",
        "",
        f"**Executado em:** {timestamp()}",
        "",
        f"**Resultado:** `{result}`",
        "",
        "## Documentos por seção",
        "",
    ]

    for section in SECTIONS:
        lines.append(
            f"- {section['title']}: **{statistics.get(section['id'], 0)}**"
        )

    lines.extend(["", "## Erros", ""])

    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- Nenhum erro estrutural encontrado.")

    lines.extend(["", "## Avisos", ""])

    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- Nenhum aviso encontrado.")

    lines.extend([
        "",
        "## Arquitetura obrigatória",
        "",
        "```text",
        "Framework EDI",
        "        ↓",
        "EIOS",
        "        ↓",
        "Core Compartilhado",
        "        ↓",
        "Produtos Especializados",
        "```",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    try:
        ensure_status_file()

        index_content, statistics, _ = build_index()
        errors, warnings = validate_structure(statistics)

        INDEX_PATH.write_text(
            index_content.strip() + "\n",
            encoding="utf-8",
        )

        update_readme()

        REPORT_PATH.write_text(
            build_report(
                errors=errors,
                warnings=warnings,
                statistics=statistics,
            ).strip() + "\n",
            encoding="utf-8",
        )

        print("EDI Atlas processado com sucesso.")
        print(f"Índice: {relative(INDEX_PATH)}")
        print(f"Status: {relative(STATUS_PATH)}")
        print(f"Relatório: {relative(REPORT_PATH)}")
        print(f"README: {relative(README_PATH)}")

        if warnings:
            print("\nAvisos encontrados:")
            for warning in warnings:
                print(f"- {warning}")

        if errors:
            print("\nErros estruturais encontrados:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)

            return 1

        return 0

    except Exception as error:
        print(
            f"Falha inesperada na automação do EDI Atlas: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
