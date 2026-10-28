from pprint import pprint
from interpreteur_lambda import lexeur

TEST = [
    "/x.y x",
    "xx (xz  t)",
    "(/x.x x) (/x.x x)",
    ")/xt.",
    "/x.x+2",
]

if __name__ == "__main__":
    for terme in TEST:
        print("=" * 60)
        print("Terme :", repr(terme))
        try:
            pprint(lexeur(terme))
        except ValueError:
            print("Erreur de syntaxe")