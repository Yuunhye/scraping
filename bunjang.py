from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import re
import os


def get_products_info(product_name, year_dict, min_date="1달 전", min_price=1000000, max_price=30000000, wait_time=5):

    options = ChromeOptions()
    #백그라운드 실행 옵션
    options.add_argument("headless")

    #브라우저 꺼짐 방지 옵션
    #options.add_experimental_option("detach", True)

    #크롬 드라이버 실행
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 5) #explicit wait
    driver.implicitly_wait(time_to_wait=wait_time)

    url = "https://m.bunjang.co.kr"
    page = 1
    is_continue = True
    min_date = convert_to_datetime(min_date)

    while(is_continue):
        search_url = url + "/search/products?order=date&page={}&q={}".format(page, product_name)
        driver.get(search_url)

        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@alt="상품 이미지"]')))
        except:
            print("TimeoutException occurred")
            break

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        lst = soup.find_all(attrs={'alt' : '상품 이미지'})

        for img in lst:
            try:
                aTag = img.parent.parent

                if aTag.find(attrs={'alt' : '판매 완료'}):  #이후에 판매중인 상품이 더이상 없음
                    break
                elif aTag.find(attrs={'alt' : '예약중'}):
                    continue

                detail_link = url + aTag.attrs['href']
                item = list(aTag.children)
                info = item[1].get_text(separator=";").split(';')
                if len(info) == 3 : #광고 게시글이 아닌 경우 (광고는 시간 정보가 없어서 len(info)가 2)
                    price = int(info[1].replace(',', ''))
                    title, upload_date = info[0], info[2]

                    if min_date >= convert_to_datetime(upload_date):
                        is_continue = False
                        break
                    if min_price <= price <= max_price:  # 최소 금액을 설정하여서 정확도를 높임
                        driver.get(detail_link) #상품 판매 상세 페이지 접속
                        detail_html = driver.page_source
                        detail_soup = BeautifulSoup(detail_html, 'html.parser')
                        product_info = detail_soup.find(attrs={'class': 'ProductInfostyle__DescriptionContent-sc-ql55c8-3'}).get_text()

                        year = get_product_year(title)

                        if year:
                            year_dict[year].append((year, title, price, upload_date, product_info, detail_link))
                        else:
                            year = get_product_year(product_info)
                            if year:
                                year_dict[year].append((year, title, price, upload_date, product_info, detail_link))

            except Exception as e:
                print("Error : ", e)

        page += 1

    return year_dict

def convert_to_datetime(date):
    #초, 시, 일, 주, 달, 년
    date = re.search(r'\d+\D', date).group()
    date_type = date[-1]
    n = int(date[:-1])
    now = datetime.now()
    if date_type == "일":
        return (now - relativedelta(days=n))
    elif date_type == "주":
        return (now - relativedelta(days=n*7))
    elif date_type == "달":
        return (now - relativedelta(months=n))
    elif date_type == "년":
        return (now - relativedelta(years=n))
    else:   #date_type => 초 or 시
        return now

    i = date_type.index(date)

def get_product_year(content):
    year_pattern1 = r'(\d{2,4})년'
    year_pattern2 = r'\b\d{4}\b'
    year = re.search(year_pattern1, content)
    if year:
        year = int(year.group()[:-1])
        if 18<=year<=24:
            year += 2000
            return year
        elif 2018<=year<=2024:
            return year
    else:
        year = re.search(year_pattern2, content)
        if year:
            year = int(year.group())
            if 2018<=year<=2024:
                return year
    return 0

def get_data(products_info):
    data = []
    for value in products_info.values():
        value.sort(key=lambda x : x[2])
        data += value

    return data

if __name__ == "__main__":
    print("실행중...")
    products = ["흑콤", "아쿠아테라 청판"]
    years = [2024, 2023, 2022, 2021, 2020, 2019, 2018]

    for product_name in products:
        year_dict = {year: [] for year in years}
        print(product_name)
        products_info = get_products_info(product_name)
        data = get_data(products_info)

        col = ['연식', '제목', '가격', '업로드 시간', '상품 설명', '링크']
        df = pd.DataFrame(data, columns = col)

        file_exists = os.path.isfile('test.xlsx')

        if file_exists:
            with pd.ExcelWriter('test.xlsx', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=product_name)
        else:
            with pd.ExcelWriter('test.xlsx', mode='w') as writer:
                df.to_excel(writer, sheet_name=product_name)

    print("종료")