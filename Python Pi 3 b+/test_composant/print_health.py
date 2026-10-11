from serial import Serial
uart = Serial("/dev/ttyAMA0", 115200, timeout=1)
req = b'\xA5\x52'
uart.write(req)
rep = uart.read(7)
print(rep.hex())
