<h1 align=center>Busca Diário Oficial</h1>

<p align="justify">Este repositório inclui o código para busca de dados em um site e envio de notificações via Telegram.</p>

Há basicamente 2 arquivos: 

<p>dependencias.txt: Inclui as bibliotecas necessárias para rodar o código.</p>
<p>buscado.py: Código python para busca no D.O de Nova Iguaçu.</p

Antes de rodar instale as bibliotecas listadas no arquivo dependencias.txt.

```bash
pip install selenium==4.23.1 requests==2.32.3 PyPDF2==3.0.1 schedule==1.2.2
```

Lembre também de criar o seu bot Telegram usando o botFather. Obtenha seu TOKEN e CHAT_ID e inclua no techo conforme abaixo

```
# Define o bot Telegram
TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
CHAT_ID = 'XXXXXXXXXXXX'
```

Não esqueça de incluit também seu nome na busca.
Escreva com as primeiras letras de nome e sobrenome em caixa alta

```
# Efetua busca de ocorrência de texto no arquivo
nome = "Escreva o Seu Nome Completo Aqui"
```

Observe os comentários com atenção. Por padrão não utilizei a opção headless. Atenção também ao fato que esse código
foi elaborado para uso com o Firefox. Com algumas alterações você também pode usá-lo com o Google Chrome ou mesmo Chromium.

<b>Use a ferramenta com reponsabilidade. Efetue no máximo 4 agendamentos para verificação durante o dia! Não há a necessidade de efetuar mais
agendamentos e sobrecarregar o site.</b>

Este tutorial foi elaborado por <b>Leonardo Bruno</b><p>
<b>souzalb@proton.me</b>

Encontrou algum erro? Sugestões?
