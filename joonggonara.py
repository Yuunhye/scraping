from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import bunjang as bj
import re

def get_products_info(product_name, year_dict, min_date="2024-03-03", min_price=1000000, max_price=30000000, wait_time=5):

    options = ChromeOptions()
    # 백그라운드 실행 옵션
    options.add_argument("headless")

    # 브라우저 꺼짐 방지 옵션
    # options.add_experimental_option("detach", True)

    #크롬 드라이버 실행
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(time_to_wait=wait_time)
    wait = WebDriverWait(driver, wait_time)

    page = 1
    home = "https://web.joongna.com"
    url = home + "/search/" + product_name + "?sort=RECENT_SORT&page=" + str(page)
    min_date = bj.convert_to_datetime(min_date)
    progress = True

    while(progress):
        driver.get(url)
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'relative')))
        except:
            print("TimeoutException occurred")
            break
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all(class_="group box-border overflow-hidden flex rounded-md cursor-pointer pe-0 pb-2 lg:pb-3 flex-col items-start transition duration-200 ease-in-out transform bg-white")

        for item in items:
            try:
                detail_link = home+item.attrs['href']
                info = item.get_text(separator=";;;").split(';;;')
                title = info[0]
                price = int(info[1][:-1].replace(',', ''))
                upload_date = info[-1]

                #min_date보다 더 오래 된 게시글이면 break
                if min_date > bj.convert_to_datetime(upload_date):
                    progress = False
                    break
                if min_price <= price <= max_price:

                    driver.get(detail_link)
                    # more_button = driver.find_element(By.CLASS_NAME, 'w-full.py-4.border.border-gray-400.rounded')
                    # if more_button.get_attribute("class")[-6:] != "hidden":
                    #     more_button.send_keys(Keys.ENTER)
                    detail_html = driver.page_source
                    detail_soup = BeautifulSoup(detail_html, 'html.parser')
                    product_info = detail_soup.find(attrs={"name" : "product-description"}).find('p').get_text()
                    product_info = re.sub(r'※.*?\n|─{10,}|📢.*?\n', '', product_info, flags=re.DOTALL)

                    year = bj.get_product_year(title)
                    if year:
                        year_dict[year].append((year, title, price, upload_date, product_info, detail_link))
                    else:
                        year = bj.get_product_year(product_info)
                        if year:
                            year_dict[year].append((year, title, price, upload_date, product_info, detail_link))

            except Exception as e:
                print("Error : ",e)

        page += 1

    return year_dict

if __name__ == "__main__":
    print("실행중...")
    years = [2024, 2023, 2022, 2021, 2020, 2019, 2018]
    year_dict = {year: [] for year in years}
    products_info = get_products_info("흑콤")

    for year in products_info.keys():
        print(f'{year} : {products_info[year]}')
