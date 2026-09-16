let yatirimEkleButonu = document.querySelector("#yatirimEkle");
let yatirimlarDiv = document.querySelector("#yatirimlar");

let secenekler = ["nvidia", "altin", "avgo", "apple", "tesla", "microsoft", "amazon", "google", "netflix", "amd"];

function tumDropdownlariGuncelle() {     //her ekleme/silme/secim degisikliginde TUM dropdown'lari yeniden ciz
    let tumSelectler = document.querySelectorAll('select[name="hisse[]"]');
    let hepsininSecimi = Array.from(tumSelectler).map(function(s) {
        return s.value;
    });

    tumSelectler.forEach(function(select) {
        let benimSecimim = select.value;     //bu dropdown'un KENDI secimi, korunmali

        let izinliSecenekler = secenekler.filter(function(secenek) {
            return secenek === benimSecimim || !hepsininSecimi.includes(secenek);     //kendi secimi VEYA baskasinda yoksa goster
        });

        select.innerHTML = "";     //once icini bosalt, yeniden ciz (to-do list'teki mantik)
        izinliSecenekler.forEach(function(secenek) {
            let option = document.createElement("option");
            option.value = secenek;
            option.textContent = secenek;
            if (secenek === benimSecimim) {
                option.selected = true;     //kendi secimini kaybetme
            }
            select.appendChild(option);
        });
    });
}

    yatirimEkleButonu.addEventListener("click", function() {
    let tumSelectler = document.querySelectorAll('select[name="hisse[]"]');
    let hepsininSecimi = Array.from(tumSelectler).map(function(s) { return s.value; });
    let kalanSecenekler = secenekler.filter(function(secenek) {
        return !hepsininSecimi.includes(secenek);
    });

    if (kalanSecenekler.length === 0) {     //kalan secenek yoksa uyar ve dur
        alert("Tum yatirim hisselerini sectiniz!");
        return;
    }

    let yeniSatir = document.createElement("div");     //select+input+sil butonunu saracak kapsayici
    yeniSatir.classList.add("yatirim-satiri");

    let yeniSelect = document.createElement("select");
    yeniSelect.name = "hisse[]";
    yeniSelect.addEventListener("change", tumDropdownlariGuncelle);     //secim degisince HEPSINI guncelle

    let yeniInput = document.createElement("input");
    yeniInput.type = "text";
    yeniInput.name = "tutar[]";
    yeniInput.placeholder = "Tutar";

    let silButonu = document.createElement("button");
    silButonu.type = "button";     //form'u gondermesin, sadece silsin
    silButonu.textContent = "Sil";
    silButonu.addEventListener("click", function() {
        yeniSatir.remove();     //kendi kapsayicisini (select+input+bu buton) DOM'dan kaldir
        tumDropdownlariGuncelle();     //sildikten SONRA hepsini guncelle, hisse tekrar secilebilir olsun
    });

    yeniSatir.appendChild(yeniSelect);
    yeniSatir.appendChild(yeniInput);
    yeniSatir.appendChild(silButonu);
    yatirimlarDiv.appendChild(yeniSatir);

    tumDropdownlariGuncelle();     //yeni satir eklendikten SONRA hepsini guncelle (kendisi dahil)
});

    let form = document.querySelector("form");
    let hesaplaBtn = document.querySelector("#hesaplaBtn");

    form.addEventListener("submit", async function(event) {
        event.preventDefault();
        let veri = new FormData(form);

        hesaplaBtn.textContent = "Hesaplaniyor...";
        hesaplaBtn.disabled = true;     // tekrar tekrar tiklanmasini engelle

            let response = await fetch("/", { method: "POST", body: veri });
            let data = await response.json();
    
        
            if (data.hata) {
                alert(data.hata);
                hesaplaBtn.textContent = "Hesapla";
                hesaplaBtn.disabled = false;
                return;            // tabloyu çizmeye devam etme, fonksiyondan çık
            }

            let sonucAlani = document.querySelector("#sonucAlani");
            sonucAlani.innerHTML = "";       //eski tabloyu temizle

            let tablo = document.createElement("table");
            let baslikSatiri = document.createElement("tr");

            let yilBaslik = document.createElement("th");
            yilBaslik.textContent = "Yil";
            baslikSatiri.appendChild(yilBaslik);

            Object.keys(data.hisse_detaylari).forEach(function(hisse){
                let hisseBaslik = document.createElement("th");
                hisseBaslik.textContent = hisse;
                baslikSatiri.appendChild(hisseBaslik);
            });
            

            let toplamBaslik = document.createElement("th");
            toplamBaslik.textContent = "Toplam";
            baslikSatiri.appendChild(toplamBaslik);

            tablo.appendChild(baslikSatiri);

            for (let i = 0; i < data.yil; i++) {
    let satir = document.createElement("tr");

    let yilSutunu = document.createElement("td");
    yilSutunu.textContent = i + 1;
    satir.appendChild(yilSutunu);

    Object.entries(data.hisse_detaylari).forEach(function([hisse, degerler]) {
        let hisseSutunu = document.createElement("td");
        hisseSutunu.textContent = degerler[i] + " TL";
        satir.appendChild(hisseSutunu);
    });

    let toplamSutunu = document.createElement("td");
    toplamSutunu.textContent = data.sonuc[i] + " TL";
    satir.appendChild(toplamSutunu);

    tablo.appendChild(satir);
}

            sonucAlani.appendChild(tablo);
            hesaplaBtn.textContent = "Hesapla";
            hesaplaBtn.disabled = false;
        });
