---
id: PUB-009
title: EduData Press Book Architecture
subtitle: Arquitetura Oficial de Livros da EduData Press
version: 1.0.0
status: Oficial
classification: Publisher
owner: EduData Press
maintainer: EDI Atlas
created: 2026
updated: 2026
---

# Arquitetura Oficial de Livros

## Objetivo

Este documento define como o patrimônio intelectual registrado no EDI Atlas deverá ser reorganizado para compor livros publicados pela EduData Press.

O objetivo não é reproduzir a estrutura do Atlas, mas transformá-la em uma narrativa editorial contínua, adequada ao público da obra.

---

# Princípio Fundamental

O EDI Atlas representa a estrutura do conhecimento.

Os livros representam a estrutura da aprendizagem.

Consequentemente, a organização dos capítulos poderá diferir da organização dos documentos do Atlas, preservando integralmente seus conceitos.

---

# Fluxo Editorial

```
EDI Atlas

↓

Seleção dos documentos

↓

Agrupamento temático

↓

Expansão editorial

↓

Capítulos

↓

Livro
```

---

# Organização das Obras

Toda obra deverá possuir a seguinte estrutura mínima.

## Elementos Pré-textuais

- Capa
- Folha de rosto
- Copyright
- Dedicatória (opcional)
- Agradecimentos (opcional)
- Prefácio
- Apresentação
- Sumário

---

## Parte I

Contextualização

Apresenta:

- problema;
- contexto;
- motivação;
- origem.

Fontes típicas:

- Foundation
- Collection
- Decisions

---

## Parte II

Fundamentos

Apresenta:

- Framework;
- princípios;
- conceitos;
- metodologia.

Fontes típicas:

- Framework EDI
- Knowledge

---

## Parte III

Arquitetura

Apresenta:

- modelos;
- ontologia;
- taxonomia;
- arquitetura conceitual.

Fontes:

- Framework
- EIOS
- Knowledge

---

## Parte IV

Aplicações

Apresenta:

- produtos;
- casos;
- aplicações;
- estudos.

Fontes:

- Collection
- ADR
- Products

---

## Parte V

Perspectivas

Apresenta:

- evolução;
- pesquisa;
- roadmap;
- futuro.

Fontes:

- Decisions
- Roadmaps
- White Papers

---

## Elementos Pós-textuais

- Glossário
- Referências
- Índice Remissivo
- Sobre os Autores

---

# Correspondência com o Atlas

Cada capítulo deverá indicar internamente sua origem documental.

Exemplo:

```
Capítulo 6

Origem

FW-001
FW-004
KO-0008
ADR-0003
```

Essa rastreabilidade deverá permanecer disponível durante todo o ciclo editorial.

---

# Expansão Editorial

Durante a geração do livro poderão ser incorporados:

- exemplos;
- estudos de caso;
- notas técnicas;
- boxes;
- quadros;
- diagramas;
- ilustrações.

Nenhum conceito poderá contradizer o Atlas.

---

# Diferentes Arquiteturas

O mesmo patrimônio poderá originar diferentes obras.

Exemplos:

- Livro científico;
- Livro técnico;
- Livro didático;
- Guia prático;
- Manual institucional;
- White Paper.

Cada arquitetura reorganiza o conteúdo sem alterar sua origem.

---

# Atualização

Sempre que o Atlas evoluir:

1. Atualizar os documentos oficiais.
2. Regenerar a arquitetura do livro.
3. Publicar nova edição.
4. Registrar alterações no Changelog.

---

# Considerações Finais

A Arquitetura Oficial de Livros estabelece a separação entre documentação técnica e publicação editorial.

O EDI Atlas permanece como fonte única de conhecimento.

A EduData Press transforma esse patrimônio em obras organizadas para diferentes públicos, preservando consistência, rastreabilidade e qualidade científica.