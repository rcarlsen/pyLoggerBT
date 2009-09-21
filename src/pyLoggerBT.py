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
lastTime = time.clock()

# set the poll rate:
timer = e32.Ao_timer()

# for padding the millis numbers:
def ljust(s,l,c):
    return(s+c*l)[:l]

# a simple class for accessing the bluetooth stack:
class BTReader:
    def connect(self):
        self.sock = socket.socket(socket.AF_BT, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        address, services = socket.bt_discover()
        log_panel.add(u"Discovered: %s, %s" % (address, services) + u'\n\r')
        target = (address, services.values()[0])
        log_panel.add(u"Connecting to " + str(target)+ u'\n\r')
        self.sock.connect(target)

    def readposition(self):    
        try:
            # set up a call and response:
            self.sock.send('A')

            while 1:
                buffer = ""
                ch = self.sock.recv(1)
                while(ch != '\r'):
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
                
                
                timeStamp = time.strftime(u"%d/%b/%Y %H:%M:%S")
                
                # there is still weirdness in the time...time() and clock() arn not in sync
    #            currentTime = time.clock()
    #            global lastTime
    #            millis = currentTime - lastTime
    #            lastTime = currentTime
    #            millis = str(millis).split('.')[1]
    #            millis = ljust(millis,3,'0')
    #                   
    #            timeStamp += u'.'+ millis
    
                #format the output string:
                out = u'\"' + timeStamp + u'\"' + u',' + data.strip() + u'\n'
                
                #print to the screen:
                log_panel.add(out)
                
                # write the data to the file
                file.write(out)
                
                # yield needs to be here e.g. in order that key pressings can be noticed
                e32.ao_yield()
                #delay then repeat:
                #e32.ao_sleep(0.25, main)
            
                #recursively call the main loop
                timer.after(0.25, main)
    

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