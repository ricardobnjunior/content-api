# Content API

API headless de gerenciamento de conteudo (CMS) construida com **FastAPI** e **SQLite**. Backend-only, sincrona e simples.

Permite gerenciar **artigos**, **categorias**, **imagens**, **estatisticas**, **exportacao** e conta com **sugestoes inteligentes de categorias via IA (LLM)**.

---

## Tech Stack

| Tecnologia | Uso |
|---|---|
| **FastAPI** | Framework web |
| **SQLAlchemy** | ORM |
| **SQLite** | Banco de dados (padrao) |
| **Pydantic** | Validacao de dados |
| **Alembic** | Migracoes de banco |
| **Uvicorn** | Servidor ASGI |
| **OpenAI SDK** | Integracao com LLM via OpenRouter |
| **Pillow** | Processamento de imagens |
| **pytest** | Testes |

---

## Instalacao

```bash
# Clone o repositorio
cd content-api

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instale as dependencias
pip install -r requirements.txt
```

---

## Executando

```bash
# Modo desenvolvimento (com auto-reload)
uvicorn app.main:app --reload

# Modo producao
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

O servidor sobe em `http://localhost:8000`.

### Documentacao interativa (auto-gerada)

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Variaveis de Ambiente

Crie um arquivo `.env` na raiz ou exporte as variaveis:

| Variavel | Padrao | Descricao |
|---|---|---|
| `DATABASE_URL` | *obrigatorio* | URL de conexao do banco (ex: `sqlite:///./app.db`) |
| `SECRET_KEY` | *obrigatorio* | Chave secreta (mude em producao!) |
| `UPLOAD_DIR` | `uploads` | Diretorio de upload de imagens |
| `OPENROUTER_API_KEY` | `""` | Chave da API OpenRouter (obrigatoria para features de IA) |
| `OPENROUTER_MODEL` | `google/gemini-2.5-flash` | Modelo LLM usado nas features de IA |

---

## Endpoints da API

Base URL: `/api/v1`

### Visao geral das rotas

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/articles/` | Listar artigos (paginado, filtros, busca) |
| `POST` | `/api/v1/articles/` | Criar artigo |
| `GET` | `/api/v1/articles/{id}` | Buscar artigo por ID |
| `PUT` | `/api/v1/articles/{id}` | Atualizar artigo |
| `DELETE` | `/api/v1/articles/{id}` | Deletar artigo |
| `POST` | `/api/v1/articles/{id}/image` | Upload de imagem |
| `DELETE` | `/api/v1/articles/{id}/image` | Deletar imagem |
| `GET` | `/api/v1/categories/` | Listar categorias |
| `POST` | `/api/v1/categories/` | Criar categoria |
| `GET` | `/api/v1/categories/{id}` | Buscar categoria por ID |
| `DELETE` | `/api/v1/categories/{id}` | Deletar categoria |
| `GET` | `/api/v1/stats` | Estatisticas gerais |
| `GET` | `/api/v1/stats/timeline` | Timeline de criacao de artigos |
| `GET` | `/api/v1/suggestions/categories/{id}` | Sugestoes de categorias (IA) |
| `GET` | `/api/v1/export/articles` | Exportar artigos (CSV/JSON) |

---

### Health Check

```
GET http://localhost:8000/health
```

Resposta:
```json
{
  "status": "ok"
}
```

---

### Artigos

#### Listar artigos (com paginacao, filtros e busca)

```
GET http://localhost:8000/api/v1/articles/?page=1&per_page=10&status=published&search=python&category_id=1
```

| Parametro | Tipo | Padrao | Descricao |
|---|---|---|---|
| `page` | int | 1 | Pagina (1-indexed) |
| `per_page` | int | 10 | Itens por pagina (max 100) |
| `status` | string | - | Filtrar por status (`draft`, `published`) |
| `search` | string | - | Busca no titulo e conteudo |
| `category_id` | int | - | Filtrar por categoria |

Resposta:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Meu Artigo",
      "content": "Conteudo do artigo...",
      "status": "published",
      "image_url": "/uploads/1_banner.png",
      "created_at": "2024-03-20T10:00:00",
      "updated_at": "2024-03-20T10:05:00",
      "categories": [
        { "id": 1, "name": "Tecnologia" }
      ]
    }
  ],
  "meta": {
    "total": 42,
    "page": 1,
    "per_page": 10,
    "pages": 5
  }
}
```

#### Criar artigo

```
POST http://localhost:8000/api/v1/articles/
Content-Type: application/json

{
  "title": "Novo Artigo",
  "content": "Conteudo aqui",
  "status": "draft",
  "category_ids": [1, 2]
}
```

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `title` | string | Sim | Titulo do artigo |
| `content` | string | Sim | Conteudo do artigo |
| `status` | string | Nao | Status (padrao: `draft`) |
| `category_ids` | list[int] | Nao | IDs das categorias |

