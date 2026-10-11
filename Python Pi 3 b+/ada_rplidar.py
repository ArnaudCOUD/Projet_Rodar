import struct,time

SYNC_BYTE = b"\xA5"
SYNC_BYTE2 = b"\x5A"

GET_INFO_BYTE = b"\x50"
GET_HEALTH_BYTE = b"\x52"

STOP_BYTE = b"\x25"
RESET_BYTE = b"\x40"

DESCRIPTOR_LEN = 7
INFO_LEN = 20
HEALTH_LEN = 3

INFO_TYPE = 4
HEALTH_TYPE = 6

_HEALTH_STATUSES = {
    0: "Good",
    1: "Warning",
    2: "Error",
}

SCAN_TYPE_NORMAL = 0

_SCAN_TYPES = ({"byte": b"\x20", "response": 129, "size": 5},)

class RPLidarException(Exception):
    """Basic exception class for RPLidar"""

def _process_scan(raw: bytes):
    """Processes input raw data and returns measurement data"""
    new_scan = bool(raw[0] & 0b1)
    inversed_new_scan = bool((raw[0] >> 1) & 0b1)
    if new_scan == inversed_new_scan:
        raise RPLidarException("New scan flags mismatch")
    check_bit = raw[1] & 0b1
    if check_bit != 1:
        raise RPLidarException("Check bit not equal to 1")
    quality = raw[0] >> 2
    angle = ((raw[1] >> 1) + (raw[2] << 7)) / 64.0
    distance = (raw[3] + (raw[4] << 8)) / 4.0
    return new_scan, quality, angle, distance


class RPLidar:

    timeout = 1  #: Serial port timeout
    motor = False  #: Is motor running?
    baudrate = 115200  #: Baudrate for serial port
    scanning = False
    descriptor_size = 0
    scan_type = SCAN_TYPE_NORMAL

    def __init__(self, motor_pin, port,baudrate: int = 115200,timeout: float = 1,logging: bool = False):

        self.motor_pin = motor_pin
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.motor_running = False
        self.logging = logging
        self.motor_value = False

        #self.control_motor(True)

    def control_motor(self, val: bool):
        """Manipulate the motor"""
        if val:
            self.motor_pin.on()
        else:
            self.motor_pin.off()

    def _send_cmd(self, cmd: bytes):
        """Sends `cmd` command to the sensor"""
        req = SYNC_BYTE + cmd
        self.port.write(req)
        print(req.hex())

    def _read_descriptor(self):
        """Reads descriptor packet"""
        descriptor = self.port.read(DESCRIPTOR_LEN)
        print(descriptor.hex())
        if len(descriptor) != DESCRIPTOR_LEN:
            raise RPLidarException("Descriptor length mismatch")
        if not descriptor.startswith(SYNC_BYTE + SYNC_BYTE2):
            if descriptor[1:3] == SYNC_BYTE + SYNC_BYTE2:
                descriptor = descriptor[1:] + self.port.read(1)
            else:
                raise RPLidarException("Incorrect descriptor starting bytes")

        is_single = descriptor[-2] == 0

        return descriptor[2], is_single, descriptor[-1]

    def _read_response(self, dsize: int):
        """Reads response packet with length of `dsize` bytes"""
        data = self.port.read(dsize)
        return data
    def reset_input_buffer(self):
        self.port.reset_input_buffer()

    @property
    def info(self):

        self._send_cmd(GET_INFO_BYTE)
        dsize, is_single, dtype = self._read_descriptor()

        if dsize != INFO_LEN:
            raise RPLidarException("Wrong info reply length")
        if not is_single:
            raise RPLidarException("Not a single response mode")
        if dtype != INFO_TYPE:
            raise RPLidarException("Wrong response data type")

        raw = self._read_response(dsize)
        serialnumber_bytes = struct.unpack("B" * len(raw[4:]), raw[4:])
        serialnumber = "".join(reversed(["%02x" % b for b in serialnumber_bytes]))
        data = {
            "model": raw[0],
            "firmware": (raw[2], raw[1]),
            "hardware": raw[3],
            "serialnumber": serialnumber,
        }
        return data

    @property
    def health(self):

        self._send_cmd(GET_HEALTH_BYTE)
        time.sleep(0.1)
        dsize, is_single, dtype = self._read_descriptor()

        if dsize != HEALTH_LEN:
            raise RPLidarException("Wrong info reply length")
        if not is_single:
            raise RPLidarException("Not a single response mode")
        if dtype != HEALTH_TYPE:
            raise RPLidarException("Wrong response data type")

        raw = self._read_response(dsize)
        status = _HEALTH_STATUSES[raw[0]]
        error_code = (raw[1] << 8) + raw[2]
        return (status, error_code)


    def start(self, scan_type: int = SCAN_TYPE_NORMAL):

        if self.scanning:
            raise RPLidarException("Scanning already running!")
        # Start the scanning process, enable laser diode and the
        # measurement system

        cmd = _SCAN_TYPES[scan_type]["byte"]
        try:
            self._send_cmd(cmd)
        except:
            time.sleep(0.5)
            self._send_cmd(cmd)
        dsize, is_single, dtype = self._read_descriptor()

        if dsize != _SCAN_TYPES[scan_type]["size"]:
            raise RPLidarException("Wrong info reply length")
        if is_single:
            raise RPLidarException("Not a multiple response mode")
        if dtype != _SCAN_TYPES[scan_type]["response"]:
            raise RPLidarException("Wrong response data type")

        self.descriptor_size = dsize
        self.scan_type = scan_type
        self.scanning = True
        print("Start")

    def stop(self):
        """Stops scanning process, disables laser diode and the measurement
        system, moves sensor to the idle state."""
        self._send_cmd(STOP_BYTE)
        time.sleep(0.001)
        self.scanning = False

    def reset(self):
        """Resets sensor core, reverting it to a similar state as it has
        just been powered up."""
        self._send_cmd(RESET_BYTE)
        #ime.sleep(0.002)

    def iter_measurements(self):
        max_buf_meas = 500
        while True:
            dsize = self.descriptor_size
            raw = self._read_response(dsize)
            yield _process_scan(raw)

    def iter_scans(self, max_buf_meas: int = 500, min_len: int = 5):
        """Iterate over scans. Note that consumer must be fast enough,
        otherwise data will be accumulated inside buffer and consumer will get
        data with increasing lag.

        Parameters

        max_buf_meas : int, optional
            Maximum number of measurements to be stored inside the buffer. Once
            number exceeds this limit buffer will be emptied out. Default is
            500.
        min_len : int, optional
            Minimum number of measurements in the scan for it to be yielded.
            Default is 5.

        Yields

        scan : list
            List of the measurements. Each measurement is tuple with following
            format: (quality, angle, distance). For values description please
            refer to `iter_measurements` method's documentation.
        """
        scan = []
        iterator = self.iter_measurements(max_buf_meas)
        for new_scan, quality, angle, distance in iterator:
            if new_scan:
                if len(scan) > min_len:
                    yield scan
                scan = []
            if quality > 0 and distance > 0:
                scan.append((quality, angle, distance))
