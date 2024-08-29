from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import requests
import PyPDF2
import io
from datetime import datetime
from urllib.parse import urlparse, unquote
import schedule
import os

# Função principal para processar o D.O.
def verifica_do():
    try:
        # Definição do nome para busca no D.O.
        nome = "INSIRA SEU NOME COMPLETO"

        # Define o bot Telegram.
        TOKEN = "INSIRA O SEU TOKEN"
        CHAT_ID = "INSIRA SEU CHAT ID"

        # Define o driver e opções.
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

        # Faz tentativa de acesso ao site.
        driver.get("https://www.doweb.novaiguacu.rj.gov.br/portal/diario-oficial")
        # Acessa link do  D.O mais recente e clica no botão.
        button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[6]/a[2]")
        button.click()
        # Aguarda a abertura da nova aba.
        time.sleep(5)
        # Alterna para a nova aba aberta.
        driver.switch_to.window(driver.window_handles[1])
        # Copia a url da nova aba aberta.
        pdf_url = driver.current_url
    except Exception as erro :
       print(f"Erro no acesso ao site: ({erro})")
    finally:
        driver.quit()

    # Bloco de captura e tratamento de arquivo.
    try:
        response = requests.get(pdf_url)
        print(f"Arquivo atual D.O: ({pdf_url})")
        parsed_url = urlparse(pdf_url)
        nome_arquivo = unquote(parsed_url.path.split('/')[-1])
        # Criação de pasta.
        pasta_do = "diario_oficial"
        if not os.path.exists(pasta_do):
            os.makedirs(pasta_do)
        # Escrita arquivo.
        caminho_arquivo = f"./{pasta_do}/{nome_arquivo}"
        with open(caminho_arquivo, "wb") as arquivo:
            arquivo.write(response.content)
    except Exception as erro :
        print(f"Erro ao obter arquivo PDF: ({erro})")

    try:
        # Leitura do conteúdo do arquivo.
        with open(caminho_arquivo, "rb") as arquivo:
            reader = PyPDF2.PdfReader(arquivo)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
    except Exception as erro :
        print(f"Erro na leitura do arquivo PDF: ({erro})")

    try:
        # Criação e envio da mensagem pela API Telegram.
        if nome in text or nome.upper() in text:
            mensagem = f"Seu nome saiu no D.O Última verificação em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        else:
            mensagem = f"Seu nome ainda não saiu no D.O Última verificação em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

        print(mensagem)

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": mensagem
        }
        resposta = requests.post(url, data=payload, timeout=10)
        # Verifica resposta API Telegram.
        if resposta.status_code == 200:
            print(f"Mensagem Telegram Enviada com sucesso em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            print(f"Falha no envio da mensagem Telegram:{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} // {(resposta)}")
    except Exception as erro :
        print(f"Erro na conexão com o servidor Telegram: ({resposta}) // Saída Erro: ({erro})")

# Executa a primeira verificação.
verifica_do()

print(f"Pressione CTRL+C para ENCERRAR o programa.")
# Define os horários de execução
schedule.every().day.at("08:05").do(verifica_do)
schedule.every().day.at("12:05").do(verifica_do)
schedule.every().day.at("16:05").do(verifica_do)
schedule.every().day.at("18:05").do(verifica_do)

# Loop contínuo para verificar e executar tarefas agendadas
while True:
    schedule.run_pending()
    time.sleep(60)  # Espera um minuto antes de verificar novamente
