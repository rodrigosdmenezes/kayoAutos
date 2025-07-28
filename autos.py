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
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="e-mail"]').send_keys('xxxxxxx')
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="senha"]').send_keys('xxxxxxxxx')
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

    print("\n✅ Todos os cards da página foram processados.")

def ir_para_proxima_pagina(numero):
    try:
        # Scroll para a área da paginação para garantir que o botão esteja visível
        paginacao_pai = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.q-pagination__middle.row.justify-center')))
        botoes = paginacao_pai.find_elements(By.TAG_NAME, "button")

        print(f"🔍 Botões na paginação encontrados: {len(botoes)}")
        for i, botao in enumerate(botoes, 1):
            texto = botao.text.strip()
            classes = botao.get_attribute('class')
            aria_label = botao.get_attribute('aria-label')
            print(f"Botão {i}: texto='{texto}', aria-label='{aria_label}' | classes='{classes}'")

        for botao in botoes:
            aria_label = botao.get_attribute("aria-label")
            classes = botao.get_attribute("class").lower()
            if aria_label == str(numero) and 'disabled' not in classes:
                print(f"➡️ Indo para página {numero}")

                # Scroll para o botão para garantir visibilidade
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                time.sleep(1)

                # Clique via JavaScript para evitar o erro de clique interceptado
                driver.execute_script("arguments[0].click();", botao)
                time.sleep(5)
                return True

        print(f"❌ Botão para página {numero} não encontrado ou está desabilitado.")
        return False

    except Exception as e:
        print(f"⚠️ Erro ao tentar ir para próxima página: {e}")
        return False
def processar_todas_paginas_e_cards():
    pagina_atual = 1
    while True:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.col-xs-12.col-lg-3.col-md-3.col-sm-6')))
        processar_cards_por_link()
        
        proxima_pagina = pagina_atual + 1
        if not ir_para_proxima_pagina(proxima_pagina):
            print("✅ Última página alcançada. Fim do processo.")
            break
        pagina_atual += 1
if __name__ == '__main__':
    login()
    ofertas()
    processar_todas_paginas_e_cards()

    