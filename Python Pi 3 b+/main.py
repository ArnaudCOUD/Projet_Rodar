from communication import communication_ordinateur
from ada_rplidar import RPLidar
from gpiozero import LED
from serial import Serial
from string_to_list import string_to_list
from envoie_donnee_lidar import *
uart = Serial("/dev/ttyAMA0", 115200)
lidar = RPLidar(LED(18),uart,timeout=3)
co = communication_ordinateur()
co.connexion()
#lidar.stop()
lidar.start()
lidar.control_motor(True)
def carte(lidar=lidar):
    #lidar.start()
    donnee=selection(lidar)
    co.envoie(donnee)
    dernier_angle = float(co.reception())
    print(dernier_angle)
    while True:
        print(dernier_angle,next(reversed(donnee)))
        if dernier_angle != next(reversed(donnee)):
            co.envoie(couper_dictionnaire(donnee,dernier_angle))
        else:
            print("ok")
            co.envoie("ok")
            break
    lidar.stop()
def scan_rotation(liste_angle,lidar=lidar,ecart=0.5):
    #lidar.start()
    points_ref={}
    for angle in liste_angle:
        points_ref[angle]=0
    temps = time.time()
    liste_angle_ini = liste_angle.copy()
    while len(liste_angle_ini)>0 and temps + 3 > time.time():
        for new_scan,quality,angle,distance in lidar.iter_measurements():
            if quality>0 and distance > 0:
                if angle>357:
                    angle=angle-360
                for ele_liste_angle in liste_angle_ini:
                    #print(angle-ecart,ele_liste_angle)
                    if angle>ele_liste_angle-ecart and angle<ele_liste_angle+ecart:
                        points_ref[(ele_liste_angle-rotation)%360]=distance
                        liste_angle_ini.remove(ele_liste_angle)
                        if len(liste_angle) < 2:
                            break
            break
    for ele in liste_angle_ini:
        del points_ref[ele]
    lidar.stop()
    lidar.reset_input_buffer()
    lidar.start()
    time.sleep(0.5)
    points={}
    list_angle_mesure=[]
    #for angle in liste_angle:
        #if angle not in liste_angle_ini:

def difference_angle(scan_initial,scan,liste_angle):
    diff={}
    for angle in liste_angle:
        try:
            diff[angle]=scan_initial[angle]-scan[angle]
        except:
            pass
    return diff

def mouvement(lidar=lidar):
    ecart=0.5
    distance_securite = 50
    direction = {"n":[0-ecart,0+ecart],"ne":[45-ecart,45+ecart],"e":[90-ecart,90+ecart],"se":[135-ecart,135+ecart],"s":[180-ecart,180+ecart],"so":[225-ecart,225+ecart],"o":[270-ecart,270+ecart],"no":[315-ecart,315+ecart]}
    sequence=string_to_list(co.reception())
    print(f'sequence : {sequence}')
    for instruction in sequence:
        ralentir = False
        if instruction[0] == "trigo" or instruction[0]=="anti-trigo":
            nbr_points_ref = 12
            liste_angle = [(i*360)/nbr_points_ref for i in range(nbr_points_ref)]
            print(liste_angle)
            scan_init=scan_rotation(liste_angle.copy(),initialisation=True)
            print(scan_init)
            #co.envoie("moteur_start_instruction")
            time.sleep(10)
            scan=scan_rotation(liste_angle.copy(),180)
            print(scan)
            print(difference_angle(scan_init,scan,liste_angle))





        else:
            #lidar.start()
            distance_initiale_mesure = None
            nombre_tour = 20

            while nombre_tour > 0 and distance_initiale_mesure == None:
                for new_scan,quality,angle,distance in lidar.iter_measurements():
                    if quality>0 and distance != 0.0:
                        if angle>357:
                            angle=angle-360
                        if angle>356.5:
                            nombre_tour -= 1
                            print(f'nombre de tour : {nombre_tour}')
                        if angle>direction.get(instruction[0])[0] and angle <direction.get(instruction[0])[1]:
                            distance_initiale_mesure=distance
                            print(f'distance initiale : {distance_initiale_mesure}')
                            break

            if distance_initiale_mesure != None:
                co.envoie("moteur_start_instruction")
                print("Moteur start")
                distance_mesure = distance_initiale_mesure
                """if distance_mesure < instruction[1]+distance_securite:
                    print("Initialisation trop proche d'un mur")
                    co.envoie("moteur_arret")
                    print("Moteur stop")
                    return"""
                while distance_mesure > distance_initiale_mesure - instruction[1]:
                    for new_scan,quality,angle,distance in lidar.iter_measurements():
                        if quality>0 and distance != 0.0:
                            """if distance_mesure < distance_securite:
                                print(f"{distance_mesure} Trop proche d'un mur à {angle} degré")
                                co.envoie("moteur_arret")
                                print("Moteur stop")
                                return"""
                            if angle > 357:
                                angle = angle - 360
                            if angle>direction.get(instruction[0])[0] and angle < direction.get(instruction[0])[1]:
                                distance_mesure = distance
                                print(distance_mesure - distance_initiale_mesure +instruction[1] )
                                co.envoie(distance_mesure - distance_initiale_mesure + instruction[1])
                            if not ralentir :
                                if 125 > distance_mesure - distance_initiale_mesure + instruction[1]:
                                    co.envoie("moteur_ralentir")
                                    ralentir = True
                        break
                co.envoie("moteur_stop_instruction")
                #time.sleep(0.1)
                print("Moteur stop")
try:
    while True:
        reception = co.reception()
        if reception == "carte":
            carte()
        if reception == "mouvement":
            mouvement()
        if reception == "fin":
            break
finally:
    co.envoie("moteur_stop_instruction")
    co.envoie("fin")
