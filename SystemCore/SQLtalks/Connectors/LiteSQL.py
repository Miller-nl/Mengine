import sqlite3

data_catalog = 'D:/Projects/ML-training/DataRecommender/data/'
conn = sqlite3.connect(data_catalog + "mydatabase.db")
cursor = conn.cursor()

# c.execute()
# conn.commit()


# Таблицы, дублирующие csv
# clients
# products
# purchases

'''
Index(['client_id', 'first_issue_date', 'first_redeem_date', 'age', 'gender'], dtype='object')

Index(['product_id', 'level_1', 'level_2', 'level_3', 'level_4', 'segment_id',
       'brand_id', 'vendor_id', 'netto', 'is_own_trademark', 'is_alcohol'],
      dtype='object')

Index(['client_id', 'transaction_id', 'transaction_datetime',
       'regular_points_received', 'express_points_received',
       'regular_points_spent', 'express_points_spent', 'purchase_sum',
       'store_id', 'product_id', 'product_quantity', 'trn_sum_from_iss',
       'trn_sum_from_red'],
      dtype='object')

'''

# Создание таблицы
cursor.execute("CREATE TABLE albums (title text, artist text, release_date text, publisher text, media_type text)")







