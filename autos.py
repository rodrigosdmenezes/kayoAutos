import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Firefox()
driver.get(" https://vendadireta.dealersclub.com.br/login")

def login():
    time.sleep(20)
    login_email = driver.find_element('css selector', 'input[aria-label="e-mail"]').send_keys('xxxxxxxxx')
    login_password = driver.find_element('css selector', 'input[aria-label="senha"]').send_keys('xxxxxxxxxx')
    login_button = driver.find_element(By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/form/div[1]/div[2]/button').click()

def ofertas():
    time.sleep(5)
    verOfertas = driver.find_element('css selector', '[class="row q-col-gutter-x-md items-end"] [type="button"]').click()
    time.sleep(3)
    evento_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'col-6') and contains(@class, 'titulo') and text()='Eventos']"))
    )   
    
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", evento_div)
    
    time.sleep(3)
    vendaDiretaUm = driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[1]/div').click()
    time.sleep(3)
    vendaDiretaDois = driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[2]/div').click()
    time.sleep(3)
    vendaToyotaUm = driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[6]/div').click()
    time.sleep(3)
    vendaToyotaDois = driver.find_element(By.XPATH,'//*[@id="q-app"]/div[1]/div[1]/div[1]/aside/div/div[2]/div[2]/div[1]/div/div/div[16]/div[2]/div/div[7]/div').click()

def get_cards():
    return driver.find_elements(By.CLASS_NAME, 'col-xs-12.col-lg-3.col-md-3.col-sm-6')

# Pegando todos os cards
cards = get_cards()

# Percorre todos os cards
for i in range(len(cards)):
    cards = get_cards()  # recarrega os elementos porque a página foi atualizada com o "voltar"

    # Scroll até o card (caso esteja fora da tela)
    driver.execute_script("arguments[0].scrollIntoView(true);", cards[i])
    time.sleep(1)

    # Clica no card
    cards[i].click()
    time.sleep(3)  # espera a nova página carregar

    # EXTRAI INFORMAÇÕES DA PÁGINA DO VEÍCULO
    try:
        titulo = driver.find_element(By.CSS_SELECTOR, 'p[class="titulo-veiculo outra-classe"]').text  # exemplo de classe
        preco = driver.find_element(By.XPATH, '//*[@id="descricao"]/div/div[2]/div/div/div[2]/div[1]/div/h6').text
        print(f"Título: {titulo}, Preço: {preco}")
    except:
        print(f"Erro ao coletar informações do veículo {i+1}")

    # Volta para a lista de veículos
    driver.back()
    time.sleep(3)



if __name__ == '__main__':
    login()
    ofertas()