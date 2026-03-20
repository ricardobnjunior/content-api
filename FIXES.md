# Fixes aplicados ao codigo do remote

Correcoes realizadas sobre o codigo vindo do remote (`origin/main`, commit `df1cdea`) que impediam a API de inicializar.

| Fix | Problema | Arquivo |
|-----|----------------------------------------------|------------------|
| 1   | Category duplicado (2 modelos, mesma tabela) | models/category.py |
| 2   | Prefixo /api/api/v1/... duplicado            | main.py            |
| 3   | Stats router sem prefix                      | router.py          |
| 4   | Import api_router inexistente                | router.py          |
| 5   | Suggestions nao registrado no router         | router.py          |

---

## Fix 1 — Modelo Category duplicado

**Problema:** A classe `Category` estava definida em dois arquivos distintos mapeando a mesma tabela `categories`:
- `app/models/article.py` — versao usada pelo CRUD e endpoints de articles/categories
- `app/models/category.py` — versao com campos extras (`slug`, `description`) usada por stats e suggestions

O SQLAlchemy rejeitava a inicializacao com:
```
sqlalchemy.exc.InvalidRequestError: Table 'categories' is already defined for this MetaData instance.
```

**Correcao:** `app/models/category.py` foi substituido por um re-export do modelo definido em `app/models/article.py`, eliminando a duplicacao. Todos os imports existentes (`from app.models.category import Category`) continuam funcionando sem alteracao.

**Arquivo alterado:** `app/models/category.py`

---

## Fix 2 — Prefixo de rota duplicado (`/api/api/v1/...`)

**Problema:** O prefixo `/api/v1` era aplicado duas vezes:
- `app/api/router.py` definia `APIRouter(prefix="/api/v1")`
- `app/main.py` adicionava `prefix="/api"` ao incluir o router

Resultado: todas as rotas ficavam em `/api/api/v1/...` em vez de `/api/v1/...`.

**Correcao:** Removido o `prefix="/api"` de `app/main.py`. O prefixo `/api/v1` fica centralizado apenas no `router.py`.

**Arquivo alterado:** `app/main.py`

---

## Fix 3 — Stats router sem prefix

**Problema:** O `stats.py` definia `APIRouter()` sem prefix e o `router.py` incluia sem prefix, causando:
```
FastAPIError: Prefix and path cannot be both empty (path operation: get_stats)
```

**Correcao:** Adicionado `prefix="/stats"` ao incluir o router de stats em `router.py`.

**Arquivo alterado:** `app/api/router.py`

---

## Fix 4 — Import `api_router` inexistente

**Problema:** `app/main.py` importava `api_router` mas `app/api/router.py` exportava a variavel como `router`.
```
ImportError: cannot import name 'api_router' from 'app.api.router'
```

**Correcao:** Renomeada a variavel em `router.py` de `router` para `api_router`.

**Arquivo alterado:** `app/api/router.py`

---

## Fix 5 — Endpoint de suggestions nao registrado

**Problema:** O arquivo `app/api/endpoints/suggestions.py` existia mas nao era importado nem incluido no router principal. O endpoint `/api/v1/suggestions/categories/{article_id}` nao ficava acessivel.

**Correcao:** Adicionado import e `include_router` de `suggestions` em `router.py`.

**Arquivo alterado:** `app/api/router.py`

---

## Rotas finais apos os fixes

```
GET    /health
GET    /api/v1/articles/
POST   /api/v1/articles/
GET    /api/v1/articles/{article_id}
PUT    /api/v1/articles/{article_id}
DELETE /api/v1/articles/{article_id}
POST   /api/v1/articles/{article_id}/image
DELETE /api/v1/articles/{article_id}/image
GET    /api/v1/categories/
POST   /api/v1/categories/
GET    /api/v1/categories/{category_id}
DELETE /api/v1/categories/{category_id}
GET    /api/v1/stats
GET    /api/v1/stats/timeline
GET    /api/v1/suggestions/categories/{article_id}
GET    /api/v1/export/articles
```
