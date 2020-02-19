

from Graphs.Directed.Old.Graph import DirectedGraph
from Graphs.Directed.GraphElement import GraphElement
import time
from CatalogCommunication.PandasSimpleReader import PandasSimpleReader


from Managers import ProcessesManager

catalog = 'E:/0_Data/Тестирование скорости скрипта'
file_name = 'Укороченный набор со статистикой.csv'
phrase_column = 'request'

ProcMan = ProcessesManager(process_name='Тест нового графа', subdirectory='Testing')
launch_module_name = 'Тест нового графа'

Graph = DirectedGraph(launch_module_name, ProcMan)  # Создали граф
Reader = PandasSimpleReader(launch_module_name=launch_module_name, process_manager=ProcMan)

Data = Reader.csv_import(directory=catalog, file_name=file_name)
# Пошли собирать штуки
value_marker = '_value'
no_value = 'no_value'

data_columns = []
for column in Data.columns.tolist():  # Берём список колонок фрейма
    if value_marker in column:  # Если это столбец со значением
        data_columns.append(column)  # добавим столбец в список

for str_id in Data.index:
    phrase_tokens = []
    for column in data_columns:  # пошли по столбцам с данными
        if Data.loc[str_id, column] != no_value:  # и значение не пустое
            phrase_tokens.append(Data.loc[str_id, column])

    # Добавим в граф элемент
    Element = GraphElement(str_id)
    Element.set_tokens(tokens=phrase_tokens)  # Установим токены
    Element.phrase = Data.loc[str_id, phrase_column]
    Graph.add_element(graph_element=Element)  # передадим в граф

Now = time.time()
print('Начинаю построение графа')
Graph.upbuild()
print(f'Затраченное на построение графа время {round(time.time()-Now,2)}')
import sys
print(f'Размер объёкта {sys.getsizeof(Graph)}')

exit()  #Закончим

'''
for j in range(1, 5):
    for k in range(0, 6):
        for z in range(0, 6):
            Element = GraphElement(element_id=j*100 + k * 10 + z)
            Element.set_tokens(tokens=[j, k, z])  # Установим токены
            result = Graph.add_element(graph_element=Element)# передадим в граф

        Element = GraphElement(element_id=j * 10000 + k + 1000)
        Element.set_tokens(tokens=[j, k])  # Установим токены
        Graph.add_element(graph_element=Element)  # передадим в граф


    Element = GraphElement(element_id=j * 100000)
    Element.set_tokens(tokens=[j])  # Установим токены
    Graph.add_element(graph_element=Element)  # передадим в граф

# Процессинг через стандартную функцию
from Graphs.Directed.Methods.Builder import single_processing_upbuild, lists_compare
result = single_processing_upbuild(Graph)
'''

# Выведем граф
heads = Graph.get_heads()
print(f'Список голов: {heads}')
def show(el_id, type='down', level=0):  # или up
    element = Graph.get_element(el_id=el_id)
    print('   '*level + str(el_id) + '  ' + str(element.tokens_list) + '   "' + element.phrase + '"')

    if type == 'down':
        go_list = element.nearest_children
    elif type == 'up':
        go_list = element.nearest_parents
    else:
        go_list = []
    for el in go_list:
        show(el_id=el, level=level+1,
             type=type)

def show_el(el_id):
    element = Graph.get_element(el_id=el_id)
    print(f'Фраза {element.phrase}')
    print(f'tokens_list={element.tokens_list}')
    print(f'nearest_parents={element.nearest_parents}')
    print(f'nearest_children={element.nearest_children}')
    print(f'doubles={element.doubles}')
    print(f'duplicate={element.duplicate}')

Ids = Graph.get_elements_ids()

A = Graph.get_element(110)
print(A.tokens_list)



