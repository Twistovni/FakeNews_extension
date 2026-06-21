# 🕵️‍♂️ A.I.D. — Agente Investigativo contra Desinformação

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Google Chrome](https://img.shields.io/badge/Google_Chrome-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)
![AI](https://img.shields.io/badge/AI-Groq%20%7C%20OpenRouter-orange?style=for-the-badge)

O **A.I.D.** é um ecossistema híbrido e inteligente de *Fact-Checking* composto por uma **Extensão para Google Chrome** e um **Servidor de Alta Performance em Python (FastAPI)**. O sistema une processamento de linguagem natural (NLP), bancos de dados vetoriais locais e raspagem ativa na web para mapear, validar e desmistificar manchetes em tempo real.

Desenvolvido como projeto final para a disciplina **Construção de Assistentes Virtuais Inteligentes**, o A.I.D. implementa as arquiteturas de recuperação de informações mais robustas do mercado, como **Retrieval-Augmented Generation (RAG) Híbrido** e **Reranqueamento Multicritério** de evidências.

---

## ✨ Funcionalidades do MVP

*   ⚡ **RAG Híbrido Avançado (Offline)** — Em vez de depender apenas de buscas semânticas densas, o sistema combina a precisão de embeddings vetoriais locais (`all-MiniLM-L6-v2` via ChromaDB) com buscas léxicas rápidas (overlap exato de palavras filtrando stopwords), superando cenários de paráfrases e nomes próprios.
*   📊 **Reranqueamento Multicritério (Reranking)** — Os resultados recuperados passam por uma fórmula de pontuação de relevância composta, priorizando as melhores evidências com base em:
    $$\text{Score Final} = (0.35 \times \text{Lexical}) + (0.35 \times \text{Semântico}) + (0.15 \times \text{Recência}) + (0.15 \times \text{Confiança da Fonte})$$
*   📰 **Metadados Ricos e Estruturados** — A pipeline local não armazena apenas títulos. Ela gerencia o ciclo de vida da notícia mapeando URL oficial, data de publicação, veículo de imprensa de origem e resumos conceituais gerados por IA.
*   🌐 **Fact-Checking Ativo na Web** — Quando a notícia está fora da base local, o agente autônomo utiliza a **NewsAPI** como canal primário ou raspa o **Google Search** (via seletores anti-frágeis com BeautifulSoup) como fallback resiliente.
*   🧠 **Tribunal de Fatos (Consenso Multi-Agente)** — As evidências coletadas em tempo real são enviadas para avaliação em paralelo pelas LLMs **Groq (Llama 3)** e **OpenRouter**. Um orquestrador de consenso avalia as convergências entre os modelos para mitigar alucinações.
*   👁️ **Expansão de Consulta (Query Expansion)** — Antes de consultar a web, uma LLM extrai o núcleo conceitual da manchete (palavras-chave e entidades), eliminando ruídos editoriais e garantindo buscas assertivas.
*   🧹 **Filtro Global de Ruído** — Sanitização automática por expressões regulares (Regex) para remover assinaturas de portais (ex: " | G1", " - UOL") capturadas no navegador.

---

## 🏗️ Arquitetura do Sistema

O fluxo de dados foi projetado em camadas claras (Coleta, Recuperação Híbrida, Reranqueamento e Explicação), dividindo o processo de forma adaptativa conforme as configurações de IA ativadas pelo usuário:

```text
[ 🧩 Extensão Chrome ] ➔ Captura Manchete + Extrai Contexto (YouTube/Aba)
         ↓
[ 🧹 Filtro Regex ]    ➔ Sanitização de Títulos e Ruídos Editoriais
         ↓
[ ⚙️ Orquestrador FastAPI ]
    /                 \
  IA OFF (Offline)    IA ON (Ativo na Web)
    ↓                   ↓
[ 🗄️ RAG Híbrido ]     [ 👁️ Expansão de Consulta (LLM) ]
(Busca Semântica         ➔ Extração de Entidades e Termos de Busca
 + Busca Lexical)               ↓
    ↓                  [ 🌐 Busca Multi-Tools ]
[ 📊 Reranking ]       ➔ Coleta de Evidências (NewsAPI ou Google Search)
(Fórmula de Score               ↓
 Ponderado)            [ ⚖️ Tribunal de Fatos ]
                        ➔ Consenso Paralelo (Groq + OpenRouter)
    \                 /
[ 📩 Resposta formatada no Frontend (Dossiê + Veredito + Contexto Factual) ]
```

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia | Uso no Projeto |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** | Framework assíncrono de alta performance para exposição de rotas REST. |
| **Banco de Dados** | **ChromaDB** | Banco vetorial local para indexação rápida dos embeddings RAG. |
| **Embeddings** | **Sentence-Transformers** | Modelo `all-MiniLM-L6-v2` para criação de vetores de alta fidelidade. |
| **NLP & LLM** | **Groq API / OpenRouter** | Modelos Llama 3.1 para o Tribunal de Fatos, classificação e expansão de query. |
| **Fact-Check** | **Google Fact Check API** | Integração oficial para validação automatizada de boatos conhecidos. |
| **Scraping** | **BeautifulSoup4 & Lxml** | Raspagem e parsing de portais nacionais de notícia para alimentar a base. |
| **Frontend** | **JS / HTML5 / CSS3** | Extensão V3 nativa do Chrome com design polido e responsivo. |

---

## 📋 Pré-requisitos

*   **Python 3.9** ou superior instalado.
*   Navegador **Google Chrome** (com Modo do Desenvolvedor ativado).
*   Chaves de API (Planos Gratuitos):
    *   [Groq Cloud](https://console.groq.com/)
    *   [OpenRouter](https://openrouter.ai/)
    *   [NewsAPI](https://newsapi.org/)

---

## 🚀 Como Instalar e Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/Twistovni/A.I.D.-Fakenews.git
cd A.I.D.-Fakenews/fakenews-backend
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
pip install -r requirements.txt

# Garantir a compatibilidade do NumPy com o ChromaDB local
pip install numpy==1.26.4 --force-reinstall
```

### 4. Configure as Chaves de API
Insira suas chaves correspondentes nos campos do cabeçalho de configuração dos arquivos `main.py` e `atualizador_rag.py`. Em produção, utilize preferencialmente variáveis de ambiente (`.env`).

### 5. Alimente o Banco de Dados (Web Scraping + ETL)
Rode a pipeline de coleta estruturada e vetorização automática para popular o banco vetorial local:
```bash
python3 atualizador_rag.py
```

### 6. Inicie o Servidor Backend
Inicie a aplicação utilizando o interpretador do ambiente virtual ativo:
```bash
python3 -m uvicorn main:app --reload
```
O servidor estará rodando em: `http://127.0.0.1:8000`

---

## 📁 Estrutura de Pastas do Projeto

```text
A.I.D.-Fakenews/
├── fakenews-backend/         # Camada de Inteligência e Armazenamento
│   ├── main.py               # API FastAPI, RAG Híbrido, Reranking e Tribunal de Fatos
│   ├── atualizador_rag.py    # Pipeline ETL de notícias com metadados estruturados
│   ├── upgrade_database.py   # Script utilitário para atualização de base legada
│   ├── database.json         # Base de conhecimento persistida com metadados ricos
│   ├── requirements.txt      # Gerenciador de dependências limpo
│   └── (venv)/               # Ambiente virtual local (ignorado pelo Git)
│
└── fakenews-extensao/        # Camada de Apresentação (Extensão Chrome)
    ├── manifest.json         # Manifesto V3 de registro da Extensão
    ├── popup.html            # Interface de usuário moderna e semântica
    ├── popup.js              # Capturador dinâmico de abas e requisições assíncronas
    ├── style.css             # Estilização moderna e refinamento de espaçamento
    ├── content_script.js     # Script de raspagem específico para o YouTube
    ├── icon48.png            # Identidade visual da extensão (48px)
    └── icon128.png           # Identidade visual da extensão (128px)
```

---

## ⚠️ Aviso Legal

Este ecossistema foi desenvolvido exclusivamente para fins **educacionais e de pesquisa científica** em arquiteturas de Inteligência Artificial e combate à desinformação de massa. O sistema apoia-se em análise de probabilidade semântica e correlação de dados públicos na web. Os vereditos emitidos pelo A.I.D. não constituem laudo oficial ou verdade factual absoluta. Sempre confirme as informações em veículos de imprensa de reputação consolidada.

---

## 👨‍💻 Autor

**Luiz Santos** — Analista de Suporte / Engenharia de Software  
*Construindo pontes robustas entre Inteligência Artificial de ponta e a verdade factual.*
