from interpreteur_lambda import lexeur, parseur, affichage, parenthese

TERMES = [
    ("T1", "/x.x (/z.y) x",         "(λx.((x (λz.y)) x))"),
    ("T2", "/x.(/y.x) (x z)",       "(λx.((λy.x) (x z)))"),
    ("T3", "(/x.x x) (/y.y z)",     "((λx.(x x)) (λy.(y z)))"),
    ("T4", "/x./y.(/u.x) y",        "(λx.(λy.((λu.x) y)))"),
    ("T5", "x (/x./z.x y z)",       "(x (λx.(λz.((x y) z))))"),
]


def tester_valides():
    ok = 0
    for nom, terme, attendu in TERMES:
        print("=" * 60)
        print()
        print(f"{nom} = {terme}")
        print()
        arbre = parseur(lexeur(terme))
        obtenu = parenthese(arbre)
        print("Parenthèse :", obtenu)
        print()
        affichage(arbre)
        if obtenu == attendu:
            ok += 1
        else:
            print("-> ERREUR, attendu :", attendu)
    print("=" * 60)
    print(f"{ok}/{len(TERMES)} termes valides corrects")


if __name__ == "__main__":
    tester_valides()