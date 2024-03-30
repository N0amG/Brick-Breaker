def Game(game_niveau = 1, game_point=0, timer=[0, 0], bonus=0):
    """
    La fonction principale pour lancer le jeu.

    Args:
        game_niveau (int): Niveau du jeu (1 par défaut).
        game_point (int): Score du joueur (0 par défaut).
        timer (list): Un timer pour mesurer le temps écoulé (0 par défaut).
        bonus (int): Les bonus accumulés par le joueur (0 par défaut).

    Returns:
        None
    """

    # Importation des modules nécessaires
    from random import randint as rd  # Pour les tirages aléatoires
    import sys  # Pour quitter proprement
    import time

    import pygame  # Le module Pygame
    import pygame.freetype  # Pour afficher du texte
    import math

    # Le chemin où se trouvent les images et les sons pour le jeu
    path = "F:/POO/casse_briques_GUEZ_Noam"

    # Initialisation de Pygame
    pygame.init()

    # Pour le texte.
    pygame.freetype.init()

    # Police de caractères pour le texte
    myfont = pygame.freetype.SysFont("arial", 20)  # texte de taille 20

    # Taille de la fenêtre (proportions de la fentre par rapport à l'écran : 1 par défaut)
    n = 1
    infoObject = pygame.display.Info()
    screen_width = infoObject.current_w // n
    screen_height = infoObject.current_h // n
    screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption("Ping")

    # Pour limiter le nombre d'images par seconde
    clock = pygame.time.Clock()

    # Définition des constantes de couleur pour le jeu
    BLANC = (255, 255, 255)
    NOIR = (0, 0, 0)

    # Initialisation des variables pour la fin de la partie
    end_sound = 0

    # Les limites de l'écran de jeu
    XMIN, YMIN = 0, 0
    XMAX, YMAX = screen_width, screen_height

    class Balle:
        """
        La classe pour la balle du jeu.
        """

        def vitesse_par_angle(self, angle):
            """
            Fonction pour calculer la vitesse de la balle en fonction de l'angle.

            Args:
                angle (int): L'angle de la balle (en degrés).

            Returns:
                None
            """
            self.vx = self.vitesse * math.cos(math.radians(angle))
            self.vy = -self.vitesse * math.sin(math.radians(angle))

        def __init__(self, raquette, vitesse):
            """
            Initialisation de la balle.

            Args:
                raquette (Raquette): La raquette pour que la balle commence sur la raquette.
                vitesse (int): La vitesse initiale de la balle.

            Returns:
                None
            """
            self.x, self.y = (raquette.x, raquette.y)
            self.vitesse = 7 + vitesse # vitesse initiale
            self.vitesse_par_angle(60) # vecteur vitesse
            self.sur_raquette = True
            self.vie = 1
            self.degat = 1
            self.image = pygame.image.load("images/ball.png")
            self.image= pygame.transform.scale(self.image, (20,20))
            self.rect = self.image.get_rect()
            self.type = "ball" or "pizza_mozarella"
            self.ecart_bot = -25
            self.timer = time.monotonic()
            
        def afficher(self):
            screen.blit(self.image, (self.x ,self.y))
            # afficher la hitbox de la balle
            #pygame.draw.rect(screen, (255,0,0), self.rect, 2)
        
        def deplacer(self, raquette):
            touche = False # variable qui indique si la balle a touché quelque chose

            # Si la balle est sur la raquette
            if self.sur_raquette: 
                # La balle est positionnée sur le haut de la raquette, centrée horizontalement
                self.y = raquette.y  - self.rect.height
                self.x = raquette.x + raquette.rect.width/2 - self.rect.width/2
                self.rect.x, self.rect.y = self.x, self.y
                
                # Si le timer n'est pas initialisé (la balle vient d'être débuggé), la balle quitte la raquette
                if self.timer == None:
                    self.sur_raquette = False
                self.timer = time.monotonic() # On initialise le timer pour prendre en compte le déplacement de la balle sur la raquette

            # Si la balle n'est pas sur la raquette
            else:
                # La balle est déplacée selon son vecteur vitesse (vx,vy)
                self.x += self.vx 
                self.y += self.vy
                # la hitbox est deplacé au position de la raquette
                self.rect.x, self.rect.y = self.x, self.y

                # Si la balle entre en collision avec la raquette et qu'elle descend
                if raquette.collision_balle(self) and self.vy > 0:
                    self.rebond_raquette(raquette) # La balle rebondit sur la raquette
                    touche = True # La balle a touché la raquette
                    self.timer = time.monotonic() # On initialise le timer pour prendre en compte le déplacement de la balle sur la raquette
                
                # Si la balle entre en collision avec le mur de droite
                if self.x + self.rect.width >= XMAX: 
                    self.vx = -self.vx # La balle rebondit sur le mur de droite
                    touche = True # La balle a touché le mur
                # Si la balle entre en collision avec le mur de gauche
                if self.x  <= XMIN: 
                    self.vx = -self.vx # La balle rebondit sur le mur de gauche
                    touche = True # La balle a touché le mur
                # Si la balle entre en collision avec le plafond
                if self.y >= YMAX: 
                    self.vie -= 1 # On enlève une vie au joueur
                    self.vy = -self.vy # La balle rebondit sur le plafond
                    touche = True # La balle a touché le plafond
                # Si la balle entre en collision avec le sol
                if self.y <= YMIN: 
                    self.vy = -self.vy # La balle rebondit sur le sol

                # Si la balle a touché quelque chose
                if touche:
                    # On joue un son aléatoire de collision
                    sound = pygame.mixer.Sound(f"sounds/ball/bip ({rd(1,5)}).ogg")
                    sound.set_volume(0.5)
                    sound.play()
        
        def rebond_raquette(self, raquette):
            # Si la raquette est en bas de l'écran, on change la valeur de l'écart_bot
            if raquette.bot:
                self.ecart_bot = not self.ecart_bot
            # On calcule la distance horizontale entre le centre de la balle et le centre de la raquette
            diff = raquette.x + raquette.longueur/2 - self.x
            # On calcule l'angle de rebond en fonction de la distance horizontale
            angle = 90 + 70 * diff/raquette.longueur
            # On s'assure que l'angle reste compris entre 20 et 160 degrés
            if angle > 160: angle = 160
            elif angle < 20: angle = 20
            
            self.vitesse_par_angle(angle)
            
        def en_vie(self):
            return self.vie > 0

    class Raquette:
        
        def __init__(self):
            self.image = pygame.image.load("images/raquette.png")
            self.rect = self.image.get_rect()
            self.longueur = self.rect.width
            self.x = (XMIN+XMAX)/2
            self.y = YMAX - self.rect.height
            self.type = "white" or "italie"
            self.bot = False
            self.bonus_looted = 0 + bonus # rajoute les stats des niveau précédents
        def afficher(self):
            screen.blit(self.image, (self.x , self.y))
            # afficher la hitbox de la raquette
            #pygame.draw.rect(screen, (255,0,0), self.rect, 3)
        
        def deplacer(self, x, jeu):
            # si le joueur a ramassé le bonus bot et qu'il y a des balles sur l'écran
            if self.bot and jeu.balles != []:
                
                # on récupère les balles et les bonus sur l'écran
                balles = jeu.balles
                bonus_list = jeu.bonus_list
                balle_imin = 0
                bonus_imin = 0
                
                # on cherche la balle la plus basse sur l'écran
                if balles != []:
                    for balle in balles:
                        if balle.y > balles[balle_imin].y:
                            balle_imin = balles.index(balle)
                
                # on cherche le bonus le plus bas sur l'écran (en ignorant les bombes)
                if bonus_list != []:
                    for bonus in bonus_list:
                        # ignore les bombes
                        if bonus.type != "bomb":
                            if bonus.coor_y > bonus_list[bonus_imin].coor_y:
                                bonus_imin = bonus_list.index(bonus)
                    # si le bonus est plus bas que la balle la plus basse, on se déplace vers le bonus
                    if bonus_list[bonus_imin].coor_y < balles[balle_imin].y:
                        self.x = balles[balle_imin].x - self.rect.width/2 + balles[balle_imin].ecart_bot # ecart pour rajouter un peu d'aléatoire sinon la bales fais justes des aller retour haut/bas
                    # sinon on se déplace vers la balle la plus basse
                    else:
                        self.x = bonus_list[bonus_imin].coor_x - self.rect.width/2
                
                # si il n'y a pas de bonus sur l'écran, on se déplace vers la balle la plus basse
                else:
                    self.x = balles[balle_imin].x - self.rect.width/2 + balles[balle_imin].ecart_bot
            
                # on empêche la raquette de sortir de l'écran à gauche
                if x < XMIN:
                    x = XMIN
            
            # sinon si la raquette n'a pas ramassé le bonus bot et qu'elle se déplace trop à gauche, on la bloque à gauche
            elif x  < XMIN:
                self.x = XMIN 
            
            # si la raquette se déplace trop à droite, on la bloque à droite
            elif x + self.rect.width > XMAX:
                self.x = XMAX - self.rect.width
            
            # sinon on déplace la raquette à la position demandée
            else:
                self.x = x
                
            # on met à jour la position de la hitbox de la raquette
            self.rect.y = self.y
            self.rect.x = self.x
            
        def collision_balle(self, balle):
            # test s'il y a une collision entre les deux boites de collisions avec une méthode de pygame
            return self.rect.colliderect(balle.rect)

        def timer_bonus(self,start):
            # Définis un timer avec comme parametre start = time.monotic() activer dans le main
            end = time.monotonic()
            if end - start >= 15:
                # Si le temps écouler est supérieur ou égale au temps d'activation du bonus, on retourne vrai
                return True
            else:
                return False

    class Brique:
        
        def __init__(self, jeu ,x, y, vie = 0):
            self.jeu = jeu
            self.x = x
            self.y = y
            self.vie = vie
            self.longueur = 4 * 15
            self.largeur = 2* 15
            self.rect = pygame.Rect(int(self.x - self.longueur / 2), int(self.y - self.largeur / 2), self.longueur, self.largeur)
            self.coloring()

        def coloring(self):
            ROUGE = (255, 0,0) ; ORANGE = (255, 170, 0) ; JAUNE = (255, 255,0) 
            VERT = (0,255,0) ; CYAN = (0,255,255) ; BLEU = (0,0,255)
            ROSE = (255, 0, 243) ; VIOLET = (162, 0, 255) ; MAX = (66, 51, 73)

            self.color_list = [VIOLET, ROSE, BLEU, CYAN, VERT, JAUNE, ORANGE, ROUGE]
            if self.vie == -10:
                self.color = BLANC
                self.longueur = 5 * 15
            elif self.vie >= 9:
                self.color = MAX
            else: 
                self.color = self.color_list[-self.vie]
        
        def en_vie(self):
            if self.vie != -10: return self.vie > 0
            return True
        
        def afficher(self):
            self.coloring()
            self.rect = pygame.Rect(int(self.x - self.longueur / 2), int(self.y - self.largeur / 2), self.longueur, self.largeur)
            pygame.draw.rect(screen, self.color, self.rect, 0)
            
        
        def collision_balle(self, balle):
            # on suppose que largeur < longueur
            marge = self.largeur/2 + balle.rect.width/2
            dy = balle.y - self.y
            touche = False
            if balle.x >= self.x: # on regarde a droite
                dx = balle.x - (self.x + self.longueur/2 - self.largeur/2)
                # Léger remaniment des conditions de collision, plus efficace comme sa.
                if self.rect.colliderect(balle.rect):
                    touche = True
                    if dx <= abs(dy):
                        balle.vy = -balle.vy
                    else: # a droite
                        balle.vx = -balle.vx
            else: # on regarde a gauche
                dx = balle.x - (self.x - self.longueur/2 + self.largeur/2)
                # Léger remaniment des conditions de collision, plus efficace comme sa.
                if self.rect.colliderect(balle.rect):
                    touche = True
                    if -dx <= abs(dy):
                        balle.vy = -balle.vy
                    else: # a gauche
                        balle.vx = -balle.vx
            if touche:
                if self.vie != -10:
                    self.vie -= balle.degat
                    self.jeu.points += balle.degat
                    sound = pygame.mixer.Sound(f"sounds/brick/break ({rd(1,8)}).ogg")
                    sound.set_volume(0.5)
                    balle.timer = time.monotonic()
                else:
                    sound = pygame.mixer.Sound(f"sounds/ball/bip ({rd(1,5)}).ogg")
                    sound.set_volume(0.5)
                    sound.play()
                sound.play()
            return touche

    class Bonus:
        def __init__(self, brique, raquette):
            # Référence au raquette qui récupère le bonus
            self.brique = brique
            # Coordonnées aléatoires de l'apparition du bonus
            self.coor_x = brique.x
            self.coor_y = brique.y
            # raquette associé
            self.player = raquette
            # Vitesse de descente du bonus
            self.vitesse =  2
            # Indicateur si le bonus a été récupéré par la raquette
            self.looted = False
            # Indicateur si le bonus est actif
            self.active = True
            # Type de bonus aléatoire (entier entre 0 et 3)
            self.type = rd(0,5)
            # Durée de vie du bonus (en secondes)
            self.timer = 15
            # Image du bonus récupéré
            self.looted_image = None

            
            # Si le type de bonus est new_balle ( rajoute une nouvelle balle)
            if self.type == 0: 
                self.type = "new_ball"
                # Chargement de l'image du bonus en chute
                self.falling_image = pygame.image.load("images/new_ball.png")
            
            # Si le type de bonus est new_life qui redonne une vie
            elif self.type == 1:
                self.type = "new_life"
                # Chargement de l'image du bonus en chute
                self.falling_image = pygame.image.load("images/new_life.png")
            
            # Si le type de bonus est pizza_mozarella (pizza mozarella qui fait 3 points de dégats)
            elif self.type == 2:
                self.type = "pizza_mozarella"

                # Chargement de l'image du bonus en chute
                self.falling_image = pygame.image.load("images/pizza_mozarella_bonus.png")   
            elif self.type == 3:
                self.type = "raquette_upgrade"
                self.falling_image = pygame.image.load("images/raquette_upgrade.png")
            
            elif self.type == 4:
                self.type = "bot"
                self.falling_image = pygame.image.load("images/bot_bonus.png")
                self.timer = 15
        
            elif self.type > 4:
                self.type = "bomb"
                self.falling_image = pygame.image.load("images/bomb.png")
                self.vitesse = 4
            # Zone de collision du bonus
            self.falling_image = pygame.transform.scale(self.falling_image, (50,50))
            # hitbox du bonus
            self.rect = self.falling_image.get_rect()
        def summon(jeu):
            # définis une chance d'aparition d'un bonus, est appelé a chaque déstruction de brique
            n = rd(0,90)
            n *= (1.15 ** jeu.niveau) # augmente la probabilité des bonus a chaque niveau
            if n >=  90 : return True
            else : return False

        def deplacer(self):
            # Si le bonus n'a pas été récupéré par la raquette
            if not self.looted:
                # Si le bonus est actif
                if self.active:
                    # Si le bonus n'est pas encore arrivé en bas de l'écran
                    if self.coor_y <= screen_height - self.falling_image.get_height():
                        # On fait descendre le bonus vers le bas de l'écran
                        self.coor_y += self.vitesse
                        self.rect.x = self.coor_x
                        self.rect.y = self.coor_y
                        return True
                    # Si le bonus a atteint le bas de l'écran
                    elif self.coor_y > screen_height - self.falling_image.get_height():
                        # On désactive le bonus
                        self.active = False
                        return False
                # Si le bonus n'est pas actif et n'a pas été récupéré
                if self.active and self.looted == False :
                    return False
                return False

        def destruct(self):
            # Désactive le bonus
            self.active = False
            return True

        def is_collide(self, raquette):
            # Si le bonus, a une boite de collision, retourne s'il est en collision avec l'ennemi
            if self.rect:
                return self.rect.colliderect(raquette.rect)

        def afficher(self):
            screen.blit(self.falling_image, (self.coor_x, self.coor_y))
            #hitbox
            #pygame.draw.rect(screen , (255,0,0), self.rect, 2)

        def pizza_mozarella(self,jeu, raquette, balles):
            aucune_balle = True
            for balle in balles:
                # test pour toute les balles s"il y en a au moins une qui n'as pas le bonus pizza
                if balle.type == "ball":
                    # si la musique pizza mozarella n'est pas encore lancé, la lance, sinon ne fait rien
                    if jeu.music == "main_theme":
                        jeu.music = "pizza_mozarella"
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("musics/pizza_mozarella.mp3")
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.2)
                        
                    
                    # si la raquette est blanche, la transforme en drapeau italien
                    if raquette.type == "white":
                        raquette.type = "italie"
                        raquette.image = pygame.image.load("images/raquette_italie.png")
                        raquette.image = pygame.transform.scale(raquette.image, (raquette.rect.width, raquette.rect.height))
                    
                    # la balle se tranforme en pizza mozarella
                    balle.image = pygame.image.load("images/pizza_mozarella.png")
                    balle.image = pygame.transform.scale(balle.image,(64,64))
                    balle.rect = balle.image.get_rect()
                    balle.degat = 3
                    balle.type = "pizza_mozarella"
                    aucune_balle = False
                    sound = pygame.mixer.Sound("sounds/bonus/its_me_mario.ogg")
                    sound.play()
                    # sort du test de toutes les balles
                    break
            # si toutes les balles sont déja en pizza, rajoute 25 points
            if aucune_balle:
                jeu.points += 25
            
        def new_life(self, jeu):
            # si la vie est < à 3 rajoute 1 pv et rajoute 10 points
            if jeu.vie < 3: jeu.vie += 1 ; jeu.points += 10
            #si vie > 3, rajoute 25 points
            else: jeu.points += 25
            
            # joue le son de + 1 vie
            sound = pygame.mixer.Sound("sounds/bonus/mario_life_up.ogg")
            sound.set_volume(0.5)
            sound.play()
        
        def new_ball(self,raquette, jeu):
            # rajoute une nouvelle balle au jeu 
            balle = Balle(raquette, jeu.niveau)
            balle.sur_raquette = False
            jeu.balles.append(balle)
        
        def raquette_upgrade(self, jeu, raquette):
            #si la taille de la raquette est < à 400, la fait grandire de 15 pixel en longueur
            if raquette.rect.width <= 400:
                raquette.image = pygame.transform.scale(raquette.image, (raquette.rect.width + 15, raquette.rect.height))
                # met a jour la hitbox
                raquette.rect = raquette.image.get_rect()
                # joue le son
                sound = pygame.mixer.Sound("sounds/bonus/mario_grow.ogg")
                sound.set_volume(0.8)
                sound.play()
            # si la taille maximae est atteinte rajoute 30 points
            else: jeu.points += 30

        def bot(self,jeu):
            sound = pygame.mixer.Sound("sounds/bonus/mario_star_powerup.ogg")
            channel_bot = pygame.mixer.Channel(0)
            # si la raquette n'es pas deja en mode bot
            if not jeu.raquette.bot:
                jeu.raquette.bot = True
                # joue la musique du bonus
                sound = pygame.mixer.Sound("sounds/bonus/mario_star_powerup.ogg")
                channel_bot.play(sound)
                return time.monotonic()
            else:
                #sinon, rajoute 45 points, renvoie le timer actuelle pour ne pas reset le timer si la raquette est en mode bot
                jeu.points += 45
                return jeu.start_timer

        def bomb(self, jeu):
            # si la raquette est en mdoe automatique, est invulnérable aux bombes
            if not jeu.raquette.bot:
                jeu.vie -= 1
                # annules les 45 points donnés par tous les bonus
                jeu.points -= 45
                if jeu.points < 0: jeu.points = 0
                sound = pygame.mixer.Sound(f"sounds/bonus/explosion ({rd(1,2)}).ogg")
                sound.play()
        
        def activation(self, jeu, raquette, balles):
            # appelle la bonne méthode en fonction du bonus ramassé par le joueur
            if self.type == "new_ball":
                self.new_ball(raquette, jeu)
            elif self.type == "new_life":
                self.new_life(jeu)
            elif self.type == "pizza_mozarella":
                self.pizza_mozarella(jeu, raquette, balles)
            elif self.type == "raquette_upgrade":
                self.raquette_upgrade(jeu, raquette)
            elif self.type =="bot":
                return self.bot(jeu)
            elif self.type == "bomb":
                self.bomb(jeu)

    class Jeu:
        
        len_niveau = 10

        def __init__(self):
            self.raquette = Raquette()
            self.balles = [Balle(self.raquette, vitesse = game_niveau)]
            self.briques = []
            self.inde_briques = []
            self.bonus_list = []
            self.vie = 3
            self.points = game_point
            self.pause = False
            self.music = None
            self.bot = False
            self.start_timer = None
            self.affichage_timer = None
            self.active = True
            self.win = False
            self.niveau = game_niveau
            self.main_theme()
            # premiere ligne vaut 0 car sinon, les briques sont a moitié dans le plafond, pas très esthétique
            # numéro dans le tableau = pv de la brique
            B = -10 # = Brique incassable
            """
            exemple niveau vide standart
            niveau =[
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    ]
            
            """
            if self.niveau == 1:
                niveau = [
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
                        [B, B, B, B, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, B, B, B, B],
                        ]
            
            elif self.niveau == 2:
                niveau =[
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4],
                        [0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0],
                        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                        ]
            
            elif self.niveau == 3:
                niveau =[
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 3, 3, 3, 0, 3, 3, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 3, 0, 3, 3, 3, 3, 3, 3, 3, 0, 3, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
            
            elif self.niveau == 4:
                niveau =[
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                        [B, B, B, B, B, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, B, B, B, B],
                        ]

            elif self.niveau == 5:
                niveau =[
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 4, 4, 4, 4, 0, 0, 3, 0, 0, 0, 3, 0, 1, 1, 1, 0, 0, 0, 2, 2, 0],
                        [4, 0, 0, 0, 0, 4, 0, 0, 3, 0, 3, 0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 2],
                        [4, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 2],
                        [4, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 2],
                        [4, 0, 0, 4, 4, 0, 0, 0, 0, 3, 0, 0, 0, 1, 1, 1, 0, 0, 2, 0, 0, 2],
                        [4, 0, 0, 0, 0, 4, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 2],
                        [4, 0, 0, 0, 0, 4, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 2],
                        [0, 4, 4, 4, 4, 0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 1, 0, 0, 2, 2, 0],
                        ]
            elif self.niveau == 6:
                niveau =[
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                        [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                        [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                        [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                        [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                        ]
            
              
            if self.niveau <= 6:
                if self.niveau == 4 or self.niveau == 6:
                    #si c'ets le niveau 4 ou 6, met la couleur des briques en aléatoire
                    for y in range(1, len(niveau)):
                        for x in range(len(niveau[y])):
                            if niveau[y][x] > 0: niveau[y][x] = rd(1,7)
                # place dans le niveau, toutes les nombres de la matrice par des briques de la même vie que le nombre, et au bonne positions
                for y in range(1, len(niveau)):
                    for x in range(len(niveau[y])):
                        if niveau[y][x] > 0: self.briques.append(Brique(self, x*4.6* 15, y*3 * 15, niveau[y][x]))
                        elif niveau[y][x] == B: self.inde_briques.append(Brique(self, x*4.6* 15, y*3 * 15, niveau[y][x]))
            
            if self.niveau >= 7:
                # nombre de briques dans une ligne en fonction de la taille de l'écran (niveau 7 et + sont tous les memes, la difficulté continue de croitre)
                # calcul le nombre colonne en fonction de la taille de l'écran
                self.colonne = round(screen_width / (4.6*15) + 1)
                # créer un niveau avec des briques de pv 1 en bas jusqu'au pv 9 en haut de l'ecran
                for y in range(1, self.len_niveau):
                    for x in range(1, self.colonne-1):
                        self.briques.append(Brique(self, x*4.6* 15, y*3 * 15, self.len_niveau-y))
                # joue le son de vitesse très élévé 
                sound = pygame.mixer.Sound("sounds/event/vitessemax-starwars-hyperdrive.ogg")
                sound.play()
            
            elif 1 < self.niveau < 7:
                        # joue le son d'augmentation de vitesse
                        sound = pygame.mixer.Sound("sounds/event/vitesse-superieur.ogg")
                        sound.play()

            

        def main_theme(self):
            
            if self.music != "main_theme":
                self.music = "main_theme"
                pygame.mixer.music.stop()
                pygame.mixer.music.load("musics/jetpack_joyride.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                
            
            if self.raquette.type == "italie":
                self.raquette.type = "white"
                self.raquette.image = pygame.image.load("images/raquette.png")
                self.raquette.image = pygame.transform.scale(self.raquette.image, (self.raquette.rect.width, self.raquette.rect.height))
        
        def gestion_evenements(self):
            # Gestion des evenements
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit() # Pour quitter
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL:
                        self.pause = not self.pause
                    if event.key == pygame.K_ESCAPE:
                        self.vie = 0
                if event.type == pygame.MOUSEBUTTONDOWN: # On vient de cliquer 
                    if event.button == 1: # Bouton gauche 
                        if self.balles != [] and self.balles[0].sur_raquette: 
                            self.balles[0].sur_raquette = False
                            self.balles[0].vitesse_par_angle(rd(60,120))

        def mise_a_jour(self):
            # On récupère la position de la souris pour déplacer la raquette
            x, y = pygame.mouse.get_pos()
            x -= self.raquette.rect.width /2
            
            # Pour chaque balle, on la déplace et on vérifie si elle a touché une brique ou est sortie de l'écran, ou si elle est coincé depuis plus de 15 secondes
            for balle in self.balles:
                balle.deplacer(self.raquette)
                if time.monotonic() - balle.timer > 15:
                    balle.sur_raquette = True
                    balle.timer = None
                if not balle.en_vie():
                    self.balles.remove(balle)
            
            # Pour chaque brique, on vérifie si elle est en vie et si une balle la touche
            for brique in self.briques:
                if brique.en_vie():
                    for balle in self.balles:
                        brique.collision_balle(balle)
                else:
                    # Si la brique est morte, on la retire et on a une chance de faire apparaitre un bonus
                    if Bonus.summon(self):
                        self.bonus_list.append(Bonus(brique, self.raquette))
                    self.briques.remove(brique)
            
            # Pour chaque brique indestructible, on vérifie si une balle la touche
            for inde_brique in self.inde_briques:
                for balle in self.balles:
                    inde_brique.collision_balle(balle)
            
            # Pour chaque bonus, on vérifie si la raquette le touche et on l'active si c'est le cas
            for bonus in self.bonus_list:
                if bonus.is_collide(self.raquette):
                    if bonus.type == "bot":
                        self.start_timer = bonus.activation(self, self.raquette, self.balles)
                    else:
                        bonus.activation(self, self.raquette, self.balles)
                    self.raquette.bonus_looted += 1
                    self.points += 15
                    self.bonus_list.remove(bonus)
                elif not bonus.deplacer():
                    self.bonus_list.remove(bonus)
            
            # Si un timer de bot est en cours, on vérifie s'il est terminé
            if self.start_timer != None:
                if self.raquette.timer_bonus(self.start_timer):
                    self.raquette.bot = False
                    self.affichage_timer = None
                    self.start_timer = None
                else:
                    self.affichage_timer = True
            
            # Si toutes les balles sont mortes et qu'il reste des briques, on perd une vie
            if self.balles == [] and self.briques != []:
                if self.vie >= 1:
                    self.vie -= 1
                    self.bonus_list = []
                    if self.vie > 0:
                        self.balles.append(Balle(self.raquette, self.niveau))
                        self.main_theme()
                    sound = pygame.mixer.Sound("sounds/event/minecraft-death.ogg")
                    sound.play()
            
            # On déplace la raquette
            self.raquette.deplacer(x, self)


        def affichage(self):
            screen.fill(NOIR)  # on efface l'écran
            
            # On affiche toutes les balles
            for balle in self.balles:
                balle.afficher()
            
            # On affiche la raquette
            self.raquette.afficher()
            
            # On affiche les briques qui sont encore en vie
            for brique in self.briques:
                if brique.en_vie():
                    brique.afficher()
            
            # On affiche les briques indestructibles
            for inde_brique in self.inde_briques:
                inde_brique.afficher()
            
            # On affiche tous les bonus
            for bonus in self.bonus_list:
                bonus.afficher()
            
            # On affiche le nombre de vies restantes
            if self.vie > 1:
                vie, vie_rect = myfont.render(f"{self.vie} vies", (0, 255, 0))
            else:
                vie, vie_rect = myfont.render(f"{self.vie} vie", (255, 0, 0))
            vie_rect.bottomright = (screen_width, 500)
            screen.blit(vie, vie_rect)
            
            # On affiche le nombre de points
            points, points_rect = myfont.render(f"{self.points} points", (0, 255, 0))
            points_rect.bottomright = (screen_width, 480)
            screen.blit(points, points_rect)
            
            # On affiche le niveau
            if self.niveau < 5:
                niveau, niveau_rect = myfont.render(f"niveau {self.niveau}", (0, 255, 0))
            else:
                niveau, niveau_rect = myfont.render(f"niveau {self.niveau}", (255, 0, 0))
            niveau_rect.bottomright = (screen_width - 3, 450)
            screen.blit(niveau, niveau_rect)
            
            # On affiche le timer si le bonus bot est actif
            if self.affichage_timer is not None:
                time_left = 15 - round(time.monotonic() - self.start_timer)
                if time_left > 5:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)
                timer, timer_rect = myfont.render(f"{time_left} secondes", color)
                timer_rect.bottomright = (screen_width, 525)
                screen.blit(timer, timer_rect)

        def en_vie(self):
            return self.vie > 0


    jeu = Jeu()
    start_game_timer= time.monotonic()

    while True:
        jeu.gestion_evenements()
        jeu.mise_a_jour()
        jeu.affichage()

        while jeu.pause:
            pause_myfont = pygame.font.SysFont("arial", 50)
            pygame.mixer.music.pause()
            screen.blit(pause_myfont.render("Partie en Pause ...", 1, (255, 255, 255)), (screen_width // 2 - 180, screen_height // 2))
            pygame.mixer.stop()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
                    jeu.pause = not jeu.pause
                    pygame.mixer.music.unpause()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    jeu.pause = not jeu.pause
                    pygame.mixer.music.unpause()

        # Victoire
        if jeu.briques == [] and jeu.en_vie():
            if end_sound == 0:
                end_sound += 1
                pygame.mixer.music.stop()
                pygame.mixer.Channel(0).stop()
                sound = pygame.mixer.Sound("sounds/event/mario-win.ogg")
                sound.play()
            jeu.win = True
            if jeu.balles:
                jeu.balles.pop(0)
            if jeu.bonus_list:
                jeu.bonus_list.pop(0)
            elif not (jeu.bonus_list or jeu.balles):
                jeu.active = False

        # Game over
        elif not jeu.en_vie():
            if end_sound == 0:
                end_sound += 1
                pygame.mixer.music.stop()
                pygame.mixer.Channel(0).stop()
                sound = pygame.mixer.Sound("sounds/event/mario-game-over.ogg")
                sound.play()
            # Supprime la première et la dernière brique de la liste de briques
            nb = 1
            if len(jeu.briques) > nb * 2:
                for i in range(nb):
                    jeu.briques.pop(i)
                    jeu.briques.pop(-i - 1)
            else:
                jeu.briques.clear()
            jeu.bonus_list.clear()
            if not jeu.briques:
                jeu.active = False

        pygame.display.flip()
        clock.tick(80)

        if not jeu.active:
            screen.fill(NOIR)

            # Couleur blanche
            color = (255, 255, 255)

            # Ombre claire du bouton
            color_light = (170, 170, 170)

            # Ombre foncée du bouton
            color_dark = (100, 100, 100)

            width = screen_width
            height = screen_height
            button_width = width / 2.5
            button_height = height / 2

            # Définit une myfont
            leave_smallfont = pygame.font.SysFont("Arial", 35)

            # Fait le rendu du texte "Rejouer" avec cette myfont
            replay_text = leave_smallfont.render("Rejouer", True, color)

            # Fait le rendu du texte "Quitter" avec cette myfont
            leave_text = leave_smallfont.render("Quitter", True, color)

            # Fait le rendu du texte "Niveau x+1" avec cette myfont
            next_text = leave_smallfont.render(f"Niveau {jeu.niveau + 1}", True, color)

            
            end_game_timer = time.monotonic() # Récupère le temps de fin de partie avec la fonction monotonic() de la bibliothèque time
            game_time = [0,round(end_game_timer - start_game_timer + timer[0]*60 + timer[1])] # Calcule le temps total de la partie en ajoutant le temps écoulé depuis le début du jeu, le temps de jeu restant et le temps de jeu passé dans les niveaux précédents
            if game_time[1] >= 60: # Si le temps de jeu total dépasse une minute
                for i in range(0,game_time[1],60): # Boucle sur toutes les minutes écoulées
                    game_time[0] = i/60 # Ajoute une minute à la variable game_time[0]
                game_time = (round(game_time[0]), round(game_time[1]-60*game_time[0])) # Calcule les secondes restantes

            while True: # Boucle principale du programme qui tourne en continu

                for ev in pygame.event.get(): # Boucle sur les événements pygame

                    if ev.type == pygame.QUIT: # Si l'utilisateur ferme la fenêtre pygame
                        pygame.quit() # Ferme la bibliothèque pygame
                        sys.exit() # Ferme le programme

                    if ev.type == pygame.MOUSEBUTTONDOWN: # Si l'utilisateur clique avec la souris

                        mouse = pygame.mouse.get_pos() # Récupère la position de la souris

                        if button_width <= mouse[0] <= button_width+140 and button_height+15 <= mouse[1] <= button_height+55: # Si l'utilisateur clique sur le bouton "quitter"
                            pygame.quit() # Ferme la bibliothèque pygame
                            sys.exit() # Ferme le programme

                        if button_width + 170 <= mouse[0] <= button_width+310 and button_height+15 <= mouse[1] <= button_height+55: # Si l'utilisateur clique sur le bouton "rejouer"
                            pygame.quit() # Ferme la bibliothèque pygame
                            if jeu.win:
                                # relance une partie avec le niveau suivant et toutes les statistiques des parties précédente sont conservés
                                Game(jeu.niveau+1, jeu.points, timer= game_time, bonus= jeu.raquette.bonus_looted) # Relance le jeu au niveau suivant avec les points accumulés, les bonus récupérés et le temps de jeu restant
                            else: 
                                Game() # Relance le jeu au niveau initial avec un temps de jeu initial de 5 minutes

                mouse = pygame.mouse.get_pos() # Récupère la position de la souris

                if button_width <= mouse[0] <= button_width+140 and button_height+15 <= mouse[1] <= button_height+55: # Si la souris passe sur le bouton "quitter"
                    pygame.draw.rect(screen,color_light,[button_width,button_height+15,140,40]) # Change la couleur de l'ombre du bouton

                else:
                    pygame.draw.rect(screen,color_dark,[button_width,button_height+15,140,40]) # Laisse la couleur de l'ombre du bouton par défaut

                if button_width+170 <= mouse[0] <= button_width+310 and button_height+15 <= mouse[1] <= button_height+55: # Si la souris passe sur le bouton "rejouer"
                    pygame.draw.rect(screen,color_light,[button_width+170,button_height+15,140,40]) # Change la couleur de l'ombre du bouton

                                
                else:
                    pygame.draw.rect(screen,color_dark,[button_width+170,button_height+15,140,40]) # Change la couleur de l'ombre du bouton par défaut
                
                # superposer les textes aux boutons
                screen.blit(leave_text , (button_width+10,button_height+15))
                if not jeu.win:
                    screen.blit(replay_text , (button_width+180,button_height+15))
                else: screen.blit(next_text , (button_width+170,button_height+15))
                
                screen.blit(leave_smallfont.render(f"Vous avez obtenue {jeu.points} points,",1,(255,255,255)), (width/2 - 215, button_height - 200))
                if not jeu.win:
                    screen.blit(leave_smallfont.render(f"Vous avez atteint le niveau {jeu.niveau}",1,(255,255,255)),(width/2 - 250, button_height - 150))
                else: screen.blit(leave_smallfont.render(f"Vous avez fini le niveau {jeu.niveau}",1,(255,255,255)),(width/2 - 250, button_height - 150))
                
                screen.blit(leave_smallfont.render(f"Vous avez récupéré {jeu.raquette.bonus_looted} bonus.",1,(255,255,255)),(width/2 - 250, button_height - 100))
                screen.blit(leave_smallfont.render(f"La partie à durée {game_time[0]} minutes et {game_time[1]} secondes.",1,(255,255,255)),(width/2 - 325, button_height - 50 ))
                
                if jeu.win:
                    texte, rect = myfont.render("Win !", (0,255,0), size = 60)
                    rect.midleft = (screen_width/2 - rect.width/2, screen_height/2 - 250)
                    screen.blit(texte, rect)
                    
                else:    
                    texte, rect = myfont.render("Game Over", (255,0,0), size = 60)
                    rect.midleft = (screen_width/2 - rect.width/2, screen_height/2-250)
                    screen.blit(texte, rect)
                
                pygame.display.update() # envoi de l'image à La carte graphique


# lance une partie
Game()