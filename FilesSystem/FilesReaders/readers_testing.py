from SystemCore.FilesSystem.FilesReaders.PandasReader import PandasReader

catalog = 'D:\Projects\Data\Данные/'
csv = 'Полная генерация min 24 со статистикой get SERP.csv'
xlsx = 'Лист Microsoft Excel.xlsx'
PR = PandasReader()
print(f'cool? - {PR._Logger.are_process_cool_yet}')
# Тест чтения
read = {}
read[21] = PR.read_excel(PR.connect_path(directory=catalog, file_name=xlsx))

print(f'cool? - {PR._Logger.are_process_cool_yet}')


print('Вывод стандартного xlsx',
      PR.write_excel(read[21],
                     PR.connect_path(directory=catalog, file_name=xlsx))
      )

print('Вывод листа xlsx',
      PR.write_excel(read[21]['Лист1'],
                     PR.connect_path(directory=catalog, file_name=xlsx))
      )

print('Вывод Series xlsx',
      PR.write_excel(read[21]['Лист1']['request'],
                     PR.connect_path(directory=catalog, file_name=xlsx))
      )

#PR._Logger._FailedMessages.failed_requests
# encoding="utf-8"
print(f'cool? - {PR._Logger.are_process_cool_yet}')