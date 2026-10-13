"""The level 2 mainframe terminal.

This is a tiny *simulation*: a Python dictionary pretends to be a filesystem and a handful of
hard-coded commands read from it. No shell, no real files, no eval, no subprocess. Whatever a
player types is only ever compared against the command names below, and the answer is shown on
the page with textContent, so it can never run as code.
"""
from dataclasses import dataclass

HOME = "/home/captain"
FLAG_FILE = "/reactor/core_access.txt"


@dataclass(frozen=True)
class File:
    pl: str
    en: str


FS = {
    "home": {
        "captain": {
            "todo.txt": File(
                "1. Kupić więcej folii bąbelkowej.\n2. Przeprosić krewetki.\n"
                "3. Nie ufać NEREUS-owi.",
                "1. Buy more bubble wrap.\n2. Apologise to the shrimp.\n3. Do not trust NEREUS.",
            ),
            "snacks_inventory.txt": File(
                "Chipsy z wodorostów: 3\nEnergetyki z wodorostów: 47\n"
                "Tajemnicza ryba: NIE PYTAJ.",
                "Kelp chips: 3\nSeaweed energy drinks: 47\nMysterious fish: DO NOT ASK.",
            ),
            "passwords_DO_NOT_OPEN.txt": File(
                "O. Otworzyłeś. Jest tu napisane: SPOOF{this_is_a_decoy_nice_try}\n"
                "(To nie jest prawdziwa flaga. Ale ładna próba.)",
                "Oh. You opened it. It says: SPOOF{this_is_a_decoy_nice_try}\n"
                "(This is not the real flag. But nice try.)",
            ),
            ".bubble_notes": File(
                "Ukryte pliki zaczynają się od kropki. Brawo, że sprawdzasz ls -a!\n"
                "Niestety nic tu nie ma poza bąbelkami. o O o O",
                "Hidden files start with a dot. Well done for checking ls -a!\n"
                "Sadly there is nothing here except bubbles. o O o O",
            ),
            "fish_memes": {
                "blub.txt": File(
                    "   ><(((º>\n\"Blub.\"\n  — każda ryba, zawsze",
                    "   ><(((º>\n\"Blub.\"\n  - every fish, always",
                ),
                "sharkbait.txt": File(
                    "Rekin wchodzi do baru.\nBarman: „Czemu taka długa ryba?”\n"
                    "(To nie jest śmieszne, ale ryby się śmieją.)",
                    "A shark walks into a bar.\nBartender: \"Why the long fin?\"\n"
                    "(It is not funny, but fish laugh anyway.)",
                ),
            },
        }
    },
    "reactor": {
        "maintenance_log.txt": File(
            "Temperatura reaktora: w normie.\nNastrój reaktora: też w normie. Chyba.",
            "Reactor temperature: fine.\nReactor mood: also fine. Probably.",
        ),
        "coffee_machine.txt": File(
            "Ekspres do kawy w reaktorze działa lepiej niż sam reaktor.",
            "The reactor's coffee machine works better than the reactor itself.",
        ),
        "core_access.txt": File(
            "=== DOSTĘP DO RDZENIA MIASTA ===\nAutoryzacja: kapitan\n"
            "Flaga: SPOOF{cat_kraken_core}\nGratulacje, hakerze!",
            "=== CITY CORE ACCESS ===\nAuthorisation: captain\n"
            "Flag: SPOOF{cat_kraken_core}\nCongratulations, hacker!",
        ),
    },
    "tmp": {
        "definitely_not_nereus.txt": File(
            "To nie jest NEREUS. Naprawdę. Idź dalej.",
            "This is not NEREUS. Really. Move along.",
        ),
    },
}

TEXT = {
    "help": {
        "pl": "Dostępne komendy:\n"
              "  help          pokazuje tę listę\n"
              "  ls            pokazuje pliki w folderze (ls -a pokazuje też ukryte)\n"
              "  cd FOLDER     wchodzi do folderu (cd .. wraca, cd / idzie na górę)\n"
              "  pwd           pokazuje, gdzie jesteś\n"
              "  cat PLIK      wyświetla zawartość pliku\n"
              "  whoami        pokazuje, kim jesteś\n"
              "  clear         czyści ekran",
        "en": "Available commands:\n"
              "  help          shows this list\n"
              "  ls            lists files in a folder (ls -a also shows hidden ones)\n"
              "  cd FOLDER     enters a folder (cd .. goes back, cd / goes to the top)\n"
              "  pwd           shows where you are\n"
              "  cat FILE      shows the contents of a file\n"
              "  whoami        shows who you are\n"
              "  clear         clears the screen",
    },
    "notfound": {"pl": "komenda nie znaleziona: {0}. Wpisz „help”.",
                 "en": "command not found: {0}. Type 'help'."},
    "nofile": {"pl": "{0}: nie ma takiego pliku ani folderu",
               "en": "{0}: no such file or directory"},
    "notdir": {"pl": "{0}: to nie jest folder", "en": "{0}: not a directory"},
    "isdir": {"pl": "{0}: to jest folder", "en": "{0}: is a directory"},
    "catmissing": {"pl": "cat: podaj nazwę pliku, np. cat todo.txt",
                   "en": "cat: missing file name, e.g. cat todo.txt"},
    "sudo": {"pl": "Ładna próba. To Kraknautica, a nie powierzchnia.",
             "en": "Nice try. This is Kraknautica, not the surface."},
    "rm": {"pl": "Nie możesz usunąć oceanu.", "en": "You can't delete the ocean."},
    "exit": {"pl": "Nie ma ucieczki. Jesteś 300 metrów pod wodą.",
             "en": "There is no escape. You are 300 metres underwater."},
    "date": {"pl": "Rok 2099, dzień 214 Wielkiego Bąbla.",
             "en": "Year 2099, day 214 of the Great Bubble."},
    "nereus": {"pl": "NEREUS: Słyszę, jak o mnie piszesz. Przestań.",
               "en": "NEREUS: I can hear you typing about me. Stop."},
    "whoami": {"pl": "captain (a przynajmniej tak mówi tabliczka)",
               "en": "captain (or so the nameplate says)"},
}


