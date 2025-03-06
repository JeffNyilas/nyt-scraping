FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o requirements.txt
COPY requirements.txt .

# Instala dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Instala Chromium e ChromiumDriver do repositório
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver

# Copia todo o resto do projeto
COPY . .

# Ajuste para o nome do seu script principal
CMD ["python", "NYScraping.py"]
