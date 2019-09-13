#!/usr/bin/env python3
import serial
import time
import struct
class Create:

    def __init__(self,port):
        self.s = serial.Serial(port, 57600)
        self.start()
        self.full_mode()
        self.leds()
        
    def start(self):
        self.s.write(struct.pack("B", 128))

    def safe_mode(self):
        print("Switching to Safe Mode\n")
        self.s.write(struct.pack("B", 131))
        self.leds()

    def full_mode(self):
        print("Switching to Full Mode\n")
        self.s.write(struct.pack("B", 132))
        self.leds()

    #required to charge
    def passive_mode(self):
        print("Switching to Passive Mode\n")
        self.s.write(struct.pack("B", 128))
        self.leds()

    def drive(self, velocity, radius):
        self.s.write(struct.pack(">Bhh", 137, velocity, radius))

    def drive_direct(self, left, right):
        self.s.write(struct.pack(">Bhh", 145, left, right))

    # color 0 = green 255 = red
    # Defaults to just a green power button
    def leds(self, play=0, advance=0, power_color=0, power_brightness=255):
        byte1 = (0x08 if advance else 0x00) | (0x02 if play else 0x00)
        self.s.write(struct.pack("BBBB", 139, byte1, power_color, power_brightness))
    
    # Read Sensors
    def sensor_check(self, packet):
        if(packet in [8,9,10,11,12,13,37]):
            print("This returns a boolean!\n")
            return self.get_bool(packet)
        elif(packet in [1,2,3,4,5,6]):
            print("This might eventually print several packets!\n")
        elif(packet in [7,14,18,34]):
            print("This returns a string of 1's and 0's!\n")
            return self.get_bool_list(packet)
        elif(packet in [19,20,22,23,25,26,27,28,29,30,31,33,39,40,41,42]):
            print("This returns a 2 byte value!\n")
            return self.get_short(packet)
        elif(packet in [17,24,36,38]):
            print("This returns a single byte value!\n")
            return self.get_byte(packet)
        elif(packet in [21,32,35]):
            print("This will return a special value!\n")
        else:
            print("This packet ID is unused!\n")
        
    # Read Boolean
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
    
    # Read Many Booleans
    def get_bool_list(self, packet):
        self.s.write(struct.pack("BB", 142, packet))
        return bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(8)
    
    # Prints packet ID and values of all Create sensors
    def sensor_print_all(self):
        self.s.write(struct.pack("BB", 142, 6))
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
        print("(17) IR: ",struct.unpack('B',self.s.read(1))[0], "\n")
        print("(18) Buttons:\n")
        tmp = bin(struct.unpack('B',self.s.read(1))[0])[2:].zfill(3)
        print("\tAdvance Pressed: ",self.bit_to_bool(tmp[0]),'\n')
        print("\tPlay Pressed: ",self.bit_to_bool(tmp[2]),'\n')
        print("(19) Distance: ",struct.unpack('>h',self.s.read(2))[0], "mm\n")
        print("(20) Angle: ",struct.unpack('>h',self.s.read(2))[0], "mm\n")
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
        
    #used to make sensor check look nicer
    def bit_to_bool(self,val):
        return val == '1'
