from machine import Pin,PWM
class moteur:
    def __init__(self,pin,difference=0,freq=25_000,):
        pin_m = Pin(pin,mode=Pin.OUT)
        self.M = PWM(pin_m)
        self.M.freq(freq)
        self.sens_rotation = 0
        self.vitesse = 0
        self.difference = difference
        self.mouvement(0)
        
    def mouvement(self,vitesse):
        #if not (self.M.duty_u16()==0 and vitesse==0):
        self.M.duty_u16(int(vitesse*(65535-self.difference)))
        

class mouvement:
    def __init__(self,M6,M7,M8,M9,M10,M11,M12,M13):
        self.M6 = M6
        self.M7 = M7
        self.M8 = M8
        self.M9 = M9
        self.M10 = M10
        self.M11 = M11
        self.M12 = M12
        self.M13 = M13
        
    def avant(self, vitesse):
        self.M6.mouvement(vitesse)
        self.M8.mouvement(vitesse)
        self.M12.mouvement(vitesse)
        self.M10.mouvement(vitesse)
        self.M7.mouvement(0)
        self.M9.mouvement(0)
        self.M13.mouvement(0)
        self.M11.mouvement(0)

    def arriere(self, vitesse):
        self.M7.mouvement(vitesse)
        self.M9.mouvement(vitesse)
        self.M13.mouvement(vitesse)
        self.M11.mouvement(vitesse)
        self.M6.mouvement(0)
        self.M8.mouvement(0)
        self.M12.mouvement(0)
        self.M10.mouvement(0)

    def gauche(self, vitesse):
        self.M6.mouvement(vitesse)
        self.M9.mouvement(vitesse)
        self.M13.mouvement(vitesse)
        self.M10.mouvement(vitesse)
        self.M7.mouvement(0)
        self.M8.mouvement(0)
        self.M12.mouvement(0)
        self.M11.mouvement(0)

    def droite(self, vitesse):
        self.M7.mouvement(vitesse)
        self.M8.mouvement(vitesse)
        self.M12.mouvement(vitesse)
        self.M11.mouvement(vitesse)
        self.M6.mouvement(0)
        self.M9.mouvement(0)
        self.M13.mouvement(0)
        self.M10.mouvement(0)

    def rotation_trigo(self, vitesse):
        self.M7.mouvement(vitesse)
        self.M8.mouvement(vitesse)
        self.M13.mouvement(vitesse)
        self.M10.mouvement(vitesse)
        self.M6.mouvement(0)
        self.M9.mouvement(0)
        self.M12.mouvement(0)
        self.M11.mouvement(0)

    def rotation_anti_trigo(self, vitesse):
        self.M6.mouvement(vitesse)
        self.M9.mouvement(vitesse)
        self.M12.mouvement(vitesse)
        self.M11.mouvement(vitesse)
        self.M7.mouvement(0)
        self.M8.mouvement(0)
        self.M13.mouvement(0)
        self.M10.mouvement(0)

    def stop(self):
        self.M6.mouvement(0)
        self.M7.mouvement(0)
        self.M8.mouvement(0)
        self.M9.mouvement(0)
        self.M10.mouvement(0)
        self.M12.mouvement(0)
        self.M11.mouvement(0)
        self.M13.mouvement(0)

if __name__ == '__main__':
    import time
    mv = mouvement(moteur(6),moteur(7),moteur(8),moteur(9),moteur(10),moteur(11),moteur(12),moteur(13))
    mv.avant(0.70)
    time.sleep(3)
    mv.arriere(0.70)
    time.sleep(3)
    mv.stop()
