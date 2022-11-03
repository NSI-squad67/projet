import pygame
import pytmx
import pyscroll

from map import *
from player import *

class Game: # fonction chargée au lancement du jeu
    def __init__(self):
        # creer la fenetre du jeu #

        # dimension de la fenêtre
        self.screen = pygame.display.set_mode((800,600))

        # titre
        pygame.display.set_caption("Ambhalla")


        # generer le joueur
        self.player = Player() # + position perso
        self.map_manager = MapManager(self.screen, self.player) # charge les maps avec leurs portails pour aller vers d'autres monde et les pnjs avec leurs dialogues etc.. 
        self.dialog_box = DialogBox() # charge la classe DialogBox pour que les pnj puissent parler

    def handle_input(self): # fonction qui s'occupe des touches du claviers
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_UP]: # en haut
            self.player.move_up()

        elif pressed[pygame.K_DOWN]: # en bas
            self.player.move_down()

        elif pressed[pygame.K_LEFT]: # à gauche
            self.player.move_left()

        elif pressed[pygame.K_RIGHT]: # à droite
            self.player.move_right()


    # LIGNE 40 (mdr tu dis pas au prof "Ici c'est la ligne 40 :) ")
    def update(self): # met à jour les changements sur la map (pnj qui bouge, si le joueur est rentré dans un autre monde, etc...)
        self.map_manager.update()


    def run(self): # fonction qui lance le jeu
        # boucle du jeu
        clock = pygame.time.Clock() # fps
        running=True
        while running: # En permanence répéter le code qui est en dessous jusqu'à ce que running = False donc quand le programme décide

            self.player.save_location() # enregistre la localisation du joueur (coordonnées) pour être réutilisé dans le porgarmme plus tard
            self.handle_input() # prends en charge les boutons pressés
            # On importe le groupe de calques pour les dessiner
            self.update() # met à jour (voir ligne 40)
            self.map_manager.draw() # affiche touts les éléments de la map et centre la vision sur le joueur en permanence
            self.dialog_box.render(self.screen) # Affiche une bulle de dialogue quand le joueur va vers un pnj et appuis sur la barre espace

            # On actualise
            pygame.display.flip()

            for event in pygame.event.get(): # pour touts les evenements dans la fenetre pygame
                if event.type == pygame.QUIT: # si le joueur arrête le jeur
                    running=False # alors arrêter proprement le programme
                
                elif event.type == pygame.KEYDOWN: # si le joueur appuis sur une touche
                    if event.key == pygame.K_SPACE: # et que cette touche est la barre espace
                        self.map_manager.check_npc_collisions(self.dialog_box) # alors il faut la fonction qui permet de gérer le dialogue et la collision avec les pnj s'enclenche


            clock.tick(60) # régule à 60 fps

        pygame.quit() # quitte la fenêtre