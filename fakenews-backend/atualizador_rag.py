import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
logging.getLogger("urllib3").setLevel(logging.ERROR)

import os
import json
from pathlib import Path
from datetime import datetime
import time
import asyncio
import httpx
from googleapiclient.discovery import build
from urllib.parse import quote
from bs4 import BeautifulSoup

# --- CONFIGURAÇÃO E CHAVES ---
# Chave do YouTube (Mantida para busca de canais e tendências)
YOUTUBE_API_KEY = "AIzaSyCSJ4F3vSo4vyUP9c3_g3YeZuRm2anped4"

# NOVA CHAVE EXCLUSIVA DO GOOGLE FACT CHECK (Garante imunidade ao erro 403)
GOOGLE_API_KEY = "AIzaSyD_7_BRDm2QzuJDcXQnL6VyzjIT1Kr77Rg"

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "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"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.json"

PORTAIS_PARA_RASPAGEM = {
    "Brasil": [
        {"nome": "G1", "url": "https://g1.globo.com/", "selector": "a.feed-post-link"},
        {"nome": "UOL", "url": "https://www.uol.com.br/", "selector": "a.hyperlink.headlineMain__link"},
        {"nome": "Folha", "url": "https://www.folha.uol.com.br/", "selector": "a.c-main-headline__url, a.c-headline__url"},
        {"nome": "Estadão", "url": "https://www.estadao.com.br/", "selector": "a.link-title"},
        {"nome": "CNN Brasil", "url": "https://www.cnnbrasil.com.br/", "selector": "a.home__title, h2.home__title"},
        {"nome": "R7", "url": "https://www.r7.com/", "selector": "a.r7-flex-title-link"},
        {"nome": "Metrópoles", "url": "https://www.metropoles.com/", "selector": "h2.m-title a, h3.m-title a"}
    ],
    "Mundo": [
        {"nome": "Reuters", "url": "https://www.reuters.com/", "selector": "a.media-story-card__heading__33b35"},
        {"nome": "AP News", "url": "https://apnews.com/", "selector": "a.hub-a-link"},
        {"nome": "BBC News", "url": "https://www.bbc.com/news", "selector": "a.gs-c-promo-heading"}
    ]
}

def buscar_checagem_google(titulo: str):
    """Busca no Google Fact Check por validações e selos oficiais de checagem."""
    try:
        query = quote(titulo)
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&languageCode=pt-BR&key={GOOGLE_API_KEY}"
        res = httpx.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if "claims" in data and data["claims"]:
            claim = data["claims"][0]
            review = claim["claimReview"][0]
            rating = review.get("textualRating", "").lower()
            
            label = None
            if any(p in rating for p in ["verdadeiro", "fato", "true", "factual"]): 
                label = True
            elif any(p in rating for p in ["falso", "false", "boato", "fakenews", "mentira"]): 
                label = False
            
            if label is not None:
                publisher_name = review.get('publisher', {}).get('name', 'Agência Oficial')
                return {
                    "label": label,
                    "text": f"Checagem Oficial ({publisher_name}): {review.get('title', 'N/A')}",
                    "reliability": 98
                }
    except Exception as e:
        print(f"   ! Falha na API do Google Fact Check: {e}")
    return None

