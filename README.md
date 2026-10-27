# EDI Atlas

> Patrimônio Científico, Metodológico e Tecnológico da EduData IA

---

# O que é o EDI Atlas?

O EDI Atlas é o repositório oficial de documentação da EduData IA.

Seu objetivo é preservar, organizar e versionar todo o patrimônio intelectual da Plataforma Operacional de Inteligência Educacional.

O Atlas reúne conhecimento científico, decisões arquiteturais, modelos conceituais, diagramas, objetos de conhecimento e documentação técnica, servindo como fonte única de referência para pesquisadores, desenvolvedores, parceiros e futuros agentes de Inteligência Artificial.

A automação documental do Atlas é orquestrada pelo **EDI Knowledge Engine**, que coordena os scripts de inventário, análise de dependências, sincronização e validação. Os relatórios de execução são artefatos operacionais; eles não substituem decisões arquiteturais aprovadas nem a revisão humana de conteúdo estratégico.

---

# Estrutura

```text
EDI Atlas

├── 00_FOUNDATION
├── 01_FRAMEWORK_EDI
├── 02_EIOS
├── 07_KNOWLEDGE
├── 09_COLLECTION
├── 11_PUBLISHER
├── ADR
├── DECISIONS
├── DIAGRAMS
├── scripts
└── README.md
```

---

# Os Dois Patrimônios

## Framework EDI

Patrimônio científico, metodológico e pedagógico da EduData IA.

Organiza os princípios, conceitos, ontologias, taxonomias e fundamentos que orientam toda a plataforma.

---

## EIOS

Educational Intelligence Operating System.

Patrimônio tecnológico da EduData IA.

Implementa computacionalmente os princípios definidos pelo Framework EDI e fornece uma infraestrutura inteligente compartilhada para todo o ecossistema.

---

# Componentes do Atlas

## Foundation

Documentos institucionais e fundamentos da EduData IA.

## Framework EDI

Documentação oficial do Framework.

## EIOS

Arquitetura tecnológica do sistema operacional inteligente.

## Knowledge

Knowledge Objects (KOs), conceitos e relações semânticas.

## Collection

Livros, publicações, white papers e documentação editorial.

## Publisher

Padrões editoriais e pipeline de publicação da EduData Press.

## ADR

Architecture Decision Records: registro histórico das decisões arquiteturais.

## Decisions

Decisões estratégicas permanentes da EduData IA.

## Diagrams

Diagramas oficiais da arquitetura, modelos conceituais e fluxos do ecossistema.

## EDI Knowledge Engine

Orquestrador de automação documental localizado em `scripts/knowledge_engine.py`. Na configuração atual, coordena:

1. `atlas_automation.py`
2. `atlas_parser.py`
3. `atlas_dependency_engine.py`
4. `atlas_sync_engine.py`
5. nova geração do inventário após sincronização;
6. `atlas_validation_engine.py`

Os artefatos gerados incluem inventário, grafo de dependências, relatório de impacto, índices automáticos das pastas derivadas e relatórios de validação e execução, conforme a configuração dos scripts.

### Limites e governança

- A automação não equivale a aprovação institucional do conteúdo.
- Documentos estratégicos e arquiteturais exigem revisão humana.
- O Sync Engine deve limitar suas alterações aos artefatos derivados que controla.
- Os relatórios representam a saída da última execução; sua presença, isoladamente, não comprova que todos os indicadores estejam sem erros.
- A Knowledge API, a busca semântica e a integração dos produtos são itens de roadmap até que sua implementação seja verificada separadamente.

---

# Arquitetura oficial da EduData IA

```text
Framework EDI
        ↓
EIOS — Educational Intelligence Operating System
        ↓
Core Compartilhado
        ↓
Produtos Especializados
```

O EDI Knowledge Engine dá suporte à manutenção do patrimônio documental do Atlas. Ele não substitui o EIOS nem deve ser tratado como uma API de produção para os produtos.

---

# Princípios

Todo conhecimento registrado no Atlas deve ser:

- científico;
- rastreável;
- versionado;
- reutilizável;
- consistente;
- evolutivo.

---

# Automação e execução

O workflow do GitHub Actions é o ponto de execução automatizada. A execução deve ser conferida na aba **Actions**, incluindo o resultado dos passos, os relatórios produzidos e o commit gerado.

Arquivos operacionais esperados, conforme os módulos instalados:

- `ATLAS_INVENTORY.md` e `ATLAS_INVENTORY.json`
- `DEPENDENCY_GRAPH.md`
- `CHANGE_IMPACT_REPORT.md`
- `ATLAS_SYNC_REPORT.md`
- `ATLAS_VALIDATION_REPORT.md`
- `ATLAS_HEALTH.md`
- `METADATA_REPORT.md`
- `BROKEN_LINKS.md`
- `DUPLICATED_IDS.md`
- `KNOWLEDGE_ENGINE_REPORT.md` e `KNOWLEDGE_ENGINE_REPORT.json`

A lista efetiva de artefatos depende da configuração e do sucesso de cada módulo. Consultar o relatório de execução antes de considerar uma atualização concluída.

---

# Evolução

O EDI Atlas evolui continuamente acompanhando o desenvolvimento da EduData IA.

Próximas evoluções propostas, ainda sujeitas à implementação e validação:

1. consolidar relatórios em um Report Engine;
2. ampliar o grafo para relações semânticas explícitas;
3. desenvolver uma Knowledge API com autenticação, autorização e versionamento;
4. avaliar busca semântica/RAG com proveniência e controle de acesso;
5. integrar os produtos à fonte oficial de conhecimento após testes de contrato e segurança.

Novos documentos, modelos, diagramas e decisões poderão ser incorporados mantendo compatibilidade com a arquitetura oficial da plataforma.

---

# Licenciamento

Salvo indicação em contrário, todo o conteúdo do EDI Atlas constitui patrimônio intelectual da EduData IA.

---

# Versão

Versão documental: **2.0.0**

Ano: **2026**

---

**EduData IA**

**Framework EDI → EIOS → Inteligência Educacional**

<!-- EDI_ATLAS_STATUS_START -->

## Status oficial da EduData IA

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
```

## Estado atual

- A plataforma já existe e está em evolução.
- A Home Estratégica está implementada.
- A infraestrutura utiliza GitHub, Vercel, Supabase, Next.js e FastAPI.
- A EduData Academy possui estrutura e inscrição integradas ao Supabase.
- A Agenda Inteligente EDI é a prioridade técnica atual.
- O Professor Digital é a principal porta de entrada comercial e formativa.
- O BackOffice único e o Experience Manager são diretrizes oficiais.
- O EDI Atlas é a fonte oficial do patrimônio intelectual.
- O EDI Publisher e a EduData Press integram a infraestrutura editorial.
- O template LaTeX da EduData Press está em homologação.

## Prioridade operacional

```text
Agenda Inteligente EDI
        ↓
Segurança e autenticação
        ↓
BackOffice unificado
        ↓
Núcleo operacional do EIOS
        ↓
Professor Digital
        ↓
EduData Academy
        ↓
EduData Analytics
        ↓
SGPA
        ↓
Observatório da Educação
        ↓
Comunidade EduData IA
```

## Regra de evolução

```text
Auditoria
    ↓
Mapeamento
    ↓
Integração
    ↓
Evolução
    ↓
Build
    ↓
Deploy
    ↓
Validação
    ↓
Documentação
```

Não reconstruir produtos existentes, não criar soluções paralelas e não alterar a arquitetura oficial sem decisão formal registrada no EDI Atlas.

<!-- EDI_ATLAS_STATUS_END -->
