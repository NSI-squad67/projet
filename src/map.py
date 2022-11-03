from dataclasses import dataclass # pour faire une classe qui contient des données (donc sans méthodes)
import pygame, pytmx, pyscroll
import time

from player import *

# generation PNJ
class NPC(Entity): # migration dans map.py

    def __init__(self,name,nb_points, dialog):
        super().__init__(name,0,0)
        self.dialog = dialog # contient le dialogue du pnj
        self.nb_points = nb_points # le nombre de points où se déplace le pnj
        self.points = [] # liste les points où est le pnj
        self.current_point = 0 # point sur lequel est actuelement le pnj
        self.target_point = 1 # le point où va se rendre le pnj (changé au cours du porgramme pour faire en sorte que le pnj bouge tt le temps)
        self.name = name # nom du pnj
        self.speed = 1

        if self.name == "boss":
            self.objet = "1er morceau de clé" # l'elfe noir (avec l'identifiant boss) a comme objet le 1er mrceau de clé

        elif self.name == "legolas": # idem mais pour le mec dans la mine mais a comme objet le 2eme morceau
            self.objet = "2eme morceau de clé"



    def move(self): # se déplace par comparaison de coordonnée (différence entre son point actuel et son point final)

        current_point = self.current_point
        target_point = self.target_point

        current_rect = self.points[current_point]
        target_rect = self.points[target_point]

        if current_rect.y < target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_down()

        elif current_rect.y > target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_up()

        elif current_rect.x > target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_left()

        elif current_rect.x < target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_right()

        
        if self.rect.colliderect(target_rect): # si collision avec le point final
            self.target_point, self.current_point = current_point, target_point # redéfinir le prochain point de déplacement

    def teleport_spawn(self): # téléporte le pnj à l'un de ses points (déplacemnts du pnj)
        location = self.points[self.current_point]
        self.position[0] = location.x
        self.position[1] = location.y
        self.save_location()

    def load_points(self, tmx_data):
        for num in range(1, self.nb_points+1): # liste le nombre de poins qu'a le pnj
            point = tmx_data.get_object_by_name(f"{self.name}_path{num}")
            rect = pygame.Rect(point.x, point.y, point.width, point.height)
            self.points.append(rect)


@dataclass
class Portal: # gère la téléportation vers une autre map
    from_world: str
    origin_point: str
    target_world: str
    teleport_point: str

# Initialiser un map
@dataclass # du coup __init__ est initialisé tout seul
class Map:
    name: str # pour importer son nom
    walls: [pygame.Rect] # rectangles des collisions
    group: pyscroll.PyscrollGroup # groupe des calques (image renvoyée à l'user)
    tmx_data: pytmx.TiledMap # données de la map
    portals: [Portal] # liste des portails
    npcs: [NPC] # liste des pnj

