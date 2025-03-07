# Importação das bibliotecas necessárias
import os                    # Para operações com arquivos e diretórios
import json                  # Para ler o arquivo de configuração (config.json)
import re                    # Para utilizar expressões regulares (tratamento de strings)
import time                  # Para inserir pausas (sleep) na execução
import requests              # Para baixar imagens via requisições HTTP
import pandas as pd          # Para manipulação de dados e criação de DataFrame (exportação para Excel)
from datetime import datetime  # Para manipulação de datas e horas
from dateutil.relativedelta import relativedelta  # Para calcular datas relativas (ex.: período de meses)
from selenium import webdriver  # Para automação do navegador
from selenium.webdriver.common.by import By  # Para localizar elementos na página via seletores
from selenium.webdriver.support.ui import WebDriverWait  # Para aguardar condições específicas (espera dinâmica)
from selenium.webdriver.support import expected_conditions as EC  # Para definir condições de espera
from selenium.webdriver.common.keys import Keys  # Para simular pressionamento de teclas (como ENTER)
from selenium.webdriver.chrome.service import Service  # Para inicializar o ChromeDriver usando objeto Service

# Função que converte a string de data extraída para o formato "Month DD, YYYY"
def parse_data_publicacao(data_str):
    """
    Converte o texto da data para o formato "Month DD, YYYY".
    - Se contiver "ago" (ex: "9 hours ago"), assume a data atual.
    - Se já contiver um ano (ex: "March 3, 2025"), mantém a string original.
    - Se estiver no formato "Month DD" sem o ano, insere o ano atual.
    """
    data_str = data_str.strip().rstrip(',')  # Remove espaços extras e vírgulas finais
    if "ago" in data_str.lower():
        # Se a data for relativa, usa a data atual
        return datetime.now().strftime("%B %d, %Y")
    if re.search(r'\d{4}', data_str):
        # Se já há um ano presente, retorna a string sem alterações
        return data_str
    try:
        # Tenta interpretar a data como "Month DD" e insere o ano atual
        dt = datetime.strptime(data_str, "%B %d")
        dt = dt.replace(year=datetime.now().year)
        return dt.strftime("%B %d, %Y")
    except ValueError:
        return data_str

