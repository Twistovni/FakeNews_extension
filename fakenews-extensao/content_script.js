// Este script roda DENTRO da pagina do YouTube

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Quando o popup.js pedir os dados da pagina, esta funcao e executada
    if (request.action === "getPageContent") {
        
        // Encontra o titulo do video na pagina
        const videoTitle = document.querySelector('h1.style-scope.ytd-watch-metadata')?.textContent || document.title;
        
        // Encontra a descricao do video
        const descriptionElement = document.querySelector('#description-inner, #description.ytd-watch-metadata');
        const videoDescription = descriptionElement ? descriptionElement.innerText : '';

        // Envia o titulo e a descricao de volta para o popup.js
        sendResponse({
            title: videoTitle.trim(),
            description: videoDescription.trim()
        });
    }
    // Mantem a porta de comunicacao aberta para a resposta assincrona
    return true; 
});