# Mercado Livre Search Scrapper by rafael_dsa

from bs4 import BeautifulSoup
import requests
import csv
from sklearn.metrics import jaccard_score
from selenium import webdriver
from selenium.webdriver.common.by import By  

# abre o arquivo csv em branco
csv_file = open('data.csv', 'a', newline='', encoding='utf_8_sig')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Cluster', 'Anúncio', 'Preço Antes', 'Preço Atual', 'Parcela', 'Juros', 'Frete', 'Vendas', 'Localização', 'Link', 'Vendedor'])

# definição da variável de pesquisa - input 1
def user_input():    
    usr_input = input('Digite a Pesquisa: ')
    usr_input = usr_input.replace(" ","-")
    return usr_input

# definição do numero de paginas para scrap - inpu
def page_number():
    num_loop = int(input('Digite o número de Páginas: '))
    while num_loop > 8:
        num_loop = int(input('Digite o número de Páginas: '))
    return num_loop

# definição do cluster jaccard (adicionar nível de similaridade)
def clusterize_products(products):
    clusters = []
    for i, (name, *_) in enumerate(products):
        found_cluster = False
        for cluster in clusters:
            for cluster_name in cluster:
                jaccard_similarity = jaccard_score(list(name), list(cluster_name), average='binary')
                if jaccard_similarity >= 0.8:
                    cluster.append(name)
                    found_cluster = True
                    break
            if found_cluster:
                break
        if not found_cluster:
            clusters.append([name])

    return clusters

### função recursiva

# definição de variáveis do request
def Main():
    count = 0
    usr_input = user_input()
    num_loop = page_number()
    pages_increment = ['0', '51', '101', '151', '201', '252', '303', '358']
    search_div = ['results-item article stack ', 'results-item article stack product ', 'results-item article article-pad stack product ', 'results-item article article-pad stack ', 'results-item']
    products = []

 # Inicializar o WebDriver
    driver = webdriver.Chrome()

#request
    for x in range(0, num_loop):
        driver = webdriver.Chrome()
        driver.get('https://lista.mercadolivre.com.br/'+usr_input+'_Desde_'+pages_increment[x]+'_DisplayType_LF')
        soup = BeautifulSoup(driver.page_source, "html.parser")



#scrapping
        for item_shop in soup.find_all('li', class_="ui-search-layout__item shops__layout-item"):
            if item_shop.find('h2', class_="ui-search-item__title shops__item-title") == None:
                name_item = 'Sem nome'
            else:
                name_item = item_shop.find('h2', class_="ui-search-item__title shops__item-title").text

            if item_shop.find('span', class_="price-tag-fraction") == None:
                before_price_item = 'Sem preço'
            else:
                before_price_item = item_shop.find('span', class_="price-tag-fraction").text

            if item_shop.find('span', class_="price-tag-amount") == None:
                price_item = 'Sem preço'
            else:
                price_item = item_shop.find('span', class_="price-tag-amount").text

            if item_shop.find('a', class_="ui-search-item__group__element shops__items-group-details ui-search-link")['href'] == None:
                link = 'Sem link'
            else:
                link = item_shop.find('a', class_="ui-search-item__group__element shops__items-group-details ui-search-link")['href']

            if item_shop.find('a', class_="ui-pdp-media__action ui-box-component__action"):
                seller_link = item_shop.find('a', class_="ui-pdp-media__action ui-box-component__action")['href']
                seller = seller_link.split('/')[-1].split('?')[0]
            else:
                driver.get(link)
                seller_elements = driver.find_elements(By.CSS_SELECTOR, 'a.ui-pdp-media__action')
                if seller_elements:
                    seller_element = seller_elements[0]
                    seller = seller_element.get_attribute('href').split('/')[-1]
                else:
                    seller = 'Sem vendedor'

            sales = item_shop.find('div', class_="item__condition")

            if item_shop.find('span', class_="ui-search-item__group__element shops__items-group-details ui-search-installments ui-search-color--LIGHT_GREEN") == None:
                installments = 'Não divide no cartão'
            else:
                installments = item_shop.find('span', class_="ui-search-item__group__element shops__items-group-details ui-search-installments ui-search-color--LIGHT_GREEN").text

            if (item_shop.find('span', class_="price__decimals") == None):
                price_d_item = '00'
            else:
                price_d_item = item_shop.find('span', class_="price__decimals").text

            if item_shop.find('p', class_="stack-item-info item--has-fulfillment") != None:
                delivery = (item_shop.find('p', class_="stack-item-info item--has-fulfillment").text).replace(' ', '', 1)
            elif item_shop.find('p', class_="stack-item-info ") == None:
                delivery = 'Combinar com o vendedor'
            else:
                delivery = (item_shop.find('p', class_="stack-item-info ").text).replace(' ', '', 1)

            if (item_shop.find('span', class_="item-installments-interest") == None):
                interest = 'com juros'
            else:
                interest = (item_shop.find('span', class_="item-installments-interest").text).replace(' ', '', 1)

            if (item_shop.find('div', class_="item__condition") == None):
                sales_2 = ['0 vendidos', 'Sem Localização']
            elif ' - ' not in (item_shop.find('div', class_="item__condition").text):
                sales_2 = ['0 vendidos', item_shop.find('div', class_="item__condition").text]
            elif item_shop.find('p', class_="stack-item-info item__free-shipping-disabled") != None:
                if item_shop.find('p', class_="stack-item-info item__free-shipping-disabled").text == ' Envio para todo o país ':
                    sales = (item_shop.find('div', class_="item__condition").text).replace(' ', '', 1)
                    sales_2 = sales.split("-")
                else:
                    sales_2 = ['0', item_shop.find('p', class_="stack-item-info item__free-shipping-disabled").text]
            else:
                sales = (item_shop.find('div', class_="item__condition").text).replace(' ', '', 1)
                sales_2 = sales.split("-")

            count += 1
            sales_2[1] = sales_2[1].replace(' ', '', 1)

            products.append((name_item, before_price_item, price_item, price_d_item, installments, interest, delivery, sales_2[0], sales_2[1], link, seller))
    # Fechar o WebDriver
    driver.quit()
    clusters = clusterize_products(products)

    for i, (name, before_price, price, price_d, installments, interest, delivery, sales, location, link, seller) in enumerate(products):
        cluster_number = 0
        for cluster in clusters:
            if name in cluster:
                cluster_number = clusters.index(cluster) + 1
                break

        csv_writer.writerow([cluster_number, name, before_price, price, price_d, installments, interest, delivery, sales, location, link, seller])

    print('Foram extraídos ' + str(count) + ' anúncios.')
    csv_file.close()

def clusterize_products(products):
    names = [name for name, _, _, _, _, _, _, _, _, _, _ in products]
    clusters = []
    for name in names:
        cluster_found = False
        for cluster in clusters:
            for item in cluster:
                if jaccard_similarity(name, item) >= 0.5:
                    cluster.append(name)
                    cluster_found = True
                    break
            if cluster_found:
                break
        if not cluster_found:
            clusters.append([name])
    return clusters


def jaccard_similarity(str1, str2):
    set1 = set(str1.lower().split())
    set2 = set(str2.lower().split())
    intersection = len(set1.intersection(set2))
    union = len(set1) + len(set2) - intersection
    return intersection / union

Main()
