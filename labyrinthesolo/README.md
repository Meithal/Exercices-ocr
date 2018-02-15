# Exercice labyrinthe

## Enonc�

http://exercices.openclassrooms.com/assessment/instructions/370853

## R�sultat

Note finale: 4 / 7

## Corrections

Correction n�1
Crit�re	Points
Le programme fonctionne comme attendu	1 / 1
Lisibilit� du code source	1 / 2
D�coupage du code source	1 / 1
Documentation du code source	1 / 2
Ouverture � l'am�lioration	0 / 1
Total	4 / 7
Commentaires

Le fait que ce programme fonctionne est tellement impressionnant 
que j'ai d�cid� d'accorder le point malgr� des probl�mes avec les 
instructions de d�placement et le fait qu'il ne fonctionne que 
dans un IDE (Rappel: l'interpr�teur Python n�cessite g�n�ralement 
des chemins absolus).

Le code est assez clair (attention toutefois aux noms de variables 
peu compr�hensibles, et � un ou deux passages au fonctionnement
peu clair: parfois, il est utile de ne pas faire TROP compact). 
Certains choix sont int�ressants, comme le fait de plus ou moins 
se d�barrasser du syst�me de coordonn�es XY, mais ces d�cisions 
pourraient �tre un frein � l'am�lioration des fonctionnalit�s du jeu.


Correction n�2
Crit�re	Points
Le programme fonctionne comme attendu	1 / 1
Lisibilit� du code source	1 / 2
D�coupage du code source	1 / 1
Documentation du code source	2 / 2
Ouverture � l'am�lioration	0 / 1
Total	5 / 7
Commentaires

Bonjour,

Je t'ai mis 5/7 avec le d�tail suivant :
- Le programme fonctionne : 1/1
- Lisibilit� du code source : 2/2
- D�coupage du code source : 0/1 (car tu n'as pas suffisamment utilis� le paradigme de la Programmation 
  Orient�e Objet, il n'y a qu'une seule classe, la classe Carte, mais pas de classe Jeu, Partie, Labyrinthe, Robot, Obstacle,
  Mur, Porte ou Sortie qui aurait grandement augment� la modularit� et la maintenabilit� dans le temps).
- Documentation du code source : 2/2
- Ouverte � l'am�lioration : 0/1 (il est difficile d'am�liorer un code qui ne respecte pas vraiment la modularit� 
  offerte par la POO, tu penses peut-�tre que c'est facile, mais si tu y reviens dans 1 mois, il te sera 
  beaucoup plus complexe de poursuivre ce code que si tu l'avais �crit avec plus de classes)

Bon travail dans l'ensemble, juste un truc, au passage, j'ai d� modifier ton code pour qu'il fonctionne d�s le lancement, 
et deuxi�mement, tu t'attends toujours � ce que l'utilisateur ne fasse aucune erreur de saisie, mais lorsque je saisis "n" 
par exemple pour me d�placer au lieu de "N" et bien j'ai une exception qui est lev�e et qui interrompt le jeu, �a c'est pas 
terrible et c'est le cas un peu partout dans ton code ! Accroche toi, et garde l'esprit ouvert pour la correction des autres ! � plus !

Si tu veux me contacter, voici mon profil sur OpenClassrooms :
https://openclassrooms.com/membres/***


Correction n�3
Crit�re	Points
Le programme fonctionne comme attendu	0 / 1
Lisibilit� du code source	2 / 2
D�coupage du code source	0 / 1
Documentation du code source	0 / 2
Ouverture � l'am�lioration	0 / 1
Total	2 / 7
Commentaires

Bonjour,

Le code ne permet pas de rentrer une direction en minuscule. Il n'a donc pas toutes les fonctionnalit�s demand�es.

Vous n'avez pas fonctionn� de la m�me fa�on que la correction, cela fonctionne mais le 
d�coupage n'est pas tr�s pouss� ainsi la compr�hension du code et la modification n'est pas facile.
