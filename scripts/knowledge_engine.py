from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"

RUN_REPORT_PATH = ROOT / "KNOWLEDGE_ENGINE_REPORT.md"
RUN_REPORT_JSON_PATH = ROOT / "KNOWLEDGE_ENGINE_REPORT.json"

DEFAULT_MODULES = (
    "atlas_automation.py",
    "atlas_parser.py",
    "atlas_dependency_engine.py",
    "atlas_sync_engine.py",
    "atlas_parser.py",
    "atlas_validation_engine.py",
)

CRITICAL_MODULES = {
    "atlas_parser.py",
    "atlas_dependency_engine.py",
    "atlas_sync_engine.py",
    "atlas_validation_engine.py",
}

GENERATED_FILES = (
    "README.md",
    "STATUS_OFICIAL.md",
    "ATLAS_INDEX.md",
    "ATLAS_VALIDATION_REPORT.md",
    "ATLAS_INVENTORY.md",
    "ATLAS_INVENTORY.json",
    "DEPENDENCY_GRAPH.md",
    "CHANGE_IMPACT_REPORT.md",
    "ATLAS_SYNC_REPORT.md",
    "ATLAS_HEALTH.md",
    "METADATA_REPORT.md",
    "BROKEN_LINKS.md",
    "DUPLICATED_IDS.md",
    "KNOWLEDGE_ENGINE_REPORT.md",
    "KNOWLEDGE_ENGINE_REPORT.json",
)


@dataclass(frozen=True)
class ModuleResult:
    module: str
    command: list[str]
    started_at: str
    finished_at: str
    duration_seconds: float
    return_code: int
    status: str
    stdout: str
    stderr: str
    critical: bool


@dataclass(frozen=True)
class EngineSummary:
    generated_at: str
    mode: str
    success: bool
    total_modules: int
    successful_modules: int
    failed_modules: int
    skipped_modules: int
    duration_seconds: float
    generated_files_present: list[str]
    generated_files_missing: list[str]
    module_results: list[ModuleResult]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(value: datetime | None = None) -> str:
    current = value or utc_now()
    return current.strftime("%Y-%m-%d %H:%M:%S UTC")


def compact_output(text: str, limit: int = 12000) -> str:
    normalized = text.strip()

    if len(normalized) <= limit:
        return normalized

    omitted = len(normalized) - limit

    return (
        normalized[:limit]
        + "\n\n"
        + f"[saída truncada: {omitted} caracteres omitidos]"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Orquestra os módulos oficiais do EDI Knowledge Engine."
        )
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Executa o Sync Engine em modo de simulação, "
            "sem alterar índices das subpastas."
        ),
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help=(
            "Continua executando os módulos após falha crítica."
        ),
    )

    parser.add_argument(
        "--skip-syntax-check",
        action="store_true",
        help="Ignora a validação de sintaxe dos módulos.",
    )

    parser.add_argument(
        "--only",
        nargs="*",
        help=(
            "Executa apenas os módulos informados. "
            "Exemplo: --only atlas_parser.py atlas_validation_engine.py"
        ),
    )

    return parser.parse_args()


def validate_script_exists(module: str) -> Path:
    path = SCRIPTS_DIR / module

    if not path.is_file():
        raise FileNotFoundError(
            f"Módulo obrigatório não encontrado: {path.relative_to(ROOT)}"
        )

    return path


