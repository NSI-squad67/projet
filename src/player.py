import pygame
import map

# Création d'une entité (PNJ, joueur)
class Entity(pygame.sprite.Sprite): # cette classe hérite de pygame.sprite.Sprite donc ...
    def __init__(self, name, x, y): # cette classe contient les fonctions de la classe pygame.sprite.Sprite
        super().__init__() # Initialise pygame.sprite.Sprite
        self.sprite_sheet = pygame.image.load(f"../sprites/{name}.png") # charge l'image de l'entité spécifié (soit le joueur, soit un pnj)
        self.speed = 2 # régule la vitesse à 2
        self.position = [x,y] # prends les coordonnées x et y de l'entité


        # Charge les images spécifiques au joueur "player"
        if name == "player":

            self.image = self.get_image(2,104) # 2 + 32*k , 14 + 45*k
            self.image.set_colorkey([0,0,0]) # enleve la couleur du fond
            self.rect = self.image.get_rect() # prends un rectangle (la "hit box" ;) )

            # changer d'image lorsque l'on change de sens
            # LIGNE 21
            self.images = { 
                'down': self.get_image(2,104),
                'left': self.get_image(2,14+45*3),
                'right': self.get_image(2,14+45),
                'up': self.get_image(2,14)
            }

        # Charge les images spécifiques au pnj princess
        elif name == "princess":
            self.image = self.get_image(0,0) # 2 + 32*k , 14 + 45*k
            self.image.set_colorkey([0,0,0]) # enleve la couleur du fond
            self.rect = self.image.get_rect() # prends un rectangle (hitbox)

            # changer d'image lorsque l'on change de sens
            # LIGNE 35
            self.images = { 
                'down': self.get_image(0,5),
                'left': self.get_image(0,47),
                'right': self.get_image(0,93),
                'up': self.get_image(0,138)
            }

        # Charge les images spécifiques aux autres pnj
        else:
            self.image = self.get_image(0,0) # 2 + 32*k , 14 + 45*k
            self.image.set_colorkey([0,0,0]) # enleve la couleur du fond
            self.rect = self.image.get_rect() # prends un rectangle

            # changer d'image lorsque l'on change de sens
            # LIGNE 49
            self.images = { 
                'down': self.get_image(0,0),
                'left': self.get_image(0,32),
                'right': self.get_image(0,64),
                'up': self.get_image(0,96)
            }            


        # la collision entre un pnj ou un joueur avec un obstacle se passe au niveau des pieds (donc à la moitié de la hitbox et c'est pour ça qu'on fait * 0.5 ou diviser par deux si tu préfères)
        self.feet = pygame.Rect(0,0, self.rect.width*0.5, 12)
        self.old_position = self.position.copy() # enregistre l'ancienne position

        # permet de sauvegarder l'anciennce position du joueur
    def save_location(self): self.old_position = self.position.copy()

 # changer d'image lorsque l'on change de sens
    def change_animation(self,name):
        self.image = self.images[name] # voir ligne 49,35,21
        self.image.set_colorkey((0,0,0)) # pour pas voir la hitbox blanche dégueulasse
    # Déplacements du perso

    def move_right(self): # fonction qui tourne à droite
        self.change_animation("right")
        self.position[0] += self.speed

    def move_left(self): # fonction qui tourne à gauche
        self.change_animation("left")
        self.position[0] -= self.speed

    def move_up(self): # fonction qui tourne en haut
        self.change_animation("up")
        self.position[1] -= self.speed

    def move_down(self): # fonction qui tourne en bas
        self.change_animation("down")
        self.position[1] += self.speed



    def update(self): # met à jour la position du joueur
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self): # permet de se remettre à la position avant si il y a collision avec un obstacle
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom        


    def get_image(self,x,y): # prends les coordonnées du sprite (pnj ou joueur)
        image = pygame.Surface([32,32]) # taille de l'image (largeur et hauteur)
        image.blit(self.sprite_sheet, (0,0), (x,y,32,32))
        return image # retourne l'image du sprite

class Player(Entity): # cette classe hérite  de la classe Entity (donc elle à toutes les fonctions de la classe Entity) (celle qu'on vient d'écrire en haut)
    def __init__(self):
        super().__init__("player",0,0) # initialisation joueur
        self.sac = [] # ptit sac à dos pour le joueur

# création d'une classe qui s'occupe des dialogues entre les pnj et le joueur
class DialogBox:

    # prends la position X et Y où afficher la bulle de dialogue
    X_POSITION = 60
    Y_POSITION = 470

    def __init__(self):
        self.box = pygame.image.load("../dialogs/dialog_box.png") # charge la bulle
        self.box = pygame.transform.scale(self.box, (700,100)) # redéfinis ça taille pour que ça soit agréable à regarder
        # LIGNE 121
        self.texts = [] # va contenir les textes que vont dire les pnj
        self.font = pygame.font.Font("../dialogs/dialog_font.ttf", 18) # charge la police
        self.text_index = 0 # va servir pour afficher le texte contenu dans la liste qui contient les textes ligne 121
        self.reading = False # va permettre d'afficher le texte si le joueur appuis sur la barre espace et est en collision avec le pnj

    def execute(self, dialog=[]): # fonction qui s'occupe du texte à lire
        if self.reading: # tant qui reste encore du texte
            self.next_text() # passer à l'autre texte quand il est lu
        else:
            self.reading = True
            self.text_index = 0
            self.texts = dialog

    def render(self,screen): # fonction qui affiche la bulle
        if self.reading:
            screen.blit(self.box, (self.X_POSITION,self.Y_POSITION)) # affiche la bulle avec ses coordonnées
            text = self.font.render(self.texts[self.text_index], False, (0,0,0)) # affiche le texte dans la bulle
            screen.blit(text, (self.X_POSITION + 60, self.Y_POSITION + 30)) # affiche la bulle et le texte

    def next_text(self): # fonction pour passer au prochain texte
        self.text_index += 1

        if self.text_index >= len(self.texts): # si il n'y a plus de texte à lire
            self.reading = False # alors arrêter de lire le texte