import sqlite3

baglanti = sqlite3.connect("magaza.db")
cursor = baglanti.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS urunler (id INTEGER PRIMARY KEY, isim TEXT UNIQUE, fiyat REAL)")
baglanti.commit()

cursor.execute("INSERT OR IGNORE INTO urunler (isim, fiyat) VALUES (?, ?)", ("Ray-Ban Aviator", 1200))
baglanti.commit()

cursor.execute("INSERT OR IGNORE INTO urunler (isim, fiyat) VALUES (?, ?)", ("Ray-Ban META", 1800))
baglanti.commit()

cursor.execute("INSERT OR IGNORE INTO urunler (isim, fiyat) VALUES (?, ?)", ("Oakley META", 2000))
baglanti.commit()

cursor.execute("SELECT * FROM urunler")
sonuclar = cursor.fetchall()
print(sonuclar)