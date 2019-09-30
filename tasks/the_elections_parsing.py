import requests
import lxml.html
import lxml.etree
import re
import pandas as pd


resp = requests.get('http://www.st-petersburg.vybory.izbirkom.ru/region/region/st-petersburg?action=show&root=1&tvd='
                    '27820001217417&vrn=27820001217413&region=78&global=&sub_region=78&prver=0&pronetvd=null&vibid='
                    '27820001217417&type=222')

tree = lxml.html.fromstring(resp.text)

tik_names = tree.xpath('//a[@style="text-decoration: none"]/text()')  # получаем названия ТИК
tik_links = tree.xpath('//a[@style="text-decoration: none"]/@href')  # получаем ссылки на ТИК


def rename(expr):
    if expr[1] == 'Территориальная избирательная комиссия':
        return 'lec' + str(expr[2])
    elif expr[1] == 'УИК':
        return str(expr[2])
    elif expr[0] == 'Цифровые избирательные участки':
        return 'dec'


tik_names = list(map(lambda x: re.sub(r'(Территориальная избирательная комиссия) №(\d+)'
                                      r'|Цифровые избирательные участки',
                                      rename, x), tik_names))

for link_num, tik_link in enumerate(tik_links):
    print(link_num, tik_link)
    resp = requests.get(tik_link)
    tree = lxml.html.fromstring(resp.text)
    if link_num < 30:
        table = tree.xpath('//table[@style="width:100%;border-color:#000000"]/tr')  # нашли таблицу
        tds = table[0].getchildren()  # берём обе половинки таблицы
        if not link_num:  # если в первый раз, то надо собрать названия полей
            tree = lxml.etree.ElementTree(tds[0])  # взяли первую
            trs = tree.xpath('//tr')  # получаем ряды таблицы
            field_keys_list = ['ec']  # список полей таблицы
            for tr in trs:  # проходимся по рядам таблицы, собирая названия полей
                fields = tr.getchildren()
                tree = lxml.etree.ElementTree(fields[1])
                field_text = tree.xpath('//text()')[0]
                field_keys_list.append(field_text)
            field_keys_list[1] = 'lec'
            field_keys_list.pop(-4)
            # закончили с первой половиной, приступаем ко второй
        field_rows_list = [[tik_names[link_num]]]  # список списков (данных) таблицы
        tree = lxml.etree.ElementTree(tds[1])
        trs = tree.xpath('//tr')
        for tr in trs:  # проходимся по рядам таблицы, собирая данные
            field_values_list = []
            fields = tr.getchildren()
            for field in fields:
                tree = lxml.etree.ElementTree(field)
                field_text = tree.xpath('//text()')
                try:
                    field_text = int(field_text[0])
                except ValueError:
                    field_text = field_text[0]
                field_values_list.append(field_text)
            field_rows_list.append(field_values_list.copy())
        field_rows_list.pop(-4)
        field_rows_list[0] *= len(field_values_list)  # дублируем название ТИК, реализуя соотношение one to many
    else:  # у страницы цифровых избирательных участков другая разметка, спарсим её отдельно
        table = tree.xpath('//table[@cellpadding="2"][@border="0"][@bgcolor="#ffffff"][@cellspacing="1"]')
        # нашли таблицу
        trs = table[0].getchildren()  # получаем ряды таблицы
        field_rows_list = [[tik_names[link_num]], '-']  # список списков (данных) таблицы
        for tr in trs:  # проходимся по рядам таблицы, собирая названия полей
            field_values_list = []
            fields = tr.getchildren()
            tree = lxml.etree.ElementTree(fields[-1])
            field_text = tree.xpath('//text()')[0]
            try:
                field_text = int(field_text)
            except ValueError:
                field_text = field_text
            field_values_list.append(field_text)
            field_rows_list.append(field_values_list.copy())
        field_rows_list.pop(-4)
        print(field_rows_list, '\n', field_values_list)

    #  заменим названия УИК только на цифры
    field_rows_list[1] = list(map(lambda x: re.sub(r'([а-яА-Я]{3}) №(\d+)', rename, x), field_rows_list[1]))
    temp_dict = dict(zip(field_keys_list, field_rows_list))  # составляем буферный словарь из сгенерированных списков
    if link_num == 30:
        print(temp_dict)

    if not link_num:  # если в первый раз, то задаём конечный словарь
        data_dict = temp_dict.copy()
    if link_num:  # если не в первый раз, то просто дописываем данные в словарь
        for key in data_dict.keys():
            data_dict[key].extend(temp_dict[key])

df = pd.DataFrame.from_dict(data_dict)
df = df.rename(columns={'ТИК': 'TIK', 'УИК': 'UIK',
                        'Число избирателей, внесенных в список избирателей на момент окончания голосования':
                            'total_voters',
                        'Число избирательных бюллетеней, полученных участковой избирательной комиссией':
                            'total_ballots',
                        'Число избирательных бюллетеней, выданных избирателям в помещении для голосования в день '
                        'голосования': 'local_ballots',
                        'Число избирательных бюллетеней, выданных избирателям, проголосовавшим вне помещения '
                        'для голосования': 'distant_ballots',
                        'Число погашенных избирательных бюллетеней': 'unused_ballots',
                        'Число избирательных бюллетеней, содержащихся в переносных ящиках для голосования':
                        'in_mobile_boxes',
                        'Число избирательных бюллетеней, содержащихся в стационарных ящиках для голосования':
                            'in_stationary_boxes',
                        'Число недействительных избирательных бюллетеней': 'spoiled_ballots',
                        'Число действительных избирательных бюллетеней': 'valid_ballots',
                        'Число утраченных избирательных бюллетеней': 'lost_ballots',
                        'Число избирательных бюллетеней, не учтенных при получении': 'unaccounted_ballots',
                        'Амосов Михаил Иванович': 'amosov', 'Беглов Александр Дмитриевич': 'beglov',
                        'Тихонова Надежда Геннадьевна': 'tikhonova'})

df.to_csv(index=False, path_or_buf='data.csv')
print(df.head())
