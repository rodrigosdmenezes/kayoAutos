import os
import re
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("xxxxxxxxxxxx")
wait = WebDriverWait(driver, 20)

veiculos = []

def login():
    time.sleep(10)
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="e-mail"]').send_keys('xxxxxxxxxx')
    driver.find_element(By.CSS_SELECTOR, 'input[aria-label="senha"]').send_keys('xxxxxxxxxxxx')
    driver.find_element(By.XPATH, '//*[@id="q-app"]/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/form/div[1]/div[2]/button').click()

def ofertas():
    time.sleep(7)
    # Clica no botão que abre os filtros
    driver.find_element(By.CSS_SELECTOR, '[class="row q-col-gutter-x-md items-end"] [type="button"]').click()
    time.sleep(3)

    # Espera a div do título "Eventos"
    evento_div = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'col-6') and contains(@class, 'titulo') and text()='Eventos']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", evento_div)
    time.sleep(3)

    # Textos parciais que identificam os filtros
    textos_parciais = [
        "Venda Direta Dealers_LEVES E MOTOS",
        "VENDA DIRETA EXCLUSIVA BANCO TOYOTA"
    ]

    filtros_para_clicar = []

    for texto_parcial in textos_parciais:
        # Procura qualquer div que contenha o texto parcial (ignorando maiúsc/minúsc)
        xpath_busca = f"//div[contains(translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{texto_parcial.upper()}')]"
        elementos = driver.find_elements(By.XPATH, xpath_busca)
        print(f"🔍 Filtros encontrados para '{texto_parcial}': {len(elementos)}")

        for elem in elementos:
            filtros_para_clicar.append(elem)

    print(f"🔎 Total filtros para clicar: {len(filtros_para_clicar)}")

    for i, filtro in enumerate(filtros_para_clicar, 1):
        try:
            print(f"➡️ Clicando no filtro {i}: {filtro.text.strip()}")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", filtro)
            time.sleep(1)
            filtro.click()
            time.sleep(3)  # espera carregar depois do clique
        except Exception as e:
            print(f"⚠️ Erro ao clicar no filtro {i}: {e}")

def salvar_info_veiculo_excel(pasta, dados_veiculo, nome_arquivo='info_veiculo.xlsx'):
    # Comportamento para salvar por veículo
    try:
        df = pd.DataFrame([dados_veiculo])  # lista com 1 dicionário
        caminho_arquivo = os.path.join(pasta, nome_arquivo)
        df.to_excel(caminho_arquivo, index=False)
        print(f"✔️ Informações do veículo salvas no Excel: {caminho_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao salvar Excel do veículo: {e}")

