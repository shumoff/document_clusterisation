import requests
import lxml.html
import lxml.etree
import re
import pandas as pd
from bs4 import BeautifulSoup


resp = requests.get('http://www.st-petersburg.vybory.izbirkom.ru/region/region/st-petersburg?action=show&root=1&tvd='
                    '27820001217417&vrn=27820001217413&region=78&global=&sub_region=78&prver=0&pronetvd=null&vibid='
                    '27820001217417&type=222')

soup = BeautifulSoup(resp.text, 'html.parser')
tree = lxml.html.fromstring(resp.text)

# tik_links = soup.find_all('a', {'style': 'text-decoration: none'})
tik_names = tree.xpath('//a[@style="text-decoration: none"]/text()')
tik_links = tree.xpath('//a[@style="text-decoration: none"]/@href')
print(tik_links)
# tik_links = list(map(lambda x: re.sub(r'amp', '', x), tik_links))
# for tik_link in tik_links:
#     print(tik_link)
#     resp = requests.get(tik_link)
#     soup = BeautifulSoup(resp.text, 'html.parser')
#     break
tik_names = list(map(lambda x: re.sub(r'Территориальная избирательная комиссия', 'ТИК', x), tik_names))
print(tik_names)
for link_num, tik_link in enumerate(tik_links[:-1]):
    print(link_num, tik_link)
    resp = requests.get(tik_link)
    tree = lxml.html.fromstring(resp.text)
    table = tree.xpath('//table[@style="width:100%;border-color:#000000"]/tr')
    # print(table)
    # print(lxml.html.tostring(table[0], pretty_print=True))
    tds = table[0].getchildren()
    tree = lxml.etree.ElementTree(tds[0])
    trs = tree.xpath('//tr')
    field_keys_list = ['ТИК']
    for tr in trs:
        fields = tr.getchildren()
        tree = lxml.etree.ElementTree(fields[1])
        field_text = tree.xpath('//text()')[0]
        field_keys_list.append(field_text)
    field_keys_list[1] = 'УИК'
    field_keys_list.pop(-4)
    # print(len(field_keys_list))
    # header_dict = dict.fromkeys(field_text_list, [])
    # print(header_dict)
    field_rows_list = [[tik_names[link_num]]]
    tree = lxml.etree.ElementTree(tds[1])
    trs = tree.xpath('//tr')
    for tr in trs:
        field_values_list = []
        fields = tr.getchildren()
        for field in fields:
            tree = lxml.etree.ElementTree(field)
            field_text = tree.xpath('//text()')
            field_values_list.append(field_text[0])
        field_rows_list.append(field_values_list.copy())
    field_rows_list.pop(-4)
    field_rows_list[0] *= len(field_values_list)
    # print(field_rows_list)
    temp_dict = dict(zip(field_keys_list, field_rows_list))
    # print(temp_dict)

    if not link_num:
        data_dict = temp_dict.copy()

    for key in data_dict.keys():
        data_dict[key].extend(temp_dict[key])

df = pd.read_csv('data.csv', index=False)
# df = pd.DataFrame.from_dict(data_dict)
# print(df.sum(numeric_only=True).head())
# df.append(df.sum(numeric_only=True))
# df.to_csv(index=False, path_or_buf='data.csv')
print(df.info())
# resp = requests.get(el_com_link)
# print(resp, resp.text)
# soup = BeautifulSoup(resp.text, 'html.parser')
# print(soup.prettify())

