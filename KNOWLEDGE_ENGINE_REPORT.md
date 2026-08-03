# Relatório do EDI Knowledge Engine

> Arquivo gerado automaticamente pelo orquestrador oficial do Atlas.

**Executado em:** 2026-08-03 12:17:27 UTC

**Modo:** `APPLY`

**Resultado geral:** `SUCESSO`

**Duração total:** 0.478 segundos

## Resumo

- Módulos executados: **6**
- Módulos concluídos: **6**
- Módulos com falha: **0**
- Módulos ignorados: **0**

## Ordem oficial de execução

1. `atlas_automation.py` — **SUCCESS**
2. `atlas_parser.py` — **SUCCESS**
3. `atlas_dependency_engine.py` — **SUCCESS**
4. `atlas_sync_engine.py` — **SUCCESS**
5. `atlas_parser.py` — **SUCCESS**
6. `atlas_validation_engine.py` — **SUCCESS**

## Resultados por módulo

### `atlas_automation.py`

- Status: **success**
- Crítico: **não**
- Código de saída: `0`
- Início: 2026-08-03 12:17:27 UTC
- Término: 2026-08-03 12:17:27 UTC
- Duração: 0.093 segundos

#### Comando

```text
/opt/hostedtoolcache/Python/3.13.14/x64/bin/python /home/runner/work/edudata-ia-edi-atlas/edudata-ia-edi-atlas/scripts/atlas_automation.py
```

#### Saída padrão

```text
EDI Atlas processado com sucesso.
Índice: ATLAS_INDEX.md
Status: STATUS_OFICIAL.md
Relatório: ATLAS_VALIDATION_REPORT.md
README: README.md

Avisos encontrados:
- Diretório da seção 'Core Compartilhado' não encontrado. Nomes aceitos: 03_CORE, 03_CORE_COMPARTILHADO.
- Diretório da seção 'Produtos' não encontrado. Nomes aceitos: 04_PRODUTOS, 04_PRODUCTS.
- Diretório da seção 'Governança' não encontrado. Nomes aceitos: 05_GOVERNANÇA, 05_GOVERNANCA, 05_GOVERNANCE.
- Diretório da seção 'Arquitetura' não encontrado. Nomes aceitos: 06_ARQUITETURA, 06_ARCHITECTURE.
- A seção 'Diagramas' existe, mas não contém documentos Markdown.
- Diretório da seção 'Roadmap' não encontrado. Nomes aceitos: 10_ROADMAP.
```

### `atlas_parser.py`

- Status: **success**
- Crítico: **sim**
- Código de saída: `0`
- Início: 2026-08-03 12:17:27 UTC
- Término: 2026-08-03 12:17:27 UTC
- Duração: 0.107 segundos

#### Comando

```text
/opt/hostedtoolcache/Python/3.13.14/x64/bin/python /home/runner/work/edudata-ia-edi-atlas/edudata-ia-edi-atlas/scripts/atlas_parser.py
```

#### Saída padrão

```text
Varredura completa do EDI Atlas concluída.
Documentos encontrados: 83
Inventário Markdown: ATLAS_INVENTORY.md
Inventário JSON: ATLAS_INVENTORY.json
```

### `atlas_dependency_engine.py`

- Status: **success**
- Crítico: **sim**
- Código de saída: `0`
- Início: 2026-08-03 12:17:27 UTC
- Término: 2026-08-03 12:17:27 UTC
- Duração: 0.075 segundos

#### Comando

```text
/opt/hostedtoolcache/Python/3.13.14/x64/bin/python /home/runner/work/edudata-ia-edi-atlas/edudata-ia-edi-atlas/scripts/atlas_dependency_engine.py
```

#### Saída padrão

```text
Análise de dependências do EDI Atlas concluída.
Documentos analisados: 83
Relações identificadas: 2259
Arquivos alterados: 10
Arquivo gerado: DEPENDENCY_GRAPH.md
Arquivo gerado: CHANGE_IMPACT_REPORT.md
```

### `atlas_sync_engine.py`

- Status: **success**
- Crítico: **sim**
- Código de saída: `0`
- Início: 2026-08-03 12:17:27 UTC
- Término: 2026-08-03 12:17:27 UTC
- Duração: 0.061 segundos

#### Comando

```text
/opt/hostedtoolcache/Python/3.13.14/x64/bin/python /home/runner/work/edudata-ia-edi-atlas/edudata-ia-edi-atlas/scripts/atlas_sync_engine.py --apply
```

#### Saída padrão

```text
EDI Atlas Sync Engine concluído.
Modo: APPLY
Documentos analisados: 83
Ações identificadas: 3
Relatório: ATLAS_SYNC_REPORT.md
```

### `atlas_parser.py`

- Status: **success**
- Crítico: **sim**
- Código de saída: `0`
- Início: 2026-08-03 12:17:27 UTC
- Término: 2026-08-03 12:17:27 UTC
- Duração: 0.081 segundos

#### Comando

```text
/opt/hostedtoolcache/Python/3.13.14/x64/bin/python /home/runner/work/edudata-ia-edi-atlas/edudata-ia-edi-atlas/scripts/atlas_parser.py
```

#### Saída padrão

```text
Varredura completa do EDI Atlas concluída.
Documentos encontrados: 83
Inventário Markdown: ATLAS_INVENTORY.md
Inventário JSON: ATLAS_INVENTORY.json
```

### `atlas_validation_engine.py`

- Status: **success**
- Crítico: **sim**
- Código de saída: `0`
- Início: 2026-08-03 12:17:27 UTC
- Término: 2026-08-03 12:17:27 UTC
- Duração: 0.060 segundos

#### Comando

```text
/opt/hostedtoolcache/Python/3.13.14/x64/bin/python /home/runner/work/edudata-ia-edi-atlas/edudata-ia-edi-atlas/scripts/atlas_validation_engine.py
```

#### Saída padrão

```text
EDI Atlas Validation Engine concluído.
Documentos analisados: 83
Erros: 164
Avisos: 273
Informações: 7
Saúde do Atlas: 0/100
```

## Arquivos gerados presentes

- `README.md`
- `STATUS_OFICIAL.md`
- `ATLAS_INDEX.md`
- `ATLAS_VALIDATION_REPORT.md`
- `ATLAS_INVENTORY.md`
- `ATLAS_INVENTORY.json`
- `DEPENDENCY_GRAPH.md`
- `CHANGE_IMPACT_REPORT.md`
- `ATLAS_SYNC_REPORT.md`
- `ATLAS_HEALTH.md`
- `METADATA_REPORT.md`
- `BROKEN_LINKS.md`
- `DUPLICATED_IDS.md`
- `KNOWLEDGE_ENGINE_REPORT.md`
- `KNOWLEDGE_ENGINE_REPORT.json`

## Arquivos gerados ausentes

- Nenhum arquivo esperado está ausente.

## Governança

- O Knowledge Engine não reescreve documentos autoritativos.
- O Sync Engine altera apenas documentos derivados controlados.
- Falhas críticas interrompem a execução, salvo quando `--continue-on-error` estiver ativo.
- O relatório JSON pode ser consumido por futuras APIs e dashboards.
