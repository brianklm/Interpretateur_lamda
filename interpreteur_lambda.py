import sys
from pprint import pprint

### PARTIE 1 : LEXEUR ET PARSEUR

LAMBDA = 'LAMBDA'
POINT = 'POINT'
ESPACE = 'ESPACE'
PARO = 'PARO'
PARF = 'PARF'
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
            tokens.append((c, PARO))
            i += 1
        elif c == ')':
            tokens.append((c, PARF))
            i += 1
        elif est_alphanum(c):
            j = i
            while j < n and est_alphanum(s[j]):
                j += 1
            tokens.append((s[i:j], VAR))
            i = j
        else:
            affiche = c if c.isprintable() else repr(c)
            raise ErreurLexicale(f"Erreur lexicale sur le ({affiche})")
    return tokens


def enlever_guillemets(s):
    """Si la saisie est entourée de guillemets, on les retire."""
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s

class ErreurSyntaxe(Exception):
    pass

class ErreurLexicale(Exception):
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


def _erreur(a, i, attendu):
    """Construit l'erreur de syntaxe pour le token i."""

    if i >= len(a):
        lieu = "à la fin du terme"
    else:
        texte, genre = a[i]
        if genre == ESPACE:
            lieu = "sur l'espace"
        elif genre == VAR:
            lieu = f"sur la variable {texte}"
        else:
            lieu = f"sur le {texte}"
    return ErreurSyntaxe(f"Erreur de syntaxe {lieu}")

def _attendre(a, i, type_attendu, message):
    """Vérifie que le token i est du type attendu, et retourne i+1."""
    if _type_a(a, i) != type_attendu:
        raise _erreur(a, i, message)
    return i + 1


# Grammaire utilisée :
#   terme       ::= abstraction | application
#   abstraction ::= LAMBDA VAR POINT terme
#   application ::= atome (ESPACE atome)* [ESPACE abstraction]
#   atome       ::= VAR | PARO terme PARF
def analyser_terme(a, i):
    if _type_a(a, i) == LAMBDA:
        return analyser_abstraction(a, i)
    return analyser_application(a, i)


def analyser_abstraction(a, i):
    i = _attendre(a, i, LAMBDA, "'/' attendu")
    i_var = i
    i = _attendre(a, i, VAR, "variable attendue après '/'")
    nom = a[i_var][0]
    i = _attendre(a, i, POINT, "'.' attendu")
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
    if t == PARO:
        interieur, i = analyser_terme(a, i + 1)
        i = _attendre(a, i, PARF, "')' attendu")
        return interieur, i
    raise _erreur(a, i, "variable ou '(' attendu")


def parseur(a):
    """Prend la liste de tokens du lexeur, retourne l'arbre de syntaxe.
    Lève ErreurSyntaxe (avec la position) si le terme est mal formé."""
    if not a:
        raise ErreurSyntaxe("Erreur de syntaxe : terme vide")
    arbre, i = analyser_terme(a, 0)
    if i != len(a):
        if a[i][1] == PARF:
            raise _erreur(a, i, "parenthèse ouvrante manquante")
        raise _erreur(a, i, "espace attendu")
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
    except (ErreurLexicale, ErreurSyntaxe) as e:
        print(e)
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

### FIN DE LA PARITE 1
