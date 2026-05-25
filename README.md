# 🤖 Monitorador Multicloud de Preços (Anti-WAF)

Um sistema avançado de rastreamento de preços de e-commerces focado em contornar bloqueios militares de segurança (WAFs como Akamai Bot Manager e Cloudflare). O projeto utiliza estratégias híbridas de extração, variando desde consumo de APIs furtivas até injeção de navegadores indetectáveis.

## 🚀 Funcionalidades

* **Bypass de Firewalls Avançados:** Utiliza `SeleniumBase UC (Undetected Mode)` para falsificar impressões digitais de rede e renderizar páginas sem disparar CAPTCHAs.
* **Extração de Imagens em Alta Resolução:** Interceptação inteligente de tags Open Graph (`og:image`) para ignorar Favicons e capturar a foto real do produto.
* **Fallback de Interface (RPA):** Módulo de contingência nativo utilizando `pyautogui` para leitura física da tela quando bloqueios de rede são intransponíveis.
* **Alertas em Tempo Real:** Integração direta com a API do Telegram Bot para notificação instantânea quando a meta de preço é atingida.
* **Armazenamento de Histórico:** Salvamento contínuo da flutuação de preços em arquivo `CSV` estruturado.

## 🛒 Lojas Monitoradas e Status Atual

| E-commerce | Motor de Extração | Status |
| :--- | :--- | :--- |
| **Mercado Livre** | Playwright (Motor Leve) | ✅ Estável |
| **Amazon Brasil** | Playwright (Motor Leve) | ✅ Estável |
| **AliExpress** | Playwright (Motor Leve) | ✅ Estável |
| **Magazine Luiza** | SeleniumBase UC | ✅ Estável |
| **Casas Bahia** | SeleniumBase UC | ✅ Estável |
| **Shopee Brasil** | SeleniumBase UC / API | ⚠️ Em Desenvolvimento |

## 🛠️ Tecnologias e Bibliotecas Principais

* `SeleniumBase`: Motor principal para renderização indetectável (Undetected ChromeDriver).
* `curl_cffi`: Camuflagem de impressão digital TLS para requisições de API limpas.
* `Playwright`: Navegação leve para sites com baixa restrição de bots.
* `BeautifulSoup4`: Parseamento elegante de HTML e varredura de tags JSON-LD de SEO.

## ⚙️ Como Instalar e Rodar

1. Clone o repositório para a sua máquina.
2. Crie e ative um ambiente virtual (`venv`).
3. Instale as dependências executando:
   ```bash
   pip install -r requirements.txt
4. Configure as chaves do seu Bot do Telegram nas variáveis de ambiente ou no arquivo de configuração principal.
5. Inicie o monitoramento multicloud:
    python main.py