class MapManager:
    def __init__(self,screen,player):
        self.maps = dict() # "house" -> Map("house",walls,group)
        self.current_map = "world" # map par défaut
        self.screen = screen
        self.player = player

        self.register_map("world", portals=[
                Portal(from_world="world", origin_point="enter_house", target_world="house", teleport_point="spawn_house"),
                Portal(from_world="world", origin_point="enter_dungeon", target_world="dungeon", teleport_point="spawn_dungeon")
            ], npcs=[
                NPC("boss",nb_points=2, dialog=["Bonjour tu dois être Galaad","Voici le premier morceau de clé","Fait vite, la princesse doit...","être morte de peur","Le prochain morceau de clé se trouve...","... dans les mines du nord"]), # nombre de points du pnj
                NPC("player", nb_points=2, dialog=["Bienvenue au royaume d'Ambhalla Galaad !", "Le roi s'est fait emprisonner sa fille...","...dans l'ambassade d'Anohllah !","Il vous missionne pour libérer sa fille !","Trouve les 2 morceaux de clé éparpillées", "... et libère la princesse !", "Le premier qui te livrera le premier morceau de clé...","... est l'elfe noir situé dans la forêt du sud !","Bonne chance !"])
            ])

        self.register_map("house", portals=[
                Portal(from_world="house",origin_point="exit_house",target_world="world",teleport_point="enter_house_exit")
            ], npcs=[
                NPC("princess", nb_points=2, dialog=["Vous êtes mon héros !","Vous serez grâcement récompensé !"])

            ])

        self.register_map("dungeon", portals=[
                Portal(from_world="dungeon", origin_point="exit_dungeon",target_world="world",teleport_point="dungeon_exit_spawn")
            ],npcs=[

                NPC("legolas",nb_points=2, dialog=["Bonjour Galaad, je vous attendais !","Voici le dernier morceau de clé !","Fait vite avant qu'il ne soit trop tard !"])
            ])

        self.teleport_player("Player")
        self.teleport_npcs() # teleport le npc

    def check_npc_collisions(self,dialog_box):
        for sprite in self.get_group().sprites():
            if sprite.feet.colliderect(self.player.rect) and type(sprite) is NPC:

                if sprite.name == "boss" or sprite.name == "legolas":
                    if sprite.objet not in self.player.sac:
                        self.player.sac.append(sprite.objet)

                dialog_box.execute(sprite.dialog)

    def check_collisions(self): # gérer les collisions
        # portails
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map:
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)

                if self.player.feet.colliderect(rect):


                    if portal.target_world == "dungeon" and self.player.sac == ["1er morceau de clé"]:
                        copy_portal = portal
                        self.current_map = portal.target_world
                        self.teleport_player(copy_portal.teleport_point)
   
                    elif portal.target_world == "house" and self.player.sac == ["1er morceau de clé","2eme morceau de clé"]:
                        copy_portal = portal
                        self.current_map = portal.target_world
                        self.teleport_player(copy_portal.teleport_point)

                    if portal.target_world == "world":
                        copy_portal = portal
                        self.current_map = portal.target_world
                        self.teleport_player(copy_portal.teleport_point)


        for sprite in self.get_group().sprites():

            if type(sprite) is NPC:
                if sprite.feet.colliderect(self.player.rect):
                    sprite.speed = 0
                else:
                    sprite.speed = 1


            if sprite.feet.collidelist(self.get_walls()) > -1: # Si les pieds rentre en collision avec un mur
                sprite.move_back() # faire un pas en arrière




    def teleport_player(self,name): # téléporter le joueur au point de spawn
        point = self.get_object(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location() # enregistrer le point où était le joueur avant le tp

    def register_map(self,name,portals=[], npcs=[]): # map a charger
        tmx_data = pytmx.util_pygame.load_pygame(f"../map/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)

            # regrouper tous les calques créés sur Tiled
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        # On zoom
        map_layer.zoom = 2

            # pas besoin de regenerer le joueur

            # definir une liste qui va stcoker les classes collisions
        walls = []
        for obj in tmx_data.objects:
            if obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=6)
        group.add(self.player)

        # recuperer tout les npcs pour les ajouter au groupe (a afficher)
        for npc in npcs:
            group.add(npc)

        # creer un objet Map
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs)

    def get_map(self): return self.maps[self.current_map] # retourne les éléments de la map en cours

    def get_group(self): return self.get_map().group # retourne le groupe de calques de la map en cours

    def get_walls(self): return self.get_map().walls # retourne les murs (collisions) de la map en cours

    def get_object(self,name): return self.get_map().tmx_data.get_object_by_name(name) # accéder à un objets des données tmx


    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs

            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()


    def draw(self):
        self.get_group().draw(self.screen) # dessine la carte en cours
        self.get_group().center(self.player.rect.center) # centre la vision sur le joueur

    def update(self):
        self.get_group().update()
        self.check_collisions() # les collisions sont vérifiées en permanence


        for npc in self.get_map().npcs:
            npc.move()
            
