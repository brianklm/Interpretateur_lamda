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



# Bêta-réductions

MAX_ITERATIONS = 1000


def est_redex(t):
    """Vrai si t est un redex (λx.M) N."""
    return t[0] == 'application' and t[1][0] == 'abstraction'


def contient_redex(t):
    """Vrai si t contient un redex (sinon t est en forme normale)."""
    if est_redex(t):
        return True
    if t[0] == 'application':
        return contient_redex(t[1]) or contient_redex(t[2])
    if t[0] == 'abstraction':
        return contient_redex(t[2])
    return False


def _reduire(t, subst):
    """Réduit le redex le plus extérieur (racine, gauche, droite) ; retourne (terme, réduit ?)."""
    if est_redex(t):
        x, m, n = t[1][1], t[1][2], t[2]
        return subst(m, x, n), True
    if t[0] == 'application':
        gauche, reduit = _reduire(t[1], subst)
        if reduit:
            return application(gauche, t[2]), True
        droite, reduit = _reduire(t[2], subst)
        if reduit:
            return application(t[1], droite), True
    elif t[0] == 'abstraction':
        corps, reduit = _reduire(t[2], subst)
        if reduit:
            return abstraction(t[1], corps), True
    return t, False


# VERSION NAÏVE - sans alpha-renommage

def substitution(m, x, n):
    """VERSION NAÏVE : M[x := N] sans renommage (peut capturer des variables)."""
    genre = m[0]
    if genre == 'variable':
        return n if m[1] == x else m
    if genre == 'application':
        return application(substitution(m[1], x, n), substitution(m[2], x, n))
    if m[1] == x:
        # x re-liée par ce lambda : rien à remplacer
        return m
    return abstraction(m[1], substitution(m[2], x, n))


def betared(t):
    """VERSION NAÏVE : une étape de bêta-réduction sur le redex le plus extérieur."""
    return _reduire(t, substitution)[0]


# VERSION CORRECTE - avec alpha-renommage

def variables_libres(t):
    """Ensemble des variables libres de t."""
    genre = t[0]
    if genre == 'variable':
        return {t[1]}
    if genre == 'abstraction':
        return variables_libres(t[2]) - {t[1]}
    return variables_libres(t[1]) | variables_libres(t[2])


def variables_liees(t):
    """Ensemble des variables liées par un lambda dans t."""
    genre = t[0]
    if genre == 'variable':
        return set()
    if genre == 'abstraction':
        return {t[1]} | variables_liees(t[2])
    return variables_liees(t[1]) | variables_liees(t[2])


def nom_frais(nom, interdits):
    """Nouveau nom y1, y2, ... absent de interdits."""
    base = nom.rstrip('0123456789') or nom
    i = 1
    while f"{base}{i}" in interdits:
        i += 1
    return f"{base}{i}"


def substitution2(m, x, n):
    """VERSION CORRECTE : M[x := N] avec alpha-renommage pour éviter la capture."""
    genre = m[0]
    if genre == 'variable':
        return n if m[1] == x else m
    if genre == 'application':
        return application(substitution2(m[1], x, n),
                           substitution2(m[2], x, n))
    y, corps = m[1], m[2]
    if y == x or x not in variables_libres(corps):
        # rien à remplacer sous ce lambda
        return m
    if y in variables_libres(n):
        # y capturé sinon : on le renomme
        interdits = (variables_libres(corps) | variables_liees(corps)
                     | variables_libres(n) | {x})
        z = nom_frais(y, interdits)
        corps = substitution2(corps, y, variable(z))
        y = z
    return abstraction(y, substitution2(corps, x, n))


def betared2(t):
    """VERSION CORRECTE : une étape de bêta-réduction avec alpha-renommage."""
    return _reduire(t, substitution2)[0]


def normaliser(t, reduction=betared2, max_iterations=MAX_ITERATIONS):
    """Réduit jusqu'à la forme normale ou max_iterations étapes (ex. Omega)."""
    for _ in range(max_iterations):
        if not contient_redex(t):
            break
        t = reduction(t)
    return t


def equivalent(t1, t2):
    """Vrai si t1 et t2 sont égaux au renommage des variables liées près."""
    return _equivalent(t1, t2, {}, {}, 0)


def _equivalent(a, b, liees_a, liees_b, profondeur):
    if a[0] != b[0]:
        return False
    if a[0] == 'variable':
        pa, pb = liees_a.get(a[1]), liees_b.get(b[1])
        if pa is None and pb is None:
            return a[1] == b[1]
        return pa == pb
    if a[0] == 'abstraction':
        return _equivalent(a[2], b[2],
                           {**liees_a, a[1]: profondeur},
                           {**liees_b, b[1]: profondeur},
                           profondeur + 1)
    return (_equivalent(a[1], b[1], liees_a, liees_b, profondeur)
            and _equivalent(a[2], b[2], liees_a, liees_b, profondeur))


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