def extrair_detalhes_na_nova_aba(card_index=None, page_num=None, oferta_card_principal="N/A"):
    current_url = driver.current_url
    print(f"🔗 URL da página de detalhes: {current_url}")

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.descricao-veiculo")))

    descricao_element = driver.find_element(By.CSS_SELECTOR, "div.descricao-veiculo")
    descricao_texto = descricao_element.text.strip()

    titulo_veiculo_element = driver.find_element(By.CSS_SELECTOR, "p.titulo-veiculo")
    titulo_veiculo = titulo_veiculo_element.text.strip().replace('\n', ' ').replace('  ', ' ')
    titulo_veiculo = re.sub(r'[\\/:"*?<>|]+', '', titulo_veiculo)

    pasta = os.path.join("imagens_veiculos", titulo_veiculo)
    os.makedirs(pasta, exist_ok=True)

    caracteristicas = {}
    
    # --- NOVO: Extrair localização ---
    empresa_localizacao = "N/A"
    endereco_completo = "N/A"
    try:
        localizacao_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.localizacao')))
        try:
            empresa_element = localizacao_div.find_element(By.CSS_SELECTOR, 'div[class="localizacao q-mb-md relative-position"] div[class="empresa"] p.nome')
            empresa_localizacao = empresa_element.text.strip()
        except:
            print("⚠️ Empresa de localização não encontrada.")
            
        try:
            endereco_element = localizacao_div.find_element(By.CSS_SELECTOR, 'div[class="localizacao q-mb-md relative-position"] div[class="endereco"] p')
            endereco_completo = endereco_element.text.strip()
        except:
            print("⚠️ Endereço completo não encontrado.")
            
        print(f"📍 Localização encontrada: Empresa='{empresa_localizacao}', Endereço='{endereco_completo}'")
    except Exception as e:
        print(f"❌ Erro ao extrair localização do veículo: {e}")

    # --- Extrair outras características ---
    caracteristicas_divs_pai = driver.find_elements(By.CSS_SELECTOR,
        "div.col-xs-4.col-md-3.col-sm-4.q-mb-md, div.col-xs-6.col-md-3.col-sm-6.aprovado, div.col-xs-6.col-md-3.col-sm-6.reprovado"
    )

    for div_carac_pai in caracteristicas_divs_pai:
        try:
            status_p_element = None
            try:
                status_p_element = div_carac_pai.find_element(By.XPATH, ".//p[contains(text(), 'Status:')]")
            except:
                pass

            if status_p_element:
                status_text = status_p_element.text.strip()
                if status_text.startswith("Status:"):
                    caracteristicas["Status"] = status_text.replace("Status:", "").strip()
            else:
                titulo_element = div_carac_pai.find_element(By.CSS_SELECTOR, "p.veiculo-caracteristica-titulo")
                titulo = titulo_element.text.strip()
                valor_element = None
                try:
                    valor_element = div_carac_pai.find_element(By.CSS_SELECTOR, "p.veiculo-caracteristica")
                except:
                    pass

                if valor_element:
                    valor = valor_element.text.strip()
                else:
                    full_text = div_carac_pai.text.strip()
                    if full_text.startswith(titulo):
                        valor = full_text[len(titulo):].strip()
                        if not valor:
                            print(f"DEBUG: Valor para '{titulo}' parece vazio ou não encontrado diretamente após o título na div pai.")
                if titulo and valor:
                    caracteristicas[titulo] = valor
                elif titulo and not valor:
                    text_in_div = div_carac_pai.text.strip()
                    if text_in_div != titulo:
                        remaining_text = text_in_div.replace(titulo, '').strip()
                        if remaining_text:
                            caracteristicas[titulo] = remaining_text
                        else:
                            caracteristicas[titulo] = "N/A"
                    else:
                        caracteristicas[titulo] = "N/A"
        except Exception as e:
            print(f"⚠️ Erro ao extrair característica de div pai: {e}")

    valor_fipe = "Não Disponível"
    try:
        fipe_value_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.col-md.col-xs-12 h6')))
        valor_fipe = fipe_value_element.text.strip()
        print(f"💲 Valor FIPE encontrado: {valor_fipe}")
    except Exception as e:
        print(f"⚠️ Não foi possível extrair o Valor FIPE: {e}")
    caracteristicas["Valor FIPE"] = valor_fipe

    oferta_detalhada_valor = "Não Disponível"
    try:
        preco_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.oferta-atual")))
        oferta_detalhada_valor = preco_element.text.strip()
        print(f"💲 Oferta Detalhada encontrada: {oferta_detalhada_valor}")
    except Exception as e:
        print(f"⚠️ Não foi possível extrair a Oferta Detalhada: {e}")

    veiculo_info = {
        "Página": page_num,
        "Card": card_index,
        "URL": current_url, # A URL da página de detalhes foi adicionada aqui
        "Título": titulo_veiculo,
        "Descrição": descricao_texto,
        "Oferta Atual": oferta_card_principal,
        "Oferta Detalhada": oferta_detalhada_valor,
        "Empresa Localização": empresa_localizacao,
        "Endereço Completo": endereco_completo,
        **caracteristicas
    }
    
    # --- Extrair imagens APENAS do carrossel principal ---
    try:
        carrossel_principal = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-12.carrossel-principal")))
        imagens_divs = carrossel_principal.find_elements(By.CSS_SELECTOR, "div.q-img__image.absolute-full")
        urls = []
        for div in imagens_divs:
            style_attr = div.get_attribute("style")
            if style_attr:
                match = re.search(r'url\("?(.*?)"?\)', style_attr)
                if match:
                    urls.append(match.group(1))

        for i, url in enumerate(urls, 1):
            try:
                resposta = requests.get(url, timeout=10)
                if resposta.status_code == 200:
                    nome_arquivo = f'img_{i}.jpg'
                    caminho = os.path.join(pasta, nome_arquivo)
                    with open(caminho, 'wb') as f:
                        f.write(resposta.content)
            except Exception as e:
                print(f"⚠️ Erro ao baixar imagem {url}: {e}")
    except Exception as e:
        print(f"❌ Não foi possível encontrar o carrossel principal ou extrair imagens: {e}")

    # --- Baixar arquivo PDF, se disponível ---
    try:
        pdf_link_element = None
        try:
            pdf_link_element = driver.find_element(By.CSS_SELECTOR, 'a[href*=".pdf"]')
        except:
            pass

        if pdf_link_element:
            pdf_url = pdf_link_element.get_attribute('href')
            if pdf_url:
                pdf_nome_arquivo = f'{titulo_veiculo}_documento.pdf'
                caminho_pdf = os.path.join(pasta, pdf_nome_arquivo)
                resposta_pdf = requests.get(pdf_url, timeout=15)
                if resposta_pdf.status_code == 200:
                    with open(caminho_pdf, 'wb') as f:
                        f.write(resposta_pdf.content)
                    veiculo_info["PDF_Anexado"] = pdf_nome_arquivo
                else:
                    veiculo_info["PDF_Anexado"] = "Erro de Download"
            else:
                veiculo_info["PDF_Anexado"] = "Link PDF Vazio"
        else:
            veiculo_info["PDF_Anexado"] = "Não Disponível"

    except Exception as e:
        print(f"❌ Erro ao tentar baixar PDF: {e}")
        veiculo_info["PDF_Anexado"] = f"Erro: {str(e)}"
    
    # Salvar Excel na pasta do veículo com todos os dados
    salvar_info_veiculo_excel(pasta, veiculo_info)

    time.sleep(2)


