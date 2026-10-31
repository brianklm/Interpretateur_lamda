from interpreteur_lambda import lexeur, parseur, affichage, parenthese, ErreurSyntaxe, ErreurLexicale
from pprint import pprint

ERREUR="ERREUR"
TERMES = [
    ("T1", "/x.x (/z.y) x",         "(λx.((x (λz.y)) x))"),
    ("T2", "/x.(/y.x) (x z)",       "(λx.((λy.x) (x z)))"),
    ("T3", "(/x.x x) (/y.y z)",     "((λx.(x x)) (λy.(y z)))"),
    ("T4", "/x./y.(/u.x) y",        "(λx.(λy.((λu.x) y)))"),
    ("T5", "x (/x./z.x y z)",       "(x (λx.(λz.((x y) z))))"),
    ("T6", "/z./x.(x./y) z ",        ERREUR),
    ("T7", "(/x./y) ((/x.(/z.y)) z x)) ", ERREUR),
    ("T8", " (/y./x.yx) (/z.y x)", ERREUR),

]


def tester_valides():
    for nom, terme, attendu in TERMES:
        print("=" * 60)
        print()
        print(f'{nom} = "{terme}"')
        print()
        try:
            tokens = lexeur(terme)
            print("Séquence de Tokens :")
            pprint(tokens)
            print()
            arbre = parseur(tokens)
        except (ErreurLexicale, ErreurSyntaxe) as e:
            print(e)
            print()
            if attendu != ERREUR:
                print("-> ERREUR inattendue, attendu :", attendu)
            continue
        obtenu = parenthese(arbre)
        print("Parenthèse :", obtenu)
        print()
        affichage(arbre)
        print()
        if attendu == ERREUR:
            print("-> aucune erreur détectée, une erreur était attendue")
        elif obtenu != attendu:
            print("-> ERREUR, attendu :", attendu)
    print("=" * 60)
    

if __name__ == "__main__":
    tester_valides()