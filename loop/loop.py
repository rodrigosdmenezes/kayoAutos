import re
import base64
import os
from shlex import quote
import time
import requests
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from yt_dlp import YoutubeDL

driver = webdriver.Firefox()
driver.maximize_window()
driver.get("https://looprevenda.com.br/login")


def login():
    time.sleep(10)
    driver.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys('xxxxx')
    driver.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys('(xxxxxx)')
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

def buscarOfertas():
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, 'div[data-sentry-source-file="PriceFields.jsx"]  button[data-sentry-element="Button"]').click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, 'input[value="Revenda"]').click()
    
def carregaCards(driver):
    time.sleep(3)

    incremento = 600
    scroll_pause = 1.0
    altura_atual = 0
    total_anterior = 0
    tentativas_sem_novo = 0

    while True:
        driver.execute_script(f"window.scrollTo(0, {altura_atual});")
        time.sleep(scroll_pause)

        cards = driver.find_elements(By.CSS_SELECTOR, 'div.VehicleCard-details')
        total_atual = len(cards)

        # 🔹 Verifica se apareceu a mensagem final
        fim = driver.find_elements(
            By.XPATH,
            "//h3[contains(text(),'Todos os veículos já foram mostrados')]"
        )

        if fim:
            print("✅ Mensagem final encontrada: todos os veículos carregados.")
            break

        # 🔹 Se não carregou novos cards
        if total_atual == total_anterior:
            tentativas_sem_novo += 1
        else:
            tentativas_sem_novo = 0

        # 🔹 Segurança: só para se falhar várias vezes
        if tentativas_sem_novo >= 5:
            print("⚠️ Nenhum card novo após várias tentativas, encerrando scroll.")
            break

        total_anterior = total_atual
        altura_atual += incremento

    print(f"📦 Total final de cards carregados: {total_atual}")

    
def voltarTopo():
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")

def limpar_nome(texto):
    if not texto:
        return "SEM_MODELO"

    texto = texto.strip()
    texto = re.sub(r'[\\/*?:"<>|]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)

    return texto


def criar_pastas_veiculo(modelo):
    data_hoje = datetime.now().strftime("%d-%m-%Y")

    modelo_limpo = limpar_nome(modelo)

    base_dir = os.path.dirname(os.path.abspath(__file__))  # 🔥 LOCAL DO SCRIPT
    pasta_base = os.path.join(base_dir, "Loop", f"Ofertas - {data_hoje}")
    pasta_veiculo = os.path.join(pasta_base, modelo_limpo)
    fotos = os.path.join(pasta_veiculo, "Fotos")

    os.makedirs(fotos, exist_ok=True)

    print(f"📁 Pasta criada: {pasta_veiculo}")

    return pasta_veiculo, fotos

def texto(driver, by, selector):
    try:
        return driver.find_element(by, selector).text.strip()
    except:
        return ""

def baixar_fotos(driver, fotos):
    wait_local = WebDriverWait(driver, 5)

    # 1️⃣ Clicar no botão que expande a galeria
    try:
        botao_galeria = wait_local.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 'button.MuiButtonBase-root.MuiButton-root.MuiButton-contained.mui-1w7d45r')
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            botao_galeria
        )
        time.sleep(1)

        driver.execute_script("arguments[0].click();", botao_galeria)
        time.sleep(2)

    except Exception as e:
        print("⚠️ Não foi possível abrir a galeria de fotos")
        print(e)
        return

    # 2️⃣ Aguarda a galeria aparecer
    try:
        wait_local.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.MuiBox-root.mui-1ule2bx')
            )
        )
    except:
        print("⚠️ Galeria de fotos não abriu")
        return

    # 3️⃣ Captura todas as imagens da galeria
    imagens = driver.find_elements(
        By.CSS_SELECTOR,
        'div.MuiBox-root.mui-1ule2bx img'
    )

    print(f"📸 Total de fotos encontradas: {len(imagens)}")

    if not imagens:
        print("⚠️ Nenhuma imagem encontrada na galeria")
        return

    # 4️⃣ Baixa as imagens
    for i, img in enumerate(imagens, start=1):
        try:
            url_img = img.get_attribute("src")

            if not url_img or not url_img.startswith("http"):
                continue

            resposta = requests.get(url_img, timeout=20)

            extensao = url_img.split(".")[-1].split("?")[0]
            nome_arquivo = f"foto_{i}.{extensao}"

            with open(os.path.join(fotos, nome_arquivo), "wb") as f:
                f.write(resposta.content)

        except Exception as e:
            print(f"❌ Erro ao baixar foto {i}: {e}")

    # 5️⃣ Fecha a galeria
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)
    except:
        pass