def processar_cards_por_link(page_num=1):
    time.sleep(5)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.col-xs-12.col-lg-3.col-md-3.col-sm-6')))
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.col-xs-12.col-lg-3.col-md-3.col-sm-6')

    card_data = []
    for card in cards:
        try:
            link_element = card.find_element(By.CSS_SELECTOR, 'a')
            href = link_element.get_attribute('href')

            oferta_card_principal = "N/A"
            try:
                valor_destaque_element = card.find_element(By.CSS_SELECTOR, 'div.valor-destaque')
                oferta_card_principal = valor_destaque_element.text.strip()
            except Exception as e:
                print(f"⚠️ Não foi possível encontrar 'div.valor-destaque' para um card. Erro: {e}")

            if href:
                card_data.append({"href": href, "oferta_principal": oferta_card_principal})
        except Exception as e:
            print(f"⚠️ Erro ao processar um card na lista principal (link ou valor-destaque): {e}")
            continue

    print(f"➡️ Total de cards encontrados com link: {len(card_data)}")

    for index, data in enumerate(card_data, 1):
        href = data["href"]
        oferta_principal = data["oferta_principal"]
        print(f"\n➡️ Abrindo card {index} de {len(card_data)} (Oferta Principal na Listagem: {oferta_principal})")

        driver.execute_script("window.open(arguments[0]);", href)
        driver.switch_to.window(driver.window_handles[1])

        try:
            extrair_detalhes_na_nova_aba(card_index=index, page_num=page_num, oferta_card_principal=oferta_principal)
        except Exception as e:
            print(f"⚠️ Erro ao extrair dados do card {index}: {e}")
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

    print("\n✅ Todos os cards da página foram processados.")

def ir_para_proxima_pagina(numero=None):
    try:
        paginacao_pai = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.q-pagination__middle.row.justify-center')))
        botoes = paginacao_pai.find_elements(By.TAG_NAME, "button")

        print(f"🔍 Botões na paginação encontrados: {len(botoes)}")
        for i, botao in enumerate(botoes, 1):
            texto = botao.text.strip()
            classes = botao.get_attribute('class')
            aria_label = botao.get_attribute('aria-label')

        if numero is None:
            for botao in botoes:
                classes = botao.get_attribute("class").lower()
                texto = botao.text.strip()
                if 'disabled' not in classes and (texto in ['>', 'Próximo', '›', '»'] or (not texto and 'q-btn--flat' in classes and 'q-btn--round' in classes)):
                    print(f"🔘 Clicando no botão próxima página")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", botao)
                    time.sleep(5)
                    return True
            print("⛔ Botão de próxima página não encontrado ou desativado.")
            return False
        else:
            for botao in botoes:
                aria_label = botao.get_attribute("aria-label")
                classes = botao.get_attribute("class").lower()
                if aria_label == str(numero) and 'disabled' not in classes:
                    print(f"➡️ Indo para página {numero}")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", botao)
                    time.sleep(5)
                    return True
            print(f"❌ Botão para página {numero} não encontrado ou está desabilitado.")
            return False

    except Exception as e:
        print(f"⚠️ Erro ao tentar ir para próxima página: {e}")
        return False

def processar_todas_paginas_e_cards():
    page_num = 1
    while True:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.col-xs-12.col-lg-3.col-md-3.col-sm-6')))
        print(f"\n===== Processando Página {page_num} =====")
        processar_cards_por_link(page_num=page_num)

        next_page_exists = False
        try:
            paginacao_pai = driver.find_element(By.CSS_SELECTOR, 'div.q-pagination__middle.row.justify-center')
            botoes = paginacao_pai.find_elements(By.TAG_NAME, "button")

            for botao in botoes:
                if botao.text.strip() == str(page_num + 1) and 'disabled' not in botao.get_attribute('class'):
                    next_page_exists = True
                    break
                if botao.text.strip() in ['>', 'Próximo', '›', '»'] and 'disabled' not in botao.get_attribute('class'):
                    next_page_exists = True
                    break
        except Exception as e:
            print(f"⚠️ Erro ao verificar botões de paginação: {e}")
            next_page_exists = False

        if not next_page_exists:
            print("✅ Última página alcançada. Fim do processo.")
            break

        if not ir_para_proxima_pagina(numero=page_num + 1):
            print("✅ Última página alcançada ou botão de próxima página genérico não encontrado. Fim do processo.")
            break

        page_num += 1

if __name__ == '__main__':
    login()
    ofertas()
    processar_todas_paginas_e_cards()
    driver.quit()