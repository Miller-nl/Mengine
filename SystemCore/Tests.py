from SystemCore.SQLtalks.Connectors.PostgreSQL import PostgreSQLconnector
from SystemCore.SQLtalks.Connectors.ConnectionDTOs import RemoteBaseConnectionData
import psycopg2

CD = RemoteBaseConnectionData(base_name='AutoSEO',
                              host='localhost', port='1234',
                              user='postgres', password='catalog')


PSC = PostgreSQLconnector(connection_data=CD)
PSC.connect()

request = 'SELECT * FROM geo_data'
print(PSC.request_fetch_all(request)[:2])
print(PSC.request_fetch_many(request, 2))
print(PSC.request_fetch_value(request))
print('Сделаем ошибку')
print(PSC.request_fetch_many(request))

print('Запросим ещё раз')
print(PSC.request_fetch_value(request + 'aaa'))

print()
print(f'Список ошибок: {PSC._mistakes}')

#print(PSC.request_fetch_all('SELECT * FROM geo_dataa'))
#print(PSC._mistakes())
