from SystemCore.SQLconnectors.Connectors import MySQLconnector
from SystemCore.SQLconnectors.Connectors import RemoteBaseConnectionData

CD = RemoteBaseConnectionData(base_name='parser',
                              host='seo-mysql.bazadev.net', port=3306,
                              user='parser', password='Oyoo8laeNgegho')

SC = MySQLconnector(connection_data=CD)
