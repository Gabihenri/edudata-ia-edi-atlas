---
id: PUB-002
title: EduData Press LaTeX Template Specification
subtitle: Template Oficial de Livros da EduData Press
version: 1.0.0
status: Oficial
classification: Publisher
owner: EduData Press
maintainer: EDI Atlas
created: 2026
updated: 2026
---

# EduData Press LaTeX Template

## Objetivo

Definir a estrutura oficial utilizada por todas as publicações produzidas pela EduData Press.

O template garante identidade visual, padronização editorial e compatibilidade entre todas as obras derivadas do EDI Atlas.

---

# Estrutura do Projeto

```
Livro/

main.tex

config/

frontmatter/

chapters/

backmatter/

images/

tables/

figures/

bibliography/

appendices/
```

---

# Arquivo Principal

Todo livro deverá possuir um arquivo principal denominado:

```
main.tex
```

Este arquivo será responsável por carregar:

- configurações;
- capítulos;
- bibliografia;
- glossário;
- índice remissivo;
- apêndices.

---

# Front Matter

A abertura do livro deverá conter:

- capa;
- folha de rosto;
- copyright;
- dedicatória (opcional);
- agradecimentos (opcional);
- prefácio;
- apresentação;
- sumário.

---

# Corpo do Livro

Cada capítulo deverá estar em arquivo independente.

Exemplo:

```
chapters/

cap01.tex

cap02.tex

cap03.tex

...
```

Nenhum capítulo deverá ser escrito diretamente no main.tex.

---

# Back Matter

O encerramento da obra deverá conter:

- glossário;
- referências;
- índice remissivo;
- anexos (quando aplicável).

---

# Diagramas

Todos os diagramas deverão ser derivados dos documentos existentes em:

```
DIAGRAMS/
```

Priorizar:

- SVG;
- PDF vetorial;
- TikZ (quando possível).

---

# Figuras

Todas as imagens deverão possuir:

- legenda;
- numeração automática;
- referência no texto;
- fonte.

---

# Tabelas

As tabelas deverão seguir padronização única.

Cada tabela deverá possuir:

- título;
- numeração;
- legenda;
- fonte.

---

# Bibliografia

Toda bibliografia deverá utilizar BibTeX.

Arquivo padrão:

```
bibliography/references.bib
```

---

# Glossário

Sempre utilizar glossário automático.

Conceitos do Framework EDI deverão possuir definição única em toda a coleção.

---

# Índice

Todos os livros deverão possuir índice remissivo automático.

---

# Numeração

Capítulos:

1

2

3

...

Seções:

1.1

1.2

1.3

Subseções:

1.1.1

1.1.2

---

# Identidade Visual

Toda obra da EduData Press deverá compartilhar:

- mesma tipografia;
- mesma estrutura;
- mesmo estilo de capítulos;
- mesma paginação;
- mesma organização visual.

---

# Compatibilidade

O template deverá gerar:

- PDF para impressão;
- PDF digital;
- ePub;
- Kindle;
- HTML (quando necessário).

---

# Evolução

Novas versões do template deverão preservar compatibilidade com livros já publicados.

---

# Considerações Finais

O Template Oficial da EduData Press garante que toda publicação derivada do EDI Atlas mantenha identidade visual, consistência editorial e qualidade técnica, permitindo a produção padronizada de livros, eBooks, cursos e demais materiais educacionais.