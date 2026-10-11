from communication import communication_robot
import ast
import time
import lidar_to_grid_map
cr=communication_robot()

def repartion(sequence_mouvement):
    pour_lidar = []
    pour_moteur = []
    for instruction in sequence_mouvement:
        if instruction[0]=="mouvement":
            pour_moteur.append([instruction[1][0],instruction[1][2]])
            pour_lidar.append(instruction[1])
        if instruction[0]=="rotation":
            pour_moteur.append([instruction[1][0],instruction[1][2]])
            pour_lidar.append(instruction[1])
    return (pour_lidar,pour_moteur)

def imprimer_carte():
    cr.envoie_lidar("carte")
    try:
        donnee=cr.reception_lidar()
        donnee=ast.literal_eval(donnee)
    except SyntaxError:
        donnee_supp = cr.reception_lidar()
        donnee = donnee + donnee_supp
        donnee = ast.literal_eval(donnee)
    while cr.reception_lidar(0.5) != "ok":
        cr.envoie_lidar(next(reversed(donnee)))
        renvoie = cr.reception_lidar(0.5)
        if renvoie == "ok":
            break
        else:
            donnee = donnee | renvoie
    lidar_to_grid_map.main(donnee)
# Séquence des directions
def mouvement(sequence_mouvement):
    cr.envoie_lidar("mouvement")
    pour_lidar,pour_moteur = repartion(sequence_mouvement)
    cr.envoie_lidar(pour_lidar)
    time.sleep(0.05)
    cr.envoie_moteur(pour_moteur)
    print(pour_moteur)


def main(sequence_mouvement):
    
    try:
        cr.connexion()
        #["mouvement",["n",1000,0.75]],
        #["mouvement",["s",500,1]],
        #["mouvement",["s",500,0.5]],
        #imprimer_carte()
        #time.sleep(3)
        mouvement(sequence_mouvement)
        imprimer_carte()
        while True:
            if cr.reception_lidar(0.1)=="fin":
                break
            
    finally:
        cr.envoie_lidar("fin")
        cr.envoie_moteur("fin")
        time.sleep(1)
        cr.shutdown()
        
        
        
sequence_mouvement=[
    ["mouvement",["n",1000,0.75]],
    ["mouvement",["s",500,1]],
    ["mouvement",["s",500,0.6]]
    ]
main(sequence_mouvement)