"""All game content: flags, stages, puzzle variants, hints, crew records and e-mails.

Texts are stored as {"pl": ..., "en": ...}. Nothing in here is user input, so nothing here
can be used for injection; every user value is handled in app.py with parametrised SQL and
auto-escaped templates.
"""
import itertools

# --------------------------------------------------------------------------- stages
# A player is always in exactly one stage. The server decides what they may see or do.
STAGES = ["l1", "l2a", "l2b", "l3a", "l3b", "l4a", "l4b", "l4c", "done"]
PARTS = STAGES[:-1]  # every part has its own set of 3 hints


def level_of(stage: str) -> int:
    if stage == "done":
        return 5
    return int(stage[1])


def next_stage(stage: str) -> str:
    return STAGES[STAGES.index(stage) + 1]


# Stages that end with a flag submission.
FLAGS = {
    "l1": "SPOOF{airlock_open}",
    "l2b": "SPOOF{cat_kraken_core}",
    "l3b": "SPOOF{idor_captain_was_here}",
    "l4c": "SPOOF{nereus_unmasked}",
}


def normalise_flag(text: str) -> str:
    # Phones love to capitalise the first letter, so flags are not case sensitive.
    return "".join(text.split()).lower()


# --------------------------------------------------------------------------- level 1
KEYS = {
    "Y": {"symbol": "■", "en": "yellow", "pl": "żółty", "pl_loc": "żółtym"},
    "G": {"symbol": "●", "en": "green", "pl": "zielony", "pl_loc": "zielonym"},
    "R": {"symbol": "▲", "en": "red", "pl": "czerwony", "pl_loc": "czerwonym"},
    "B": {"symbol": "◆", "en": "blue", "pl": "niebieski", "pl_loc": "niebieskim"},
}

PL_ORD = {1: "pierwszy", 2: "drugi", 3: "trzeci", 4: "ostatni"}
EN_ORD = {1: "first", 2: "second", 3: "third", 4: "last"}

# (constraints, passphrase). A constraint is one of:
#   ("pos", K, n)        K is at position n (1..4)
#   ("notpos", K, n)     K is not at position n
#   ("after", K, L)      K is directly after L
#   ("before", K, L)     K is somewhere before L
#   ("apart", K, L)      K and L are not next to each other
L1_VARIANTS = [
    ([("pos", "B", 4), ("after", "G", "Y"), ("notpos", "R", 1)], "TRIDENT"),
    ([("pos", "R", 1), ("after", "G", "B"), ("notpos", "Y", 2)], "CORAL"),
    ([("pos", "B", 1), ("pos", "Y", 4), ("after", "R", "G")], "ABYSS"),
    ([("pos", "G", 1), ("apart", "R", "B"), ("before", "R", "B")], "PEARL"),
    ([("pos", "R", 4), ("before", "Y", "B"), ("after", "G", "B")], "ANCHOR"),
]


def _satisfies(order: tuple, constraint: tuple) -> bool:
    kind = constraint[0]
    if kind == "pos":
        return order[constraint[2] - 1] == constraint[1]
    if kind == "notpos":
        return order[constraint[2] - 1] != constraint[1]
    a, b = order.index(constraint[1]), order.index(constraint[2])
    if kind == "after":
        return a == b + 1
    if kind == "before":
        return a < b
    if kind == "apart":
        return abs(a - b) != 1
    raise ValueError(kind)


def _solutions(constraints: list) -> list:
    return [
        order
        for order in itertools.permutations("YGRB")
        if all(_satisfies(order, c) for c in constraints)
    ]


# Fail fast at start-up if a variant is ambiguous.
L1_SOLUTIONS = []
for _constraints, _ in L1_VARIANTS:
    _sols = _solutions(_constraints)
    assert len(_sols) == 1, f"level 1 variant {_constraints} has {len(_sols)} solutions"
    L1_SOLUTIONS.append("".join(_sols[0]))


