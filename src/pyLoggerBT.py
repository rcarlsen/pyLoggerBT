######################################################################
##
##    pyLoggerBT
##    Data logger for S60 phones with bluetooth connected devices
##    Robert Carlsen | robertcarlsen.net
##
##    Based off bluetooth connection examples from Nokia
##
##    Initially written in service of course work at 
##    NYU's Interactive Telecommunications Program (ITP) | itp.nyu.edu
##
##    This program is released under the BSD License, or something.
##
######################################################################

SYMBIAN_UID = 0x0fffffff

import socket
# imort appuifw and the e32 modules
import appuifw, e32, time

# Run this once when your program starts
CLOCK_OFFSET = int(round(time.time())) - int(round(time.clock()))

# Call this to return UNIX timestamp to nearest millisecond
def getTime():
    return time.clock() + CLOCK_OFFSET

# hack for the milliseconds
lastTime = getTime()

# set the poll rate:
timer = e32.Ao_timer()

# for padding the millis numbers:
def ljust(s,l,c):
    return(s+c*l)[:l]

# set up some variables:
callChar = u"a"
delimiter = u" "

connectionDescription = u""

# a simple class for accessing the bluetooth stack:
class BTReader:
    def connect(self):
        self.sock = socket.socket(socket.AF_BT, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        address, services = socket.bt_discover()
        global connectionDescription
        connectionDescription = u"Discovered: %s, %s" % (address, services) + u'\n\r'
        log_panel.set(connectionDescription)
        target = (address, services.values()[0])
        connectionDescription += u"Connecting to " + str(target)+ u'\n\r'
        log_panel.set(connectionDescription)
        self.sock.connect(target)
        
        

    def readposition(self):    
        try:
            # set up a call and response:
            # TODO: set up a user preference for this character
            self.sock.send(callChar)

            while 1:
                ch = self.sock.recv(1)
                buffer = ch
                # TODO: this assumes a message line delimiter of 0x10. make this a user preference
                while(ch != '\n'):
                    ch = self.sock.recv(1)
                    buffer += ch
                return buffer
        except:
            return None
        
    def close(self):
        self.sock.close()

        
# set up the global objects:
bt = BTReader()      
datadir = None
file = None
      
def init():
    if(logging==0):
        # define the directory and file name to write the file into
        filetimestamp = time.strftime(u"%d_%b_%Y_%H%M%S")
        global datadir
        datadir = u'e:/Python/Data/' + filetimestamp + u'.csv'
        global file
        file = open(datadir, 'a+')

        bt.connect()
        
        #read the first to bits of data to clear out the headers
        print bt.readposition()
        print bt.readposition()
        
        global logging
        logging = 1
        
        # drop into the main loop:
        main()
    else:
        appuifw.note(u"Already logging.", "info")


# flag to prevent the program from reading the radio when closing
closing = 0
logging = 0

# here is the main application  
def main():
    if(closing!=1 & logging == 1):     
            #read the current data:
            data = bt.readposition()
            
            if(data != None):
                #get the timestamp:
                # the microseconds keep returning 0 on the phone
                # microseconds = str(time.time()).split('.')[1]
                # timeStamp = time.strftime("%a, %d %b %Y %H:%M:%S") +'.' + microseconds
                
                # getTime returns: 1226521341.98437
                # we only want the three most significant digits of the decimal
                
                timeSeconds = getTime()
                timeStamp = time.strftime(u"%d/%b/%Y %H:%M:%S",time.gmtime(timeSeconds))
                microsecond = str(timeSeconds).split('.')[1]
                timeStamp += u'.' + ljust(microsecond,3,'0') #padding/trimming the microsecond time
                
                # there is still weirdness in the time...time() and clock() are not in sync
#                global lastTime
#                currentTime = getTime()
#                millisDelta = (currentTime - lastTime)%1000
#                lastTime = currentTime
#                       
#                timeStamp += u'.'+ str(millisDelta)
                    
                #format the output string:
                #split the incoming data into an array and then format for CSV
                global delimiter
                fields = data.strip().split(delimiter)
                output = u",".join(fields)
                out = u'\"' + timeStamp + u'\"' + u',' + output + u'\n'
                
                #print to the screen:
                global connectionDescription
                log_panel.set(connectionDescription + u'\n\r' + out)
#                log_panel.add(out)
                
                # write the data to the file
                file.write(out)
                
                # yield needs to be here e.g. in order that key pressings can be noticed
                e32.ao_yield()
                #delay then repeat:
                #e32.ao_sleep(0.25, main)
            
                #recursively call the main loop
                #timer.after(0.25, main)
                timer.after(0.1, main)
    

# create the "callback functions" for the application menu
def info():
    appuifw.note(u"Bluetooth data logger. Saves time-stamped data to memory card", "info")

def stopLogging():
    if(logging==1):
        global logging
        logging=0 
          
        timer.cancel()
        
        # close the file
        file.close()
        
        #indicate "status"
        log_panel.add(u"Data file: " + datadir + u'\n')
        
        #close the bluetooth device:
        bt.close() 
        
        appuifw.note(u"Logging stopped", "info")
    else:
        appuifw.note(u"Not logging. Start logging with Connect...", "info")

def options():
    # creating a pop-up menu for options
    L = [u"Set callChar", u"Other options..."]
    test = appuifw.popup_menu(L, u"Options")

    if test == 0 :
        global callChar
        callChar = appuifw.query(u"Set callChar char", "text", callChar) 
    elif test == 1 :
        appuifw.note(u"Other options will go here.", "info")

    
# define an exit handler function
def quit():
    global closing
    closing = 1

    if(logging==1):
        stopLogging()

    #quit:
    app_lock.signal()
    appuifw.app.set_exit()


# create the application menu include the selectable options (one, two)
# and the related callback functions (item1, item2) 
appuifw.app.menu = [(u"Connect...",init),
                    (u"Stop Logging",stopLogging),
                    (u"Configure...",options),
                    (u"Info", info)]

appuifw.app.exit_key_handler = quit
appuifw.app.title = u'Data Logger'

log_panel = appuifw.Text()
log_panel.set(u"PyData Logger.\n\rRobert Carlsen\n\rrcarlsen@nyu.edu\n\r\n\r*'Connect...' from Options menu*\n\r")

# put the application screen size to full screen
#appuifw.app.screen='full' #(a full screen)

# other options:
appuifw.app.screen='normal' #(a normal screen with title pane and softkeys)
#appuifw.app.screen='large' #(only softkeys visible)

appuifw.app.body = log_panel

# create an active object
app_lock = e32.Ao_lock()
app_lock.wait()