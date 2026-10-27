# ADR-0007 — Plano de Remediação da Qualidade Documental do EDI Atlas

- **ID:** ADR-0007
- **Status:** proposed
- **Versão:** 1.0
- **Data:** 2026-10-27
- **Tipo:** decisão de governança documental
- **Responsável:** Governança EduData IA
- **Revisão:** pendente de aprovação humana
- **Tags:** EDI Atlas, qualidade documental, metadados, validação, governança

## Contexto

A execução registrada em `KNOWLEDGE_ENGINE_REPORT.md` em 2026-10-27 concluiu os seis módulos do orquestrador sem falha de execução. Entretanto, o Validation Engine reportou 171 erros, 273 avisos, 7 informações e pontuação de saúde de 0/100 em 84 documentos.

O relatório de saúde agrupa ocorrências principalmente em metadados (440 ocorrências), além de documentos órfãos (7) e duplicidade (4). O relatório de links internos não identificou links quebrados. A contagem de ocorrências por categoria não equivale à contagem de documentos: um documento pode gerar vários apontamentos.

A execução bem-sucedida dos scripts comprova a execução técnica, mas não a qualidade ou aprovação do conteúdo documental.

## Decisão proposta

Adotar remediação incremental, rastreável e revisada por humanos, sem preencher metadados factuais por suposição e sem alterar em lote documentos autoritativos.

## Achado técnico confirmado: contrato de metadados divergente

A inspeção do validador e dos documentos de referência identificou uma incompatibilidade entre o contrato exigido por `scripts/atlas_validation_engine.py` e o padrão documental já registrado em `00_FOUNDATION/ORG-010_DOCUMENTATION_STANDARD.md` e usado, por exemplo, em `01_FRAMEWORK_EDI/FW-001_FRAMEWORK.md`.

O validador exige `document_id`, `author`, `reviewed`, `document_type` e `tags`; documentos existentes usam campos como `id`, `owner`, `maintainer`, `classification`, `created` e `updated`. Isso explica parte importante dos apontamentos e exige revisão do contrato antes de editar dezenas de documentos.

**Não se deve assumir equivalência automática para todos os campos.** Em particular, `updated` não comprova revisão humana e `maintainer` não necessariamente identifica o autor original. A correção recomendada é harmonizar o validador com o padrão oficial, definindo aliases seguros e mantendo campos sem equivalência como pendências explícitas, após testes com documentos de cada classe.

### Fase 1 — Diagnóstico reproduzível

1. Preservar os relatórios gerados pelo Validation Engine como linha de base.
2. Agrupar ocorrências por categoria, caminho, severidade e tipo de metadado ausente.
3. Distinguir falhas reais de conteúdo de limitações ou regras excessivamente rígidas do validador.
4. Não tratar arquivos gerados automaticamente como documentos autoritativos.

### Fase 2 — Contrato de metadados

1. Confirmar o esquema oficial de metadados e os valores permitidos para `status`, `document_type` e `reviewed`.
2. Definir quais campos são obrigatórios para cada classe documental.
3. Definir tratamento específico para índices automáticos, relatórios, documentos históricos e rascunhos.
4. Não marcar um documento como `approved` ou `official` sem aprovação explícita.
5. Não preencher `author` ou `reviewed` com valores inventados. Quando desconhecidos, registrar a pendência conforme o padrão que vier a ser aprovado.

### Fase 3 — Correção por lotes pequenos

1. Começar pelos documentos autoritativos em `00_FOUNDATION/`, `01_FRAMEWORK_EDI/`, `02_EIOS/`, `ADR/` e `DECISIONS/`.
2. Atualizar lotes pequenos e revisar o diff antes de cada commit.
3. Preservar o conteúdo semântico original; a primeira rodada deve corrigir metadados e referências, não reescrever decisões.
4. Manter um registro dos documentos corrigidos, pendentes e rejeitados na revisão.

### Fase 4 — Estrutura e taxonomia

1. Avaliar os avisos de seções ausentes emitidos por `atlas_automation.py`.
2. Antes de criar diretórios, verificar se o conteúdo correspondente já existe sob outro nome ou seção.
3. Não criar diretórios vazios apenas para silenciar avisos.
4. Resolver documentos órfãos e duplicidades com revisão da origem e da autoridade de cada documento.

### Fase 5 — Critérios de saída

A remediação será considerada concluída somente quando:

- os documentos autoritativos tiverem metadados consistentes com o contrato aprovado;
- não houver aprovações ou autoria fabricadas;
- links, IDs e dependências tiverem sido revalidados;
- a pontuação e as ocorrências forem recalculadas por uma nova execução;
- os relatórios atualizados forem revisados;
- a governança humana aprovar o resultado.

## Salvaguardas

- O Sync Engine deve continuar restrito às áreas configuradas e aos índices derivados.
- Não alterar em lote `README.md`, `STATUS_OFICIAL.md`, `ATLAS_INDEX.md` ou relatórios gerados sem respeitar os seus geradores.
- Não considerar uma execução verde como sinônimo de conteúdo validado.
- Não iniciar Knowledge API, RAG ou integrações de produto com base em documentos cuja autoridade e proveniência estejam indefinidas.

## Estado

**Proposto — aguardando revisão humana.** Este ADR registra o plano de trabalho e não declara que os 171 erros ou 273 avisos foram corrigidos.

## Evidências de referência

- `KNOWLEDGE_ENGINE_REPORT.md`
- `ATLAS_VALIDATION_REPORT.md`
- `ATLAS_HEALTH.md`
- `METADATA_REPORT.md`
- `BROKEN_LINKS.md`
- `DUPLICATED_IDS.md`
