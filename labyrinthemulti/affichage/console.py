import jeu


def notification(chaine):
        print(chaine)


def affiche_niveau():
    for (i, c) in enumerate(jeu.carte.flux):
        # if i == self.position_par_defaut.index_:
        #     print(jeu.reglages.CARACTERE_JOUEUR, end='')
        # else:
        print(c, end='')
        if (i + 1) % jeu.carte.taille_ligne == 0:
            print(end='\n')
    print(end='\n')


def affiche_niveau_client(position):
    pass
