import sys
from pprint import pprint

LAMBDA = 'LAMBDA'
POINT = 'POINT'
ESPACE = 'ESPACE'
PARENO = 'PARENO'
PARENF = 'PARENF'
VAR = 'VAR'


def est_alphanum(c):
    """Lettre (non accentuée) ou chiffre."""
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9')


def lexeur(s):
    """Retourne la liste des paires (texte, type) des tokens de s."""
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '/':
            tokens.append((c, LAMBDA))
            i += 1
        elif c == '.':
            tokens.append((c, POINT))
            i += 1
        elif c == ' ':
            tokens.append((c, ESPACE))
            i += 1
        elif c == '(':
            tokens.append((c, PARENO))
            i += 1
        elif c == ')':
            tokens.append((c, PARENF))
            i += 1
        elif est_alphanum(c):
            j = i
            while j < n and est_alphanum(s[j]):
                j += 1
            tokens.append((s[i:j], VAR))
            i = j
        else:
            raise ValueError(f"Caractère invalide {c!r} à la position {i}")
    return tokens


def enlever_guillemets(s):
    """Si la saisie est entourée de guillemets, on les retire."""
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


if __name__ == "__main__":
    # Cas 1 : terme donné en argument -> python lexeur.py "/x.y x"
    if len(sys.argv) > 1:
        pprint(lexeur(sys.argv[1]))
    # Cas 2 : mode interactif -> on tape les termes un par un
    else:
        print("Entrez un lambda-terme ou ligne vide pour quitter.")
        while True:
            saisie = input("> ")
            if saisie == "":
                break
            try:
                pprint(lexeur(enlever_guillemets(saisie)))
            except ValueError as e:
                print("Erreur :", e)