def _t(key: str, lang: str, *args) -> str:
    return TEXT[key][lang].format(*args)


def _split(path: str) -> list:
    return [p for p in path.split("/") if p]


def _normalise(cwd: str, arg: str) -> list:
    """Turns a typed path into a clean list of folder names (handles ~, .., ., absolute)."""
    if arg == "~" or arg.startswith("~/"):
        parts = _split(HOME) + _split(arg[1:])
    elif arg.startswith("/"):
        parts = _split(arg)
    else:
        parts = _split(cwd) + _split(arg)
    clean: list = []
    for p in parts:
        if p == ".":
            continue
        if p == "..":
            if clean:
                clean.pop()
            continue
        clean.append(p)
    return clean


def _node(parts: list):
    node = FS
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return None
    return node


def _display(cwd: str) -> str:
    if cwd == HOME:
        return "~"
    if cwd.startswith(HOME + "/"):
        return "~" + cwd[len(HOME):]
    return cwd


def valid_cwd(cwd: str) -> str:
    """The client sends its current folder; fall back to home if it is not a real folder."""
    if not isinstance(cwd, str) or len(cwd) > 200:
        return HOME
    parts = _normalise("/", cwd)
    if not parts:
        return "/"
    return "/" + "/".join(parts) if isinstance(_node(parts), dict) else HOME


def run(command: str, cwd: str, lang: str) -> dict:
    """Runs one command. Returns {"output": str, "cwd": str, "prompt": str, "clear": bool}."""
    lang = "en" if lang == "en" else "pl"
    cwd = valid_cwd(cwd)
    tokens = command.split()
    out = ""
    clear = False

    if tokens:
        cmd, args = tokens[0].lower(), tokens[1:]
        if cmd == "help":
            out = _t("help", lang)
        elif cmd == "clear":
            clear = True
        elif cmd == "pwd":
            out = cwd
        elif cmd == "whoami":
            out = _t("whoami", lang)
        elif cmd == "ls":
            show_all = any(a.startswith("-") and "a" in a for a in args)
            targets = [a for a in args if not a.startswith("-")]
            target = targets[0] if targets else "."
            parts = _normalise(cwd, target)
            node = _node(parts)
            if node is None:
                out = _t("nofile", lang, f"ls: {target}")
            elif isinstance(node, File):
                out = target
            else:
                names = sorted(
                    (n + "/" if isinstance(v, dict) else n)
                    for n, v in node.items()
                    if show_all or not n.startswith(".")
                )
                out = "  ".join(names)
        elif cmd == "cd":
            target = args[0] if args else "~"
            parts = _normalise(cwd, target)
            node = _node(parts)
            if node is None:
                out = _t("nofile", lang, f"cd: {target}")
            elif isinstance(node, File):
                out = _t("notdir", lang, f"cd: {target}")
            else:
                cwd = "/" + "/".join(parts)
        elif cmd == "cat":
            if not args:
                out = _t("catmissing", lang)
            else:
                chunks = []
                for target in args:
                    node = _node(_normalise(cwd, target))
                    if node is None:
                        chunks.append(_t("nofile", lang, f"cat: {target}"))
                    elif isinstance(node, dict):
                        chunks.append(_t("isdir", lang, f"cat: {target}"))
                    else:
                        chunks.append(getattr(node, lang))
                out = "\n".join(chunks)
        elif cmd == "echo":
            out = " ".join(args)
        elif cmd == "date":
            out = _t("date", lang)
        elif cmd == "sudo":
            out = _t("sudo", lang)
        elif cmd == "rm":
            out = _t("rm", lang)
        elif cmd in ("exit", "logout"):
            out = _t("exit", lang)
        elif cmd == "nereus":
            out = _t("nereus", lang)
        else:
            out = _t("notfound", lang, cmd[:40])

    return {"output": out, "cwd": cwd, "prompt": _display(cwd), "clear": clear}
