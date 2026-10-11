import time
while True:
    from moteur import *
    mv = mouvement(moteur(6),moteur(7),moteur(8,3500),moteur(9,3500),moteur(10,3500),moteur(11,3500),moteur(12,3500),moteur(13,3500))
    try:
        from communication import communication_ordinateur
        from convert_list import string_to_list
        
        direction={"n":mv.avant,"s":mv.arriere,"o":mv.gauche,"e":mv.droite,"trigo":mv.rotation_trigo,"anti-trigo":mv.rotation_anti_trigo}
        co = communication_ordinateur()
        co.connexion()

        sequence = co.reception()
        sequence = string_to_list(sequence)
        print(sequence)
        
        for etape in sequence:
            reception = co.reception()
            while reception != "_start_instruction":
                if reception == "fin":
                    break
                print("j'attends debut")
                mv.stop()
                reception = co.reception()
                
            print("Start moteur")
            print(etape[0])
            print(etape)
            direction[etape[0]](etape[1])
            
            reception = co.reception()
            while reception != "_stop_instruction":
                if reception == "_arret" or "fin":
                    break
                elif reception == "_ralentir":
                    print("ralentir")
                    direction[etape[0]](0.4)
                reception = co.reception()
            print("Stop moteur")
            #if reception == "_arret" or "fin":
                    #break
        mv.stop()
        print("fin")
        co.envoie("fin")
        time.sleep(1)
        
    except Exception as e:
        print(e)
        time.sleep(1)
