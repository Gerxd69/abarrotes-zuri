import sqlite3

con = sqlite3.connect("database/zuri.db")
cur = con.cursor()
cur.execute("UPDATE producto SET stock_actual = 30")
con.commit()
con.close()
print(f"Stock actualizado a 30 en todos los productos.")