def validate_syntax(modules: Sequence[str]) -> None:
    errors: list[str] = []

    for module in modules:
        script_path = validate_script_exists(module)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(script_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            details = result.stderr.strip() or result.stdout.strip()
            errors.append(
                f"{module}: {details or 'erro de sintaxe não detalhado'}"
            )

    if errors:
        joined = "\n\n".join(errors)

        raise RuntimeError(
            "Falha na validação de sintaxe:\n\n"
            f"{joined}"
        )


def command_for_module(
    module: str,
    dry_run: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(SCRIPTS_DIR / module),
    ]

    if module == "atlas_sync_engine.py":
        command.append(
            "--dry-run"
            if dry_run
            else "--apply"
        )

    return command


def run_module(
    module: str,
    dry_run: bool,
) -> ModuleResult:
    started = utc_now()
    started_clock = time.perf_counter()
    command = command_for_module(
        module=module,
        dry_run=dry_run,
    )

    environment = os.environ.copy()

    if module == "atlas_sync_engine.py":
        environment["EDI_ATLAS_SYNC_APPLY"] = (
            "false"
            if dry_run
            else "true"
        )

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )

    finished = utc_now()
    duration = time.perf_counter() - started_clock

    return ModuleResult(
        module=module,
        command=command,
        started_at=utc_text(started),
        finished_at=utc_text(finished),
        duration_seconds=round(duration, 3),
        return_code=result.returncode,
        status=(
            "success"
            if result.returncode == 0
            else "failed"
        ),
        stdout=compact_output(result.stdout),
        stderr=compact_output(result.stderr),
        critical=module in CRITICAL_MODULES,
    )


def generated_files_status() -> tuple[list[str], list[str]]:
    present: list[str] = []
    missing: list[str] = []

    for relative in GENERATED_FILES:
        path = ROOT / relative

        if path.exists():
            present.append(relative)
        else:
            missing.append(relative)

    return present, missing


def build_markdown_report(
    summary: EngineSummary,
) -> str:
    lines = [
        "# Relatório do EDI Knowledge Engine",
        "",
        "> Arquivo gerado automaticamente pelo orquestrador oficial do Atlas.",
        "",
        f"**Executado em:** {summary.generated_at}",
        "",
        f"**Modo:** `{summary.mode}`",
        "",
        f"**Resultado geral:** `{'SUCESSO' if summary.success else 'FALHA'}`",
        "",
        f"**Duração total:** {summary.duration_seconds:.3f} segundos",
        "",
        "## Resumo",
        "",
        f"- Módulos executados: **{summary.total_modules}**",
        f"- Módulos concluídos: **{summary.successful_modules}**",
        f"- Módulos com falha: **{summary.failed_modules}**",
        f"- Módulos ignorados: **{summary.skipped_modules}**",
        "",
        "## Ordem oficial de execução",
        "",
    ]

    for index, result in enumerate(
        summary.module_results,
        start=1,
    ):
        lines.append(
            f"{index}. `{result.module}` — "
            f"**{result.status.upper()}**"
        )

    lines.extend(
        [
            "",
            "## Resultados por módulo",
            "",
        ]
    )

    for result in summary.module_results:
        lines.extend(
            [
                f"### `{result.module}`",
                "",
                f"- Status: **{result.status}**",
                f"- Crítico: **{'sim' if result.critical else 'não'}**",
                f"- Código de saída: `{result.return_code}`",
                f"- Início: {result.started_at}",
                f"- Término: {result.finished_at}",
                f"- Duração: {result.duration_seconds:.3f} segundos",
                "",
                "#### Comando",
                "",
                "```text",
                " ".join(result.command),
                "```",
                "",
            ]
        )

        if result.stdout:
            lines.extend(
                [
                    "#### Saída padrão",
                    "",
                    "```text",
                    result.stdout,
                    "```",
                    "",
                ]
            )

        if result.stderr:
            lines.extend(
                [
                    "#### Saída de erro",
                    "",
                    "```text",
                    result.stderr,
                    "```",
                    "",
                ]
            )

    lines.extend(
        [
            "## Arquivos gerados presentes",
            "",
        ]
    )

    if summary.generated_files_present:
        lines.extend(
            f"- `{path}`"
            for path in summary.generated_files_present
        )
    else:
        lines.append("- Nenhum arquivo gerado foi encontrado.")

    lines.extend(
        [
            "",
            "## Arquivos gerados ausentes",
            "",
        ]
    )

    if summary.generated_files_missing:
        lines.extend(
            f"- `{path}`"
            for path in summary.generated_files_missing
        )
    else:
        lines.append("- Nenhum arquivo esperado está ausente.")

    lines.extend(
        [
            "",
            "## Governança",
            "",
            "- O Knowledge Engine não reescreve documentos autoritativos.",
            "- O Sync Engine altera apenas documentos derivados controlados.",
            "- Falhas críticas interrompem a execução, salvo quando "
            "`--continue-on-error` estiver ativo.",
            "- O relatório JSON pode ser consumido por futuras APIs e dashboards.",
            "",
        ]
    )

    return "\n".join(lines)


