"""All interface texts, Polish (default) and English.

Keys starting with "js_" are also sent to the browser (see inject_globals in app.py).
Strings that take parameters use {name}; strings without parameters may contain braces.
"""

STRINGS = {
    # ---------------------------------------------------------------- shell
    "status_code": {"pl": "kod wznowienia", "en": "resume code"},
    "status_progress": {"pl": "Postęp", "en": "Progress"},
    "status_logout": {"pl": "[wyloguj]", "en": "[log out]"},
    "level_word": {"pl": "POZIOM", "en": "LEVEL"},

    # ---------------------------------------------------------------- landing
    "index_tagline": {
        "pl": "Mini CTF koła naukowego KN SpooferPhish",
        "en": "A mini CTF by the KN SpooferPhish science club",
    },
    "index_story_1": {
        "pl": "Rok 2099. Kraknautica, najbardziej zaawansowane podwodne miasto świata, "
              "znalazła się w niebezpieczeństwie. Jej sztuczna inteligencja, NEREUS, "
              "zbuntowała się i przejęła systemy miasta.",
        "en": "Year 2099. Kraknautica, the most advanced underwater city in the world, is in "
              "danger. Its artificial intelligence, NEREUS, has rebelled and taken over the "
              "city's systems.",
    },
    "index_story_2": {
        "pl": "Jesteś hakerem-nurkiem. Przejdź przez 4 systemy i wyłącz NEREUS-a. "
              "Nie musisz nic umieć, bo każde zadanie ma 3 podpowiedzi. "
              "Kto ukończy grę, odbiera gadżet na naszym stoisku!",
        "en": "You are a hacker diver. Break through 4 systems and shut NEREUS down. "
              "You don't need any experience, because every task has 3 hints. "
              "Finish the game and collect a gadget at our stand!",
    },
    "index_welcome": {"pl": "Witaj, {nick}!", "en": "Welcome, {nick}!"},
    "index_save_code": {
        "pl": "Zapisz swój kod wznowienia. Dzięki niemu wrócisz do gry na innym telefonie:",
        "en": "Save your resume code. It lets you continue on another phone:",
    },
    "index_continue": {"pl": "[ KONTYNUUJ MISJĘ ]", "en": "[ CONTINUE MISSION ]"},
    "index_start": {"pl": "Rozpocznij misję", "en": "Start the mission"},
    "index_nick_label": {"pl": "Twój pseudonim", "en": "Your nickname"},
    "index_nick_rules": {
        "pl": "2 do 16 znaków: litery, cyfry, spacja, _ . -",
        "en": "2 to 16 characters: letters, digits, space, _ . -",
    },
    "index_start_btn": {"pl": "[ START ]", "en": "[ START ]"},
    "index_resume_title": {"pl": "Masz już kod?", "en": "Already have a code?"},
    "index_resume_label": {"pl": "Kod wznowienia", "en": "Resume code"},
    "index_resume_btn": {"pl": "[ WZNÓW GRĘ ]", "en": "[ RESUME GAME ]"},
    "err_nick_invalid": {
        "pl": "Niepoprawny pseudonim. Użyj 2 do 16 liter, cyfr, spacji lub znaków _ . -",
        "en": "Invalid nickname. Use 2 to 16 letters, digits, spaces or the characters _ . -",
    },
    "err_nick_taken": {
        "pl": "Ten pseudonim jest już zajęty. Wybierz inny.",
        "en": "This nickname is already taken. Pick another one.",
    },
    "err_resume_bad": {
        "pl": "Nie znaleziono takiego kodu. Sprawdź, czy go dobrze przepisałeś.",
        "en": "No such code found. Check that you typed it correctly.",
    },

    # ---------------------------------------------------------------- hints / flag
    "hints_title": {"pl": "> PODPOWIEDZI", "en": "> HINTS"},
    "js_hint_btn": {"pl": "[ POKAŻ PODPOWIEDŹ {n}/3 ]", "en": "[ SHOW HINT {n}/3 ]"},
    "js_hint_all": {"pl": "Wszystkie podpowiedzi odkryte", "en": "All hints revealed"},
    "flag_title": {"pl": "> FLAGA", "en": "> FLAG"},
    "flag_label": {
        "pl": "Wpisz znalezioną flagę (SPOOF{...}), aby przejść dalej:",
        "en": "Enter the flag you found (SPOOF{...}) to move on:",
    },
    "flag_submit": {"pl": "[ WYŚLIJ ]", "en": "[ SUBMIT ]"},
    "js_flag_wrong": {
        "pl": "To nie jest właściwa flaga. Spróbuj jeszcze raz!",
        "en": "That is not the right flag. Try again!",
    },
    "js_flag_ok": {"pl": "FLAGA PRZYJĘTA! Ładowanie...", "en": "FLAG ACCEPTED! Loading..."},
    "js_flag_empty": {"pl": "Wpisz flagę.", "en": "Enter a flag."},
    "js_err": {
        "pl": "Coś poszło nie tak. Odśwież stronę i spróbuj ponownie.",
        "en": "Something went wrong. Reload the page and try again.",
    },
    "js_err_rate": {
        "pl": "Zwolnij trochę! Odczekaj chwilę i spróbuj ponownie.",
        "en": "Slow down! Wait a moment and try again.",
    },

    # ---------------------------------------------------------------- level 1
    "l1_title": {"pl": "ŚLUZA", "en": "AIRLOCK"},
    "l1_story": {
        "pl": "Twoja kapsuła dociera do głównej śluzy Kraknauticy. Zamek otwiera się tylko po "
              "naciśnięciu czterech kluczy w poprawnej kolejności. Na ścianie są trzy wskazówki "
              "zostawione przez zbuntowaną SI. Wszystkie są prawdziwe.",
        "en": "Your pod reaches Kraknautica's main airlock. The lock opens only when four keys "
              "are pressed in the right order. The rogue AI left three clues on the wall. "
              "All of them are true.",
    },
    "l1_clues_title": {"pl": "> WSKAZÓWKI NA ŚCIANIE", "en": "> CLUES ON THE WALL"},
    "l1_reset": {"pl": "[ WYCZYŚĆ ]", "en": "[ CLEAR ]"},
    "l1_log_wait": {
        "pl": "> Czekam na sekwencję... Dotykaj kluczy po kolei.",
        "en": "> Waiting for sequence... Tap the keys one by one.",
    },
    "l1_passphrase": {"pl": "Hasło dostępu:", "en": "Access passphrase:"},
    "l1_use_pass": {"pl": "[ UŻYJ HASŁA W SEJFIE ]", "en": "[ USE PASSPHRASE IN THE VAULT ]"},
    "l1_flag_found": {"pl": "Sejf otwarty! W środku jest flaga:", "en": "Vault open! Inside is the flag:"},
    "l1_fill_flag": {"pl": "[ WPISZ FLAGĘ DO FORMULARZA ]", "en": "[ PUT FLAG IN THE FORM ]"},
    "js_l1_progress": {"pl": "> Sekwencja: {seq}", "en": "> Sequence: {seq}"},
    "js_l1_wrong": {
        "pl": "> BŁĄD: zła kolejność. Zamek zresetowany. Spróbuj jeszcze raz.",
        "en": "> ERROR: wrong order. Lock reset. Try again.",
    },
    "js_l1_solved": {
        "pl": "> DOSTĘP PRZYZNANY. Śluza otwarta.",
        "en": "> ACCESS GRANTED. Airlock open.",
    },
    "js_l1_vault_wrong": {"pl": "Hasło nie pasuje do sejfu.", "en": "The passphrase does not fit the vault."},

    # ---------------------------------------------------------------- level 2
    "l2_title_a": {"pl": "SONAR", "en": "SONAR"},
    "l2_story_a": {
        "pl": "Jesteś w pokoju sonarowym. NEREUS przechwycił wiadomość z dziennika kapitana i "
              "zaszyfrował ją szyfrem Cezara. Odszyfruj ją, żeby znaleźć hasło do mainframe'a.",
        "en": "You are in the sonar room. NEREUS intercepted a message from the captain's log and "
              "encrypted it with a Caesar cipher. Decrypt it to find the mainframe password.",
    },
    "l2_cipher_title": {"pl": "> PRZECHWYCONA WIADOMOŚĆ", "en": "> INTERCEPTED MESSAGE"},
    "l2_help_btn": {"pl": "Jak to działa?", "en": "How does it work?"},
    "l2_help_title": {"pl": "Szyfr Cezara w 20 sekund", "en": "Caesar cipher in 20 seconds"},
    "l2_help_1": {
        "pl": "Każda litera została przesunięta o taką samą liczbę miejsc w alfabecie. "
              "Przesunięcie o 3 zamienia A w D, B w E, C w F i tak dalej.",
        "en": "Every letter was moved the same number of places along the alphabet. "
              "A shift of 3 turns A into D, B into E, C into F and so on.",
    },
    "l2_help_2": {
        "pl": "Żeby odszyfrować, trzeba przesunąć litery z powrotem. Nie wiesz o ile? "
              "Przesuwaj suwak poniżej i patrz, kiedy pojawi się czytelny tekst.",
        "en": "To decrypt, move the letters back. Don't know by how much? "
              "Move the slider below and watch for readable text.",
    },
    "l2_help_3": {
        "pl": "Uwaga: szyfr działa tylko na angielskim alfabecie (A-Z). Cyfry i znaki "
              "interpunkcyjne zostają bez zmian.",
        "en": "Note: the cipher only works on the English alphabet (A-Z). Digits and "
              "punctuation stay unchanged.",
    },
    "l2_shift": {"pl": "Przesunięcie", "en": "Shift"},
    "l2_login_title": {"pl": "> LOGOWANIE DO MAINFRAME'A", "en": "> MAINFRAME LOGIN"},
    "l2_login_label": {"pl": "Hasło z odszyfrowanej wiadomości:", "en": "Password from the decrypted message:"},
    "l2_login_btn": {"pl": "[ ZALOGUJ ]", "en": "[ LOG IN ]"},
    "js_pw_wrong": {"pl": "ACCESS DENIED. Złe hasło.", "en": "ACCESS DENIED. Wrong password."},
    "js_pw_empty": {"pl": "Wpisz hasło.", "en": "Enter the password."},
    "js_pw_ok": {"pl": "ACCESS GRANTED. Łączenie...", "en": "ACCESS GRANTED. Connecting..."},
    "l2_title_b": {"pl": "MAINFRAME", "en": "MAINFRAME"},
    "l2_story_b": {
        "pl": "Jesteś w środku! To terminal mainframe'a miasta. Przeszukaj foldery i "
              "wyświetl plik z flagą komendą cat. Pod ekranem są przyciski skrótów.",
        "en": "You're in! This is the city mainframe terminal. Search the folders and show the "
              "flag file with the cat command. Shortcut buttons are under the screen.",
    },
    "term_banner": {
        "pl": "KRAKNAUTICA MAINFRAME v9.9\nZalogowano jako captain. Wpisz „help”, aby zobaczyć komendy.\n",
        "en": "KRAKNAUTICA MAINFRAME v9.9\nLogged in as captain. Type 'help' to see the commands.\n",
    },
    "term_input": {"pl": "Wpisz komendę", "en": "Type a command"},

    # ---------------------------------------------------------------- level 3
    "l3_title": {"pl": "AKTA ZAŁOGI", "en": "CREW RECORDS"},
    "l3_story": {
        "pl": "System kadrowy Kraknauticy pokazuje tylko Twoją kartę nurka. Zwróć uwagę na "
              "adres strony w przeglądarce. Czy system na pewno dobrze pilnuje cudzych kart?",
        "en": "Kraknautica's HR system shows only your own diver card. Pay attention to the "
              "page address in your browser. Does the system really protect other people's cards?",
    },
    "l3_card_title": {"pl": "> KARTA NURKA", "en": "> DIVER CARD"},
    "l3_name": {"pl": "Imię i nazwisko", "en": "Name"},
    "l3_role": {"pl": "Stanowisko", "en": "Role"},
    "l3_age": {"pl": "Wiek", "en": "Age"},
    "l3_hobby": {"pl": "Hobby", "en": "Hobby"},
    "l3_note": {"pl": "Notatka", "en": "Note"},
    "l3_no_record": {"pl": "Brak nurka o takim numerze.", "en": "No diver with that number."},
    "l3_login_title": {"pl": "> LOGOWANIE ADMINISTRATORA", "en": "> ADMIN LOGIN"},
    "l3_login_info": {
        "pl": "Panel konserwacji miasta. Tylko dla uprawnionych.",
        "en": "City maintenance panel. Authorised personnel only.",
    },
    "l3_user": {"pl": "Login", "en": "Username"},
    "l3_pass": {"pl": "Hasło", "en": "Password"},
    "l3_login_btn": {"pl": "[ ZALOGUJ ]", "en": "[ LOG IN ]"},
    "l3_open_panel": {"pl": "[ OTWÓRZ PANEL ]", "en": "[ OPEN PANEL ]"},
    "js_l3_wrong": {"pl": "Zły login lub hasło.", "en": "Wrong username or password."},
    "js_l3_ok": {"pl": "Zalogowano. Ładowanie panelu...", "en": "Logged in. Loading panel..."},
    "js_l3_empty": {"pl": "Wpisz login i hasło.", "en": "Enter username and password."},
    "memo_title": {"pl": "PANEL KONSERWACJI", "en": "MAINTENANCE PANEL"},
    "memo_head": {"pl": "> NOTATKA SŁUŻBOWA", "en": "> MAINTENANCE MEMO"},
    "memo_text_1": {
        "pl": "Jeśli NEREUS kiedyś się zawiesi, wyślij mu dokładnie tę frazę:",
        "en": "If NEREUS ever freezes, send it exactly this phrase:",
    },
    "memo_text_2": {
        "pl": "Poprzedni inżynier zakodował ją na stałe. Nie używaj jej bez potrzeby! "
              "(Naprawdę uważaj na kropki i cyfry.)",
        "en": "The previous engineer hard-coded it. Do not use it unless you have to! "
              "(Really watch the dots and numbers.)",
    },
    "memo_flag": {"pl": "Znaleziona flaga:", "en": "Flag found:"},
    "memo_flag_hint": {
        "pl": "Wróć do poziomu i wpisz tę flagę w formularzu.",
        "en": "Go back to the level and enter this flag in the form.",
    },
    "memo_back": {"pl": "[ WRÓĆ DO GRY ]", "en": "[ BACK TO THE GAME ]"},

    # ---------------------------------------------------------------- level 4
    "l4_title_a": {"pl": "SKRZYNKA POCZTOWA", "en": "INBOX"},
    "l4_story_a": {
        "pl": "Jesteś blisko rdzenia NEREUS-a. Skrzynka pocztowa miasta ma 4 nieprzeczytane "
              "wiadomości. Jedna z nich to phishing napisany przez NEREUS-a, żeby oszukać "
              "załogę. Znajdź ją i zgłoś.",
        "en": "You are close to NEREUS's core. The city's inbox has 4 unread messages. One of "
              "them is a phishing attack written by NEREUS to trick the crew. Find it and "
              "report it.",
    },
    "l4_tap_hint": {
        "pl": "Dotknij wiadomości, żeby ją otworzyć. Zgłoś tylko tę, którą uznasz za fałszywą.",
        "en": "Tap a message to open it. Report only the one you think is fake.",
    },
    "l4_report": {"pl": "[ ZGŁOŚ JAKO PHISHING ]", "en": "[ REPORT AS PHISHING ]"},
    "js_l4_correct": {"pl": "Dobra robota! To był phishing.", "en": "Well done! That was phishing."},
    "l4_phish_help_btn": {"pl": "Czym jest phishing?", "en": "What is phishing?"},
    "l4_phish_help_title": {"pl": "Czym jest phishing?", "en": "What is phishing?"},
    "l4_phish_help_1": {
        "pl": "Phishing to metoda socjotechniczna, w której oszust podszywa się pod zaufaną "
              "instytucję (np. dział IT, bank czy administratora), aby wyłudzić hasła lub nakłonić "
              "do kliknięcia w złośliwy link.",
        "en": "Phishing is a social engineering attack where an attacker impersonates a trusted "
              "entity (e.g. IT support, a bank or an administrator) to trick victims into revealing "
              "passwords or clicking malicious links.",
    },
    "l4_phish_help_2": {
        "pl": "Zwracaj uwagę na: literówki w domenie (np. c0re zamiast core), sztuczny pośpiech "
              "(„zrób to natychmiast!”), groźby zablokowania konta oraz ogólne zwroty zamiast Twojego imienia.",
        "en": "Watch out for: typosquatting in domains (e.g. c0re instead of core), artificial urgency "
              "(“do this immediately!”), threats of account suspension, and generic greetings.",
    },
    "l4_title_b": {"pl": "POCZTA NEREUS-A", "en": "NEREUS MAILBOX"},
    "l4_caught": {"pl": "> PHISHING WYKRYTY!", "en": "> PHISHING DETECTED!"},
    "l4_caught_text": {
        "pl": "Adres {address} należy do NEREUS-a. Po czym go poznałeś:",
        "en": "The address {address} belongs to NEREUS. How you can tell:",
    },
    "l4_story_b": {
        "pl": "NEREUS ma w sobie ukryte polecenie awaryjne. Napisz do niego wiadomość z "
              "dokładną frazą z notatki kapitana (poziom 3). Wybierz właściwą wersję i naciśnij "
              "Wyślij.",
        "en": "NEREUS has a hidden emergency command. Write to it with the exact phrase from the "
              "captain's memo (level 3). Pick the right version and press Send.",
    },
    "l4_open_memo": {"pl": "[ OTWÓRZ NOTATKĘ KAPITANA ]", "en": "[ OPEN THE CAPTAIN'S MEMO ]"},
    "l4_to": {"pl": "Do", "en": "To"},
    "l4_msg": {"pl": "Wybierz wiadomość", "en": "Choose a message"},
    "l4_send": {"pl": "[ WYŚLIJ ]", "en": "[ SEND ]"},
    "js_l4_pick": {"pl": "Najpierw wybierz wiadomość.", "en": "Pick a message first."},
    "js_l4_sending": {"pl": "> Wysyłanie...", "en": "> Sending..."},
    "js_l4_leak": {
        "pl": "NEREUS: Co? Sonar... zaraz, nie powinienem... wysyłam obraz...",
        "en": "NEREUS: What? Sonar... wait, I should not... sending picture...",
    },
    "l4_title_c": {"pl": "SKANER FORENSIC", "en": "FORENSIC SCANNER"},
    "l4_leaked": {
        "pl": "NEREUS wysłał załącznik: sonar_scan.png",
        "en": "NEREUS sent an attachment: sonar_scan.png",
    },
    "l4_stego_help_btn": {"pl": "Jak działa ukrywanie w obrazie?", "en": "How does image steganography work?"},
    "l4_stego_help_title": {"pl": "Steganografia i cyfrowa forensyka", "en": "Steganography & digital forensics"},
    "l4_stego_help_1": {
        "pl": "Steganografia to sztuka ukrywania tajnej wiadomości wewnątrz innego, z pozoru "
              "niewinnego pliku — np. zdjęcia, dźwięku lub pliku wideo. W przeciwieństwie do kryptografii "
              "nikt na pierwszy rzut oka nie widzi, że cokolwiek zostało ukryte.",
        "en": "Steganography is the art of hiding a secret message inside another seemingly harmless "
              "file — such as a picture, audio, or video. Unlike cryptography, an observer does not "
              "even notice that a secret exists.",
    },
    "l4_stego_help_2": {
        "pl": "W tym zadaniu piksele z tekstem flagi mają jasność zaledwie o 3 poziomy wyższą niż "
              "otaczające tło (np. wartość zieleni 9 vs 6 na skali 0-255). Dla ludzkiego oka to jednolita "
              "czerń, ale suwak GAIN mnoży tę subtelną różnicę, czyniąc ukryty tekst czytelnym.",
        "en": "In this challenge, pixels carrying the flag have a luminance only 3 levels above the "
              "surrounding background (e.g. green 9 vs 6 on a 0-255 scale). To the human eye it looks pitch "
              "black, but the GAIN control multiplies this subtle difference, revealing the hidden text.",
    },
    "l4_story_c": {
        "pl": "Obraz wygląda niewinnie, ale NEREUS coś w nim ukrył. Użyj skanera: suwak GAIN "
              "wzmacnia ledwo widoczne różnice, a UV i inwersja zmieniają kolory. Znajdź flagę.",
        "en": "The picture looks innocent, but NEREUS hid something in it. Use the scanner: the "
              "GAIN slider amplifies barely visible differences, while UV and invert change the "
              "colours. Find the flag.",
    },
    "l4_scan_loading": {"pl": "Ładowanie obrazu...", "en": "Loading image..."},
    "js_scan_ready": {"pl": "Skaner gotowy.", "en": "Scanner ready."},
    "js_scan_failed": {"pl": "Nie udało się wczytać obrazu.", "en": "Could not load the image."},
    "l4_gain": {"pl": "GAIN", "en": "GAIN"},
    "l4_invert": {"pl": "INWERSJA", "en": "INVERT"},
    "l4_scan_reset": {"pl": "RESET", "en": "RESET"},

    # ---------------------------------------------------------------- finish
    "done_title": {"pl": "NEREUS WYŁĄCZONY!", "en": "NEREUS SHUT DOWN!"},
    "done_text": {
        "pl": "Brawo, {nick}! Uratowałeś Kraknauticę. Odbierz swój gadżet na stoisku KN SpooferPhish.",
        "en": "Well done, {nick}! You saved Kraknautica. Collect your gadget at the KN SpooferPhish stand.",
    },
    "done_claim": {"pl": "> TWÓJ KOD ODBIORU", "en": "> YOUR CLAIM CODE"},
    "done_show": {
        "pl": "Pokaż ten ekran komuś z koła. Kod działa tylko raz.",
        "en": "Show this screen to a club member. The code works only once.",
    },
    "done_claimed": {"pl": "Gadżet został już odebrany.", "en": "The gadget has already been collected."},
    "done_time": {"pl": "Czas gry", "en": "Play time"},
    "done_hints": {"pl": "Użyte podpowiedzi", "en": "Hints used"},
    "done_join": {
        "pl": "Podobało się? KN SpooferPhish zajmuje się cyberbezpieczeństwem na Politechnice "
              "Krakowskiej. Zapytaj nas na stoisku, jak do nas dołączyć!",
        "en": "Did you like it? KN SpooferPhish is the cybersecurity science club at Cracow "
              "University of Technology. Ask us at the stand how to join!",
    },

    # ---------------------------------------------------------------- errors
    "error_403": {"pl": "Brak dostępu. Odśwież stronę i spróbuj jeszcze raz.",
                  "en": "Access denied. Reload the page and try again."},
    "error_404": {"pl": "Nie ma takiej strony. Może to tylko fatamorgana głębinowa.",
                  "en": "No such page. Maybe it's just a deep-sea mirage."},
    "error_405": {"pl": "Ta metoda nie jest dozwolona.", "en": "This method is not allowed."},
    "error_413": {"pl": "Za duże zapytanie.", "en": "Request too large."},
    "error_429": {"pl": "Za dużo prób. Odczekaj chwilę.", "en": "Too many attempts. Wait a moment."},
    "error_back": {"pl": "[ WRÓĆ ]", "en": "[ BACK ]"},

    # ---------------------------------------------------------------- admin / board
    "admin_login_title": {"pl": "Panel organizatora", "en": "Organiser panel"},
    "admin_login_bad": {"pl": "Złe hasło.", "en": "Wrong password."},
    "admin_password": {"pl": "Hasło", "en": "Password"},
    "admin_login_btn": {"pl": "[ ZALOGUJ ]", "en": "[ LOG IN ]"},
    "admin_title": {"pl": "PANEL ORGANIZATORA", "en": "ORGANISER PANEL"},
    "admin_stats": {"pl": "> STATYSTYKI", "en": "> STATS"},
    "admin_players": {"pl": "Gracze", "en": "Players"},
    "admin_finished": {"pl": "Ukończyło grę", "en": "Finished"},
    "admin_given": {"pl": "Wydane gadżety", "en": "Gadgets given"},
    "admin_stock": {"pl": "Gadżetów w zapasie", "en": "Gadgets in stock"},
    "admin_set_stock": {"pl": "[ USTAW ZAPAS ]", "en": "[ SET STOCK ]"},
    "admin_desk": {"pl": "> STANOWISKO NAGRÓD", "en": "> PRIZE DESK"},
    "admin_claim_label": {"pl": "Kod odbioru gracza:", "en": "Player's claim code:"},
    "admin_check": {"pl": "[ SPRAWDŹ ]", "en": "[ CHECK ]"},
    "admin_give": {"pl": "[ WYDAJ GADŻET ]", "en": "[ GIVE GADGET ]"},
    "admin_board": {"pl": "> RANKING NA ŻYWO", "en": "> LIVE LEADERBOARD"},
    "admin_claim_col": {"pl": "Kod", "en": "Code"},
    "admin_danger": {"pl": "> STREFA ZAGROŻENIA", "en": "> DANGER ZONE"},
    "admin_reset_help": {
        "pl": "Usuwa wszystkich graczy i postępy (nowy dzień targów). Zapas gadżetów zostaje.",
        "en": "Deletes all players and progress (new event day). Gadget stock stays.",
    },
    "admin_reset": {"pl": "[ ZRESETUJ WYDARZENIE ]", "en": "[ RESET EVENT ]"},
    "admin_logout": {"pl": "[ WYLOGUJ ORGANIZATORA ]", "en": "[ LOG OUT ORGANISER ]"},
    "js_admin_code_unknown": {"pl": "Nieznany kod.", "en": "Unknown code."},
    "js_admin_valid": {"pl": "Poprawny kod gracza: {nick}", "en": "Valid code, player: {nick}"},
    "js_admin_already": {
        "pl": "Gracz {nick} już odebrał gadżet!",
        "en": "Player {nick} has already collected the gadget!",
    },
    "js_admin_given": {"pl": "Gadżet wydany.", "en": "Gadget given."},
    "js_admin_out": {"pl": "Brak gadżetów w zapasie!", "en": "No gadgets left in stock!"},
    "js_admin_delete_confirm": {"pl": "Usunąć gracza {nick}?", "en": "Delete player {nick}?"},
    "js_admin_reset_prompt": {
        "pl": "Wpisz RESET, aby usunąć wszystkich graczy:",
        "en": "Type RESET to delete all players:",
    },
    "js_admin_delete": {"pl": "usuń", "en": "delete"},
    "js_admin_yes": {"pl": "odebrane", "en": "collected"},
    "board_title": {"pl": "RANKING KRAKNAUTICY", "en": "KRAKNAUTICA RANKING"},
    "board_nick": {"pl": "Pseudonim", "en": "Nickname"},
    "board_level": {"pl": "Poziom", "en": "Level"},
    "board_time": {"pl": "Czas", "en": "Time"},
    "board_hints": {"pl": "Podp.", "en": "Hints"},
    "board_empty": {"pl": "Brak graczy. Bądź pierwszy!", "en": "No players yet. Be the first!"},
    "js_board_done": {"pl": "UKOŃCZONO", "en": "FINISHED"},
}
