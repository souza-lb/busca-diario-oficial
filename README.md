<h1 align=center>Busca Diário Oficial</h1>

<p align="justify">Este repositório inclui o código para busca de dados em um site e envio de notificações via Telegram, E-mail e Janela Tk.</p>

Há basicamente 3 arquivos: 

<p>dependencias.txt: Inclui as bibliotecas necessárias para rodar o código.</p>
<p>buscado.py: Código python para busca no D.O de Nova Iguaçu.</p>
<p>env: Arquivo de variáveis de ambiente.</p>

Antes de rodar instale as bibliotecas listadas no arquivo dependencias.txt.

```bash
pip install selenium==4.23.1 requests==2.32.3 PyPDF2==3.0.1 schedule==1.2.2 python-dotenv==1.0.1
```

Lembre também de criar o seu bot Telegram usando o botFather. Obtenha seu TOKEN e CHAT_ID.
Edite seu arquivo "env" de variáveis de ambiente conforme abaixo:

```
TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
CHAT_ID = 'XXXXXXXXXXXX'
```
Lembre de incluir também dados da conta para envio de E-mail. 
Se você utiliza autenticação de dois fatores, crie uma senha específica para uso no app.

```
EMAIL = "email_envio@exemplo.com"
SENHA_EMAIL = "evyk ifdk khdf zxwk" 
EMAIL_DESTINATARIO = "email_destinatario@exemplo.com"
```

Não esqueça de incluit também seu nome na busca.
Escreva com as primeiras letras de nome e sobrenome em caixa alta

```
NOME = "Escreva o Seu Nome Completo Aqui"
```

Para alterar o agendamento modifique o trecho abaixo:

```
# Configuração do agendamento.
horarios = ["08:05", "12:05", "16:05", "18:05"]
for hora in horarios:
    schedule.every().day.at(hora).do(busca_do)
```

Observe os comentários com atenção. Por padrão não utilizei a opção headless. Atenção também ao fato que esse código
foi elaborado para uso com o Firefox. Com algumas alterações você também pode usá-lo com o Google Chrome ou mesmo Chromium.

<b>Use a ferramenta com reponsabilidade. Efetue no máximo 4 agendamentos para verificação durante o dia! Não há a necessidade de efetuar mais
agendamentos e sobrecarregar o site.</b>

Este tutorial foi elaborado por <b>Leonardo Bruno</b><p>
<b>souzalb@proton.me</b>

Encontrou algum erro? Sugestões?
