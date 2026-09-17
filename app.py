from flask import Flask, render_template, request, jsonify
import yfinance as yf
from datetime import datetime, timedelta
import math 
import os

app = Flask(__name__)

def turkce_formatla(sayi):     #binlik ayrac + virgullu ondalik icin
    ingilizce = f"{sayi:,.2f}"          # "123,456.79"
    turkce = ingilizce.replace(",", "X").replace(".", ",").replace("X", ".")
    return turkce                        # "123.456,79"


def gercek_getiriyi_getir(sembol, yil):     #gercek CAGR getirisini yfinance ile hesaplama
    try:
        bitis = datetime.now()
        baslangic = bitis - timedelta(days=365 * yil)
        hisse = yf.Ticker(sembol)
        veri = hisse.history(start=baslangic, end=bitis)
        ilk_fiyat = veri["Close"].iloc[0]
        son_fiyat = veri["Close"].iloc[-1]
        cagr = (son_fiyat / ilk_fiyat) ** (1 / yil) - 1
        return cagr * 100
    except Exception:
        return None     #veri cekilemezse None dondur, program cokmesin

def yatirimi_hesapla(tutar, getiri, yil):     #bilesik buyume hesaplama
    yilsonu_gelisim = []              #bos liste, fonksiyonun EN BASINDA
    for i in range(1, yil + 1):
        tutar = tutar * (1 + getiri / 100)
        yilsonu_gelisim.append(round(float(tutar), 2))        #her yilin sonucunu listeye ekle, float() numpy turunu normale cevirir
    return yilsonu_gelisim               #artik TEK bir sayi degil, TUM YILLARIN listesini donduruyor

borsa_sembolleri = {     #isim -> yfinance sembolu eslestirmesi (BIST hisseleri guvenilmez veri yuzunden kaldirildi)
    "nvidia": "NVDA",
    "altin": "GC=F",
    "avgo": "AVGO",
    "apple": "AAPL",
    "tesla": "TSLA",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "google": "GOOG",
    "netflix": "NFLX",
    "amd": "AMD",
}

@app.route("/", methods=["GET", "POST"])     #hem sayfa gorunumu hem form gonderimi kabul et
def anasayfa():
    if request.method == "POST":     #form gonderildiyse bu blok calisir
        hisseler = request.form.getlist("hisse[]")     #coklu secilen hisseleri liste olarak al
        tutarlar = request.form.getlist("tutar[]")      #karsilik gelen tutarlari liste olarak al
        yil_str = request.form["yil"]

        try:
            yil = int(yil_str)

            if yil <= 0:
                return jsonify(hata="Lutfen yil icin pozitif bir deger giriniz!")
        
            toplam_gelisim = [0] * yil     #yil sayisi kadar 0'lardan olusan baslangic listesi
            hisse_detaylari = {}       #her hissenin kendi yil yil gelisimini tutacak sozluk

            for hisse, tutar_str in zip(hisseler, tutarlar):     #DIS dongu: her hisseyi sirayla isle
                hisse = hisse.lower()

                if hisse not in borsa_sembolleri:     #sunucu tarafi dogrulama, dropdown olsa bile kalmali
                    return jsonify(hata=f"{hisse} gecersiz bir yatirim araci!")

                sembol = borsa_sembolleri[hisse]
                tutar = float(tutar_str)     #form verisi hep string gelir, sayiya cevir
                if tutar <= 0:
                    return jsonify(hata=f"{hisse} icin tutar pozitif olmalidir!")

                getiri = gercek_getiriyi_getir(sembol, yil)
                if getiri is None or math.isnan(getiri):     #None VE NaN ikisi de kontrol edilmeli
                    return jsonify(hata=f"{hisse} icin veri alinamadi!")

                yillik_liste = yatirimi_hesapla(tutar, getiri, yil)     #bu hissenin yil yil gelisimi
                hisse_detaylari[hisse] = yillik_liste      #bu hissenin sonucunu sozlukte, kendi ismiyle sakla

                for i in range(yil):     #IC dongu: bu hissenin payini genel toplama ekle
                    toplam_gelisim[i] += yillik_liste[i]

            toplam_gelisim = [round(deger, 2) for deger in toplam_gelisim]     #tum hisseler islendikten SONRA son yuvarlama
            toplam_gelisim = [turkce_formatla(deger) for deger in toplam_gelisim]     #YENI: bicimlendir

            for hisse in hisse_detaylari:     #YENI: sozlukteki her hissenin listesini de bicimlendir
                hisse_detaylari[hisse] = [turkce_formatla(deger) for deger in hisse_detaylari[hisse]]
            return jsonify(sonuc=toplam_gelisim, yil=yil, hisse_detaylari=hisse_detaylari)
        except ValueError:
            return jsonify(hata="Lutfen gecerli bir deger giriniz!")

    return render_template("index.html", sonuc=None)     #ilk acilista (GET) form bos gosterilir


if __name__ == "__main__":
    test_mesaji = os.environ.get("TEST_MESAJI", "Ortam degiskeni bulunamadi, varsayilan calisiyor!")
    print(test_mesaji)
    app.run(debug=True)     #debug=True: kod kaydedince sunucu otomatik yenilenir

