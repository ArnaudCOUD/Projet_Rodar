import time
from ada_rplidar import RPLidar
from gpiozero import LED
from serial import Serial


# Initialize RPLidar object
uart = Serial("/dev/ttyAMA0", 115200)
print(uart)
lidar = RPLidar(LED(18),uart,timeout=3)
lidar.control_motor(True)
time.sleep(0.3)
lidar.control_motor(False)
print(lidar.health)
lidar.start()

try:
    for new_scan, quality, angle, distance in lidar.iter_measurements():
        print(angle,distance,quality)
finally:
    lidar.stop()