def write_reports(summary: EngineSummary) -> None:
    RUN_REPORT_PATH.write_text(
        build_markdown_report(summary).rstrip() + "\n",
        encoding="utf-8",
    )

    RUN_REPORT_JSON_PATH.write_text(
        json.dumps(
            asdict(summary),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def resolve_modules(args: argparse.Namespace) -> tuple[str, ...]:
    if not args.only:
        return DEFAULT_MODULES

    requested = tuple(
        module.strip()
        for module in args.only
        if module.strip()
    )

    if not requested:
        raise ValueError(
            "A opção --only foi informada sem módulos válidos."
        )

    return requested


def execute_engine(
    modules: Sequence[str],
    dry_run: bool,
    continue_on_error: bool,
) -> EngineSummary:
    engine_started = utc_now()
    engine_clock = time.perf_counter()
    results: list[ModuleResult] = []
    skipped = 0

    for index, module in enumerate(modules):
        validate_script_exists(module)

        print(
            f"[{index + 1}/{len(modules)}] "
            f"Executando {module}..."
        )

        result = run_module(
            module=module,
            dry_run=dry_run,
        )

        results.append(result)

        if result.status == "success":
            print(
                f"{module}: sucesso "
                f"({result.duration_seconds:.3f}s)"
            )
            continue

        print(
            f"{module}: falha "
            f"(código {result.return_code})",
            file=sys.stderr,
        )

        if result.critical and not continue_on_error:
            skipped = len(modules) - index - 1
            break

    present, missing = generated_files_status()
    duration = time.perf_counter() - engine_clock

    failed = sum(
        1
        for result in results
        if result.status == "failed"
    )

    successful = sum(
        1
        for result in results
        if result.status == "success"
    )

    success = failed == 0 and skipped == 0

    return EngineSummary(
        generated_at=utc_text(engine_started),
        mode="DRY-RUN" if dry_run else "APPLY",
        success=success,
        total_modules=len(results),
        successful_modules=successful,
        failed_modules=failed,
        skipped_modules=skipped,
        duration_seconds=round(duration, 3),
        generated_files_present=present,
        generated_files_missing=missing,
        module_results=results,
    )


def main() -> int:
    try:
        args = parse_args()
        modules = resolve_modules(args)

        if not args.skip_syntax_check:
            print("Validando sintaxe dos módulos...")
            validate_syntax(modules)
            print("Sintaxe validada com sucesso.")

        summary = execute_engine(
            modules=modules,
            dry_run=args.dry_run,
            continue_on_error=args.continue_on_error,
        )

        write_reports(summary)

        print("")
        print("EDI Knowledge Engine concluído.")
        print(f"Modo: {summary.mode}")
        print(
            f"Resultado: "
            f"{'SUCESSO' if summary.success else 'FALHA'}"
        )
        print(
            f"Módulos concluídos: "
            f"{summary.successful_modules}"
        )
        print(
            f"Módulos com falha: "
            f"{summary.failed_modules}"
        )
        print(
            f"Módulos ignorados: "
            f"{summary.skipped_modules}"
        )
        print(
            f"Relatório: {RUN_REPORT_PATH.name}"
        )
        print(
            f"Relatório JSON: {RUN_REPORT_JSON_PATH.name}"
        )

        return 0 if summary.success else 1

    except Exception as error:
        fallback = EngineSummary(
            generated_at=utc_text(),
            mode="INDEFINIDO",
            success=False,
            total_modules=0,
            successful_modules=0,
            failed_modules=1,
            skipped_modules=0,
            duration_seconds=0.0,
            generated_files_present=[],
            generated_files_missing=list(GENERATED_FILES),
            module_results=[],
        )

        try:
            write_reports(fallback)
        except Exception:
            pass

        print(
            f"Falha no EDI Knowledge Engine: {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
