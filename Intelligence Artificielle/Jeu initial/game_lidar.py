import pygame,sys,math
from pygame.locals import *
from get_distance import distance
from random import randint,randrange
import numpy as np
import statistics as stat
pygame.init()
mesure_lidar={}
DISPLAYSURF = pygame.display.set_mode((800, 800))
font_small = pygame.font.SysFont("Verdana", 20)
FPS = 60
FramePerSec = pygame.time.Clock()
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


class Robot():
    def __init__(self):
        self.rect = pygame.Rect((396, 395, 9, 11))
        self.image_original = pygame.image.load("joueur/Rectangle_rouge.png")
        self.angle_rotation = 0
        self.angle_variation = 0 #randrange(0,358,2)
        self.nombre_angle = 20
        self.distance_de_securite = 1.6 #en metre
        self.mesure_apres = {}
        self.nombre_victoire = 0

    def mouvement(self,init=False):
        key = pygame.key.get_pressed()
        pas = 3
        global bg_image_x
        global bg_image_y
        angle = math.radians(self.angle_rotation+self.angle_variation)
        if key[K_LEFT]:
            bg_image_x -= -pas*0.75 * math.cos(angle)
            bg_image_y -= pas*0.75 * math.sin(angle)#self.rect = self.rect.move(-pas * math.cos(angle), pas * math.sin(angle))
        elif key[K_RIGHT]:
            bg_image_x -= pas*0.75 * math.cos(angle)
            bg_image_y -= -pas*0.75 * math.sin(angle)#self.rect = self.rect.move(pas * math.cos(angle), -pas * math.sin(angle))
        elif key[K_UP] or init:
            bg_image_x -= -pas * math.sin(angle)
            bg_image_y -= -pas * math.cos(angle)#self.rect = self.rect.move(-pas * math.sin(angle), -pas * math.cos(angle))
        elif key[K_DOWN]:
            bg_image_x -= pas * math.sin(angle)
            bg_image_y -= pas * math.cos(angle)#self.rect = self.rect.move(pas * math.sin(angle), pas * math.cos(angle))
        else :
            Robot.rotate(self)
    def draw(self, DISPLAYSURF):
        rotated_image = pygame.transform.rotate(self.image_original, self.angle_rotation+self.angle_variation)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        DISPLAYSURF.blit(rotated_image, rotated_rect.topleft)
        #pygame.draw.rect(DISPLAYSURF, BLACK, self.rect)

    def lidar(self):
        for i in range(self.nombre_angle):
            mesure_lidar[i*360/self.nombre_angle]=round(distance((400,400), ((i * 360)/self.nombre_angle + self.angle_rotation + 90)%360, DISPLAYSURF),3)
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
    
    def rotate(self):
        key = pygame.key.get_pressed()
        if key[K_a]: #SENS trigo
            self.angle_rotation += 2
        if key[K_e]: #SENS anti-trigo
            self.angle_rotation -= 2
        self.angle_rotation = self.angle_rotation % 360
        

    def angle_print(self):
        return (self.angle_rotation+self.angle_variation)%360

        '''i = list(mesure_lidar.keys())
        index = 0
        while mesure_lidar[i[index]] == 0:
            #print("0")
            index +=1
        print(i[index],mesure_lidar[i[index]])'''
        
        
    def cali(self,mesure_cali):
        for key in mesure_cali.keys():
            mesure_cali[key].append(distance((400,400), key+90, DISPLAYSURF))
        #print(mesure_cali)
        return mesure_cali
        
        

    def mort(self):
        if DISPLAYSURF.get_at((400,400)) == BLACK : 
            print("Mort")
            pygame.quit()
            sys.exit()
            
    def victoire(self):
        if DISPLAYSURF.get_at((400, 400)) == BLUE:
            self.nombre_victoire +=1
            if self.nombre_victoire > 180:
                print("Victoire")
                pygame.quit()
                sys.exit()
        else:
            self.nombre_victoire = 0
            
            
class Carte():
    def __init__(self):
        global bg_image_x,bg_image_y
        self.carte = 'carte_4.png' #MODIFIER LA CARTE ICI
        self.bg_image = pygame.image.load("cartes/"+self.carte)
        
        
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

        
    def impression_carte(self,angle):
        obj = (self.objectif[0]+bg_image_x , self.objectif[1]+bg_image_y)
        DISPLAYSURF.blit(self.bg_image, (bg_image_x, bg_image_y))
        pygame.draw.circle(DISPLAYSURF,BLUE,obj,10)
        pygame.draw.line(DISPLAYSURF, GREEN, (402,402), obj,2)
        temp = (400+100*math.sin(math.radians(angle)) , 400+100*math.cos(math.radians(angle)))
        centre = (400,400)
        self.angle_obj_robot = round(math.degrees(math.acos(sum((centre[i]-temp[i])*(obj[i]-centre[i]) for i in range(len(temp)))/(math.sqrt(sum((centre[i]-temp[i])**2 for i in range(len(temp))))*math.sqrt(sum((obj[i]-centre[i])**2 for i in range(len(temp))))))))
        self.distance_obj_robot = round(math.sqrt((obj[0]-centre[0])**2 + (obj[1]-centre[1])**2) * 12/400,3)
        
    def get_angle_obj_robot(self):
        return self.angle_obj_robot
    
    def get_distance_obj_robot(self):
        return self.distance_obj_robot



def calibrage_robot_lidar():
    mesure_cali = {i:[] for i in range(0,360,2)}
    for i in range(10):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
        DISPLAYSURF.fill(WHITE)
        carte.impression_carte(robot.angle_print())
        angle = font_small.render(str(robot.angle_print()), True, RED)
        DISPLAYSURF.blit(angle, (10,10))
        
        robot.lidar()
        robot.indicateur()    
        robot.draw(DISPLAYSURF)
        robot.mouvement(True)
        pygame.display.update()
        
        carte.impression_carte()
        FramePerSec.tick(FPS)
        mesure_cali = robot.cali(mesure_cali)
    return calcul_angle(mesure_cali)

#angle_de_calibrage = calibrage_robot_lidar()




def game():
    
    while True:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
        DISPLAYSURF.fill(WHITE)
        
        carte.impression_carte(robot.angle_print())
        
        angle = font_small.render(str(robot.angle_print()), True, RED)
        DISPLAYSURF.blit(angle, (10,10))
        
        robot.mouvement()
        robot.mort()
        robot.victoire()
        robot.lidar()
        robot.indicateur()    
        robot.draw(DISPLAYSURF)
    
        pygame.display.update()
        FramePerSec.tick(FPS)
        
robot = Robot()
carte = Carte()
game()