Resposta: `201 Created` com o artigo criado.

#### Buscar artigo por ID

```
GET http://localhost:8000/api/v1/articles/{article_id}
```

Resposta: `200 OK` com o artigo ou `404 Not Found`.

#### Atualizar artigo

```
PUT http://localhost:8000/api/v1/articles/{article_id}
Content-Type: application/json

{
  "title": "Titulo Atualizado",
  "status": "published",
  "category_ids": [3]
}
```

Todos os campos sao opcionais. Resposta: `200 OK` com o artigo atualizado.

#### Deletar artigo

```
DELETE http://localhost:8000/api/v1/articles/{article_id}
```

Resposta: `204 No Content`.

#### Upload de imagem do artigo

```
POST http://localhost:8000/api/v1/articles/{article_id}/image
Content-Type: multipart/form-data

file: <arquivo de imagem>
```

Aceita: `image/png`, `image/jpeg`, `image/gif`, `image/webp`.

Resposta `201`:
```json
{
  "filename": "1_banner.png",
  "url": "/uploads/1_banner.png",
  "size": 12345
}
```

#### Deletar imagem do artigo

```
DELETE http://localhost:8000/api/v1/articles/{article_id}/image
```

Resposta: `204 No Content`.

---

### Categorias

#### Listar categorias

```
GET http://localhost:8000/api/v1/categories/
```

Resposta:
```json
[
  { "id": 1, "name": "Tecnologia" },
  { "id": 2, "name": "Ciencia" }
]
```

#### Criar categoria

```
POST http://localhost:8000/api/v1/categories/
Content-Type: application/json

{ "name": "Tecnologia" }
```

Resposta: `201 Created`. Retorna `409` se o nome ja existir.

#### Buscar categoria por ID

```
GET http://localhost:8000/api/v1/categories/{category_id}
```

Resposta: `200 OK` ou `404 Not Found`.

#### Deletar categoria

```
DELETE http://localhost:8000/api/v1/categories/{category_id}
```

Resposta: `204 No Content`. Artigos associados **nao** sao deletados.

---

### Estatisticas

#### Estatisticas gerais

```
GET http://localhost:8000/api/v1/stats
```

Resposta `200`:
```json
{
  "total_articles": 15,
  "by_status": {
    "draft": 3,
    "published": 12
  },
  "by_category": [
    {
      "category_id": 1,
      "category_name": "Tecnologia",
      "article_count": 8
    }
  ],
  "total_categories": 5,
  "latest_article": {
    "id": 15,
    "title": "Ultimo Artigo Criado",
    "created_at": "2024-03-20T10:00:00"
  }
}
```

#### Timeline de criacao

```
GET http://localhost:8000/api/v1/stats/timeline
```

Resposta `200`:
```json
{
  "timeline": [
    { "month": "2024-01", "count": 4 },
    { "month": "2024-02", "count": 7 },
    { "month": "2024-03", "count": 4 }
  ]
}
```

---

### Exportacao

#### Exportar artigos

```
GET http://localhost:8000/api/v1/export/articles?format=csv
```

| Parametro | Tipo | Padrao | Descricao |
|---|---|---|---|
| `format` | string | `csv` | Formato de exportacao (`csv` ou `json`) |

- `format=csv` — retorna arquivo CSV com header `Content-Disposition: attachment; filename="articles.csv"`
- `format=json` — retorna arquivo JSON com header `Content-Disposition: attachment; filename="articles.json"`

Retorna `400` se o formato nao for `csv` ou `json`.

---

### Sugestoes de Categorias (IA)

Usa LLM para classificar automaticamente um artigo nas categorias existentes.

#### Obter sugestoes de categorias para um artigo

```
GET http://localhost:8000/api/v1/suggestions/categories/{article_id}?limit=3
```

| Parametro | Tipo | Padrao | Descricao |
|---|---|---|---|
| `limit` | int | 3 | Maximo de sugestoes (minimo 1) |

Resposta `200`:
```json
{
  "article_id": 1,
  "suggestions": [
    {
      "category_id": 2,
      "category_name": "Tecnologia",
      "confidence": 0.92
    },
    {
      "category_id": 5,
      "category_name": "Programacao",
      "confidence": 0.78
    }
  ]
}
```

| Campo | Tipo | Descricao |
|---|---|---|
| `category_id` | int | ID da categoria sugerida |
| `category_name` | string | Nome da categoria |
| `confidence` | float | Confianca da sugestao (0.0 a 1.0) |

