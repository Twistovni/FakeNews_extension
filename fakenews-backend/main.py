import warnings
import logging

# Silencia avisos desnecessários para um terminal mais limpo
warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("urllib3").setLevel(logging.ERROR)

import os
import json
import difflib
import re
import random
from urllib.parse import quote
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
import httpx
import time

# --- CONFIGURAÇÃO E CHAVES ---
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "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"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.json"

app = FastAPI(
    title="A.I.D. Verificador Híbrido Assíncrono",
    description="API para análise de desinformação com RAG turbinado e LLM"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DOMINIOS_CONFIAVEIS = {
    "G1": "g1.globo.com",
    "UOL": "uol.com.br",
    "Estadão": "estadao.com.br",
    "Folha de S.Paulo": "folha.uol.com.br",
    "CNN Brasil": "cnnbrasil.com.br"
}

# --- SISTEMA DE CACHE INTELIGENTE EM MEMÓRIA RAM ---
CACHE_DB = []
ULTIMA_MODIFICACAO = 0

def obter_banco_em_memoria():
    """
    Lê o banco de dados do disco apenas na primeira vez ou se o arquivo foi modificado.
    Em todas as outras chamadas, retorna a versão em cache na memória RAM.
    """
    global CACHE_DB, ULTIMA_MODIFICACAO
    try:
        modificacao_atual = os.path.getmtime(DB_PATH)
        if modificacao_atual > ULTIMA_MODIFICACAO:
            print("💾 Recarregando banco de dados do disco para o cache em memória...")
            with open(DB_PATH, "r", encoding="utf-8") as f:
                CACHE_DB = json.load(f)
            ULTIMA_MODIFICACAO = modificacao_atual
            print("✅ Cache atualizado com sucesso!")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Aviso: Não foi possível carregar o banco de dados: {e}")
        CACHE_DB = []
    return CACHE_DB

# --- MODELO DE VALIDAÇÃO (Pydantic) ---
class Consulta(BaseModel):
    text: str = Field(..., min_length=10, max_length=250)
    use_llm: bool

    @field_validator('text')
    @classmethod
    def text_must_contain_words(cls, v):
        if len(v.split()) < 2:
            raise ValueError('A consulta deve conter pelo menos duas palavras.')
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('A consulta deve conter letras.')
        return v.strip()

# --- FUNÇÃO DE ANÁLISE LOCAL (RAG OTIMIZADO) ---
def analise_local_rag_contextual(titulo_usuario: str):
    db = obter_banco_em_memoria()  # Usa a versão em cache, muito mais rápida
    if not db: return None

    titulo_limpo = re.sub(r'\s*[-\|]\s*[\w\s]+$', '', titulo_usuario.lower().strip(), flags=re.IGNORECASE)

    # Loop Otimizado: Calcula o score uma vez só
    melhor_match = None
    melhor_score = 0.0
    for item in db:
        titulo_bd = item.get("title", "").lower()
        score_inicio = difflib.SequenceMatcher(None, titulo_limpo[:70], titulo_bd[:70]).ratio()
        score_total = difflib.SequenceMatcher(None, titulo_limpo, titulo_bd).ratio()
        score_calculado = (score_inicio * 0.7) + (score_total * 0.3)
        if score_calculado > melhor_score:
            melhor_score = score_calculado
            melhor_match = item
    
    # Lógica de Contexto
    palavras_chave = {p for p in titulo_limpo.split() if len(p) > 3} - {"o", "a", "e", "de", "que", "do", "da", "em"}
    rel_v = [n['title'] for n in db if n.get("label") and n.get('title') != melhor_match.get('title') and len(palavras_chave.intersection(set(n.get('title', '').lower().split()))) >= 2][:2]
    rel_f = [n['title'] for n in db if not n.get("label") and n.get('title') != melhor_match.get('title') and len(palavras_chave.intersection(set(n.get('title', '').lower().split()))) >= 2][:2]

    # Cenário 1: Match Direto
    if melhor_score > 0.65:
        veredicto = "✅ VERDADEIRO" if melhor_match.get("label") else "❌ FALSO (Segundo análise prévia)"
        texto_resp = f"<b>Fato Encontrado:</b> {melhor_match.get('title', '')}<br><b>Detalhes:</b> {melhor_match.get('text', '')}"
        if rel_v or rel_f:
            texto_resp += "<br><br>📚 <b>Contexto Adicional sobre o Tema:</b>"
            if rel_f: texto_resp += "<br>🔴 <b>Exemplos de Desinformação:</b><ul>" + "".join(f"<li>{t}</li>" for t in rel_f) + "</ul>"
            if rel_v: texto_resp += "<br>🟢 <b>Exemplos de Fatos Verídicos:</b><ul>" + "".join(f"<li>{t}</li>" for t in rel_v) + "</ul>"
        return {"label": veredicto, "text": texto_resp, "reliability": int(melhor_score * 100), "source": "RAG Local"}

    # Cenário 2: Match Indireto (Contextual)
    if rel_v or rel_f:
        texto_resp = "Não encontrei um match direto, mas achei os seguintes contextos no banco:<br><br>"
        if rel_f: texto_resp += "<b>🔴 Mentiras Mapeadas:</b><ul>" + "".join(f"<li>{t}</li>" for t in rel_f) + "</ul>"
        if rel_v: texto_resp += "<b>🟢 Fatos Mapeados:</b><ul>" + "".join(f"<li>{t}</li>" for t in rel_v) + "</ul>"
        return {"label": "❓ INCONCLUSIVO", "text": texto_resp, "reliability": 50, "source": "RAG Contextual"}

    return None

def limpar_json_ia(conteudo: str) -> dict:
    try:
        conteudo = conteudo.strip()
        if conteudo.startswith("```"):
            conteudo = conteudo.strip("`").replace("json", "", 1).strip()
        return json.loads(conteudo)
    except json.JSONDecodeError:
        # Se falhar, retorna um dicionário vazio para não quebrar o código principal
        return {}

# --- FUNÇÃO DE CHAMADA À IA (MÁXIMA PERFORMANCE) ---
async def chamar_provedor_ia_assincrono(prompt: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Tentativa Primária: OpenRouter
        try:
            print("\n🧠 Tentando OpenRouter...")
            payload = {"model": "openrouter/free", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            res.raise_for_status()
            dados = limpar_json_ia(res.json()["choices"][0]["message"]["content"])
            return dados, "A.I.D. (OpenRouter)"
        except Exception as e_or:
            print(f"⚠️ OpenRouter falhou ({e_or}). Acionando backup Groq...")

        # 2. Tentativa Secundária: Groq
        try:
            print("⚡️ Tentando Groq (Llama 3)...")
            payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2, "response_format": {"type": "json_object"}}
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            res = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
            res.raise_for_status()
            dados = limpar_json_ia(res.json()["choices"][0]["message"]["content"])
            return dados, "A.I.D. (Groq)"
        except Exception as e_groq:
            raise HTTPException(status_code=503, detail=f"Sistemas de IA indisponíveis no momento: {e_groq}")

# --- ROTA PRINCIPAL DA API ---
@app.post("/analisar")
async def analisar_noticia(consulta: Consulta):
    if not consulta.use_llm:
        resultado = analise_local_rag_contextual(consulta.text)
        if resultado: return resultado
        raise HTTPException(status_code=404, detail="Não encontrado no banco. Ative a 'IA Avançada' no rodapé.")

    prompt_aid = f"""
    Você é o A.I.D. — Agente Investigativo contra Desinformação. Sua missão é avaliar: "{consulta.text}".
    REGRA DE OURO: Se o texto parecer uma manchete jornalística real, NÃO o classifique como FALSO só por precaução. Assuma como '✅ VERDADEIRO' (plausível) ou '❓ INCONCLUSIVO' (incerto). Guarde o '❌ FALSO' para exageros óbvios, conspirações ou mentiras claras.
    Responda APENAS E EXCLUSIVAMENTE em formato JSON com as chaves: "verdict" (string), "confidence_score" (int), "objective_explanation" (array de strings), "educational_context" (objeto com "true_example" e "fake_example"), e "investigation_keywords" (array de strings).
    """
    
    dados_ia, provedor_usado = await chamar_provedor_ia_assincrono(prompt_aid)

    # --- FORMATAÇÃO ROBUSTA DA RESPOSTA ---
    texto_resp = "🧠 <b>Explicação Objetiva:</b><ul>"
    explicacao = dados_ia.get("objective_explanation", [])
    if isinstance(explicacao, list): texto_resp += "".join(f"<li>{item}</li>" for item in explicacao)
    texto_resp += "</ul>"

    contexto = dados_ia.get("educational_context")
    if contexto and isinstance(contexto, dict):
        t_ex = contexto.get('true_example', 'N/A')
        f_ex = contexto.get('fake_example', 'N/A')
        if t_ex not in ('N/A', 'None', ''): texto_resp += f"<br><b>🟢 Cenário Factual:</b> <i>'{t_ex}'</i>"
        if f_ex not in ('N/A', 'None', ''): texto_resp += f"<br><b>🔴 Cenário Enganoso:</b> <i>'{f_ex}'</i>"

    keywords = dados_ia.get("investigation_keywords")
    if keywords and isinstance(keywords, list):
        portal_nome, portal_dominio = random.choice(list(DOMINIOS_CONFIAVEIS.items()))
        termo = " ".join([str(k) for k in keywords])
        link = f"https://www.google.com/search?q={quote(f'site:{portal_dominio} {termo}')}"
        texto_resp += f"<br><br>🔗 <b>Investigue: <a href='{link}' target='_blank'>Pesquise sobre '{termo}' no {portal_nome}</a>.</b>"

    return {"label": dados_ia.get("verdict", "❓ INCONCLUSIVO"), "text": texto_resp, "reliability": dados_ia.get("confidence_score", 0), "source": provedor_usado}

# --- Ponto de Entrada para Execução Direta ---
if __name__ == "__main__":
    import uvicorn
    # Carrega o banco de dados em memória na primeira inicialização
    obter_banco_em_memoria()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
