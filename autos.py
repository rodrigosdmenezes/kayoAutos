from asyncio import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.get("https://vendadireta.dealersclub.com.br/login")
wait = WebDriverWait(driver, 15)

def login():
    time.sleep(20)
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="e-mail"]').send_keys('rafaelctba@sorepasse.com.br')
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="senha"]').send_keys('Paloma01**')
    driver.find_element(By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/form/div[1]/div[2]/button').click()

def ofertas():
    time.sleep(10)
    driver.find_element(By.CSS_SELECTOR, '[class="row q-col-gutter-x-md items-end"] [type="button"]').click()
    time.sleep(3)
    evento_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'col-6') and contains(@class, 'titulo') and text()='Eventos']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", evento_div)
    time.sleep(3)
    driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[1]/div').click()
    time.sleep(3)
    driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[2]/div').click()
    time.sleep(3)
    driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[6]/div').click()
    time.sleep(3)
    driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[7]/div').click()

def extrair_detalhes_do_card():
    """Extrai os dados da página de detalhes do card"""
    # Espera algum conteúdo específico da página de detalhes aparecer
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class='card-principal']")))
    dados = driver.find_element(By.CSS_SELECTOR, "[class='card-principal']").text
    print("🔎 Dados do card:", dados)
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, 'div[class="carrosel-carros"]').click()

def voltar_para_listagem():
    """Volta para a tela principal"""
    time.sleep(5)
    # Pode ser um botão, um link ou o botão de voltar do navegador
    driver.back()
    # Espera a lista de cards aparecer novamente
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="carrosel-carros"]')))

def processar_todos_os_cards():
    """Lê e processa todos os cards da tela atual"""
    time.sleep(5)
    container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="carrosel-carros"]')))
    time.sleep(5)
    cards = container.find_elements(By.CSS_SELECTOR, 'div[class="card-principal"]')  # ajuste o seletor
    print(f"📦 Encontrado {len(cards)} cards")

    for i in range(len(cards)):
        # Refaz a busca dos elementos após cada navegação
        time.sleep(5)
        container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="carrosel-carros"]')))
        time.sleep(5)
        cards = container.find_elements(By.CSS_SELECTOR, 'div[class="card-principal"]')

        try:
            card = cards[i]
            wait.until(EC.element_to_be_clickable(card)).click()
            extrair_detalhes_do_card()
            voltar_para_listagem()
        except Exception as e:
            print(f"⚠️ Erro ao processar card {i + 1}: {e}")
            voltar_para_listagem()
            continue

    
if __name__ == '__main__':
    login()
    ofertas()
    extrair_detalhes_do_card()
    voltar_para_listagem()
    processar_todos_os_cards()
    