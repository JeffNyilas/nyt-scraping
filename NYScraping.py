import os
import json
import re
import time
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

def parse_data_publicacao(data_str):
    """
    Converte o texto de data em um formato padronizado 'Month DD, YYYY'.
    - Se contiver 'ago' (ex: '9 hours ago'), usa a data de hoje.
    - Se já tiver ano (ex: 'March 3, 2025'), mantém como está.
    - Se for 'March 4' (sem vírgula/ano), assume o ano atual.
    """
    data_str = data_str.strip().rstrip(',')
    if "ago" in data_str.lower():
        return datetime.now().strftime("%B %d, %Y")
    if re.search(r'\d{4}', data_str):
        return data_str
    try:
        dt = datetime.strptime(data_str, "%B %d")
        dt = dt.replace(year=datetime.now().year)
        return dt.strftime("%B %d, %Y")
    except ValueError:
        return data_str

def automacao_nytimes(frase_pesquisa, categoria, numero_meses):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Utiliza o objeto Service para inicializar o ChromeDriver
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Define diretórios para salvar imagens, se necessário
        current_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(current_dir, "imagens")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # 1. Acessa o site do NYTimes
        driver.get("https://www.nytimes.com/")
        driver.maximize_window()
        print("Site acessado!")
        
        # 2. Fecha pop-up de privacidade, se aparecer
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="fides-button-group"]/div[1]/button[2]'))
            ).click()
            print("Preferências de privacidade aceitas.")
        except Exception as e:
            print("Pop-up de privacidade não apareceu ou já foi fechado.", e)
        
        # 3. Fecha pop-up de termos de uso, se aparecer
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="complianceOverlay"]/div/div/button/div/span[1]/span'))
            ).click()
            print("Termos de uso clicados.")
        except Exception as e:
            print("Pop-up de termos de uso não apareceu ou já foi fechado.", e)
        
        # Aguarda o overlay de compliance desaparecer
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "complianceOverlay"))
            )
            print("Overlay de compliance desapareceu.")
        except Exception as e:
            print("Overlay de compliance ainda visível, mas prosseguindo...", e)
        
        # 4. Clica no botão de pesquisa
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div[2]/header/section[1]/div[1]/div/button'))
        ).click()
        print("Botão de pesquisa clicado.")
        
        # 5. Digita e envia a frase de pesquisa
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[data-testid="search-input"]'))
        )
        search_box.send_keys(frase_pesquisa)
        search_box.send_keys(Keys.ENTER)
        print("Termo de pesquisa digitado e enviado.")
        
        # 6. Fecha overlay se reaparecer após a busca
        time.sleep(2)
        try:
            compliance_btn2 = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="complianceOverlay"]/div/div/button/div/span[1]/span'))
            )
            compliance_btn2.click()
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "complianceOverlay"))
            )
            print("Overlay de compliance fechado novamente após a busca.")
        except Exception as e:
            print("Nenhum overlay adicional apareceu após a busca.", e)
        
        # 7. Clica no botão de seção (usando o XPATH fornecido)
        section_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[2]/div/div/button'))
        )
        section_button.click()
        print("Botão de seção clicado.")
        
        # 8. Seleciona a opção "World" (usando o XPATH fornecido)
        world_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[10]/label/span'))
        )
        world_option.click()
        print("Opção 'World' selecionada.")
        
        # 9. Seleciona a opção de período: "notícias mais recentes"
        select_periodo = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/form/div[2]/div[1]/select'))
        )
        select_periodo.click()
        option_mais_recentes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/form/div[2]/div[1]/select/option[2]'))
        )
        option_mais_recentes.click()
        print("Opção 'notícias mais recentes' selecionada.")
        
        # Aguarda o carregamento dos resultados
        time.sleep(3)
        
        # 10. Coleta todas as notícias
        noticias = driver.find_elements(By.XPATH, '//li[@data-testid="search-bodega-result"]')
        print(f"Foram encontradas {len(noticias)} notícias.")
        
        # Filtra por período: calcula a data de corte com base no número de meses
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=numero_meses)
        dados_lista = []
        ordem = 0
        
        for noticia in noticias:
            ordem += 1
            try:
                # Extração do título
                titulo_elem = noticia.find_element(By.TAG_NAME, 'h4')
                titulo = titulo_elem.text.strip() if titulo_elem else ""
                
                # Extração da descrição (se disponível)
                try:
                    descricao_elem = noticia.find_element(By.CSS_SELECTOR, 'p.css-e5tzus')
                    descricao = descricao_elem.text.strip()
                except Exception:
                    descricao = ""
                
                # Extração da data
                try:
                    data_elem = noticia.find_element(By.XPATH, './/span[@data-testid="todays-date"]')
                    data_publicacao = parse_data_publicacao(data_elem.get_attribute("aria-label"))
                except Exception:
                    data_publicacao = ""
                
                try:
                    dt_noticia = datetime.strptime(data_publicacao, "%B %d, %Y")
                except Exception:
                    continue  # Pula a notícia se a data não puder ser convertida
                
                if dt_noticia < cutoff_date:
                    continue
                
                # Extração da imagem
                try:
                    imagem_tag = noticia.find_element(By.TAG_NAME, 'img')
                    imagem_url = imagem_tag.get_attribute('src')
                    imagem_nome = imagem_url.split('/')[-1].split('?')[0] if imagem_url else ""
                except Exception:
                    imagem_url = ""
                    imagem_nome = ""
                
                # Baixa a imagem, se houver URL
                if imagem_url:
                    try:
                        response = requests.get(imagem_url, stream=True)
                        if response.status_code == 200:
                            image_path = os.path.join(images_dir, imagem_nome)
                            with open(image_path, 'wb') as f:
                                for chunk in response.iter_content(1024):
                                    f.write(chunk)
                            print(f"Imagem '{imagem_nome}' baixada com sucesso.")
                        else:
                            print(f"Falha ao baixar imagem: {imagem_url}")
                    except Exception as e:
                        print("Erro ao baixar imagem:", e)
                
                # Contagem de ocorrências da frase de pesquisa
                contagem_titulo = titulo.lower().count(frase_pesquisa.lower())
                contagem_descricao = descricao.lower().count(frase_pesquisa.lower())
                
                # Verificação de presença de valores monetários
                padrao_valor = re.compile(r'(\$[\d,\.]+|US\$[\d,\.]+|\d+\s*dólares?)', re.IGNORECASE)
                possui_valor = bool(padrao_valor.search(titulo)) or bool(padrao_valor.search(descricao))
                
                dados_noticia = {
                    "ordem": ordem,
                    "titulo": titulo,
                    "data": data_publicacao,
                    "descricao": descricao,
                    "imagem_nome": imagem_nome,
                    "contagem_titulo": contagem_titulo,
                    "contagem_descricao": contagem_descricao,
                    "possui_valor": possui_valor
                }
                dados_lista.append(dados_noticia)
            except Exception as e:
                print(f"Erro ao processar notícia: {e}")
        
        df = pd.DataFrame(dados_lista)
        df.sort_values("ordem", inplace=True)
        df.drop(columns=["ordem"], inplace=True)
        
        excel_filename = "noticias_nytimes.xlsx"
        if os.path.exists(excel_filename):
            os.remove(excel_filename)
        df.to_excel(excel_filename, index=False)
        print(f"Extração concluída! {len(df)} notícias salvas em '{excel_filename}'.")
        
    finally:
        driver.quit()
        print("Fim")

if __name__ == "__main__":
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(CURRENT_DIR, "config.json")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    frase_pesquisa = config["frase_pesquisa"]
    categoria = config["categoria"]  
    numero_meses = config["numero_meses"]
    
    automacao_nytimes(frase_pesquisa, categoria, numero_meses)
