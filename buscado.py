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
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# Carregar variáveis de ambiente de arquivo local.
load_dotenv("./env")

# Configurar logger.
LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "buscado.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)

# Variáveis de ambiente.
NOME = os.getenv("NOME_BUSCA")
TOKEN = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = os.getenv("CHAT_ID_TELEGRAM")
EMAIL = os.getenv("EMAIL_ENVIO")
SENHA_EMAIL = os.getenv("SENHA_EMAIL")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINO")

def configurar_driver():
    options = Options()
    options.add_argument("-headless")
    return webdriver.Firefox(options=options)

# Acessa site e retorna url de D.O mais recente.
def acessar_site(driver):
    try:
        driver.get("https://www.doweb.novaiguacu.rj.gov.br/portal/diario-oficial")
        driver.find_element(By.XPATH, "/html/body/div[3]/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[6]/a[2]").click()
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[1])
        return driver.current_url
    except Exception as e:
        logging.error(f"Erro ao acessar o site: {e}")
        return None

# Faz o download de arquivo pdf do D.O mais recente.
def baixar_pdf(pdf_url):
    try:
        resposta = requests.get(pdf_url)
        resposta.raise_for_status()
        nome_arquivo = unquote(urlparse(pdf_url).path.split('/')[-1])
        logging.info(f"Arquivo D.O mais recente: {nome_arquivo}")
        caminho_arquivo = os.path.join("diario_oficial", nome_arquivo)
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        with open(caminho_arquivo, "wb") as f:
            f.write(resposta.content)
        return caminho_arquivo
    except requests.RequestException as e:
        logging.error(f"Erro ao baixar o PDF: {e}")
        return None

# Faz a busca pelo nome no arquivo.
def ler_pdf(caminho_arquivo, nome):
    paginas_nome = []
    try:
        with open(caminho_arquivo, "rb") as f:
            leitor = PyPDF2.PdfReader(f)
            for i, pagina in enumerate(leitor.pages):
                texto = pagina.extract_text()
                if texto and (nome in texto or nome.upper() in texto):
                    paginas_nome.append(i + 1)
    except Exception as e:
        logging.error(f"Erro ao ler o PDF: {e}")
    return paginas_nome

# Função para abertura do arquivo pdf na janela Tk.
def abrir_pdf(caminho_arquivo):
    if os.path.isfile(caminho_arquivo):
        try:
            if os.name == 'nt':
                os.startfile(caminho_arquivo)
            elif os.name == 'posix':
                subprocess.call(['xdg-open', caminho_arquivo])  # Para Linux
                # subprocess.call(['open', caminho_arquivo])  # Para macOS
        except Exception as e:
            logging.error(f"Erro ao abrir o PDF: {e}")

# Função para exibição da janela de alerta Tk.
def mostrar_janela(mensagem, caminho_arquivo):
    def run():
        root = tk.Tk()
        root.title("Busca D.O.")
        root.attributes('-topmost', True)
        
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        tk.Label(root, text=mensagem, padx=20, pady=20, justify='center').pack(expand=True)
        tk.Label(root, text=f"{nome_arquivo}", padx=20, pady=10).pack()

        tk.Button(root, text="Abrir PDF", command=lambda: abrir_pdf(caminho_arquivo)).pack(pady=10)
        root.after(60000, root.destroy)
        root.mainloop()
    
    Thread(target=run).start()

# Função para envio de notificação via Telegram.
def enviar_mensagem_telegram(mensagem, caminho_arquivo):
    
    # Endpoints API Telegram.
    url_mensagem = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    url_arquivo = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    dados_mensagem = {"chat_id": CHAT_ID, "text": mensagem}
    
    # Envio de mensagem.
    try:
        resposta = requests.post(url_mensagem, data=dados_mensagem, timeout=5)
        resposta.raise_for_status()
        logging.info(f"Mensagem Telegram enviada para: {CHAT_ID}")
    except requests.RequestException as e:
        logging.error(f"Erro ao enviar mensagem Telegram: {e}")
    
    # Envio do arquivo.
    try:
        with open(caminho_arquivo, "rb") as f:
            arquivos = {"document": f}
            resposta = requests.post(url_arquivo, data={"chat_id": CHAT_ID}, files=arquivos, timeout=5)
            resposta.raise_for_status()
            logging.info(f"Mensagem Telegram PDF enviada para: {CHAT_ID}")
    except requests.RequestException as e:
        logging.error(f"Erro ao enviar mensagem Telegram PDF: {e}")

# Função para envio de notificação por e-mail.
def enviar_email(mensagem, caminho_arquivo):
    try:
        envio = MIMEMultipart()
        envio["From"] = EMAIL
        envio["To"] = EMAIL_DESTINATARIO
        envio["Subject"] = f"Atualização Diário Oficial {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        envio.attach(MIMEText(mensagem, "plain"))
        
        
        # Adiciona anexo.
        if caminho_arquivo:
            with open(caminho_arquivo, "rb") as f:
                anexo = MIMEApplication(f.read(), _subtype="pdf")
                anexo.add_header('Content-Disposition', 'attachment', filename=os.path.basename(caminho_arquivo))
                envio.attach(anexo)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, SENHA_EMAIL)
            server.send_message(envio)
        logging.info(f"Mensagem e-mail enviada para: {EMAIL_DESTINATARIO}")
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")

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
            mensagem = (f"Olá {NOME}\n"
                        f"Seu nome foi localizado no D.O mais recente!\n" 
                        f"Verifique a(s) página(s): {paginas_evento}\n"
                        f"Última verificação em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            mensagem = (f"Olá {NOME}\n"
                        f"Seu nome ainda não saiu no D.O\n"
                        f"Última verificação em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logging.info(mensagem)
        mostrar_janela(mensagem, caminho_arquivo)
        enviar_mensagem_telegram(mensagem, caminho_arquivo)
        enviar_email(mensagem, caminho_arquivo)
    finally:
        # Fecha o driver.
        if driver:
            driver.quit()

# Configuração do agendamento
HORARIOS = ["08:05", "12:05", "16:05", "18:05"]
for hora in HORARIOS:
    schedule.every().day.at(hora).do(busca_do)

# Executa a primeira verificação e inicia o loop do agendamento
busca_do()
print("Programa em execução. Pressione CTRL+C para ENCERRAR.")

while True:
    schedule.run_pending()
    time.sleep(60)