> Apenas categorias ja cadastradas no sistema sao sugeridas.

Erros possiveis:
- `404` — Artigo nao encontrado.
- `500` — Falha na chamada ao LLM.

---

## Modelos do Banco de Dados

### Article

| Coluna | Tipo | Descricao |
|---|---|---|
| `id` | int (PK) | ID auto-incremento |
| `title` | string(300) | Titulo |
| `content` | text | Conteudo |
| `status` | string(20) | Status (padrao: `draft`) |
| `image_url` | string(500) | URL da imagem (nullable) |
| `created_at` | datetime | Data de criacao (auto) |
| `updated_at` | datetime | Data de atualizacao (auto) |

### Category

| Coluna | Tipo | Descricao |
|---|---|---|
| `id` | int (PK) | ID auto-incremento |
| `name` | string(100) | Nome (unico) |

Relacao **many-to-many** entre Article e Category via tabela `article_categories`.

---

## Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar um arquivo especifico
pytest tests/test_articles.py -v

# Rodar com cobertura
pytest tests/ --cov=app

# Filtrar por nome
pytest tests/ -k "search" -v
```

Os testes usam um banco SQLite isolado e diretorio temporario para uploads.

---

## Testando com curl

```bash
# Health check
curl http://localhost:8000/health

# Criar categoria
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Tecnologia"}'

# Criar artigo
curl -X POST http://localhost:8000/api/v1/articles/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Meu Artigo", "content": "Conteudo aqui", "category_ids": [1]}'

# Listar artigos
curl http://localhost:8000/api/v1/articles/

# Buscar artigos publicados
curl "http://localhost:8000/api/v1/articles/?status=published&search=python"

# Upload de imagem
curl -X POST http://localhost:8000/api/v1/articles/1/image \
  -F "file=@imagem.png"

# Atualizar artigo
curl -X PUT http://localhost:8000/api/v1/articles/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'

# Estatisticas
curl http://localhost:8000/api/v1/stats

# Timeline
curl http://localhost:8000/api/v1/stats/timeline

# Exportar artigos como CSV
curl -O http://localhost:8000/api/v1/export/articles?format=csv

# Exportar artigos como JSON
curl -O http://localhost:8000/api/v1/export/articles?format=json

# Sugestao de categorias (IA)
curl http://localhost:8000/api/v1/suggestions/categories/1?limit=3

# Deletar artigo
curl -X DELETE http://localhost:8000/api/v1/articles/1
```

---

## Estrutura do Projeto

```
content-api/
├── app/
│   ├── main.py              # Inicializacao do FastAPI
│   ├── config.py            # Configuracoes (env vars)
│   ├── database.py          # Conexao com banco
│   ├── ai/
│   │   ├── prompts.py      # Templates de prompts para o LLM
│   │   └── classifier.py   # Classificador de categorias via LLM
│   ├── api/
│   │   ├── router.py        # Router central (/api/v1)
│   │   └── endpoints/
│   │       ├── articles.py       # Endpoints de artigos
│   │       ├── categories.py     # Endpoints de categorias
│   │       ├── stats.py          # Estatisticas e timeline
│   │       ├── export.py         # Exportacao CSV/JSON
│   │       └── suggestions.py    # Sugestoes de categorias (IA)
│   ├── models/
│   │   ├── article.py       # Modelos ORM Article e Category
│   │   └── category.py      # Re-export do modelo Category
│   ├── schemas/
│   │   ├── article.py       # Schemas de artigo
│   │   ├── category.py      # Schemas de categoria
│   │   ├── image.py         # Schema de imagem
│   │   └── stats.py         # Schemas de estatisticas
│   └── crud/
│       ├── article.py       # CRUD de artigos
│       └── category.py      # CRUD de categorias
├── tests/                   # Suite de testes
├── conftest.py              # Fixtures do pytest
├── requirements.txt         # Dependencias
└── .github/workflows/ci.yml # CI com GitHub Actions
```

---

## Fixes aplicados

Correcoes realizadas sobre o codigo do remote que impediam a API de inicializar:

| Fix | Problema | Arquivo |
|---|---|---|
| 1 | `Category` duplicado (2 modelos, mesma tabela) | `models/category.py` |
| 2 | Prefixo `/api/api/v1/...` duplicado | `main.py` |
| 3 | Stats router sem prefix | `router.py` |
| 4 | Import `api_router` inexistente | `router.py` |
| 5 | Suggestions nao registrado no router | `router.py` |

Detalhes completos em [FIXES.md](FIXES.md).

---

## CI/CD

O projeto usa **GitHub Actions** para rodar os testes automaticamente em push/PR para `main`.
