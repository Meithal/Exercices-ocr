# Exercice labyrinthe

## Enoncé

http://exercices.openclassrooms.com/assessment/instructions/370853

## Résultat

Note finale: 4 / 7

## Corrections

Correction n°1
Critère	Points
Le programme fonctionne comme attendu	1 / 1
Lisibilité du code source	1 / 2
Découpage du code source	1 / 1
Documentation du code source	1 / 2
Ouverture à l'amélioration	0 / 1
Total	4 / 7
Commentaires

Le fait que ce programme fonctionne est tellement impressionnant 
que j'ai décidé d'accorder le point malgré des problèmes avec les 
instructions de déplacement et le fait qu'il ne fonctionne que 
dans un IDE (Rappel: l'interpréteur Python nécessite généralement 
des chemins absolus).

Le code est assez clair (attention toutefois aux noms de variables 
peu compréhensibles, et à un ou deux passages au fonctionnement
peu clair: parfois, il est utile de ne pas faire TROP compact). 
Certains choix sont intéressants, comme le fait de plus ou moins 
se débarrasser du système de coordonnées XY, mais ces décisions 
pourraient être un frein à l'amélioration des fonctionnalités du jeu.


Correction n°2
Critère	Points
Le programme fonctionne comme attendu	1 / 1
Lisibilité du code source	1 / 2
Découpage du code source	1 / 1
Documentation du code source	2 / 2
Ouverture à l'amélioration	0 / 1
Total	5 / 7
Commentaires

Bonjour,

Je t'ai mis 5/7 avec le détail suivant :
- Le programme fonctionne : 1/1
- Lisibilité du code source : 2/2
- Découpage du code source : 0/1 (car tu n'as pas suffisamment utilisé le paradigme de la Programmation 
  Orientée Objet, il n'y a qu'une seule classe, la classe Carte, mais pas de classe Jeu, Partie, Labyrinthe, Robot, Obstacle,
  Mur, Porte ou Sortie qui aurait grandement augmenté la modularité et la maintenabilité dans le temps).
- Documentation du code source : 2/2
- Ouverte à l'amélioration : 0/1 (il est difficile d'améliorer un code qui ne respecte pas vraiment la modularité 
  offerte par la POO, tu penses peut-être que c'est facile, mais si tu y reviens dans 1 mois, il te sera 
  beaucoup plus complexe de poursuivre ce code que si tu l'avais écrit avec plus de classes)

Bon travail dans l'ensemble, juste un truc, au passage, j'ai dû modifier ton code pour qu'il fonctionne dès le lancement, 
et deuxièmement, tu t'attends toujours à ce que l'utilisateur ne fasse aucune erreur de saisie, mais lorsque je saisis "n" 
par exemple pour me déplacer au lieu de "N" et bien j'ai une exception qui est levée et qui interrompt le jeu, ça c'est pas 
terrible et c'est le cas un peu partout dans ton code ! Accroche toi, et garde l'esprit ouvert pour la correction des autres ! À plus !

Si tu veux me contacter, voici mon profil sur OpenClassrooms :
https://openclassrooms.com/membres/***


Correction n°3
Critère	Points
Le programme fonctionne comme attendu	0 / 1
Lisibilité du code source	2 / 2
Découpage du code source	0 / 1
Documentation du code source	0 / 2
Ouverture à l'amélioration	0 / 1
Total	2 / 7
Commentaires

Bonjour,

Le code ne permet pas de rentrer une direction en minuscule. Il n'a donc pas toutes les fonctionnalités demandées.

Vous n'avez pas fonctionné de la même façon que la correction, cela fonctionne mais le 
découpage n'est pas très poussé ainsi la compréhension du code et la modification n'est pas facile.
