"""Tests des entiers de Church et de l'addition."""

from interpreteur_lambda import entier_church, valeur_church, addition


def verifier(nom, fonction, attendu):
    try:
        obtenu = fonction()
        ok = obtenu == attendu
        print(f"{'RÉUSSI' if ok else 'ÉCHEC'} — {nom} : obtenu={obtenu!r}, attendu={attendu!r}")
        return ok
    except Exception as exc:
        print(f"ÉCHEC — {nom} : exception {type(exc).__name__}: {exc}")
        return False


def erreur_attendue(nom, fonction, type_erreur):
    try:
        fonction()
    except type_erreur:
        print(f"RÉUSSI — {nom} : erreur attendue détectée")
        return True
    except Exception as exc:
        print(f"ÉCHEC — {nom} : mauvaise exception {type(exc).__name__}: {exc}")
        return False

    print(f"ÉCHEC — {nom} : aucune erreur détectée")
    return False


def main():
    resultats = []

    for n in (0, 1, 2, 3, 5):
        resultats.append(
            verifier(
                f"encodage/décodage {n}",
                lambda n=n: valeur_church(entier_church(n)),
                n
            )
        )

    for m, n, attendu in (
        (0, 0, 0),
        (0, 3, 3),
        (3, 0, 3),
        (1, 2, 3),
        (2, 3, 5),
        (3, 2, 5)
    ):
        resultats.append(
            verifier(
                f"addition({m}, {n})",
                lambda m=m, n=n: addition(m, n),
                attendu
            )
        )

    resultats.append(
        erreur_attendue(
            "entier négatif",
            lambda: entier_church(-1),
            ValueError
        )
    )

    resultats.append(
        erreur_attendue(
            "entier non entier",
            lambda: entier_church(1.5),
            ValueError
        )
    )

    resultats.append(
        erreur_attendue(
            "terme non Church",
            lambda: valeur_church(('variable', 'a')),
            ValueError
        )
    )

    print('=' * 55)
    print(f"{sum(resultats)}/{len(resultats)} tests réussis")

    if not all(resultats):
        raise SystemExit(1)


if __name__ == '__main__':
    main()