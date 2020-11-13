from numpy import random
from kivy.logger import Logger

# A very crude simulator for PySerial assuming it
# is emulating an Arduino.


# a Serial class emulator

class Serial:

    ## init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    def __init__( self, port='COM1', baudrate = 19200, timeout=1,
                  bytesize = 8, parity = 'N', stopbits = 1, xonxoff=0,
                  rtscts = 0):
        self.port     = port
        self.timeout  = timeout
        self.parity   = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self._isOpen  = True
        self._receivedData = ""
        self._data = "start\n"

        if self.port == "COM3":
            self.name = "F1"
        elif self.port == "COM4":
            self.name = "F2"
        elif self.port == "COM5":
            self.name = "F3"

    ## isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def isOpen( self ):
        return self._isOpen

    ## open()
    # opens the port
    def open( self ):
        self._isOpen = True

    def mkdata(self):
        x = str(random.randint(100))
        return self.name + "\nti" + x + "\nTe" + x + "\nDO" + x + "\nPH" + x + "\n"

    ## close()
    # closes the port
    def close( self ):
        self._isOpen = False

    ## write()
    # writes a string of characters to the Arduino
    def write( self, string ):
        Logger.info('Arduino ' + self.name + ': Got: "' + string.decode() + '"' )
        self._receivedData += string.decode()

    ## read()
    # reads n characters from the fake Arduino. Actually n characters
    # are read from the string _data and returned to the caller.
    def read( self, n=1 ):
        s = self._data[0:n]
        self._data = self._data[n:]
        #print( "read: now self._data = ", self._data )
        return s

    ## readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):
        returnIndex = self._data.index( "\n" )
        self._data += self.mkdata()

        if returnIndex != -1:
            s = self._data[0:returnIndex+1]
            self._data = self._data[returnIndex+1:]
            return s.encode()
        else:
            return ""

    ## __str__()
    # returns a string representation of the serial class
    def __str__( self ):
        return  "Serial<id=0xa81c10, open=%s>( port='%s', baudrate=%d," \
               % ( str(self.isOpen), self.port, self.baudrate ) \
               + " bytesize=%d, parity='%s', stopbits=%d, xonxoff=%d, rtscts=%d)"\
               % ( self.bytesize, self.parity, self.stopbits, self.xonxoff,
                   self.rtscts )
