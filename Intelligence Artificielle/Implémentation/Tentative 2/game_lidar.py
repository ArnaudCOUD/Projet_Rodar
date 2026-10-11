import pygame,sys,math
from pygame.locals import *
from get_distance import get_distance
from random import randint,randrange
from time import time
import numpy as np
import statistics as stat

pygame.init()
mesure_lidar={}
DISPLAYSURF = pygame.display.set_mode((800, 800))
font_small = pygame.font.SysFont("Verdana", 20)
VITESSE = 60
bg_image_x = 0
bg_image_y = 0
# Def Couleurs
BLUE = (0, 0, 255,255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0,255)
WHITE = (255, 255, 255)



def calcul_angle(mesure_cali):
    divt = {}
    for j in range(0,360,2):
        #print(mesure_cali[j])
        ecarts = [abs(mesure_cali[j][i+1] - mesure_cali[j][i]) for i in range(len(mesure_cali[j])-1)]

        if all(ecart == 0 for ecart in ecarts):
            score_regularite = 2
            divt[j]=score_regularite
            continue

        variance_ecarts = sum((ecart - sum(ecarts) / len(ecarts)) ** 2 for ecart in ecarts) / len(ecarts)

        score_regularite = 1 - (variance_ecarts / max(ecarts))
        #if score_regularite>0.998 and stat.variance(mesure_cali[j])<0.075 :
        divt[j]=(score_regularite,stat.variance(mesure_cali[j]))
    print(divt)
    print(list(divt.keys()))
    print(stat.mean(list(divt.keys())))


