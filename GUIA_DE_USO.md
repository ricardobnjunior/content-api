# Guia de Uso - Content API (Postman)

Passo a passo para subir a API, popular com dados e testar todas as funcionalidades usando o **Postman**.

---

## 1. Preparando o ambiente

Crie o arquivo `.env` na raiz do projeto com o seguinte conteudo:

```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=minha-chave-secreta-123
UPLOAD_DIR=uploads
OPENROUTER_API_KEY=sk-or-sua-chave-aqui
OPENROUTER_MODEL=google/gemini-2.5-flash
```

> `DATABASE_URL` e `SECRET_KEY` sao obrigatorios. Sem o `.env` a API nao sobe.
>
> Para usar as features de IA (sugestoes de categorias), voce precisa de uma chave da API do [OpenRouter](https://openrouter.ai). Crie uma conta gratuita e gere sua chave.

Instale as dependencias e suba o servidor:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

O servidor sobe em `http://localhost:8000`. Confirme acessando `http://localhost:8000/health` no navegador ou no Postman.

---

## 2. Configurando o Postman

1. Crie uma nova **Collection** chamada `Content API`.
2. Na aba **Variables** da collection, crie a variavel:
   - `base_url` = `http://localhost:8000/api/v1`
3. Todos os requests abaixo usam `{{base_url}}` como prefixo.
4. Para requests com body JSON, selecione a aba **Body** → **raw** → tipo **JSON**.

---

## 3. Cadastrando categorias

Crie 8 requests `POST` para popular as categorias. Para cada uma:

- **Metodo:** `POST`
- **URL:** `{{base_url}}/categories/`
- **Body (raw JSON):**

```json
{"name": "Programacao"}
```

Repita para cada categoria:

| # | Body |
|---|---|
| 1 | `{"name": "Programacao"}` |
| 2 | `{"name": "Inteligencia Artificial"}` |
| 3 | `{"name": "DevOps"}` |
| 4 | `{"name": "Frontend"}` |
| 5 | `{"name": "Backend"}` |
| 6 | `{"name": "Banco de Dados"}` |
| 7 | `{"name": "Cloud"}` |
| 8 | `{"name": "Seguranca"}` |

**Resposta esperada:** `201 Created` com o JSON da categoria criada.

Para confirmar, faca um `GET {{base_url}}/categories/` — deve retornar as 8 categorias.

> Se tentar criar uma categoria com nome repetido, a API retorna `409 Conflict`.

---

## 4. Cadastrando artigos

Crie requests `POST` para cada artigo:

- **Metodo:** `POST`
- **URL:** `{{base_url}}/articles/`
- **Body (raw JSON):**

### Artigo 1 — Python e IA

```json
{
  "title": "Introducao ao Machine Learning com Python",
  "content": "Machine Learning e um campo da inteligencia artificial que usa algoritmos para aprender padroes a partir de dados. Python e a linguagem mais popular para ML gracas a bibliotecas como scikit-learn, TensorFlow e PyTorch. Neste artigo, vamos explorar os conceitos basicos de aprendizado supervisionado e nao supervisionado, e como implementar seu primeiro modelo de classificacao.",
  "status": "published",
  "category_ids": [1, 2]
}
```

### Artigo 2 — Docker

```json
{
  "title": "Docker para Iniciantes: Containers na Pratica",
  "content": "Docker revolucionou a forma como empacotamos e distribuimos aplicacoes. Containers sao ambientes isolados que contem tudo que uma aplicacao precisa para rodar. Neste guia, vamos aprender a criar Dockerfiles, gerenciar imagens e orquestrar multiplos containers com docker-compose. Ideal para desenvolvedores que querem padronizar seus ambientes de desenvolvimento e deploy.",
  "status": "published",
  "category_ids": [3, 5]
}
```

### Artigo 3 — React

```json
{
  "title": "React Hooks: useState, useEffect e Custom Hooks",
  "content": "React Hooks mudaram a forma como escrevemos componentes em React. Em vez de classes, agora usamos funcoes com hooks para gerenciar estado e efeitos colaterais. O useState gerencia estado local, o useEffect lida com side effects como chamadas a APIs, e custom hooks permitem reutilizar logica entre componentes. Veja exemplos praticos de cada um.",
  "status": "published",
  "category_ids": [1, 4]
}
```

### Artigo 4 — APIs REST

```json
{
  "title": "Construindo APIs REST com FastAPI e SQLAlchemy",
  "content": "FastAPI e um framework moderno para construir APIs em Python, com tipagem automatica, validacao via Pydantic e documentacao auto-gerada. Combinado com SQLAlchemy como ORM, voce consegue criar APIs robustas rapidamente. Neste tutorial, vamos construir uma API completa com CRUD, autenticacao e testes automatizados.",
  "status": "published",
  "category_ids": [1, 5]
}
```

### Artigo 5 — Seguranca

```json
{
  "title": "OWASP Top 10: Vulnerabilidades que Todo Dev Precisa Conhecer",
  "content": "A OWASP Top 10 lista as vulnerabilidades mais criticas em aplicacoes web. Injection, Broken Authentication, XSS e CSRF sao apenas algumas delas. Entender essas vulnerabilidades e essencial para qualquer desenvolvedor que quer construir aplicacoes seguras. Vamos analisar cada uma com exemplos e como se proteger.",
  "status": "published",
  "category_ids": [8]
}
```

### Artigo 6 — Kubernetes (draft)

```json
{
  "title": "Kubernetes: Orquestracao de Containers em Producao",
  "content": "Kubernetes (K8s) e a plataforma padrao para orquestrar containers em producao. Ele gerencia deploy, scaling e operacoes de aplicacoes containerizadas. Vamos aprender sobre Pods, Deployments, Services e Ingress, e como fazer deploy de uma aplicacao real em um cluster K8s.",
  "status": "draft",
  "category_ids": [3, 7]
}
```

### Artigo 7 — LLMs

```json
{
  "title": "Como Integrar LLMs na sua Aplicacao com a API da OpenAI",
  "content": "Large Language Models como GPT e Claude estao transformando o desenvolvimento de software. Neste artigo, vamos ver como integrar a API da OpenAI em uma aplicacao Python, incluindo prompt engineering, streaming de respostas, function calling e como gerenciar custos. Exemplos praticos com FastAPI como backend.",
  "status": "published",
  "category_ids": [1, 2, 5]
}
```

### Artigo 8 — PostgreSQL

```json
{
  "title": "PostgreSQL Avancado: Indices, CTEs e Window Functions",
  "content": "PostgreSQL e o banco relacional open-source mais avancado. Alem do SQL basico, ele oferece recursos poderosos como indices parciais, Common Table Expressions, Window Functions e JSONB. Vamos explorar cada recurso com queries reais e ver como otimizar a performance do seu banco de dados.",
  "status": "published",
  "category_ids": [6]
}
```

### Artigos hibridos (bons para testar sugestoes da IA)

Estes artigos tocam varias categorias — ideais para comparar o que a IA sugere vs o que voce escolheria:

**Artigo 9:**
```json
{
  "title": "Deploy de modelos de ML com FastAPI e Docker",
  "content": "Aprenda a empacotar um modelo de Machine Learning treinado em um container Docker e servi-lo como API REST usando FastAPI. Cobrimos desde a serializacao do modelo com joblib ate o Dockerfile otimizado para producao, passando por health checks e monitoramento basico.",
  "status": "published",
  "category_ids": [1, 2, 3]
}
```

**Artigo 10:**
```json
{
  "title": "Monitorando APIs Python com Grafana e Prometheus",
  "content": "Observabilidade e essencial para manter APIs em producao. Neste guia, configuramos Prometheus para coletar metricas de uma API FastAPI e Grafana para visualizar dashboards em tempo real. Inclui alertas, metricas customizadas e integracao com Docker Compose.",
  "status": "published",
  "category_ids": [5, 3, 7]
}
```

**Artigo 11:**
```json
{
  "title": "Construindo um chatbot com RAG, PostgreSQL e React",
  "content": "Retrieval-Augmented Generation combina busca em banco de dados com geracao de texto via LLM. Neste tutorial, construimos um chatbot completo: backend em Python com pgvector no PostgreSQL para busca semantica, e frontend em React com streaming de respostas.",
  "status": "published",
  "category_ids": [2, 6, 4]
}
```

---

## 5. Verificando os dados

### Listar todos os artigos

- **Metodo:** `GET`
- **URL:** `{{base_url}}/articles/`

### Filtrar por status

- **URL:** `{{base_url}}/articles/?status=published`

### Buscar por termo

- **URL:** `{{base_url}}/articles/?search=python`

### Filtrar por categoria

- **URL:** `{{base_url}}/articles/?category_id=1`

### Combinar filtros com paginacao

- **URL:** `{{base_url}}/articles/?status=published&category_id=2&page=1&per_page=5`

### Ver artigo especifico

- **URL:** `{{base_url}}/articles/1`

---

## 6. Testando upload de imagem

### Upload

- **Metodo:** `POST`
- **URL:** `{{base_url}}/articles/1/image`
- **Body:** selecione **form-data**
  - Key: `file` (mude o tipo para **File** clicando no dropdown ao lado do campo)
  - Value: selecione um arquivo de imagem (PNG, JPG, GIF ou WebP)
- **Resposta esperada:** `201` com `filename`, `url` e `size`

### Verificar

- `GET {{base_url}}/articles/1` — o campo `image_url` deve estar preenchido

### Remover imagem

- **Metodo:** `DELETE`
- **URL:** `{{base_url}}/articles/1/image`
- **Resposta esperada:** `204 No Content`

---

## 7. Testando estatisticas

### Estatisticas gerais

- **Metodo:** `GET`
- **URL:** `{{base_url}}/stats`

**Resposta esperada:**
```json
{
  "total_articles": 11,
  "by_status": { "published": 10, "draft": 1 },
  "by_category": [
    { "category_id": 1, "category_name": "Programacao", "article_count": 5 },
    { "category_id": 2, "category_name": "Inteligencia Artificial", "article_count": 4 }
  ],
  "total_categories": 8,
  "latest_article": { "id": 11, "title": "Construindo um chatbot...", "created_at": "..." }
}
```

### Timeline

- **Metodo:** `GET`
- **URL:** `{{base_url}}/stats/timeline`

**Resposta esperada:**
```json
{
  "timeline": [
    { "month": "2026-03", "count": 11 }
  ]
}
```

---

## 8. Testando exportacao de artigos

### Exportar como CSV

- **Metodo:** `GET`
- **URL:** `{{base_url}}/export/articles?format=csv`
- No Postman, clique em **Send and Download** para salvar o arquivo `articles.csv`

### Exportar como JSON

- **Metodo:** `GET`
- **URL:** `{{base_url}}/export/articles?format=json`
- Clique em **Send and Download** para salvar `articles.json`

> Formato invalido (ex: `?format=xml`) retorna `400 Bad Request`.

---

## 9. Testando sugestoes de categorias (IA)

> Requer `OPENROUTER_API_KEY` configurada no `.env`.

### Sugestoes para artigos basicos

| Request | URL | Categorias esperadas |
|---|---|---|
| Artigo 1 (ML) | `GET {{base_url}}/suggestions/categories/1` | Programacao, Inteligencia Artificial |
| Artigo 2 (Docker) | `GET {{base_url}}/suggestions/categories/2` | DevOps, Backend, Cloud |
| Artigo 5 (OWASP) | `GET {{base_url}}/suggestions/categories/5` | Seguranca, Backend |
| Artigo 7 (LLMs) | `GET {{base_url}}/suggestions/categories/7?limit=5` | Programacao, IA, Backend |

### Sugestoes para artigos hibridos

Estes sao os mais interessantes — compare com as categorias que voce atribuiu manualmente:

| Request | URL | O que a IA pode sugerir |
|---|---|---|
| Artigo 9 (ML + FastAPI + Docker) | `GET {{base_url}}/suggestions/categories/9` | Programacao, IA, DevOps, Backend |
| Artigo 10 (Monitoring) | `GET {{base_url}}/suggestions/categories/10` | DevOps, Backend, Cloud |
| Artigo 11 (RAG + PG + React) | `GET {{base_url}}/suggestions/categories/11?limit=5` | IA, Banco de Dados, Frontend, Backend, Programacao |

**O que observar:**
- Cada sugestao vem com `confidence` de 0.0 a 1.0
- Compare as sugestoes da IA com as categorias que voce atribuiu manualmente
- Os artigos hibridos costumam revelar categorizacoes que voce nao tinha pensado

---

## 10. Fluxo completo de uso real

Simule o dia a dia de um editor de conteudo:

**Passo 1 — Criar artigo como draft (sem categorias)**

- `POST {{base_url}}/articles/`
```json
{
  "title": "Terraform vs Pulumi: Infraestrutura como Codigo",
  "content": "Infraestrutura como codigo (IaC) permite gerenciar servidores, redes e servicos cloud de forma declarativa. Terraform usa HCL como linguagem, enquanto Pulumi permite usar Python, TypeScript e Go. Ambas se integram com AWS, Azure e GCP. Vamos comparar as duas ferramentas em cenarios reais de deploy.",
  "status": "draft"
}
```
- Anote o `id` retornado (ex: 12)

**Passo 2 — Pedir sugestoes de categorias para a IA**

- `GET {{base_url}}/suggestions/categories/12`
- Analise as sugestoes retornadas (ex: DevOps 0.91, Cloud 0.85, Programacao 0.42)

**Passo 3 — Categorizar e publicar**

- `PUT {{base_url}}/articles/12`
```json
{
  "status": "published",
  "category_ids": [3, 7]
}
```

**Passo 4 — Upload de imagem de capa**

- `POST {{base_url}}/articles/12/image`
- Body: **form-data**, key `file` (tipo File), selecione a imagem

**Passo 5 — Verificar estatisticas atualizadas**

- `GET {{base_url}}/stats`

**Passo 6 — Exportar backup**

- `GET {{base_url}}/export/articles?format=json` → **Send and Download**

---

## 11. Testando com o Swagger UI

Se preferir uma interface visual alternativa ao Postman:

1. Abra `http://localhost:8000/docs` no navegador
2. Endpoints organizados por tags: **articles**, **categories**, **stats**, **export**, **suggestions**
3. Clique em qualquer endpoint → **Try it out** → preencha os campos → **Execute**

---

## 12. Rodando os testes automatizados

```bash
# Todos os testes
pytest tests/ -v

# Apenas testes de artigos
pytest tests/ -k "article" -v

# Apenas testes de categorias
pytest tests/ -k "categor" -v

# Com cobertura de codigo
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Dicas

- **Sem chave OpenRouter?** Os endpoints de CRUD (artigos, categorias, imagens), estatisticas e exportacao funcionam normalmente. So o endpoint de `/suggestions` precisa da chave.
- **Modelo LLM:** O padrao e `google/gemini-2.5-flash` (rapido e barato). Voce pode trocar para qualquer modelo disponivel no OpenRouter via a variavel `OPENROUTER_MODEL`.
- **Categorias precisam existir** para o endpoint de sugestoes funcionar. Ele so sugere categorias ja cadastradas.
- **Exportacao** funciona com qualquer quantidade de artigos — o CSV/JSON e gerado via streaming, entao nao sobrecarrega a memoria.
- **Stats e timeline** refletem o estado atual do banco. A timeline agrupa por mes de criacao.
- **Postman tip:** use **Send and Download** (seta ao lado do botao Send) para baixar os arquivos de exportacao diretamente.