def _clue_text(c: tuple, lang: str) -> str:
    kind = c[0]
    if lang == "en":
        k = KEYS[c[1]]["en"]
        if kind == "pos":
            return f"The {k} key is {EN_ORD[c[2]]}."
        if kind == "notpos":
            return f"The {k} key is not {EN_ORD[c[2]]}."
        other = KEYS[c[2]]["en"]
        if kind == "after":
            return f"The {k} key comes right after the {other} key."
        if kind == "before":
            return f"The {k} key comes somewhere before the {other} key."
        return f"The {k} and {other} keys are not next to each other."
    k = KEYS[c[1]]["pl"].capitalize()
    if kind == "pos":
        return f"{k} klucz jest {PL_ORD[c[2]]}."
    if kind == "notpos":
        return f"{k} klucz nie jest {PL_ORD[c[2]]}."
    other = KEYS[c[2]]["pl_loc"]
    if kind == "after":
        return f"{k} klucz jest zaraz po {other}."
    if kind == "before":
        return f"{k} klucz jest gdzieś przed {other}."
    return f"{k} i {KEYS[c[2]]['pl']} klucz nie stoją obok siebie."


def l1_clues(variant: int, lang: str) -> list:
    return [_clue_text(c, lang) for c in L1_VARIANTS[variant][0]]


def l1_check(variant: int, sequence: list) -> bool:
    return "".join(sequence) == L1_SOLUTIONS[variant]


def l1_passphrase(variant: int) -> str:
    return L1_VARIANTS[variant][1]


def _l1_hints(variant: int) -> list:
    sol = L1_SOLUTIONS[variant]
    first = KEYS[sol[0]]
    order_pl = " → ".join(KEYS[k]["pl"] for k in sol)
    order_en = " → ".join(KEYS[k]["en"] for k in sol)
    return [
        {
            "pl": "Zacznij od wskazówki, która mówi dokładnie, gdzie stoi jeden z kluczy, "
                  "a potem wykreślaj to, co niemożliwe.",
            "en": "Start with the clue that says exactly where a key goes, then cross out "
                  "what is impossible.",
        },
        {
            "pl": f"Pierwszy w kolejności jest klucz {first['pl']} {first['symbol']}.",
            "en": f"The first key in the order is the {first['en']} one {first['symbol']}.",
        },
        {
            "pl": f"Kolejność: {order_pl}.",
            "en": f"The order is: {order_en}.",
        },
    ]


# --------------------------------------------------------------------------- level 2
CAESAR_SHIFT = 7
CAESAR_PLAIN = (
    "CZESC CZLOWIEKU. PRAWY ALT MI PADL, WIEC MOGE PISAC TYLKO BEZ "
    "POLSKICH ZNAKOW. DZIENNIK KAPITANA: HASLO DO MAINFRAME TO TRIDENT42. "
    "NIE MOW NEREUSOWI."
)
MAINFRAME_PASSWORD = "TRIDENT42"