# Função principal que executa a automação de scraping
def automacao_nytimes(frase_pesquisa, categoria, numero_meses):
    """
    Executa a automação para extrair notícias do NYT.
    
    Parâmetros:
    - frase_pesquisa: O termo que será pesquisado ("War in Ukraine").
    - categoria: A seção do NYT a ser filtrada ("World").
    - numero_meses: Quantos meses para filtrar as notícias recentes.
    """
    # Configura as opções do navegador para rodar sem interface gráfica (headless) e sem sandbox
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")                # Modo headless (sem UI)
    options.add_argument("--no-sandbox")              # Desativa sandbox (necessário em containers)
    options.add_argument("--disable-dev-shm-usage")     # Evita problemas de memória compartilhada
    
    # Inicializa o ChromeDriver utilizando o objeto Service
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Define o diretório atual e cria as pastas "imagens" e "output" se não existirem
        current_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(current_dir, "imagens")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        output_dir = os.path.join(current_dir, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 1. Acessa o site do NYTimes
        driver.get("https://www.nytimes.com/")
        driver.maximize_window()  # Maximiza a janela para garantir o carregamento completo dos elementos
        print("Site acessado!")
        
        # 2. Fecha o pop-up de privacidade (se aparecer)
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="fides-button-group"]/div[1]/button[2]'))
            ).click()
            print("Preferências de privacidade aceitas.")
        except Exception as e:
            print("Pop-up de privacidade não apareceu ou já foi fechado.", e)
        
        # 3. Fecha o pop-up de termos de uso (se aparecer)
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
        
        # 5. Digita a frase de pesquisa e envia (simula pressionar ENTER)
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[data-testid="search-input"]'))
        )
        search_box.send_keys(frase_pesquisa)
        search_box.send_keys(Keys.ENTER)
        print("Termo de pesquisa digitado e enviado.")
        
        # 6. Após a busca, tenta fechar novamente o overlay de compliance, se reaparecer
        time.sleep(2)  # Pausa para permitir o aparecimento do overlay, se houver
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
        
        # 7. Clica no botão de "Section" (filtro de seções) usando o XPATH fornecido
        section_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[2]/div/div/button'))
        )
        section_button.click()
        print("Botão de seção clicado.")
        
        # 8. Seleciona a opção "World" usando o XPATH fornecido
        world_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[10]/label/span'))
        )
        world_option.click()
        print("Opção 'World' selecionada.")
        
        # 9. Seleciona a opção de período "notícias mais recentes"
        select_periodo = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/form/div[2]/div[1]/select'))
        )
        select_periodo.click()
        option_mais_recentes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div[1]/div[1]/form/div[2]/div[1]/select/option[2]'))
        )
        option_mais_recentes.click()
        print("Opção 'notícias mais recentes' selecionada.")
        
        # 10. Aguarda um tempo para o carregamento dos resultados
        time.sleep(3)
        
        # Coleta todas as notícias encontradas na página
        noticias = driver.find_elements(By.XPATH, '//li[@data-testid="search-bodega-result"]')
        print(f"Foram encontradas {len(noticias)} notícias.")
        
        # Define a data de corte com base no número de meses especificado
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=numero_meses)
        dados_lista = []
        ordem = 0  # Variável para manter a ordem das notícias conforme aparecem na página
        
        # Itera sobre cada notícia e extrai as informações desejadas
        for noticia in noticias:
            ordem += 1
            try:
                # Extrai o título da notícia (de um elemento <h4>)
                titulo_elem = noticia.find_element(By.TAG_NAME, 'h4')
                titulo = titulo_elem.text.strip() if titulo_elem else ""
                
                # Extrai a descrição, se disponível, de um parágrafo com a classe 'css-e5tzus'
                try:
                    descricao_elem = noticia.find_element(By.CSS_SELECTOR, 'p.css-e5tzus')
                    descricao = descricao_elem.text.strip()
                except Exception:
                    descricao = ""
                
                # Extrai a data da notícia, usando o atributo 'aria-label'
                try:
                    data_elem = noticia.find_element(By.XPATH, './/span[@data-testid="todays-date"]')
                    data_publicacao = parse_data_publicacao(data_elem.get_attribute("aria-label"))
                except Exception:
                    data_publicacao = ""
                
                # Converte a data extraída para um objeto datetime para comparação
                try:
                    dt_noticia = datetime.strptime(data_publicacao, "%B %d, %Y")
                except Exception:
                    continue  # Pula a notícia se a data não puder ser convertida
                
                # Verifica se a notícia está dentro do período desejado
                if dt_noticia < cutoff_date:
                    continue
                
                # Extrai a imagem da notícia e define seu nome
                try:
                    imagem_tag = noticia.find_element(By.TAG_NAME, 'img')
                    imagem_url = imagem_tag.get_attribute('src')
                    imagem_nome = imagem_url.split('/')[-1].split('?')[0] if imagem_url else ""
                except Exception:
                    imagem_url = ""
                    imagem_nome = ""
                
                # Baixa a imagem, se a URL estiver disponível, salvando-a na pasta 'imagens'
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
                
                # Conta as ocorrências da frase de pesquisa no título e na descrição
                contagem_titulo = titulo.lower().count(frase_pesquisa.lower())
                contagem_descricao = descricao.lower().count(frase_pesquisa.lower())
                
                # Verifica se há valores monetários nos textos utilizando regex
                padrao_valor = re.compile(r'(\$[\d,\.]+|US\$[\d,\.]+|\d+\s*dólares?)', re.IGNORECASE)
                possui_valor = bool(padrao_valor.search(titulo)) or bool(padrao_valor.search(descricao))
                
                # Armazena os dados da notícia em um dicionário
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
        
        # Cria um DataFrame com os dados coletados e ordena conforme a ordem original
        df = pd.DataFrame(dados_lista)
        df.sort_values("ordem", inplace=True)
        df.drop(columns=["ordem"], inplace=True)
        
        # Define o caminho para salvar o arquivo Excel dentro da pasta 'output'
        excel_filename = os.path.join("output", "noticias_nytimes.xlsx")
        if os.path.exists(excel_filename):
            os.remove(excel_filename)
        df.to_excel(excel_filename, index=False)
        print(f"Extração concluída! {len(df)} notícias salvas em '{excel_filename}'.")
        
    finally:
        # Encerra o navegador e finaliza a automação
        driver.quit()
        print("Fim")

# Execução principal do script
if __name__ == "__main__":
    # Define o diretório atual e o caminho para o arquivo de configuração 'config.json'
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(CURRENT_DIR, "config.json")
    
    # Abre e carrega o arquivo de configuração
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Extrai as variáveis de configuração
    frase_pesquisa = config["frase_pesquisa"]
    categoria = config["categoria"]  # Neste caso, espera-se que seja "World"
    numero_meses = config["numero_meses"]
    
    # Inicia a automação passando os parâmetros configurados
    automacao_nytimes(frase_pesquisa, categoria, numero_meses)
