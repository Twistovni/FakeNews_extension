markdown
# 🕵️‍♂️ A.I.D. — Agente Investigativo contra Desinformação

Um ecossistema híbrido de Fact-Checking composto por uma **Extensão para Chrome** e um **Backend avançado em Python (FastAPI)**. O A.I.D. cruza inteligência artificial, bancos de dados vetoriais locais e ferramentas de busca na web para validar a veracidade de notícias em tempo real, fornecendo aos usuários um dossiê investigativo e contexto educacional.

Projeto focado em combater as *Fake News* através de arquiteturas de Inteligência Artificial de última geração, incluindo **RAG Híbrido** e **Consenso Multi-Agente (Tribunal de Fatos)**.

---

## **✨ Funcionalidades**

* ⚡ **RAG Híbrido Ultrarrápido (Offline)** — Busca instantânea de notícias em uma base de conhecimento local, cruzando similaridade semântica (vetores) e textual (strings).
* 🌐 **Fact-Checking Ativo na Web** — Quando a notícia não está no banco local, o Agente busca ativamente evidências em agências oficiais via **NewsAPI** ou raspa o **Google/DuckDuckGo** como fallback anti-bloqueio.
* 🧠 **Tribunal de Fatos (Consenso Multi-Agente)** — As evidências coletadas são processadas paralelamente por múltiplas LLMs (Groq/Llama-3 e OpenRouter). O sistema avalia a concordância entre os modelos para garantir um veredito livre de alucinações.
* 🎓 **Contexto Educacional Rico** — Não entrega apenas "Verdadeiro" ou "Falso". A IA gera exemplos de manchetes reais (**🟢 Cenário Factual**) e boatos clássicos (**🔴 Boato Clássico**) sobre o tema, educando o usuário.
* 👁️ **Expansão de Consulta (Visão Periférica)** — Antes de buscar na web, uma LLM extrai as entidades principais do título, otimizando os termos de busca para encontrar as melhores evidências jornalísticas.
* 🧹 **Filtro Global de Ruído** — Sanitização automática das manchetes capturadas no navegador, removendo sufixos de portais (ex: " | G1", " - UOL") via Regex antes da análise.

---

## **🏗️ Arquitetura do Sistema**

O backend utiliza uma arquitetura adaptativa que decide o melhor fluxo de acordo com as configurações do usuário:

