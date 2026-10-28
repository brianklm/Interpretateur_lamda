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

class ErreurSyntaxe(Exception):
    pass


# Arbre de syntaxe abstraite :
#   ('variable', nom)
#   ('abstraction', nom, corps)
#   ('application', gauche, droite)
def variable(nom):
    return ('variable', nom)


def abstraction(nom, corps):
    return ('abstraction', nom, corps)


def application(gauche, droite):
    return ('application', gauche, droite)


def _type_a(a, i):
    """Type du token à la position i (None si on est à la fin)."""
    return a[i][1] if i < len(a) else None


def _attendre(a, i, type_attendu):
    """Vérifie que le token i est du type attendu, et retourne i+1."""
    t = _type_a(a, i)
    if t != type_attendu:
        trouve = "fin du terme" if t is None else f"{a[i][0]!r} ({t})"
        raise ErreurSyntaxe(
            f"{type_attendu} attendu au token {i}, trouvé : {trouve}")
    return i + 1


# Grammaire utilisée :
#   terme       ::= abstraction | application
#   abstraction ::= LAMBDA VAR POINT terme
#   application ::= atome (ESPACE atome)* [ESPACE abstraction]
#   atome       ::= VAR | PARENO terme PARENF
def analyser_terme(a, i):
    if _type_a(a, i) == LAMBDA:
        return analyser_abstraction(a, i)
    return analyser_application(a, i)


def analyser_abstraction(a, i):
    i = _attendre(a, i, LAMBDA)
    if _type_a(a, i) != VAR:
        raise ErreurSyntaxe(f"VAR attendu après '/' au token {i}")
    nom = a[i][0]
    i = _attendre(a, i + 1, POINT)
    # RÈGLE 2 : le corps est un terme complet, il consomme tous les
    # tokens possibles (jusqu'à un ')' ou la fin) : "le plus loin possible"
    corps, i = analyser_terme(a, i)
    return abstraction(nom, corps), i


def analyser_application(a, i):
    gauche, i = analyser_atome(a, i)
    # RÈGLE 1 : on accumule vers la gauche : x y z -> ((x y) z)
    while _type_a(a, i) == ESPACE:
        i += 1
        if _type_a(a, i) == LAMBDA:
            droite, i = analyser_abstraction(a, i)
        else:
            droite, i = analyser_atome(a, i)
        gauche = application(gauche, droite)
    return gauche, i


def analyser_atome(a, i):
    t = _type_a(a, i)
    if t == VAR:
        return variable(a[i][0]), i + 1
    if t == PARENO:
        interieur, i = analyser_terme(a, i + 1)
        i = _attendre(a, i, PARENF)
        return interieur, i
    trouve = "fin du terme" if t is None else f"{a[i][0]!r} ({t})"
    raise ErreurSyntaxe(
        f"variable ou '(' attendu au token {i}, trouvé : {trouve}")


def parseur(a):
    """Prend la liste de tokens du lexeur, retourne l'arbre de syntaxe.
    Lève ErreurSyntaxe si le terme est mal formé."""
    if not a:
        raise ErreurSyntaxe("terme vide")
    arbre, i = analyser_terme(a, 0)
    if i != len(a):
        raise ErreurSyntaxe(
            f"token inattendu {a[i][0]!r} ({a[i][1]}) au token {i}")
    return arbre


def _lignes(arbre, prefixe_noeud, prefixe_enfants):
    """Génère les lignes de l'affichage de l'arbre."""
    genre = arbre[0]
    if genre == 'variable':
        yield f"{prefixe_noeud}variable {arbre[1]}"
    elif genre == 'abstraction':
        yield f"{prefixe_noeud}abstraction"
        yield f"{prefixe_enfants}├── λ{arbre[1]}"
        yield from _lignes(arbre[2], prefixe_enfants + "└── ",
                           prefixe_enfants + "    ")
    else:
        yield f"{prefixe_noeud}application"
        yield from _lignes(arbre[1], prefixe_enfants + "├── ",
                           prefixe_enfants + "│   ")
        yield from _lignes(arbre[2], prefixe_enfants + "└── ",
                           prefixe_enfants + "    ")


def affichage(arbre):
    """Affiche l'arbre de syntaxe, un noeud par ligne."""
    for ligne in _lignes(arbre, "", ""):
        print(ligne)


def parenthese(arbre):
    """Terme complètement parenthèse (pour vérifier la précédence)."""
    genre = arbre[0]
    if genre == 'variable':
        return arbre[1]
    if genre == 'abstraction':
        return f"(λ{arbre[1]}.{parenthese(arbre[2])})"
    return f"({parenthese(arbre[1])} {parenthese(arbre[2])})"


def traiter(s):
    try:
        tokens = lexeur(s)
        print("Séquence de Tokens :")
        pprint(tokens)
        a = parseur(tokens)
        print("Terme :", parenthese(a))
        affichage(a)
    except (ValueError, ErreurSyntaxe):
        print("Erreur de syntaxe")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        traiter(sys.argv[1])
    else:
        print("Entrez un lambda-terme ou ligne vide pour quitter.")
        while True:
            saisie = input("> ")
            if saisie == "":
                break
            traiter(enlever_guillemets(saisie))