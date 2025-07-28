from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.get("https://vendadireta.dealersclub.com.br/login")
wait = WebDriverWait(driver, 10)

def login():
    time.sleep(20)
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="e-mail"]').send_keys('rafaelctba@sorepasse.com.br')
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="senha"]').send_keys('Paloma01**')
    driver.find_element(By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/form/div[1]/div[2]/button').click()

def ofertas():
    time.sleep(7)
    driver.find_element(By.CSS_SELECTOR, '[class="row q-col-gutter-x-md items-end"] [type="button"]').click()
    time.sleep(3)
    evento_div = WebDriverWait(driver, 5).until(
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

def extrair_detalhes_na_nova_aba():
    """Extrai os dados da página do card na div correta"""
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.veiculo-descricao.q-pa-lg.q-mb-md")))
    dados = driver.find_element(By.CSS_SELECTOR, "div.veiculo-descricao.q-pa-lg.q-mb-md").text
    print("🔎 Dados do veículo:\n", dados)
    time.sleep(2)

def processar_cards_por_link():
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-xs-12.col-lg-3.col-md-3.col-sm-6')))
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.col-xs-12.col-lg-3.col-md-3.col-sm-6')

    hrefs = []
    for card in cards:
        try:
            link_element = card.find_element(By.CSS_SELECTOR, 'a')
            href = link_element.get_attribute('href')
            if href:
                hrefs.append(href)
        except:
            continue

    print(f"➡️ Total de cards encontrados com link: {len(hrefs)}")

    for index, href in enumerate(hrefs):
        print(f"\n➡️ Abrindo card {index + 1} de {len(hrefs)}")
        driver.execute_script("window.open(arguments[0]);", href)
        driver.switch_to.window(driver.window_handles[1])

        try:
            extrair_detalhes_na_nova_aba()
        except Exception as e:
            print(f"⚠️ Erro ao extrair dados do card {index + 1}: {e}")
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

    print("\n✅ Todos os cards foram processados.")

if __name__ == '__main__':
    login()
    ofertas()
    processar_cards_por_link()
