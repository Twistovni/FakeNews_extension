# 🕵️‍♂️ A.I.D. — Agente Investigativo contra Desinformação

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Google Chrome](https://img.shields.io/badge/Google_Chrome-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)
![AI](https://img.shields.io/badge/AI-Groq%20%7C%20OpenRouter-orange?style=for-the-badge)

Um ecossistema híbrido de Fact-Checking composto por uma **Extensão para Chrome** e um **Backend avançado em Python (FastAPI)**. O A.I.D. cruza inteligência artificial, bancos de dados vetoriais locais e ferramentas de busca na web para validar a veracidade de notícias em tempo real, fornecendo aos usuários um dossiê investigativo e contexto educacional.

Projeto focado em combater as *Fake News* através de arquiteturas de Inteligência Artificial de última geração, incluindo **RAG Híbrido** e **Consenso Multi-Agente (Tribunal de Fatos)**.

---

## ✨ Funcionalidades

*   ⚡ **RAG Híbrido Ultrarrápido (Offline)** — Busca instantânea de notícias em uma base de conhecimento local, cruzando similaridade semântica (vetores) e textual (strings).
*   🌐 **Fact-Checking Ativo na Web** — Quando a notícia não está no banco local, o Agente busca ativamente evidências via **NewsAPI** ou usa o **DuckDuckGo** como fallback anti-bloqueio.
*   🧠 **Tribunal de Fatos (Consenso Multi-Agente)** — As evidências coletadas são processadas paralelamente por múltiplas LLMs (Groq e OpenRouter). O sistema avalia a concordância entre os modelos para garantir um veredito livre de alucinações.
*   🎓 **Contexto Educacional Rico** — Não entrega apenas "Verdadeiro" ou "Falso". A IA gera exemplos de manchetes reais (**🟢 Cenário Factual**) e boatos clássicos (**🔴 Boato Clássico**) sobre o tema.
*   👁️ **Expansão de Consulta (Visão Periférica)** — Antes de buscar na web, uma LLM extrai as entidades principais do título, otimizando os termos de busca para encontrar as melhores evidências.
*   🧹 **Filtro Global de Ruído** — Sanitização automática das manchetes capturadas no navegador, removendo sufixos de portais (ex: " | G1", " - UOL") via Regex.

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
