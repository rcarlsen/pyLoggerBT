pyLoggerBT
Robert Carlsen | robertcarlsen.net
NYU Interactive Telecommunication Program | itp.nyu.edu

This is a simple data logger for bluetooth-enabled S60 mobile phones.
 
It's written in python and can either be run as a script in the Python app, 
or can be installed as a self-contained standalone app (bundling the Python runtime).

Get an appropriate version of Python for S60 from:
http://opensource.nokia.com/projects/pythonfors60/

The easiest way to install the script is to send pyLoggerBT.py to the phone
via Bluetooth. If Python for S60 is already on the phone the script will be automatically
installed to the correct location and will be accessible within the Python app.

A standalone version of pyLoggerBT may created from the pyLoggerBT.py file using py2ng or ensymble.
Look in the builds folder to pre-made SIS bundles. Send the appropriate SIS file to your phone
to install the standalone version (if available). At the moment there is a version for
S60 2nd Edition (works with a Nokia 6682 handset).


Note: this software is rudimentary at the moment. I'm using it for basic data logging for
physical computing and wearable experiments. It's been robust enough for me, but no promises :)

While I'd like to make the software flexible enough to work with many possible configurations, I'll
describe the current scenario.

I have an ATMega168 (Arduino) reading several sensors and is connected to a BlueSMIRF module.
It is configured for a call and response protocol over serial. The microcontroller will sent 
one set of readings delimited by spaces (0x20) and terminated with linefeed and carriage 
return (0x0A,0x0D) when it receives an 'a' character over serial. The call character is 
configurable within the Configure menu of pyLoggerBT. The delimiter character is hard coded 
at the moment (although it can easily be changed in the source code). I plan on making this
another configuration option shortly.

Each response is time-stamped and written to a file on the phone's memory card in CSV format.
There is a bug in getting timestamps with millisecond resolution, which I'm actively working 
to resolve. I'm also looking to improve performance with the rate of reading from the hardware.

Usage
Launch pyLoggerBT, then select Options -> Configure. Set the appropriate call character (default: 'a').

Select Options -> Connect... to choose the bluetooth device connected to your sensor hardware.
After a successful connection the program will automatically begin displaying logging data
while simultaneously writing received data to the memory card in CSV format.

Select Option -> Stop Logging to end the logging session and disconnect from the bluetooth device.
This also closes the file and will display the file name.

You can lock the keys and dim the phone screen with the logger still functioning.
This may vary between devices.

That's it for now. Improvements welcome!
-Robert
