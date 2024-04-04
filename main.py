import joonggonara as jn
import bunjang as bj
import pandas as pd
import os
def get_sorted_data(products_info):
    data = []
    for value in products_info.values():
        value.sort(key=lambda x : x[2])
        data += value

    return data

print("실행중...")
products = ["흑콤", "아쿠아테라 청판"]

years = [2024, 2023, 2022, 2021, 2020, 2019, 2018]

for product_name in products:

    year_dict = {year: [] for year in years}

    print(product_name, "- 번개장터")
    bj.get_products_info(product_name, year_dict)
    print(product_name, " - 중고나라")
    jn.get_products_info(product_name, year_dict)

    data = get_sorted_data(year_dict)

    col = ['연식', '제목', '가격', '업로드 시간', '상품 설명', '링크']
    df = pd.DataFrame(data, columns=col)

    file_exists = os.path.isfile('test.xlsx')

    if file_exists:
        with pd.ExcelWriter('test.xlsx', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=product_name)
    else:
        with pd.ExcelWriter('test.xlsx', mode='w') as writer:
            df.to_excel(writer, sheet_name=product_name)

print("종료")