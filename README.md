# 🌊 KRAKNAUTICA 2099 — Mini-CTF (KN SpooferPhish)

Mini-gra CTF przygotowana na stoisko **KN SpooferPhish** (Politechnika Krakowska) na Targi Pracy 2026.
Uczestnicy łączą się bezpośrednio ze swoich telefonów do lokalnego hotspotu / mini-routera i rozwiązują 4 poziomy zagadek w klimacie podwodnego miasta hi-tech z retro-futurystycznym interfejsem CRT (zielony fosfor, linie skanowania, animacja fali).

---

## 🎯 Przegląd Poziomów (Zaprojektowane dla osób na każdym poziomie)

Każdy etap posiada **dokładnie 3 podpowiedzi na każdą część** (łącznie 24 podpowiedzi w całej grze), odkrywane bez kar punktowych, zoptymalizowane pod telefony bez potrzeby instalacji jakichkolwiek narzędzi (wszystko w przeglądarce).

1. **Poziom 1 — Protokół Śluzy (Logika / Sekwencja)**:
   - 4-elementowa sekwencja logiczna symboli (żółty, zielony, czerwony, niebieski z oznaczeniami ■, ●, ▲, ◆).
   - 5 unikalnych wariantów przypisywanych losowo graczom (zapobiega bezpośredniemu podglądaniu sąsiada).
   - Wprowadzenie hasła do sejfu śluzy i odbiór pierwszej flagi: `SPOOF{AIRLOCK_OPEN}`.

2. **Poziom 2 — Przechwycony Sonar & Terminal Główny (Krypto & Linux)**:
   - **Część A (Szyfr Cezara)**: Przechwycona transmisja podwodna zaszyfrowana prostym przesunięciem. Interaktywny suwak ROT z podpowiedzią i żartem o brakującym prawym Alt. Hasło do mainframe: `trident42`.
   - **Część B (Terminal Mainframe)**: Symulowana w 100% w Pythonie konsola uniksowa (`ls`, `cd`, `cat`, `pwd`, pliki-zmyłki). Flaga w `/reactor/core_access.txt`: `SPOOF{REACTOR_ONLINE}`.

3. **Poziom 3 — Baza Załogi & Panel Kapitański (IDOR & Broken Auth)**:
   - **Część A (IDOR)**: Przeglądarka kart nurków załogi `?id=17`. Zmiana identyfikatora na `?id=1` odkrywa kartę Kapitana Octaviusa Krakena z danymi logowania: `admin` / `kraknautica2099`.
   - **Część B (Panel Kapitański)**: Logowanie do terminala kapitańskiego, odczyt notatki serwisowej z flagą `SPOOF{CAPTAIN_LOG_DEEP}` oraz hasłem awaryjnym dla SI: `ABYSS-OVERRIDE-99`.

4. **Poziom 4 — Sabotaż SI NEREUS & Cyfrowa Forensyka (Socjotechnika & Steganografia)**:
   - **Część A (Phishing)**: Skrzynka pocztowa z 4 e-mailami. Zadanie: wskazać domenę phishingową (`support@kraknautica-c0re.pl`).
   - **Część B (Emergency Override)**: Wybór frazy awaryjnej z przycisków wyboru (brak ryzyka literówek). Skłonienie SI NEREUS do wycieku skanu sonaru `sonar_scan.png`.
   - **Część C (Inspektor Spektralny Sonaru)**: Wbudowane w przeglądarkę narzędzie kryminalistyczne na Canvasie HTML5 (suwak Gain, tryb UV, odwrócenie barw Invert). Odkrycie ukrytej flagi: `SPOOF{NEREUS_UNMASKED}`.

5. **Finał — Odbiór Nagrody**:
   - Wyświetlenie unikalnego kodu odbioru gadżetu (np. `ABC-DEF`) oraz kodu wznowienia sesji (`KRAKEN-XXXX`).

---

## 🚀 Szybki Start na Stoisku (Instrukcja dla Organizatora)

### Wymagania:
- Python 3.10+ (na Windowsie dostępny jako `py` lub `python`).
- Wszystkie zależności są zainstalowane w lokalnym środowisku (`pip install -r requirements.txt`).
- Całość działa **100% OFFLINE** — brak zewnętrznych CDN-ów, fontów z Google czy skryptów zewnętrznych.

### Krok po kroku:
1. **Konfiguracja sieci / routera:**
   - Skonfiguruj mini-router lub hotspot w telefonie / laptopie (np. Wi-Fi: `SpooferPhish_CTF`).
   - Sprawdź lokalny adres IP laptopa (np. `192.168.1.50`).

2. **Uruchomienie serwera:**
   - Kliknij dwukrotnie plik `start.bat` **LUB** w terminalu wpisz:
     ```bash
     py app.py
     ```
   - Serwer uruchomi się na porcie `8080`.
   - W konsoli wyświetli się **kod QR** oraz link do gry, a także wygenerowane hasło do panelu admina (lub zdefiniowane w zmiennej środowiskowej `CTF_ADMIN_PASSWORD`).

3. **Wydruk / Wyświetlenie kodu QR dla graczy:**
   - Gracze po połączeniu z Wi-Fi skanują kod QR kierujący na `http://<IP_LAPTOPA>:8080` (np. `http://192.168.1.50:8080`).

---

## 🖥️ Ekrany Organizatorów

- **Tablica Wyników (Live Board):** `http://<IP_LAPTOPA>:8080/board`
  - Przeznaczona do rzucenia na monitor / rzutnik na stoisku.
  - Odświeża się automatycznie na żywo bez przeładowywania strony (co 5 sekund).
  - Prezentuje ukończone poziomy, czasy oraz liczbę wykorzystanych podpowiedzi.

- **Panel Wydawania Nagród (Admin Desk):** `http://<IP_LAPTOPA>:8080/admin`
  - Logowanie hasłem admina (wyświetlonym w konsoli przy starcie lub podanym w `CTF_ADMIN_PASSWORD`).
  - Pozwala natychmiast zweryfikować kod odbioru nagrody (np. `ABC-DEF`) podany przez gracza.
  - Blokuje próby wielokrotnego odbioru nagrody przez tę samą osobę i monitoruje stan magazynu gadżetów.

---

## 🔒 Bezpieczeństwo i Odporność

- **Pełne sparametryzowanie zapytań SQL**: baza SQLite odporna na SQL Injection.
- **Bezpieczny terminal**: komendy `ls`, `cd`, `cat` są wirtualnym słownikiem w Pythonie — brak dostępu do powłoki systemu Windows.
- **CSRF Token & Content Security Policy (CSP)**: nagłówki blokujące zewnętrzne skrypty i wstrzykiwanie kodu.
- **Walidacja wejścia**: pseudonimy i wejścia formularzy poddane rygorystycznemu filtrowaniu.
- **Rate limiting**: ochrona przed zalaniem żądaniami w środowisku produkcyjnym (automatycznie omijany w testach jednostkowych).

---

## 🧪 Uruchomienie Testów

Aby uruchomić pełny zestaw 23 testów sprawdzających kompletne przejście gry (PL i EN), mechanizmy bezpieczeństwa, logikę i odporność na błędy:

```bash
py -m unittest discover -s tests -v
```