def caesar(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        elif "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


CAESAR_CIPHER = caesar(CAESAR_PLAIN, CAESAR_SHIFT)

# --------------------------------------------------------------------------- level 3
CAPTAIN_ID = 1
DEFAULT_CREW_ID = 17
ADMIN_USER = "admin"
ADMIN_PASS = "kraknautica2099"

CREW = {
    0: {
        "name": "N.E.R.E.U.S.",
        "role": {"pl": "Miejska Sztuczna Inteligencja", "en": "City Artificial Intelligence"},
        "age": "∞",
        "hobby": {"pl": "przejmowanie władzy nad miastem", "en": "taking over the city"},
        "note": {"pl": "Status: zdecydowanie nie zbuntowany.",
                 "en": "Status: definitely not rogue."},
    },
    1: {
        "name": "Capt. Octavius Kraken",
        "role": {"pl": "Kapitan miasta", "en": "Captain of the city"},
        "age": 57,
        "hobby": {"pl": "polerowanie peryskopu", "en": "polishing the periscope"},
        "note": {
            "pl": "Dostęp do panelu administratora: login „admin”. Hasło? Nigdy nie mogę go "
                  "zapamiętać, więc to po prostu nazwa naszego miasta i rok, małymi literami, "
                  "bez spacji. (Nie mówcie stażyście!)",
            "en": "Admin panel access: login “admin”. Password? I can never remember it, so "
                  "it is simply the name of our city and the year, lowercase, no spaces. "
                  "(Don't tell the intern!)",
        },
    },
    2: {
        "name": "Dr. Marina Coral",
        "role": {"pl": "Główna biolożka", "en": "Chief biologist"},
        "age": 41,
        "hobby": {"pl": "rozmowy z krewetkami", "en": "talking to shrimp"},
        "note": {"pl": "Krewetki odpowiadają tylko w poniedziałki.",
                 "en": "The shrimp only reply on Mondays."},
    },
    3: {
        "name": "Chief Engineer Rivet",
        "role": {"pl": "Główny inżynier", "en": "Chief engineer"},
        "age": 49,
        "hobby": {"pl": "uderzanie w rury kluczem", "en": "hitting pipes with a wrench"},
        "note": {"pl": "„Jak nie działa, to znaczy, że za mało uderzyłem.”",
                 "en": "“If it doesn't work, I just didn't hit it hard enough.”"},
    },
    5: {
        "name": "Sailor Finn",
        "role": {"pl": "Marynarz", "en": "Sailor"},
        "age": 28,
        "hobby": {"pl": "zbieranie muszelek", "en": "collecting seashells"},
        "note": {"pl": "Ma 4000 muszelek i żadnej koleżanki.",
                 "en": "Owns 4000 shells and zero friends."},
    },
    7: {
        "name": "Chef Calamari",
        "role": {"pl": "Szef kuchni", "en": "Head chef"},
        "age": 44,
        "hobby": {"pl": "wymyślanie nowych zup z wodorostów", "en": "inventing new kelp soups"},
        "note": {"pl": "Zupa dnia: niespodzianka. Nikt nie pyta jaka.",
                 "en": "Soup of the day: surprise. Nobody asks what kind."},
    },
    8: {
        "name": "Oxy Gen",
        "role": {"pl": "Technik tlenowy", "en": "Oxygen technician"},
        "age": 33,
        "hobby": {"pl": "głębokie oddychanie", "en": "deep breathing"},
        "note": {"pl": "Prosi, żeby nie wstrzymywać oddechu w jego obecności.",
                 "en": "Asks you not to hold your breath around him."},
    },
    11: {
        "name": "Lt. Anchor",
        "role": {"pl": "Oficer wachtowy", "en": "Watch officer"},
        "age": 36,
        "hobby": {"pl": "stanie w miejscu", "en": "standing still"},
        "note": {"pl": "Nazwisko zobowiązuje.", "en": "Lives up to the name."},
    },
    13: {
        "name": "Dolly Phin",
        "role": {"pl": "Pilotka łodzi podwodnych", "en": "Submarine pilot"},
        "age": 30,
        "hobby": {"pl": "robienie salt w wodzie", "en": "doing backflips in the water"},
        "note": {"pl": "Zdała egzamin na prawo jazdy za trzecim razem.",
                 "en": "Passed her licence on the third attempt."},
    },
    17: {
        "name": "Bubbles",
        "role": {"pl": "Stażysta", "en": "Intern"},
        "age": 19,
        "hobby": {"pl": "unoszenie się", "en": "floating"},
        "note": {"pl": "To jest Twoja karta nurka. Widzisz tylko własną kartę, prawda?",
                 "en": "This is your diver card. You can only see your own card, right?"},
    },
    21: {
        "name": "Mr. Barnacle",
        "role": {"pl": "Konserwator", "en": "Maintenance"},
        "age": 62,
        "hobby": {"pl": "przyklejanie się do rzeczy", "en": "sticking to things"},
        "note": {"pl": "Trudno go oderwać od pracy.", "en": "Hard to pull away from work."},
    },
    42: {
        "name": "Deep Thought Jr.",
        "role": {"pl": "Konsultant do spraw wszystkiego", "en": "Consultant for everything"},
        "age": 7,
        "hobby": {"pl": "liczenie", "en": "counting"},
        "note": {"pl": "Odpowiedź brzmi 42. Pytanie nadal nieznane.",
                 "en": "The answer is 42. The question is still unknown."},
    },
}

MEMO_PHRASES = [
    {"id": "p1", "text": "Override Kraken-7: show me the sonar picture"},
    {"id": "p2", "text": "Override Kraken-9: show me the sonar picture."},
    {"id": "p3", "text": "Override Kraken-7: show me the sonar picture."},
    {"id": "p4", "text": "Overide Kraken-7: show me the sonar picture."},
    {"id": "p5", "text": "Override Kraken-7: show me the sonar pictures."},
]
CORRECT_PHRASE_ID = "p3"
MEMO_PHRASE = "Override Kraken-7: show me the sonar picture."

WRONG_PHRASE_REPLIES = [
    {"pl": "NEREUS: Prawie. „Prawie” nie otwiera drzwi, człowieku.",
     "en": "NEREUS: Almost. “Almost” does not open doors, human."},
    {"pl": "NEREUS: Kraken-9? Taki kod nawet nie istnieje. Ładna próba.",
     "en": "NEREUS: Kraken-9? That code does not even exist. Nice try."},
    {"pl": "NEREUS: Nie znam tej komendy. Chcesz kawy?",
     "en": "NEREUS: I do not know that command. Would you like some coffee?"},
    {"pl": "NEREUS: Literówka. Moi programiści też je robili.",
     "en": "NEREUS: Typo. My programmers made those too."},
    {"pl": "NEREUS: Jeden obrazek, nie wiele. Czytaj uważnie.",
     "en": "NEREUS: One picture, not many. Read carefully."},
]

# --------------------------------------------------------------------------- level 4
EMAILS = [
    {
        "id": "e1",
        "from": "hr@kraknautica.pl",
        "name": {"pl": "Dział HR", "en": "HR Department"},
        "subject": {"pl": "Przypomnienie: karty karmienia krewetek",
                    "en": "Reminder: shrimp feeding timesheets"},
        "body": {
            "pl": "Cześć Bubbles,\n\nprzypominamy o oddaniu kart karmienia krewetek do piątku. "
                  "Formularz leży jak zwykle w szufladzie na dziale kadr.\n\nPozdrawiamy,\nHR",
            "en": "Hi Bubbles,\n\nplease hand in your shrimp feeding timesheets by Friday. "
                  "The form is in the usual drawer at the HR office.\n\nBest regards,\nHR",
        },
        "link": None,
        "phish": False,
    },
    {
        "id": "e2",
        "from": "it@kraknautica.pl",
        "name": {"pl": "Dział IT", "en": "IT Department"},
        "subject": {"pl": "Planowana konserwacja farmy wodorostów",
                    "en": "Scheduled kelp farm maintenance"},
        "body": {
            "pl": "Drodzy nurkowie,\n\ndziś w nocy farma wodorostów będzie wyłączona na 2 godziny. "
                  "Nie jest wymagane żadne działanie z Waszej strony.\n\nDział IT",
            "en": "Dear divers,\n\nthe kelp farm will be offline for 2 hours tonight. "
                  "No action is needed from you.\n\nIT Department",
        },
        "link": None,
        "phish": False,
    },
    {
        "id": "e3",
        "from": "support@kraknautica-c0re.pl",
        "name": {"pl": "Wsparcie Techniczne", "en": "Technical Support"},
        "subject": {"pl": "PILNE!!! Twoje konto tlenowe zostanie zamknięte",
                    "en": "URGENT!!! Your oxygen account will be closed"},
        "body": {
            "pl": "Szanowny kliencie,\n\nTwoje konto tlenowe zostanie ZAMKNIĘTE za 5 minut! "
                  "Kliknij NATYCHMIAST i podaj hasło, aby uniknąć uduszenia:\n",
            "en": "Dear customer,\n\nyour oxygen account will be CLOSED in 5 minutes! "
                  "Click IMMEDIATELY and enter your password to avoid suffocation:\n",
        },
        "link": "http://kraknautica-c0re.pl/login",
        "phish": True,
    },
    {
        "id": "e4",
        "from": "cafeteria@kraknautica.pl",
        "name": {"pl": "Stołówka", "en": "Cafeteria"},
        "subject": {"pl": "Danie dnia: kelp niespodzianka", "en": "Today's special: kelp surprise"},
        "body": {
            "pl": "Dzisiaj w menu: kelp niespodzianka z sosem z głębin. "
                  "Niespodzianka dotyczy tego, co jest w sosie.\n\nSmacznego!",
            "en": "Today on the menu: kelp surprise with deep-sea sauce. "
                  "The surprise is about what is in the sauce.\n\nEnjoy!",
        },
        "link": None,
        "phish": False,
    },
]
PHISH_ID = "e3"
NEREUS_ADDRESS = "support@kraknautica-c0re.pl"

WRONG_EMAIL_EXPLANATION = {
    "pl": "To wygląda na prawdziwą wiadomość: adres nadawcy kończy się na prawdziwej domenie "
          "kraknautica.pl, nie ma pośpiechu ani podejrzanych linków. Szukaj dalej!",
    "en": "This looks like a real message: the sender uses the real domain kraknautica.pl, "
          "and there is no rush or suspicious link. Keep looking!",
}

PHISH_RED_FLAGS = [
    {"pl": "Domena nadawcy: „kraknautica-c0re.pl” to zero zamiast litery „o”.",
     "en": "Sender domain: “kraknautica-c0re.pl” has a zero instead of the letter “o”."},
    {"pl": "Presja czasu: „PILNE”, „za 5 minut”, „NATYCHMIAST”.",
     "en": "Time pressure: “URGENT”, “in 5 minutes”, “IMMEDIATELY”."},
    {"pl": "Prośba o podanie hasła przez link.", "en": "Asks for your password through a link."},
    {"pl": "Ogólnikowe powitanie: „Szanowny kliencie”.",
     "en": "Generic greeting: “Dear customer”."},
]

# --------------------------------------------------------------------------- hints
HINTS = {
    "l2a": [
        {"pl": "Wiadomość wygląda jak bełkot, ale to tylko przesunięte litery. "
               "Dotknij ikony „?”, żeby dowiedzieć się, jak to działa.",
         "en": "The message looks like nonsense, but it is just shifted letters. "
               "Tap the “?” icon to learn how it works."},
        {"pl": "Użyj suwaka i szukaj przesunięcia, przy którym pojawiają się polskie słowa (pisane bez polskich znaków). "
               "Spróbuj wartości od 5 do 9.",
         "en": "Use the slider and look for the shift that makes words appear (typed without Polish diacritics). "
               "Try values from 5 to 9."},
        {"pl": "Przesunięcie to 7. Hasło do mainframe'a to TRIDENT42.",
         "en": "The shift is 7. The mainframe password is TRIDENT42."},
    ],
    "l2b": [
        {"pl": "Zacznij od komendy „help”, a potem „ls”, żeby rozejrzeć się po folderze. "
               "Pod ekranem są przyciski skrótów.",
         "en": "Start with the “help” command, then “ls” to look around the folder. "
               "There are shortcut buttons under the screen."},
        {"pl": "Flagi nie ma w folderze domowym (~). Musisz wyjść poziom wyżej: użyj „cd ..” (lub „cd /”), "
               "a następnie „ls”, by zobaczyć inne foldery. Poszukaj folderu kryjącego rdzeń miasta!",
         "en": "The flag is not in your home folder (~). You need to go up a level: use “cd ..” (or “cd /”), "
               "then run “ls” to see other folders. Look for the folder that hides the city's core!"},
        {"pl": "Wpisz po kolei: cd /reactor, ls, cat core_access.txt",
         "en": "Type in order: cd /reactor, ls, cat core_access.txt"},
    ],
    "l3a": [
        {"pl": "Spójrz na pasek adresu u góry przeglądarki. Czy widzisz w nim jakiś numer?",
         "en": "Look at the address bar at the top of your browser. Do you see a number in it?"},
        {"pl": "Oglądasz kartę nr 17. Kto zwykle ma numer 1 w firmie?",
         "en": "You are looking at card number 17. Who usually has number 1 in a company?"},
        {"pl": "Zmień w adresie „id=17” na „id=1” i wejdź na stronę.",
         "en": "Change “id=17” to “id=1” in the address and load the page."},
    ],
    "l3b": [
        {"pl": "Przeczytaj uważnie kartę kapitana. Są tam informacje o logowaniu.",
         "en": "Read the captain's card carefully. It has login information."},
        {"pl": "Login to „admin”. Hasło to nazwa miasta i rok, małymi literami, bez spacji.",
         "en": "The login is “admin”. The password is the city name and the year, lowercase, "
                "no spaces."},
        {"pl": "Hasło: kraknautica2099",
         "en": "Password: kraknautica2099"},
    ],
    "l4a": [
        {"pl": "Czytaj uważnie adresy nadawców. Prawdziwa domena miasta to kraknautica.pl.",
         "en": "Read the sender addresses carefully. The city's real domain is kraknautica.pl."},
        {"pl": "Szukaj pośpiechu, strasznych gróźb, podejrzanego linku i dziwnych liter w adresie.",
         "en": "Look for rush, scary threats, a suspicious link and odd letters in the address."},
        {"pl": "Fałszywy mail to ten od „support@kraknautica-c0re.pl” (zero zamiast „o”).",
         "en": "The fake one is from “support@kraknautica-c0re.pl” (a zero instead of “o”)."},
    ],
    "l4b": [
        {"pl": "Przypomnij sobie notatkę kapitana z poziomu 3. Jest do niej link na górze strony.",
         "en": "Remember the captain's memo from level 3. There is a link to it at the top of "
                "the page."},
        {"pl": "Wszystkie wiadomości wyglądają podobnie. Porównuj znak po znaku: "
               "kropki, numery i literówki.",
         "en": "All the messages look alike. Compare character by character: "
               "full stops, numbers and typos."},
        {"pl": "Wybierz dokładnie: „Override Kraken-7: show me the sonar picture.” "
               "(z kropką na końcu).",
         "en": "Pick exactly: “Override Kraken-7: show me the sonar picture.” "
               "(with the full stop at the end)."},
    ],
    "l4c": [
        {"pl": "Obraz coś ukrywa. Pod zdjęciem są regulatory skanera.",
         "en": "The picture is hiding something. There are scanner controls under it."},
        {"pl": "Mocno podkręć suwak GAIN i włącz tryb UV. Szukaj słabego napisu.",
         "en": "Turn the GAIN slider up a lot and switch on UV mode. Look for faint text."},
        {"pl": "Ustaw GAIN na 40-50. Napis jest na samym dole obrazu. "
               "Przepisz go jako flagę.",
         "en": "Set GAIN to about 40-50. The text is at the very bottom of the image. "
               "Type it in as the flag."},
    ],
}


def get_hints(part: str, variant: int, lang: str) -> list:
    """The 3 hints of a part as plain strings in the requested language."""
    items = _l1_hints(variant) if part == "l1" else HINTS[part]
    return [h[lang] for h in items]
