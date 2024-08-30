import os
import time
import requests
import PyPDF2
import logging
import schedule
from datetime import datetime
from urllib.parse import urlparse, unquote
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import tkinter as tk

# Configuração do logger
pasta_log = "log"
os.makedirs(pasta_log, exist_ok=True)
arquivo_log = os.path.join(pasta_log, "buscado.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(arquivo_log, encoding='utf-8')
    ]
)

# Nome para busca.
NOME = "Nome para busca"

# Dados bot Telegram.
TOKEN = "Seu Token para o Bot Telegram"
CHAT_ID = "Chat id do seu usuário"

# Função para configuração do driver.
def configurar_driver():
    options = Options()
    options.add_argument("-headless")
    return webdriver.Firefox(options=options)

# Função para acesso ao site e captura de url do D.O.
def acessar_site(driver):
    try:
        driver.get("https://www.doweb.novaiguacu.rj.gov.br/portal/diario-oficial")
        driver.find_element(By.XPATH, "/html/body/div[3]/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[6]/a[2]").click()
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[1])
        return driver.current_url
    except Exception as erro:
        logging.error(f"Erro ao acessar o site: {erro}")
        return None

# Função para download do PDF.
def baixar_pdf(pdf_url):
    try:
        resposta = requests.get(pdf_url)
        resposta.raise_for_status()
        nome_arquivo = unquote(urlparse(pdf_url).path.split('/')[-1])
        logging.info(f"Arquivo D.O mais recente: {nome_arquivo}")
        caminho_arquivo = os.path.join("diario_oficial",nome_arquivo)
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        with open(caminho_arquivo, "wb") as arquivo:
            arquivo.write(resposta.content)
        return caminho_arquivo
    except requests.RequestException as erro:
        logging.error(f"Erro ao baixar o PDF: {erro}")
        return None

# Função para leitura e processamento do arquivo.
def ler_pdf(caminho_arquivo, nome):
    # Lista com a(s) página(s) onde o nome foi localizado.
    paginas_nome = []
    try:
        with open(caminho_arquivo, "rb") as arquivo:
            leitor = PyPDF2.PdfReader(arquivo)
            for i, pagina in enumerate(leitor.pages):
                texto = pagina.extract_text()
                if texto and (nome in texto or nome.upper() in texto):
                    paginas_nome.append(i + 1)
    except Exception as erro:
        logging.error(f"Erro ao ler o PDF: {erro}")
    return paginas_nome

# Função para exibir janela alerta Tk.
def mostrar_janela(mensagem):
    def run():
        root = tk.Tk()
        root.title("Busca D.O.")
        # Janela no topo.
        root.attributes('-topmost', True)
        label = tk.Label(root, text=mensagem, padx=20, pady=20, justify='center')
        label.pack(expand=True)
        # Fecha a janela após 30 segundos (10000 milissegundos)
        root.after(30000, root.destroy)
        root.mainloop()
    
    # Executa a janela em uma thread separada
    janela_thread = Thread(target=run)
    janela_thread.start()

# Função para envio de mensagem Telegram.
def enviar_mensagem_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requisicao = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        resposta = requests.post(url, data=requisicao, timeout=10)
        reposta.raise_for_status()
        logging.info(f"Mensagem Telegram enviada com sucesso.")
    except requests.RequestException as erro:
        logging.error(f"Erro ao enviar mensagem Telegram.")

# Função principal.
def busca_do():
    driver = None
    try:
        driver = configurar_driver()
        pdf_url = acessar_site(driver)
        if not pdf_url:
            return

        caminho_arquivo = baixar_pdf(pdf_url)
        if not caminho_arquivo:
            return

        paginas_nome = ler_pdf(caminho_arquivo, NOME)
        if paginas_nome:
            paginas_evento = ", ".join(map(str, paginas_nome))
            mensagem = (f"Seu nome foi localizado no D.O mais recente! \n" 
                        f"verifique a(s) página(s): {paginas_evento} \n"
                        f"Última verificação em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            mensagem = (f"Seu nome ainda não saiu no D.O \n "
                        f"Última verificação em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logging.info(mensagem)
        mostrar_janela(mensagem)
        enviar_mensagem_telegram(mensagem)
    finally:
        if driver:
            driver.quit()

# Configuração do agendamento.
horarios = ["08:05", "12:05", "16:05", "18:05"]
for hora in horarios:
    schedule.every().day.at(hora).do(busca_do)

# Executa a primeria verificação e inicia o loop do agendamento.
busca_do()
print("Programa em execução. Pressione CTRL+C para ENCERRAR.")

while True:
    schedule.run_pending()
    time.sleep(60)