async def chamar_ia_para_analise(client: httpx.AsyncClient, titulo: str):
    """Fallback: Se não houver checagem oficial, usa a inteligência do OpenRouter (ou Groq)."""
    prompt = f'Analise o título: "{titulo}". Responda APENAS com um JSON válido com as chaves "label" (bool) e "text" (string).'
    try:
        # OpenRouter - Gemma 2
        payload = {"model": "google/gemma-2-9b-it:free", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        res = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}, timeout=20)
        res.raise_for_status()
        return json.loads(res.json()["choices"][0]["message"]["content"])
    except Exception:
        try:
            # Groq - Llama 3
            payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
            res = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=20)
            res.raise_for_status()
            return json.loads(res.json()["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"   ❌ Falha em ambas as IAs para '{titulo[:30]}...': {e}")
            return None

async def etapa_1_raspagem_de_portais(client: httpx.AsyncClient):
    """Coleta notícias de 10 grandes portais do Brasil e do Mundo de forma assíncrona paralelizada."""
    print("📰 Etapa 1: Coletando notícias dos portais...")
    tasks = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    lista_portais = []
    for regiao, portais in PORTAIS_PARA_RASPAGEM.items():
        for portal in portais:
            lista_portais.append(portal)
            tasks.append(client.get(portal['url'], headers=headers, timeout=15))
    
    titulos = []
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, res in enumerate(responses):
        if isinstance(res, httpx.Response):
            portal = lista_portais[i]
            try:
                sopa = BeautifulSoup(res.content, 'lxml')
                for link in sopa.select(portal['selector'])[:5]:
                    t = link.get_text(strip=True)
                    if len(t) > 40:
                        titulos.append(t)
            except Exception as e:
                print(f"     ! Erro de parsing em {portal['nome']}: {e}")
                
    return list(set(titulos))

def etapa_2_busca_youtube():
    """Busca vídeos recentes no YouTube em tópicos sensíveis de debate social."""
    print("🎥 Etapa 2: Coletando tendências do YouTube...")
    titulos_videos = []
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY, cache_discovery=False)
        for termo in ["notícias brasil hoje", "tecnologia e ia novidades", "política brasileira debate"]:
            req = youtube.search().list(part="snippet", q=termo, type="video", order="date", maxResults=3, regionCode="BR").execute()
            for item in req.get("items", []):
                titulos_videos.append(item["snippet"]["title"])
    except Exception as e:
        print(f"   ! Falha na API do YouTube: {e}")
    return list(set(titulos_videos))

async def main():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- INICIANDO ATUALIZADOR EM CAMADAS ---")
    
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db_atual = json.load(f)
    except:
        db_atual = []
    existentes = {n.get("title", "").lower().strip() for n in db_atual}
    
    async with httpx.AsyncClient() as client:
        task_web = etapa_1_raspagem_de_portais(client)
        task_yt = asyncio.to_thread(etapa_2_busca_youtube)
        resultados_web, resultados_yt = await asyncio.gather(task_web, task_yt)
        
    novos_titulos = set(resultados_web + resultados_yt) - existentes
    
    if not novos_titulos:
        print("--- RAG já está atualizado. ---")
        return

    print(f"\n🤖 Analisando {len(novos_titulos)} novidades com checagem de fatos priorizada...")
    
    novas_entradas = []
    async with httpx.AsyncClient() as client:
        for titulo in novos_titulos:
            info = None
            
            # --- CAMADA 1: Google Fact Check ---
            checagem_oficial = await asyncio.to_thread(buscar_checagem_google, titulo)
            
            if checagem_oficial:
                print(f"   ✅ Match no Google Fact Check: '{titulo[:40]}...'")
                info = checagem_oficial
            else:
                # --- CAMADA 2: Inteligência Artificial (OpenRouter/Groq) ---
                analise_ia = await chamar_ia_para_analise(client, titulo)
                if analise_ia:
                    info = {
                        "label": analise_ia.get("label") is True,
                        "text": f"Análise IA: {analise_ia.get('text', '')}",
                        "reliability": 85
                    }

            if info:
                novas_entradas.append({"title": titulo, **info})
            time.sleep(1.2) # Pausa segura de requisições

    if novas_entradas:
        uid = max((n.get("id", 0) for n in db_atual), default=0)
        for n in novas_entradas:
            uid += 1
            n["id"] = uid
            db_atual.append(n)
        
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db_atual, f, indent=2, ensure_ascii=False)
        print(f"\n--- SUCESSO: {len(novas_entradas)} notícias salvas no banco de dados. ---")

if __name__ == "__main__":
    asyncio.run(main())
