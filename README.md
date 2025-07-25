# Program za analizu fotografija po dominantnoj boji i Hue vrijednosti

Program je dostupan u dvije verzije: 

[WEB VERZIJA PROGRAMA](https://marioolcar.github.io/HUE_SORT/) i Python skripta

Ovaj program analizira skup slika (.jpg/.png) unutar zadane mape, detektira dominantne boje, ton i svjetlinu boje, te generira interaktivnu HTML stranicu s:

- trakom boja s HEX tooltipima
- galerijom slika sortiranim po hue vrijednosti
- klikabilnim slikama s modalnim prikazom (fullscreen + next/prev navigacija)

---

## Zahtjevi (Python verzija)

Python 3.7+
Preporučeno virtualno okruženje (`venv`, `conda`, itd.)

---

## Instalacija biblioteka (Python verzija)

1. Kloniraj repozitorij (ili kopiraj skriptu i `requirements.txt`)
2. Pokreni terminal i instaliraj potrebne biblioteke:

```bash
pip install -r requirements.txt
```

---

# Pokretanje skripte (Python verzija)

1. Pokreni skriptu s ovom naredbom i zamijeni `./putanja/do/slika` sa željenom putanjom do mape s .jpg ili .png fotografijama

```bash
python HueSort.py ./putanja/do/slika
```

---

## Rezultat

Otvori **output.html** koji se nalazi u istoj mapi kao i program u Web pregledniku za prikaz sortiranih fotografija i dominantnih boja

![Screenshot nastale web stranice](screenshot.png "Screenshot Web stranice")
