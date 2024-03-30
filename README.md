

Menu:

- ctrl gauche = pause
- echap = fin de partie
- menu de fin, game over ou win 
- bouton pour l'écran de fin, quitter, et rejouer si game over, niveau suivant si win
- systeme de statistiques de la partie (s'affiche a la fin de chaque niveau):
	- nombre de bonus ramassé
	- nombre de points
	- durée totale de la partie en cours
	- affiche du niveau atteint

--------------------------------------

Gameplay:

- un malus : certaine fois une bombe peu tomber des briques cassées, inflige un point de dégat au joueur

- 4 bonus qui spawn aléatoirement. Plus le niveau est élevé plus la chance d'en obtenir est élevé, chaque bonus donne des points:
	- un bonus qui fait gagné une vie si le joueur en a moins de 3, sinon donne plus de points
	- un bonus d'upgrade de raquette qui la fait grandir un peu, le bonus est cumulable
	- un bonus bot : pendant un lapse de temps de 15 seconde, la raquette joue automatiquement et rattrape toutes les balles, tous les bonus peu importe leur nombre, et est invulnérable aux bombes
	- un bonus pizza mozarrella : lance un son de mario, puis lance la musique pizza mozarela, transforme la balle en pizza, est plus grande et fais 3 points de dégats au lieu de 1, la raquette se transforme en drapeau italien

- amélioration des systèmes de collision entre tous les élément du jeu avec les hitbox

- systeme de débogage : quand la balle est coincé ou qu'elle est bloqué dans un rebond indéfinis (sur un briques incassable par exemple) : si elle ne touche aucune briques cassable ou qu'elle ne touche pas la raquette pendant 15 secondes, la balle coincée reviens sur a raquette est est relancée tout de suite pour éviter la triche

- Une jolie animation de fin de game over ( détruit toutes les briques en spirales) ( se voit tres bien sur le niveau 7)

PS : J'ai fais en sorte de simplifier au maximum la création de niveau et de la rendre intuitive, si jamais vous avez tu temps vous pouvez vous amusez a créer vos propres niveaux en copiant la matrice exemple et en remplacant les 0 par les nombres indiquant le nombre de points de vie des briques ou par des "B" pour les priques incassables.

Amusez-vous bien :)


Re PS: le pizza mozarella c'est une référence faut pas chercher a comprendre 😂