# Desafio NYT Scraping 

Este projeto realiza a extração de notícias do site do New York Times (NYT) de forma automatizada, utilizando Python, Selenium, Requests e Pandas. A automação é executada dentro de um container Docker, configurado para rodar no WSL2 (Ubuntu) em ambientes Windows.

## Descrição

- Busca e Filtragem: Pesquisa por um termo específico ("War in Ukraine"), filtra por seção (“World”) e seleciona notícias recentes dentro de um período configurável (em meses).
- Extração de Dados: Coleta título, data, descrição e imagem de cada notícia.
- Armazenamento: Salva os dados em um arquivo Excel e baixa as imagens localmente.
- Configuração Flexível: As variáveis de pesquisa (termo, seção e meses) podem ser definidas no arquivo config.json.

## Tecnologias Utilizadas

- Python 3.10
- Selenium: Interação automatizada com o site do NYT.
- Pandas: Manipulação de dados e exportação para Excel.
- Requests: Download das imagens.
- Docker + WSL2: Execução containerizada para garantir portabilidade e consistência do ambiente.

## Estrutura do Projeto 

desafio-nyt-scraping/
├── config.json            # Parâmetros de pesquisa e filtro
├── Dockerfile             # Definição do ambiente Docker
├── LICENSE                # (Opcional) Licença do projeto
├── NYScraping.py          # Script principal de automação
├── README.md              # Documentação do projeto
├── requirements.txt       # Dependências Python


## Como Executar 

1. **Clonar o repositório:**

git clone https://github.com/seu-usuario/desafio-nyt-scraping.git
cd desafio-nyt-scraping


2. **Configurar variáveis no arquivo config.json:**

frase_pesquisa: termo que será pesquisado ("War in Ukraine").
categoria: seção do NYT ("World").
numero_meses: quantos meses de notícias ("2").


3. **Construir a imagem Docker (no WSL2 ou ambiente Linux):**

docker build -t minha-automacao .


4. **Executar o container:**

docker run --rm \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/imagens:/app/imagens" \
  minha-automacao


# Observações

- Certifique-se de ter o Docker Desktop configurado para usar o WSL2 e a distribuição Ubuntu habilitada.
- Caso queira editar as variáveis (termo, seção, meses), basta alterar o arquivo config.json.
- Se ocorrer algum erro de versão entre Chrome e ChromeDriver, verifique se o Dockerfile está instalando Chromium e ChromiumDriver compatíveis.

# Licença

Este projeto pode ser licenciado sob a MIT License. Verifique o arquivo LICENSE para mais detalhes.

