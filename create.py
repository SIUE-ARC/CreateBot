#!/usr/bin/env python3
import serial
import time
import struct
class Create:

    # Initializes Serial Connection and starts robot communication
    def __init__(self,port = "/dev/ttyUSB0"):
        self.s = serial.Serial(port, 57600)
        self.start()
        self.full_mode()
        self.leds()
        
    # Required for further commands to be read
    def start(self):
        self.s.write(struct.pack("B", 128))

    # Allows direct control
    # Reverts To Passive Mode when:
    # -Detects Cliff
    # -Detects Wheel Drop
    # -Attempting to Charge
    def safe_mode(self):
        print("Switching to Safe Mode\n")
        self.s.write(struct.pack("B", 131))
        self.leds()

    # Allows direct control
    # Disallows Charging
    def full_mode(self):
        print("Switching to Full Mode\n")
        self.s.write(struct.pack("B", 132))
        self.leds()

    # Allows Sensor Checks & Charging
    # Disallows direct control
    def passive_mode(self):
        print("Switching to Passive Mode\n")
        self.s.write(struct.pack("B", 128))
        self.leds()

    # Control direction and speed
    def drive(self, velocity, radius):
        self.s.write(struct.pack(">Bhh", 137, velocity, radius))

    # Directly control wheel speeds
    def drive_direct(self, left, right):
        self.s.write(struct.pack(">Bhh", 145, left, right))

    # Control LEDs
    # power_color Green(0) - Red(255)
    def leds(self, play=0, advance=0, power_color=0, power_brightness=255):
        byte1 = (0x08 if advance else 0x00) | (0x02 if play else 0x00)
        self.s.write(struct.pack("BBBB", 139, byte1, power_color, power_brightness))
    
    # Read Sensors
    def sensor_check(self, packet):
        if(packet in [8,9,10,11,12,13,37]):
            return self.get_bool(packet)
        # TODO Make this return sensor values instead of just printing them
        elif(packet in [1,2,3,4,5,6]):
            self.sensor_print_group(packet)
        elif(packet in [7,14,18,34]):
            return self.get_bool_list(packet)
        elif(packet in [19,20,22,23,25,26,27,28,29,30,31,33,39,40,41,42]):
            return self.get_short(packet)
        elif(packet in [17,21,24,35,36,38]):
            return self.get_byte(packet)
        elif(packet == 32):
            tmp = self.get_bool_list(packet)
            if(tmp[0]):
                tmp[0] = 57600
            else:
                tmp[0] = 19200
        else:
            print("This packet ID is unused!\n")
        
    # Read Single Boolean
    def get_bool(self, packet):
        self.s.write(struct.pack("BB", 142, packet))
        return struct.unpack('?',self.s.read(1))[0]
    
    # Read Single Byte
    def get_byte(self, packet):
        self.s.write(struct.pack("BB", 142, packet))
        return struct.unpack('B',self.s.read(1))[0]
        
    # Read Multi-byte Value
    def get_short(self, packet):
        self.s.write(struct.pack("BB", 142, packet))
        return struct.unpack('>h',self.s.read(2))[0]
    
    # Read List of Booleans
    def get_bool_list(self, packet):
        self.s.write(struct.pack("BB", 142, packet))
        tmp = bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(5)
        for val in range(len(tmp)):
            tmp[val] = self.bit_to_bool(tmp[val])
        return tmp
    
    # Prints packet ID and values of all Create sensors in a group
    def sensor_print_group(self, packet):
        self.s.write(struct.pack("BB", 142, packet))
        if(packet in [0,1,6]):
            print("(7) Bumps & Drops:\n")
            tmp = bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(5)
            print("\tCaster Dropped: ",self.bit_to_bool(tmp[0]),'\n')
            print("\tLeft Wheel Dropped: ",self.bit_to_bool(tmp[1]),'\n')
            print("\tRight Wheel Dropped: ",self.bit_to_bool(tmp[2]),'\n')
            print("\tLeft Bump: ",self.bit_to_bool(tmp[3]),'\n')
            print("\tRight Bump: ",self.bit_to_bool(tmp[4]),'\n')
            print("(8) Wall Detected: ",struct.unpack('?',self.s.read(1))[0], "\n")
            print("(9) Left Cliff: ",struct.unpack('?',self.s.read(1))[0], "\n")
            print("(10) Left Front Cliff: ",struct.unpack('?',self.s.read(1))[0], "\n")
            print("(11) Right Front Cliff: ",struct.unpack('?',self.s.read(1))[0], "\n")
            print("(12) Right Cliff: ",struct.unpack('?',self.s.read(1))[0], "\n")
            print("(13) Virtual Wall: ",struct.unpack('?',self.s.read(1))[0], "\n")
            print("(14) Overcurrents:\n")
            tmp = bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(5)
            print("\tLeft Wheel: ",self.bit_to_bool(tmp[0]),'\n')
            print("\tRight Wheel: ",self.bit_to_bool(tmp[1]),'\n')
            print("\tLow Side Driver 2: ",self.bit_to_bool(tmp[2]),'\n')
            print("\tLow Side Driver 0: ",self.bit_to_bool(tmp[3]),'\n')
            print("\tLow Side Driver 1: ",self.bit_to_bool(tmp[4]),'\n')
            self.s.read(2)
        if(packet in [0,2,6]):
            print("(17) IR: ",struct.unpack('B',self.s.read(1))[0], "\n")
            print("(18) Buttons:\n")
            tmp = bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(3)
            print("\tAdvance Pressed: ",self.bit_to_bool(tmp[0]),'\n')
            print("\tPlay Pressed: ",self.bit_to_bool(tmp[2]),'\n')
            print("(19) Distance: ",struct.unpack('>h',self.s.read(2))[0], "mm\n")
            print("(20) Angle: ",struct.unpack('>h',self.s.read(2))[0], "mm\n")
        if(packet in [0,3,6]):
            print("(21) Charging State: ")
            tmp = struct.unpack('B',self.s.read(1))[0]
            if(tmp == '5'):
                print("Charging Fault Condition\n")
            elif(tmp == '4'):
                print("Waiting\n")
            elif(tmp == '3'):
                print("Trickle Charging\n")
            elif(tmp == '2'):
                print("Full Charging\n")
            elif(tmp == '1'):
                print("Reconditioning Charging\n")
            else:
                print("Not Charging\n")
            print("(22) Battery Voltage: ",struct.unpack('>h',self.s.read(2))[0], "mV\n")
            print("(23) Current: ",struct.unpack('>h',self.s.read(2))[0], "mA\n")
            print("(24) Battery Temp: ",struct.unpack('B',self.s.read(1))[0], "C\n")
            print("(25) Battery Charge: ",struct.unpack('>h',self.s.read(2))[0], "mAh\n")
            print("(26) Battery Capacity: ",struct.unpack('>h',self.s.read(2))[0], "mAh\n")
        if(packet in [4,6]):
            print("(27) Wall Signal: ",struct.unpack('>h',self.s.read(2))[0], "\n")
            print("(28) Left Cliff Signal: ",struct.unpack('>h',self.s.read(2))[0], "\n")
            print("(29) Left Front Cliff Signal: ",struct.unpack('>h',self.s.read(2))[0], "\n")
            print("(30) Right Front Cliff Signal: ",struct.unpack('>h',self.s.read(2))[0], "\n")
            print("(31) Right Cliff Signal: ",struct.unpack('>h',self.s.read(2))[0], "\n")
            print("(32) User Digital I/O:\n")
            tmp = bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(5)
            if(self.bit_to_bool(tmp[0])):
                print("\tBaud Rate: 57600\n")
            else:
                print("\tBaud Rate: 19200\n")
            print("\tDigital Input 3 (pin 6): ",tmp[1],'\n')
            print("\tDigital Input 2 (pin 18): ",tmp[2],'\n')
            print("\tDigital Input 1 (pin 5): ",tmp[3],'\n')
            print("\tDigital Input 0 (pin 17): ",tmp[4],'\n')
            print("(33) User Analog I/O: ",struct.unpack('>h',self.s.read(2))[0], "\n")
            print("(34) Available Chargers:\n")
            tmp = bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(2)
            print("\tHome Base: ",self.bit_to_bool(tmp[0]),'\n')
            print("\tInternal Charger: ",self.bit_to_bool(tmp[1]),'\n')
        if(packet in [5,6]):
            print("(35) Mode: ")
            tmp = struct.unpack('B',self.s.read(1))[0]
            if(tmp == '3'):
                print("Full Mode\n")
            elif(tmp == '2'):
                print("Safe Mode\n")
            elif(tmp == '1'):
                print("Passive Mode\n")
            elif(tmp == '0'):
                print("Off\n")
            else:
                print(tmp)
            print("(36) Song Selected: ",struct.unpack('B',self.s.read(1))[0], "\n")
            print("(37) Song Playing: ",struct.unpack('?',self.s.read(1))[0], "\n")
            print("(38) Number of Packets: ",struct.unpack('B',self.s.read(1))[0], "\n")
            print("(39) Velocity: ",struct.unpack('>h',self.s.read(2))[0], "mm/s\n")
            print("(40) Radius: ",struct.unpack('>h',self.s.read(2))[0], "mm\n")
            print("(41) Right Velocity: ",struct.unpack('>h',self.s.read(2))[0], "mm/s\n")
            print("(42) Left Velocity: ",struct.unpack('>h',self.s.read(2))[0], "mm/s\n")
        
    # Converts bits read from create into Boolean Values
    def bit_to_bool(self,val):
        return val == '1'
