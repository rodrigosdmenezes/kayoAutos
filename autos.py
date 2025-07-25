from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.get("https://vendadireta.dealersclub.com.br/login")

def login():
    time.sleep(20)
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="e-mail"]').send_keys('rafaelctba@sorepasse.com.br')
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="senha"]').send_keys('Paloma01**')
    driver.find_element(By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/form/div[1]/div[2]/button').click()

def ofertas():
    time.sleep(5)
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

def get_cards():
    # Aguarda os cards voltarem a carregar
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'col-xs-12.col-lg-3.col-md-3.col-sm-6'))
    )
    return driver.find_elements(By.CLASS_NAME, 'col-xs-12.col-lg-3.col-md-3.col-sm-6')

if __name__ == '__main__':
    login()
    ofertas()

    total_cards = len(get_cards())

    for i in range(total_cards):
        cards = get_cards()

        # Scroll até o card
        driver.execute_script("arguments[0].scrollIntoView(true);", cards[i])
        time.sleep(1)

        # Clica no card
        cards[i].click()
        time.sleep(3)

        # Extrai as informações
        try:
            titulo = driver.find_element(By.CSS_SELECTOR, 'p[class^="titulo-veiculo"]').text
            preco = driver.find_element(By.XPATH, '//*[@id="descricao"]/div/div[2]/div/div/div[2]/div[1]/div/h6').text
            print(f"Título: {titulo}, Preço: {preco}")
        except Exception as e:
            print(f"Erro ao coletar informações do veículo {i+1}: {e}")

        # Volta para a lista
        driver.back()

        # Aguarda os cards recarregarem
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'col-xs-12.col-lg-3.col-md-3.col-sm-6'))
        )
        time.sleep(2)


if __name__ == '__main__':
    login()
    ofertas()
    get_cards()