class RobotAI():
    def __init__(self):
        self.rect = pygame.Rect((396, 395, 9, 11))
        self.image_original = pygame.image.load("joueur/Rectangle_rouge.png")
        self.nombre_angle = 8
        self.angle_rotation = 270
        self.distance_de_securite = 0.6 #en metre
        self.nombre_victoire = 0
        self.reset()
        self.clock = pygame.time.Clock()
        self.frame_iteration = 0
        self.distance_initiale = None
        self.derniere_distance_obj = 0
        self.dernier_angle_obj = 0

    def reset(self):
        self.angle_variation = 0 #randrange(0,358,1)
        self.temps_debut_jeu = time()
        carte.reset_carte()
        carte.impression_carte(self.angle_print())
        self.angle_rotation = 270
        self.frame_iteration = 0
        self.distance_initiale = carte.get_distance_obj_robot()
        #self.moyenne_distance_obj = []
        self.record = 99


    def deroulement(self,action):

        if self.distance_initiale == None:
                self.distance_initiale = carte.get_distance_obj_robot()
                self.record = round(self.distance_initiale)

        DISPLAYSURF.fill(WHITE)

        self.frame_iteration +=1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # mouvement
        self.mouvement(action)

        distance_obj_robot = carte.get_distance_obj_robot()
        #self.moyenne_distance_obj.append(distance_obj_robot)
        #if len(self.moyenne_distance_obj) > 100 :
            #self.moyenne_distance_obj.pop(0)
        # affichage
        carte.impression_carte(self.angle_print())
        # mort
        self.reward = 0
        game_over = False

        if DISPLAYSURF.get_at((400,400)) == BLACK or time() > self.temps_debut_jeu + 20:
            game_over = True
            self.reward = -100
            return self.reward, game_over, self.distance_initiale, distance_obj_robot

        # victoire
        if distance_obj_robot == 0.0:
            self.nombre_victoire +=1
            if self.nombre_victoire >= 120:
                game_over = True
                print("Victoire")
                self.reward = 500
                return self.reward, game_over, self.distance_initiale, 0.0

            # recompense d'etre sur l'objectif
            self.reward = 1
            #return reward, game_over, self.distance_initiale, carte.get_distance_obj_robot()
        else:
            self.nombre_victoire = 0

        # Autre reward

        if np.array_equal(action,[0, 0, 0, 0, 1, 0]) or np.array_equal(action,[0, 0, 0, 0, 0, 1]) or np.array_equal(action,[0, 0, 0, 1, 0, 0]):
            self.reward -= 1

        """try :
            old_moyenne = moyenne
            moyenne = stat.mean(self.moyenne_distance_obj)
            if old_moyenne == moyenne :
                reward -= 10
        except:
            moyenne = stat.mean(self.moyenne_distance_obj)

        if distance_obj_robot < moyenne :
            reward += 2
        else :
            reward -= 1

        """

        """if carte.get_angle_obj_robot() < 5:
            self.reward += 5"""

        if self.record > round(carte.get_distance_obj_robot()):
            self.record = round(carte.get_distance_obj_robot())
            print(self.record)
            self.reward += 5
        elif self.record+1 < round(carte.get_distance_obj_robot()):
            self.reward -=3

        self.ui()
        return self.reward, game_over,  self.distance_initiale, distance_obj_robot

    def ui(self):
        self.draw_robot()
        self.lidar()
        self.indicateur()
        pygame.display.flip()
        self.clock.tick(VITESSE)


    def mouvement(self,action,init=False):
        key = pygame.key.get_pressed()
        pas = 3
        global bg_image_x
        global bg_image_y
        angle = math.radians(self.angle_rotation+self.angle_variation)
        if np.array_equal(action,[0, 0, 0, 0, 1, 0]):
            bg_image_x -= -pas*0.6 * math.cos(angle)
            bg_image_y -= pas*0.6 * math.sin(angle)#self.rect = self.rect.move(-pas * math.cos(angle), pas * math.sin(angle))
        elif np.array_equal(action,[0, 0, 0, 0, 0, 1]):
            bg_image_x -= pas*0.6 * math.cos(angle)
            bg_image_y -= -pas*0.6 * math.sin(angle)#self.rect = self.rect.move(pas * math.cos(angle), -pas * math.sin(angle))
        elif np.array_equal(action,[0, 0, 1, 0, 0, 0]) or init:
            bg_image_x -= -pas * math.sin(angle)
            bg_image_y -= -pas * math.cos(angle)#self.rect = self.rect.move(-pas * math.sin(angle), -pas * math.cos(angle))
        elif np.array_equal(action,[0, 0, 0, 1, 0, 0]):
            bg_image_x -= pas * math.sin(angle)
            bg_image_y -= pas * math.cos(angle)#self.rect = self.rect.move(pas * math.sin(angle), pas * math.cos(angle)

        elif np.array_equal(action,[1, 0, 0, 0, 0, 0]): #SENS trigo
            self.angle_rotation += 1
        elif np.array_equal(action,[0, 1, 0, 0, 0, 0]): #SENS anti-trigo
            self.angle_rotation -= 1
        self.angle_rotation = self.angle_rotation % 360



    def draw_robot(self):
        rotated_image = pygame.transform.rotate(self.image_original, self.angle_rotation+self.angle_variation)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        DISPLAYSURF.blit(rotated_image, rotated_rect.topleft)
        #pygame.draw.rect(DISPLAYSURF, BLACK, self.rect)

    def lidar(self):
        for i in range(self.nombre_angle):
            mesure_lidar[i*360/self.nombre_angle]=round(get_distance((400,400), ((i * 360)/self.nombre_angle + self.angle_rotation + 90)%360, DISPLAYSURF),3)
            #print(list(mesure_lidar.values())[0])

    def indicateur(self):
        danger = []
        for angle,distance in mesure_lidar.items():
            #print(angle)
            angle = math.radians(angle+self.angle_rotation+90)
            danger_temp = int(distance < self.distance_de_securite and distance !=0)
            danger.append(danger_temp)
            pygame.draw.arc(DISPLAYSURF,(RED if danger_temp else GREEN),pygame.Rect(720,0,80,80),angle,angle+math.radians(360/self.nombre_angle),width=4)
        return danger

    def sur_objectif(self):
        return carte.get_distance_obj_robot(True)

    def angle_print(self):
        return (self.angle_rotation+self.angle_variation)%360


    def cali(self,mesure_cali):
        for key in mesure_cali.keys():
            mesure_cali[key].append(get_distance((400,400), key+90, DISPLAYSURF))
        #print(mesure_cali)
        return mesure_cali



