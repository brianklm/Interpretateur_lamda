from interpreteur_lambda import (lexeur, parseur, parenthese, betared,
                                 betared2, normaliser, equivalent,
                                 contient_redex, variables_libres)


def terme(s):
    return parseur(lexeur(s))


def normaliser_naif(t):
    return normaliser(t, reduction=betared)


# (nom, fonction, entrée, résultat attendu, mode de comparaison)
#   'identique'      : même arbre exactement
#   'equivalent'     : même terme au renommage des variables liées près
#   'non_equivalent' : le résultat NE doit PAS être équivalent à l'attendu
TESTS_REDUCTION = [
    # --- Étape 3 : version naïve, cas simples ---
    ("R1",  betared, "(/x.x) y",             "y",            'identique'),
    ("R2",  betared, "(/x.x x) y",           "y y",          'identique'),
    ("R3",  betared, "x y",                  "x y",          'identique'),
    ("R4",  betared, "(/x.y) ((/z.z) w)",    "y",            'identique'),
    ("R5",  betared, "/z.(/x.x) z",          "/z.z",         'identique'),
    ("R6",  betared, "(/x./y.x) a b",        "(/y.a) b",     'identique'),
    ("R7",  normaliser_naif, "(/x./y.x) a b", "a",           'identique'),
    # --- Étape 3 : capture (résultat FAUX attendu en version naïve) ---
    ("R8",  betared, "(/x./y.x) y",          "/y.y",         'identique'),
    ("R9",  betared, "(/x./y.x y) (y z)",    "/y.(y z) y",   'identique'),
    # --- Étape 4 : version correcte, la capture est évitée ---
    ("R10", betared2, "(/x./y.x) y",         "/z.y",         'equivalent'),
    ("R11", betared2, "(/x./y.x) y",         "/y.y",         'non_equivalent'),
    ("R12", betared2, "(/x./y.x y) (y z)",   "/w.(y z) w",   'equivalent'),
    ("R13", betared2, "(/x./y.x) z",         "/y.z",         'identique'),
    ("R14", normaliser, "(/x.x) ((/y.y) z)", "z",            'identique'),
    ("R15", normaliser,
     "(/x./y./z.x z (y z)) (/x./y.x) (/x./y.x) a",           "a", 'identique'),
]

# (nom, terme 1, terme 2, attendu)
TESTS_EQUIVALENT = [
    ("E1", "/x.x",       "/y.y",       True),
    ("E2", "/x./y.x",    "/a./b.a",    True),
    ("E3", "/x./y.x",    "/x./y.y",    False),
    ("E4", "/x.y",       "/x.z",       False),
    ("E5", "/x.y",       "/y.y",       False),
    ("E6", "x y",        "x y",        True),
]


def comparer(obtenu, attendu, mode):
    if mode == 'identique':
        return obtenu == attendu
    if mode == 'equivalent':
        return equivalent(obtenu, attendu)
    return not equivalent(obtenu, attendu)


def tester_reductions():
    ok = 0
    for nom, fonction, entree, attendu, mode in TESTS_REDUCTION:
        obtenu = fonction(terme(entree))
        reussi = comparer(obtenu, terme(attendu), mode)
        ok += reussi
        print("=" * 60)
        print(f"{nom}  {fonction.__name__}({entree})")
        print(f"  attendu ({mode}) : {parenthese(terme(attendu))}")
        print(f"  obtenu           : {parenthese(obtenu)}")
        print(f"  -> {'RÉUSSI' if reussi else 'ÉCHEC'}")
    return ok, len(TESTS_REDUCTION)


def tester_omega():
    """Omega n'a pas de forme normale : normaliser doit s'arrêter quand même."""
    omega = terme("(/x.x x) (/x.x x)")
    obtenu = normaliser(omega, max_iterations=50)
    reussi = contient_redex(obtenu) and equivalent(obtenu, omega)
    print("=" * 60)
    print("R16  normaliser(Omega) avec 50 itérations au maximum")
    print(f"  obtenu : {parenthese(obtenu)} (s'arrête, toujours un redex)")
    print(f"  -> {'RÉUSSI' if reussi else 'ÉCHEC'}")
    return int(reussi), 1


def tester_variables_libres():
    cas = [("/x.x y", {'y'}), ("(/x.x) x", {'x'}), ("/x./y.x y", set())]
    ok = 0
    print("=" * 60)
    for entree, attendu in cas:
        obtenu = variables_libres(terme(entree))
        reussi = obtenu == attendu
        ok += reussi
        print(f"libres({entree}) = {sorted(obtenu)}"
              f"  -> {'RÉUSSI' if reussi else 'ÉCHEC'}")
    return ok, len(cas)


def tester_equivalent():
    ok = 0
    print("=" * 60)
    for nom, s1, s2, attendu in TESTS_EQUIVALENT:
        obtenu = equivalent(terme(s1), terme(s2))
        reussi = obtenu == attendu
        ok += reussi
        print(f"{nom}  equivalent({s1}, {s2}) = {obtenu}"
              f"  -> {'RÉUSSI' if reussi else 'ÉCHEC'}")
    return ok, len(TESTS_EQUIVALENT)


if __name__ == "__main__":
    total_ok = total = 0
    for test in (tester_reductions, tester_omega,
                 tester_variables_libres, tester_equivalent):
        ok, n = test()
        total_ok += ok
        total += n
    print("=" * 60)
    print(f"{total_ok}/{total} tests réussis")
