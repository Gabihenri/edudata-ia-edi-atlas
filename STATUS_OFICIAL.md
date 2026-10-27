# Status Oficial da EduData IA

**Atualização documental:** 2026-10-27

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

O EDI Atlas é a fonte oficial do patrimônio intelectual e documental. O EDI Knowledge Engine automatiza tarefas de inventário, análise de dependências, sincronização de índices derivados e validação documental. Ele é uma ferramenta de manutenção do Atlas, não um substituto do EIOS nem uma Knowledge API de produção.

## Estado da documentação e automação do Atlas

Os scripts presentes no repositório e orquestrados por `scripts/knowledge_engine.py` são:

- `atlas_automation.py` — automação principal existente;
- `atlas_parser.py` — inventário documental;
- `atlas_dependency_engine.py` — análise de dependências;
- `atlas_sync_engine.py` — sincronização de índices derivados;
- `atlas_validation_engine.py` — validação documental;
- `knowledge_engine.py` — orquestração e relatório consolidado.

A execução e o resultado devem ser confirmados em GitHub Actions e nos arquivos de relatório gerados. A existência dos scripts não significa que todos os documentos estejam sem erros nem que todos os requisitos de qualidade estejam atendidos.

## Estado atual da EduData IA

- A plataforma já existe e está em evolução.
- A Home Estratégica está implementada.
- A infraestrutura utiliza GitHub, Vercel, Supabase, Next.js e FastAPI.
- A EduData Academy possui estrutura e inscrição integradas ao Supabase.
- A Agenda Inteligente EDI é a prioridade técnica atual.
- O Professor Digital é a principal porta de entrada comercial e formativa.
- O BackOffice único e o Experience Manager são diretrizes oficiais.
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

## Roadmap do Atlas

Os itens abaixo são próximos passos, não funcionalidades consideradas concluídas:

1. Report Engine para consolidar os relatórios existentes;
2. Knowledge Graph com relações semânticas explícitas e rastreáveis;
3. Knowledge API com autenticação, autorização, versionamento e proveniência;
4. busca semântica/RAG com controles de acesso;
5. integração dos produtos à Knowledge API após validação de contratos e segurança;
6. governança de versões, testes automatizados e revisão humana dos documentos estratégicos.

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
