# LIBRARY
import psycopg
import pandas as pd
import tabulate
import os




# DIBAWAH INI HANYA BUAT REFERENSI CARA NULIS PSYCOPG, SILAHKAN BERKREASI DIATA

friendsHeader = ["NAME", "ADDRESS", "UNIVERSITY", "DEPARTEMENT", "MAJOR"]
friends = []

def lihat_data():
    os.system('cls')
    friends = []
    with psycopg.connect("dbname=postgres user=postgres password=dammahom51") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM friends
                """)
            for i in cur:
                friends.append(i)
    df = pd.DataFrame(friends)
    print(tabulate.tabulate(df, tablefmt="grid", headers=friendsHeader))

menu = input("pilih menu : ")

if menu == '1':
    lihat_data()
elif menu =='2':
    pass
