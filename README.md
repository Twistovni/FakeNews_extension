# 🕵️‍♂️ A.I.D. — Agente Investigativo contra Desinformação

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Google Chrome](https://img.shields.io/badge/Google_Chrome-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)
![AI](https://img.shields.io/badge/AI-Groq%20%7C%20OpenRouter-orange?style=for-the-badge)

Um ecossistema híbrido de Fact-Checking composto por uma **Extensão para Chrome** e um **Backend avançado em Python (FastAPI)**. O A.I.D. cruza inteligência artificial, bancos de dados vetoriais locais e ferramentas de busca na web para validar a veracidade de notícias em tempo real, fornecendo aos usuários um dossiê investigativo e contexto educacional.

Projeto focado em combater as *Fake News* através de arquiteturas de Inteligência Artificial de última geração, incluindo **RAG Híbrido** e **Consenso Multi-Agente (Tribunal de Fatos)**.

---

## ✨ Funcionalidades

* ⚡ **RAG Híbrido Ultrarrápido (Offline)** — Busca instantânea de notícias em uma base de conhecimento local, cruzando similaridade semântica (vetores) e textual (strings).
* 🌐 **Fact-Checking Ativo na Web** — Quando a notícia não está no banco local, o Agente busca ativamente evidências via **NewsAPI** ou usa o **DuckDuckGo** como fallback anti-bloqueio.
* 🧠 **Tribunal de Fatos (Consenso Multi-Agente)** — As evidências coletadas são processadas paralelamente por múltiplas LLMs (Groq e OpenRouter). O sistema avalia a concordância entre os modelos para garantir um veredito livre de alucinações.
* 🎓 **Contexto Educacional Rico** — Não entrega apenas "Verdadeiro" ou "Falso". A IA gera exemplos de manchetes reais (**🟢 Cenário Factual**) e boatos clássicos (**🔴 Boato Clássico**) sobre o tema.
* 👁️ **Expansão de Consulta (Visão Periférica)** — Antes de buscar na web, uma LLM extrai as entidades principais do título, otimizando os termos de busca para encontrar as melhores evidências.
* 🧹 **Filtro Global de Ruído** — Sanitização automática das manchetes capturadas no navegador, removendo sufixos de portais (ex: " | G1", " - UOL") via Regex.

---

## 🏗️ Arquitetura do Sistema

O backend utiliza uma arquitetura adaptativa que decide o melhor fluxo de acordo com as configurações do usuário:

```text
[ 🧩 Extensão Chrome ] ➔ Captura Manchete
         ↓
[ 🧹 Filtro Regex ]    ➔ Sanitização de Ruídos
         ↓
[ ⚙️ Orquestrador FastAPI ]
    /                 \
  IA OFF             IA ON
    ↓                   ↓
[ 🗄️ RAG Local ]   [ 🌐 Multi-Tools (NewsAPI / DDGS) ]
  (ChromaDB)            ↓
                   [ ⚖️ Tribunal de Fatos ]
                  (Groq + OpenRouter)
                       ↓
[ 📩 Resposta (Dossiê + Veredito + Contexto) ]
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso no Projeto |
| :--- | :--- |
| **FastAPI** | Framework principal do Backend, comunicação via rotas REST. |
| **ChromaDB** | Banco de dados vetorial para o funcionamento do RAG Local. |
| **Sentence-Transformers** | Criação de embeddings (`all-MiniLM-L6-v2`) para busca semântica. |
| **Groq API / Llama 3** | Modelo de Linguagem primário ultrarrápido para extração e inferência. |
| **OpenRouter API** | Modelos de Linguagem secundários para o "Tribunal de Consenso" e failover. |
| **NewsAPI & DDGS** | Coleta estruturada de evidências jornalísticas na web. |
| **JS / HTML / CSS** | Desenvolvimento da Extensão para Google Chrome (Frontend). |

---

## 📋 Pré-requisitos

* **Python 3.9** ou superior instalado.
* Navegador **Google Chrome**.
* Chaves de API ativas das seguintes plataformas (Planos Gratuitos):
  * [Groq Cloud](https://console.groq.com/)
  * [OpenRouter](https://openrouter.ai/)
  * [NewsAPI](https://newsapi.org/)

---

## 🚀 Como Instalar e Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
cd NOME_DO_REPOSITORIO/fakenews-backend
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install fastapi uvicorn httpx pydantic beautifulsoup4 lxml google-api-python-client sentence-transformers scikit-learn numpy chromadb==0.4.24 newsapi-python duckduckgo-search

# IMPORTANTE: Forçar versão do NumPy compatível com ChromaDB
pip install numpy==1.26.4 --force-reinstall
```

### 4. Configure as Chaves de API

Abra os arquivos `main.py` e `atualizador_rag.py` e insira suas respectivas `API_KEYS` nas variáveis de configuração no topo do arquivo. *(Em produção, utilize variáveis de ambiente `.env`)*.

### 5. Alimente o Banco de Dados

Antes de rodar a API, popule seu banco local executando o robô de coleta:

```bash
python3 atualizador_rag.py
```

### 6. Inicie o Servidor

```bash
uvicorn main:app --reload
```

O servidor estará rodando em `http://127.0.0.1:8000`.

---

## 📁 Estrutura do Projeto

```text
A.I.D.-Fakenews/
├── fakenews-backend/
│   ├── main.py               # API, RAG, Multi-Tools e Tribunal de IAs
│   ├── atualizador_rag.py    # Pipeline ETL que faz scraping e popula o DB
│   ├── database.json         # Base de conhecimento local em texto
│   └── (venv)/               # Ambiente virtual Python
│
└── extension/                # Frontend (Não incluído neste repositório)
    ├── manifest.json
    ├── popup.html
    ├── popup.js
    └── styles.css
```

---

## ⚠️ Aviso Legal

Este projeto tem fins **educacionais e de pesquisa** em arquiteturas de Inteligência Artificial e combate à desinformação. Nenhum veredito gerado pelo A.I.D. deve ser considerado uma verdade absoluta ou laudo oficial. Sempre cheque fontes de jornais reconhecidos e agências de fact-checking.

---

## 👨‍💻 Autor

**Luiz Santos** — Analista de Suporte / Engenharia de Software  
*Construindo pontes entre Inteligência Artificial e a verdade factual.*
