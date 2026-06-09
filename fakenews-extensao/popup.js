const textToAnalyze = document.getElementById('text-to-analyze');
const resultArea = document.getElementById('result-area');
const analyzeButton = document.getElementById('analyze-button');
const llmToggle = document.getElementById('llm-toggle');

function setLoading(isLoading) {
    analyzeButton.disabled = isLoading;
    if (isLoading) {
        analyzeButton.innerHTML = '<div class="spinner"></div><span>Analisando...</span>';
    } else {
        analyzeButton.innerHTML = '<span>Analisar Texto</span>';
    }
}

function showResult(data) {
    let bgColor, textColor;
    switch (data.label) {
        case "Verdadeiro": bgColor = 'var(--success-bg)'; textColor = 'var(--success-text)'; break;
        case "Falso": bgColor = 'var(--error-bg)'; textColor = 'var(--error-text)'; break;
        default: bgColor = 'var(--warning-bg)'; textColor = 'var(--warning-text)'; break;
    }
    resultArea.style.backgroundColor = bgColor;
    resultArea.style.color = textColor;

    const confidenceText = `${data.source || 'IA'} (${data.reliability}%)`;

    resultArea.innerHTML = `<span class="source">${confidenceText}</span><strong>${data.label}</strong><p style="margin: 8px 0 0 0;">${data.text}</p>`;
    resultArea.style.display = 'block';

    resultArea.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            chrome.tabs.create({ url: link.href });
        });
    });
}

function showError(message) {
    resultArea.style.backgroundColor = 'var(--warning-bg)';
    resultArea.style.color = 'var(--warning-text)';
    resultArea.innerHTML = `<strong>Aviso:</strong> ${message}`;
    resultArea.style.display = 'block';
}

async function analyzeContent() {
    setLoading(true);
    resultArea.style.display = 'none';
    try {
        const useLLM = llmToggle.checked;
        const content = textToAnalyze.value;

        if (!content || content.trim() === "") throw new Error("A caixa de texto está vazia.");

        const response = await fetch("http://localhost:8000/analisar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: content, use_llm: useLLM })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erro no servidor (código: ${response.status})`);
        }
        
        showResult(await response.json());
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function extrairDadosDaPagina() {
    let titulo = document.title;
    let contexto = "";
    if (window.location.hostname.includes("youtube.com") && window.location.pathname === "/watch") {
        const ytTitleElement = document.querySelector('h1.ytd-video-primary-info-renderer');
        if (ytTitleElement) titulo = ytTitleElement.innerText;
        const ytDescElement = document.querySelector('#description-inner yt-formatted-string');
        if (ytDescElement) contexto = " | Contexto: " + ytDescElement.innerText.substring(0, 300).replace(/\n/g, " ");
    }
    return titulo + contexto;
}

document.addEventListener("DOMContentLoaded", async () => {
    chrome.storage.local.get(['useLLM'], result => llmToggle.checked = !!result.useLLM);
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.scripting.executeScript({ target: { tabId: tab.id }, func: extrairDadosDaPagina }, 
            (results) => {
                if (results && results[0] && results[0].result) {
                    textToAnalyze.value = results[0].result;
                } else {
                    textToAnalyze.placeholder = "Não foi possível ler o título. Cole o texto aqui.";
                }
            }
        );
    } catch (e) {
        textToAnalyze.placeholder = "Erro ao acessar a aba.";
    }
    analyzeButton.addEventListener("click", analyzeContent);
    llmToggle.addEventListener('change', event => chrome.storage.local.set({ useLLM: event.currentTarget.checked }));
});