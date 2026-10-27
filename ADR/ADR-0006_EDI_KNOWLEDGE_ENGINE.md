# ADR-0006 — EDI Knowledge Engine como orquestrador documental do Atlas

- **Status:** Aceita para a automação documental do repositório
- **Data:** 2026-10-27
- **Decisores:** Governança técnica da EduData IA

## Contexto

O EDI Atlas é a fonte oficial do patrimônio intelectual e da documentação institucional, científica, metodológica e tecnológica da EduData IA. A manutenção do inventário, dos índices derivados, da análise de dependências e dos relatórios exige uma sequência de execução consistente e auditável.

## Decisão

Adotar `scripts/knowledge_engine.py` como ponto de entrada para orquestrar os módulos documentais existentes do Atlas:

1. `atlas_automation.py`;
2. `atlas_parser.py`;
3. `atlas_dependency_engine.py`;
4. `atlas_sync_engine.py`;
5. nova execução de `atlas_parser.py) após a sincronização;
6. `atlas_validation_engine.py`.

A automação é acionada pelo workflow do GitHub Actions. Os relatórios de execução devem permitir identificar os módulos executados, códigos de saída e artefatos encontrados.

## Limites

- A existência de um script ou relatório não comprova, por si só, a qualidade total da documentação.
- Documentos estratégicos, científicos e arquiteturais continuam sujeitos a revisão humana.
- O Sync Engine deve modificar somente artefatos derivados que estejam explicitamente sob seu controle.
- O Knowledge Engine não é, por si só, a Knowledge API e não deve ser descrito como serviço de produção consumido pelos produtos.
- A Knowledge API, o grafo semântico e a busca semântica permanecem no roadmap até implementação e validação específicas.

## Consequências

### Positivas

- Um ponto de entrada conhecido para a automação documental.
- Ordem de execução padronizada.
- Relatórios de execução em Markdown e JSON para auditoria e integrações futuras.
- Separação entre documentos autoritativos e artefatos derivados.

### Custos e riscos

- A sequência depende da compatibilidade entre os scripts existentes.
- O workflow deve continuar sendo testado após mudanças nos módulos.
- Índices gerados automaticamente podem sobrescrever edições manuais; entradas permanentes devem residir no gerador ou em arquivos-fonte controlados.
- A saída de validação precisa ser examinada; uma execução bem-sucedida não significa necessariamente zero avisos ou erros documentais.

## Verificação

A implementação deve ser verificada pela execução do workflow em GitHub Actions e pela inspeção de `KNOWLEDGE_ENGINE_REPORT.md`, `KNOWLEDGE_ENGINE_REPORT.json` e dos relatórios específicos. Esta ADR registra a decisão arquitetural e não substitui essa verificação operacional.

## Roadmap relacionado

1. Consolidar relatórios com um Report Engine.
2. Evoluir o grafo documental para relações semânticas explícitas.
3. Especificar e implementar a Knowledge API com autenticação, autorização, versionamento e proveniência.
4. Avaliar busca semântica/RAG com controles de acesso.
5. Integrar produtos somente após contratos, segurança e testes de aceitação.