def salvar_laudo_full_scroll(driver):
    """
    Verifica se o card de laudo existe e extrai o parecer técnico.
    Retorna o texto do parecer ou 'SEM LAUDO'.
    """
    try:
        # 1️⃣ Espera o Card de Laudo aparecer
        wait_local = WebDriverWait(driver, 5)
        seletor_card = 'div[id="laudoCautelar"]'
        
        card_laudo = wait_local.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, seletor_card))
        )

        # 2️⃣ Tenta capturar o texto de um dos dois seletores possíveis
        # O seletor abaixo busca o primeiro OU o segundo (separados por vírgula)
        try:
            seletores_texto = 'p.mui-e9ps85, p.mui-kvhvpv'
            elemento_texto = card_laudo.find_element(By.CSS_SELECTOR, seletores_texto)
            parecer_texto = elemento_texto.text.strip()
            
            print(f"✅ Parecer técnico encontrado: {parecer_texto}")
            return parecer_texto if parecer_texto else "LAUDO DISPONÍVEL"
            
        except Exception:
            # Se o card existir mas o parágrafo de texto ainda não estiver lá
            return "LAUDO DISPONÍVEL"

    except (TimeoutException, NoSuchElementException):
        print("ℹ️ Veículo sem laudo.")
        return "SEM LAUDO"
    except Exception as e:
        print(f"⚠️ Erro ao verificar laudo: {e}")
        return "ERRO VERIFICAÇÃO"
    
def baixar_video_youtube(driver, pasta):
    url = None
    wait_rapido = WebDriverWait(driver, 2)
    
    try:
        seletor_video = 'iframe[src*="youtube"], iframe[src*="youtu.be"]'
        elemento = wait_rapido.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_video)))
        
        if elemento.tag_name == 'iframe':
            url = elemento.get_attribute("src")
        else:
            url = elemento.get_attribute("href")
            
    except TimeoutException:
        print("🎥 Veículo sem vídeo")
        return "SEM VÍDEO"
    except Exception as e:
        print(f"⚠️ Erro ao localizar elemento de vídeo: {e}")
        return "SEM VÍDEO"

    if not url:
        return "SEM VÍDEO"

    if "embed/" in url:
        video_id = url.split("embed/")[-1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"🎬 Vídeo encontrado: {url}. Iniciando download...")

    os.makedirs(pasta, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(pasta, 'video_veiculo.mp4'),
        'format': 'best[ext=mp4]',
        'quiet': True,
        'no_warnings': True,
        'noprogress': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ Vídeo salvo com sucesso")
        return "VÍDEO SALVO"
    except Exception as e:
        print(f"❌ Erro no yt-dlp ao baixar: {e}")
        return "ERRO NO DOWNLOAD"

def extrair_dados_veiculo():
    dados = {}

    dados["URL"] = driver.current_url
    dados["Modelo"] = texto(driver, By.CSS_SELECTOR, 'h1[data-sentry-element="Typography"]')
    dados["Versão"] = texto(driver, By.CSS_SELECTOR, 'p.mui-1b2cdd7')
    dados["Valor"] = texto(driver, By.CSS_SELECTOR, 'h3.mui-19uwv58')
    dados["Localização"] = texto(driver, By.CSS_SELECTOR, 'strong.mui-y3gusw')

    infos = driver.find_elements(
        By.CSS_SELECTOR,
        'div.mui-st3jp6 p.MuiTypography-body1'
    )

    chaves = ["Câmbio", "Combustível", "KM", "PLaca", "Ano", "Cor", "Classificação"]
    for chave, item in zip(chaves, infos):
        dados[chave] = item.text

    try:
        box_fipe = driver.find_element(By.CSS_SELECTOR, 'div.mui-1qfco99')
        if "fipe" in box_fipe.text.lower():
            dados["FIPE"] = driver.find_element(By.CSS_SELECTOR, 'h3.mui-w8796s').text
    except:
        dados["FIPE"] = ""

    return dados

def salvar_excel(dados, pasta):
    caminho = os.path.join(pasta, "dados_veiculo.xlsx")
    df = pd.DataFrame([dados])
    df.to_excel(caminho, index=False)
    print(f"📊 Excel salvo em: {caminho}")
    
def processar_ofertas():
    time.sleep(3)

    cards = driver.find_elements(By.CSS_SELECTOR, 'div.VehicleCard-details')

    if not cards:
        print("Nenhuma oferta encontrada.")
        return

    print(f"Total de ofertas encontradas: {len(cards)}")

    aba_principal = driver.current_window_handle

    for i in range(len(cards)):
        cards = driver.find_elements(By.CSS_SELECTOR, 'div.VehicleCard-details')

        if i >= len(cards):
            break

        card = cards[i]

        print(f"Abrindo oferta {i + 1}")

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", card
        )
        time.sleep(1)

        driver.execute_script("arguments[0].click();", card)

        WebDriverWait(driver, 10).until(
            lambda d: len(d.window_handles) > 1
        )

        nova_aba = [h for h in driver.window_handles if h != aba_principal][0]
        driver.switch_to.window(nova_aba)

        time.sleep(2)

        dados = extrair_dados_veiculo()

        pasta, fotos = criar_pastas_veiculo(
            dados.get(f"Modelo", ""),
        )

        baixar_fotos(driver, fotos)
        dados["Status Laudo"] = salvar_laudo_full_scroll(driver)
        salvar_excel(dados, pasta)

        driver.close()
        driver.switch_to.window(aba_principal)
        time.sleep(1)

  

if __name__ == '__main__':
    login()
    buscarOfertas()
    carregaCards(driver)
    voltarTopo()
    processar_ofertas()