```text
Manchete capturada pela Extensão Chrome
        ↓
Filtro Regex de Sanitização (Remove sufixos de jornais)
        ↓
[IA Avançada Desligada?] 
   ↳ RAG Híbrido Local (ChromaDB) -> Veredito ou Contexto Visual -> Retorna Resposta
        ↓
[IA Avançada Ligada?]
   ↳ 1. Expansão de Consulta: LLM extrai conceitos principais da manchete
   ↳ 2. Ferramenta Primária: Busca evidências via NewsAPI
   ↳ 3. Ferramenta de Backup: Se NewsAPI falhar, raspa o Google/DuckDuckGo
   ↳ 4. Tribunal de Fatos: Evidências vão para Groq E OpenRouter simultaneamente
   ↳ 5. Consenso e Formatação: Retorna Dossiê, Veredito e Contexto Educacional
🛠️ Tecnologias Utilizadas
Tecnologia	Uso no Projeto
FastAPI	Framework principal do Backend, comunicação via rotas REST (CORS).
ChromaDB	Banco de dados vetorial para o funcionamento do RAG Local.
Sentence-Transformers	Criação de embeddings (all-MiniLM-L6-v2) para busca semântica.
Groq API / Llama 3.1	Modelo de Linguagem primário ultrarrápido para extração e inferência.
OpenRouter API	Modelos de Linguagem secundários para o "Tribunal de Consenso" e failover.
NewsAPI	Ferramenta primária para coleta estruturada de evidências jornalísticas.
BeautifulSoup / DDGS	Ferramenta de backup anti-frágil para raspagem de evidências do Google/DuckDuckGo.
JavaScript / HTML / CSS	Desenvolvimento da Extensão para Google Chrome (Frontend).
 
📋 Pré-requisitos
Python 3.9 ou superior instalado.

Navegador Google Chrome (para rodar a extensão cliente).

Chaves de API ativas das seguintes plataformas (Planos Gratuitos):

Groq Cloud

OpenRouter

NewsAPI

🚀 Como Instalar e Rodar o Backend
1. Clone o repositório
bash
git clone https://github.com/SEU_USUARIO/A.I.D.-Fakenews.git
cd A.I.D.-Fakenews/backend
2. Crie e ative o ambiente virtual
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. Instale as dependências
bash
pip install fastapi uvicorn httpx pydantic beautifulsoup4 lxml google-api-python-client sentence-transformers scikit-learn numpy chromadb==0.4.24 newsapi-python duckduckgo-search

# IMPORTANTE: Forçar versão do NumPy compatível com ChromaDB
pip install numpy==1.26.4 --force-reinstall
4. Configure as Chaves de API
Abra os arquivos main.py e atualizador_rag.py e insira suas respectivas API_KEYS nas variáveis de configuração no topo do arquivo (ou configure via variáveis de ambiente .env).

5. Alimente o Banco de Dados (Web Scraping)
Antes de rodar a API, popule seu banco local executando o robô de coleta. Ele raspará notícias dos principais portais, categorizará e gerará os vetores:

bash
python atualizador_rag.py
6. Inicie o Servidor
bash
uvicorn main:app --reload
O servidor estará rodando em http://127.0.0.1:8000.

📁 Estrutura do Projeto
text
A.I.D.-Fakenews/
├── backend/
│   ├── main.py               # Orquestrador da API, RAG, Multi-Tools e Tribunal de IAs
│   ├── atualizador_rag.py    # Pipeline ETL que faz scraping, vetoriza e popula o DB
│   ├── upgrade_database.py   # Script de manutenção para bases de dados antigas
│   ├── database.json         # Base de conhecimento local em texto
│   └── chroma_db/            # (Gerado automaticamente) Banco de dados vetorial
│
└── extension/                # Frontend
    ├── manifest.json         # Configuração da extensão do Chrome
    ├── popup.html            # Interface do usuário (UI)
    ├── popup.js              # Lógica de captura de aba, extração de contexto e chamadas HTTP
    └── styles.css            # Estilos e animações
⚠️ Aviso Legal
Este projeto tem fins educacionais e de pesquisa em arquiteturas de Inteligência Artificial e combate à desinformação. O sistema baseia-se em interpretação probabilística de Modelos de Linguagem (LLMs) e informações publicamente disponíveis na web. Nenhum veredito gerado pelo A.I.D. deve ser considerado uma verdade absoluta ou laudo oficial. Sempre cheque fontes de jornais reconhecidos e agências de fact-checking oficiais.

👨‍💻 Autor
Luiz Santos — Analista de Suporte / Engenharia de Software
Construindo pontes entre Inteligência Artificial e a verdade factual.


### Dicas extras para o seu GitHub:
1. Lembre-se de não subir arquivos como pastas `venv` ou a pasta gerada `chroma_db/`. (Crie um arquivo `.gitignore`).
2. Nunca faça commit com suas senhas expostas no código aberto. Troque as strings fixas por `os.getenv("GROQ_API_KEY")` e ensine os usuários a usar um arquivo `.env` antes de colocar seu repositório público!
Analisar como ficou o readme do meu proje e veja como deixar no mesmo padrão visual do projeto GranaBOT

Imagem PNG
Imagem PNG
Imagem PNG
Resposta concluída
O Gemini respondeu
Como seu Arquiteto de Software, eu analisei as capturas de tela do seu repositório no GitHub. O seu README já está excelente em termos de conteúdo, mas você tem razão: falta aquele "polimento visual" que projetos de destaque (como o GranaBot) possuem para encher os olhos de quem visita.

O segredo do "padrão visual" no GitHub está no uso de Badges (selos), tabelas bem formatadas, negrito estratégico e diagramas ASCII limpos.

Fiz uma revisão completa do seu markdown para adicionar esse acabamento premium.

🎨 O que foi melhorado nesta versão:
Badges (Selos): Adicionei selos visuais com as tecnologias no topo (Python, FastAPI, Chrome, etc.), o que dá uma cara muito profissional logo de cara.

Diagrama de Arquitetura Aprimorado: Refiz o diagrama em formato de fluxo de blocos, que fica muito mais bonito e fácil de ler dentro do bloco de código no GitHub.

Tabela de Tecnologias: Formatação mais limpa e direta.

Espaçamento e Negrito: Ajustei o respiro entre os tópicos para a leitura ficar mais fluida.

📋 Copie o código abaixo e cole no seu README.md
markdown
# 🕵️‍♂️ A.I.D. — Agente Investigativo contra Desinformação

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Google Chrome](https://img.shields.io/badge/Google_Chrome-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)
![AI](https://img.shields.io/badge/AI-Groq%20%7C%20OpenRouter-orange?style=for-the-badge)

Um ecossistema híbrido de Fact-Checking composto por uma **Extensão para Chrome** e um **Backend avançado em Python (FastAPI)**. O A.I.D. cruza inteligência artificial, bancos de dados vetoriais locais e ferramentas de busca na web para validar a veracidade de notícias em tempo real.

Projeto focado em combater as *Fake News* através de arquiteturas de Inteligência Artificial de última geração, incluindo **RAG Híbrido** e **Consenso Multi-Agente (Tribunal de Fatos)**.

---

## **✨ Funcionalidades**

* ⚡ **RAG Híbrido Ultrarrápido (Offline)** — Busca instantânea de notícias em uma base de conhecimento local, cruzando similaridade semântica (vetores) e textual (strings).
* 🌐 **Fact-Checking Ativo na Web** — Quando a notícia não está no banco local, o Agente busca ativamente evidências via **NewsAPI** ou raspa o **Google/DuckDuckGo** como fallback anti-bloqueio.
* 🧠 **Tribunal de Fatos (Consenso)** — As evidências coletadas são processadas paralelamente por múltiplas LLMs (Groq e OpenRouter). O sistema avalia a concordância entre os modelos.
* 🎓 **Contexto Educacional Rico** — Não entrega apenas "Verdadeiro" ou "Falso". A IA gera exemplos de manchetes reais (**🟢 Factual**) e boatos clássicos (**🔴 Boato**) sobre o tema, educando o usuário.
* 👁️ **Expansão de Consulta** — Antes de buscar na web, uma LLM extrai as entidades principais do título, otimizando os termos de busca para encontrar as melhores evidências.
* 🧹 **Filtro Global de Ruído** — Sanitização automática das manchetes capturadas no navegador, removendo sufixos de portais (ex: " | G1", " - UOL") via Regex.

---

## **🏗️ Arquitetura do Sistema**

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
🛠️ Tecnologias Utilizadas
Tecnologia	Uso no Projeto
FastAPI	Framework principal do Backend, comunicação via rotas REST.
ChromaDB	Banco de dados vetorial para o funcionamento do RAG Local.
Sentence-Transformers	Criação de embeddings para busca semântica.
Groq API / Llama 3	Modelo de Linguagem primário ultrarrápido para extração e inferência.
OpenRouter API	Modelos de Linguagem secundários para o "Tribunal" e failover.
NewsAPI & DDGS	Coleta estruturada de evidências jornalísticas.
JS / HTML / CSS	Desenvolvimento da Extensão para Google Chrome (Frontend).
 
📋 Pré-requisitos
Python 3.9 ou superior instalado.

Navegador Google Chrome.

Chaves de API ativas das seguintes plataformas (Planos Gratuitos):

Groq Cloud

OpenRouter

NewsAPI

🚀 Como Instalar e Rodar
1. Clone o repositório
bash
git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
cd NOME_DO_REPOSITORIO
2. Crie e ative o ambiente virtual
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. Instale as dependências
bash
pip install fastapi uvicorn httpx pydantic beautifulsoup4 lxml google-api-python-client sentence-transformers scikit-learn numpy chromadb==0.4.24 newsapi-python duckduckgo-search

# IMPORTANTE: Forçar versão do NumPy compatível com ChromaDB
pip install numpy==1.26.4 --force-reinstall
4. Configure as Chaves de API
Abra os arquivos main.py e atualizador_rag.py e insira suas respectivas API_KEYS nas variáveis de configuração. (Em produção, utilize variáveis de ambiente .env).

5. Alimente o Banco de Dados (Web Scraping)
Antes de rodar a API, popule seu banco local executando o robô de coleta:

bash
python atualizador_rag.py
6. Inicie o Servidor
bash
uvicorn main:app --reload
O servidor estará rodando em http://127.0.0.1:8000.

📁 Estrutura do Projeto
text
A.I.D.-Fakenews/
├── backend/
│   ├── main.py               # API, RAG, Multi-Tools e Tribunal de IAs
│   ├── atualizador_rag.py    # Pipeline ETL que faz scraping e popula o DB
│   ├── database.json         # Base de conhecimento local em texto
│   └── chroma_db/            # Banco de dados vetorial gerado automaticamente
│
└── extension/                # Frontend
    ├── manifest.json         # Configuração da extensão do Chrome
    ├── popup.html            # Interface do usuário (UI)
    ├── popup.js              # Lógica de captura de aba e chamadas HTTP
    └── styles.css            # Estilos e animações
⚠️ Aviso Legal
Este projeto tem fins educacionais e de pesquisa em arquiteturas de Inteligência Artificial e combate à desinformação. O sistema baseia-se em interpretação probabilística de Modelos de Linguagem (LLMs) e informações publicamente disponíveis na web. Nenhum veredito gerado pelo A.I.D. deve ser considerado uma verdade absoluta ou laudo oficial. Sempre cheque fontes de jornais reconhecidos e agências de fact-checking.

👨‍💻 Autor
Luiz Santos — Analista de Suporte / Engenharia de Software
Construindo pontes entre Inteligência Artificial e a verdade factual.


Basta colar esse texto, não esquecendo de trocar o `SEU_USUARIO` e o `NOME_DO_REPOSITORIO` no passo 1 do guia de instalação pelo seu link real do GitHub! O resultado visual na plataforma vai ficar espetacular.
