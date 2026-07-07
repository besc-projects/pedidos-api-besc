# Documentacao do Projeto

Esta pasta documenta a API Manager Orders de forma pratica: como rodar, como o codigo esta organizado, quais rotas existem e como usar as tabelas do banco.

## Indice

- [`setup.md`](./setup.md): instalacao, variaveis de ambiente, migrations, build e execucao.
- [`architecture.md`](./architecture.md): camadas da aplicacao, fluxo de uma requisicao e convencoes.
- [`api.md`](./api.md): rotas HTTP por dominio, filtros e payloads principais.
- [`database.md`](./database.md): schemas PostgreSQL, tabelas, campos, relacionamentos e uso das tabelas.
- [`operations.md`](./operations.md): comandos frequentes, Docker, Alembic, troubleshooting e pontos de atencao.
- [`history_process/USAGE.md`](./history_process/USAGE.md): exemplos especificos para o historico de processos.

## O que esta API faz

A API centraliza o ciclo operacional de pedidos:

1. Cadastra pedidos e produtos.
2. Relaciona pedidos com propostas comerciais e expedicoes.
3. Mantem uma tabela de precos por PN e destino/UF.
4. Armazena referencias fiscais de produtos, como NCM, IPI, ICMS e ICMS-ST.
5. Controla tickets, seus progressos e divergencias.
6. Registra eventos de auditoria no historico de processos.

## Stack

- FastAPI para HTTP.
- Pydantic para validacao de payloads.
- SQLAlchemy 2.0 async para ORM.
- PostgreSQL como banco.
- Alembic para migrations.
- JWT para autenticacao.
- `uv` para dependencias e comandos Python.

## Leitura recomendada

Para subir o projeto pela primeira vez, comece por [`setup.md`](./setup.md).
Para entender as tabelas antes de integrar outro sistema, leia [`database.md`](./database.md) e depois [`api.md`](./api.md).