class Carte():
    def __init__(self):
        self.carte = 'carte_2.png'
        self.bg_image = pygame.image.load("cartes/"+self.carte)
        self.reset_carte()

    def reset_carte(self):
        global bg_image_x,bg_image_y
        if self.carte == 'carte_2.png':
            # Initialisation emplacement Robot
            bg_image_x = randint(70,350)
            bg_image_y = randint(-15,65)
            # Initialisation Objectif
            self.objectif =(randint(540,750),randint(330,410))


        elif self.carte == 'carte_3.png':
            cote = randint(0,1)
            if cote:
                # Initialisation emplacement Robot
                bg_image_x = randint(180,320)
                bg_image_y = randint(-5,115)
                # Initialisation Objectif
                self.objectif = (randint(540,650),randint(540,640))
            else :
                # Initialisation emplacement Robot
                bg_image_x = randint(-250,-140)
                bg_image_y = randint(-230,-90)
                # Initialisation Objectif
                self.objectif = (240,410)#(randint(80,240),randint(280,410))


        elif self.carte == 'carte_4.png':
            cote = randint(0,1)
            if cote:
                # Initialisation emplacement Robot
                bg_image_x = randint(160,260)
                bg_image_y = randint(-260,-120)
                # Initialisation Objectif
                self.objectif = (randint(290,420),randint(550,650))
            else :
                # Initialisation emplacement Robot
                bg_image_x = randint(-20,100)
                bg_image_y = randint(-270,-170)
                # Initialisation Objectif
                self.objectif = (randint(135,240),randint(510,670))


        elif self.carte == 'carte_1.png':
            # Initialisation emplacement Robot
            bg_image_x = randint(70,350)
            bg_image_y = randint(-15,65)
            # Initialisation Objectif
            self.objectif =(randint(540,750),randint(330,410))


        elif self.carte == 'carte_care.png':
            # Initialisation emplacement Robot
            bg_image_x = 0
            bg_image_y = 0
            # Initialisation Objectif
            self.objectif =(0,0)


    def impression_carte(self , angle):
        obj = (self.objectif[0]+bg_image_x , self.objectif[1]+bg_image_y)
        DISPLAYSURF.blit(self.bg_image, (bg_image_x, bg_image_y))
        pygame.draw.circle(DISPLAYSURF,BLUE,obj,10)

        temp = (400+100*math.sin(math.radians(angle)) , 400+100*math.cos(math.radians(angle)))
        centre = (400,400)
        self.angle_obj_robot = round(math.degrees(math.acos(sum((centre[i]-temp[i])*(obj[i]-centre[i]) for i in range(len(temp)))/(math.sqrt(sum((centre[i]-temp[i])**2 for i in range(len(temp))))*math.sqrt(sum((obj[i]-centre[i])**2 for i in range(len(temp))))))))
        self.distance_obj_robot = round(math.sqrt((obj[0]-centre[0])**2 + (obj[1]-centre[1])**2) * 12/400,3)
        if self.distance_obj_robot >0.75:
            pygame.draw.line(DISPLAYSURF, GREEN, (402,402), obj,2)

    def get_angle_obj_robot(self):
        angle = robot.angle_print()
        obj = (self.objectif[0]+bg_image_x , self.objectif[1]+bg_image_y)
        temp = (400+100*math.sin(math.radians(angle)) , 400+100*math.cos(math.radians(angle)))
        centre = (400,400)

        self.angle_obj_robot = round(math.degrees(math.acos(sum((centre[i]-temp[i])*(obj[i]-centre[i]) for i in range(len(temp)))/(math.sqrt(sum((centre[i]-temp[i])**2 for i in range(len(temp))))*math.sqrt(sum((obj[i]-centre[i])**2 for i in range(len(temp))))))))


        return self.angle_obj_robot

    def get_distance_obj_robot(self,bool_=False):
        try:
            angle = robot.angle_print()
        except:
            angle = 0

        obj = (self.objectif[0]+bg_image_x , self.objectif[1]+bg_image_y)
        temp = (400+100*math.sin(math.radians(angle)) , 400+100*math.cos(math.radians(angle)))
        centre = (400,400)

        self.distance_obj_robot = round(math.sqrt((obj[0]-centre[0])**2 + (obj[1]-centre[1])**2) * 12/400,3)

        if self.distance_obj_robot > 0.2:
            if bool_:
                return False
            else :
                return self.distance_obj_robot
        else:
            if bool_:
                return True
            else:
                return 0.0

#angle_de_calibrage = calibrage_robot_lidar()


carte = Carte()
robot = RobotAI()

