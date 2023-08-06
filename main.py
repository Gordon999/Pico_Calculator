from machine import Pin,Timer,I2C
import time
from ssd1306 import SSD1306_I2C
import framebuf
import math

# setup the screen
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=200000)
oled = SSD1306_I2C(128, 64, i2c)

# define normal keys
keyName = [['1','2','3','+'],
           ['4','5','6','-'],
           ['7','8','9','*'],
           ['.','0','=','/']]
# define maths function keys, including clear screen (C)
keyFunc = [['log','log10','int' ,'exp' ],
           ['rad','asin' ,'acos','atan'],
           ['deg','sin'  ,'cos' ,'tan' ],
           ['C'  ,'sqrt' ,'^X'  ,'^'   ]]

# setup gpios for buttons
keypadRowPins = [13,12,11,10]
keypadColPins = [9,8,7,6]
row = []
col = []
for i in keypadRowPins:
    row.append(Pin(i,Pin.IN,Pin.PULL_UP))
for i in keypadColPins:
    col.append(Pin(i,Pin.OUT))

# carry out basic function calculations
def solve(oprt, oprdA, oprdB):
    if(oprt == "+"):
        return oprdA + oprdB
    elif(oprt == "-"):
        return oprdA - oprdB
    elif(oprt == "*"):
        return oprdA * oprdB
    elif oprt == "/" and oprdB > 0:
        return round(oprdA / oprdB,6)
    elif(oprt == "^"):
        return round(math.pow(oprdA,oprdB),6)

# read buttons
def keypadRead():
    global row,col,entry0
    key = ''
    held_time = 0
    # scan for pressed button 
    for i in range(0,len(col)):
        col[i].low()
        time.sleep(0.005) #settling time
        for j in range(0,len(row)):
            if row[j].value() == 0:
                # store button pressed
                key = keyName[j][i]
                ki = i
                kj = j
        col[i].high()
    if key != '': # measure button held down time
        start = time.ticks_us()
        col[ki].low()
        time.sleep(0.005)
        while row[kj].value() == 0:
            if int((time.ticks_us() - start)/1000000) > 0: # and entry0 != '':
                # show button held down time
                k = keyFunc[kj][ki]
                oled.fill_rect(0, 56, 128, 64, 0)
                if k == 'C' and time.ticks_us() - start > 3000000:
                    oled.text(" AC" ,1,56,1)
                elif k == '^X' and time.ticks_us() - start > 1000000:
                    oled.text(" ^" + str(int((time.ticks_us() - start)/1000000)),1,56,1)
                else:
                    oled.text(" " + k ,1,56,1)
                oled.show()
        held_time = time.ticks_us() - start
        col[ki].high()
    # clear button time
    oled.fill_rect(0, 56, 128, 64, 0)
    oled.show()
    if held_time > 1000000: # use maths functions instead of basic functions
        key = keyFunc[kj][ki]
    if key != '': # button pressed return with button name and held_time
        return key,held_time
    else: # if no button pressed return with -1
        return -1,0
    
 
# initialise parameters
entry0  = '' # working string
entry   = 1  # set to show stage reached, 1 first number entry, 2 second number entry, 3 output 
entry1  = '' # string for first number
entry2  = '' # string for second number
entry3  = '' # string for third number
nentry0 = 0  # set to 1 to prevent multiple decimal points if a number
result  = '' # string for result

# clear screen and show title
oled.fill(0)
oled.show()
oled.text("Pico Calculator",5,2,1)
oled.show()

#main loop
if __name__ == '__main__':
    while True:
        # read buttons
        key,held_time = keypadRead()
        if key != -1: # if a button has been pressed
            # if reached answer stage then reset to stage 1
            if entry == 4:
                entry   = 1
                nentry0 = 0
                output  = ''
                entry0  = ''
            # maths functions or clear screen when buttons held > 1 second
            if held_time > 1000000:
                try:
                    entry4 = ''
                    if key == 'log':
                        entry4 = str(math.log(float(entry0)))
                    elif key == 'log10':
                        entry4 = str(math.log10(float(entry0)))
                    elif key == 'int':
                        entry4 = str(math.trunc(float(entry0)))
                    elif key == 'rad':
                        entry4 = str(math.radians(float(entry0)))
                    elif key == 'deg':
                        entry4 = str(math.degrees(float(entry0)))
                    elif key == 'sin':
                        entry4 = str(math.sin(float(entry0))) 
                    elif key == 'cos':
                        entry4 = str(math.cos(float(entry0)))
                    elif key == 'tan':
                        entry4 = str(math.tan(float(entry0)))
                    elif key == 'sqrt':
                        entry4 = str(math.sqrt(float(entry0)))
                    elif key == '^X':
                        entry4 = str(math.pow(float(entry0),int(held_time/1000000)))
                    elif key == 'exp':
                        entry4 = str(math.exp(float(entry0)))
                    elif key == 'asin':
                        entry4 = str(math.asin(float(entry0)))
                    elif key == 'acos':
                        entry4 = str(math.acos(float(entry0)))
                    elif key == 'atan':
                        entry4 = str(math.atan(float(entry0)))
                    elif key == 'C':
                        if held_time > 3000000: # clear full screen if > 3 seconds
                            entry   = 1
                            entry0  = ""
                            entry1  = ""
                            entry2  = ""
                            entry3  = ""
                            entry4  = ""
                            nentry0 = 0
                            result  = ""
                            oled.fill(0)
                            oled.show()
                            oled.text("Pico Calculator",5,2,1)
                            oled.show()
                        else: # clear part of screen if > 1 second
                            entry0  = ""
                            nentry0 = 0
                            oled.fill_rect(0, 6 + (entry * 10), 128, 64, 0)
                            oled.show()
                
                  # copy maths function result to entry0
                    if entry4 != '':
                        entry0 = entry4
                        entry4 = ''
                        # don't allow a second decimal point to be added
                        nentry0 = 1
                except:
                    # print error
                    oled.text("Error",1,56,1)
                    oled.show()
                    time.sleep(2)
            
            # add number entry 
            if key <= '9' and key >='0':
                entry0 += key

            
            # add decimal point in a number
            elif key == '.' and held_time < 1000000:
                if entry0 != '' and nentry0 == 0:
                    entry0 += "."
                    # set to stop more than one decimal point
                    nentry0 = 1
            
            # add negative sign before a number
            elif entry0 == '' and key == '=':
                entry0 += "-"
                
            # add basic functions of +, -,*, / or ^
            elif entry0 != '' and (key == '+' or key == '-' or key == '*' or key == '/' or key == '^'):
                if entry == 1:
                    oprt = key
                    entry1 = entry0 # copy latest number entry to entry1
                    entry = 2
                    entry0 = ''
                    nentry0 = 0
                elif entry == 2 :
                    oprt2 = key
                    entry2 = entry0 # copy latest number entry to entry2
                    entry = 3
                    entry0 = ''
                    nentry0 = 0
            
            # show result if only 1 entry and = button pressed
            elif entry == 1 and entry0 != '' and entry0 != '-' and key == '=':
                result = str(entry0)
                # show result
                oled.text("= " + result,1,46,1)
                oled.show()
                # clear variables
                entry  = 4
                entry1 = ""
                entry2 = ""
                nentry0 = 0
            
            # carry out calculations if 2 entries and = button pressed
            elif entry == 2 and entry1 != '' and entry0 != '' and entry0 != '-' and key == '=':
                entry2 = entry0
                oprdA  = float(entry1)
                oprdB  = float(entry2)
                # call solve routine
                result = str(solve(oprt, oprdA, oprdB))
                # show result
                oled.text("= " + result,1,46,1)
                oled.show()
                # clear variables
                entry  = 4
                entry1 = ""
                entry2 = ""
                nentry0 = 0
             
            # carry out calculations if 3 entries and = button pressed
            elif entry == 3 and entry1 != '' and entry2 != '' and entry0 != '' and entry0 != '-' and key == '=':
                entry3 = entry0
                # determine calculations order of preference, eg * before +
                if oprt2 == "^":
                    oprf = 3
                elif oprt == "^":
                    oprf = 2
                elif oprt2 == "*" or oprt2 == "/":
                    oprf = 1
                else:
                    oprf = 0
                # carry out calculations
                if oprf == 2 or oprf == 0:
                    oprdA  = float(entry1)
                    oprdB  = float(entry2)
                    # call solve routine
                    result = str(solve(oprt, oprdA, oprdB))
                    oprdA  = float(result)
                    oprdB  = float(entry3)
                    # call solve routine
                    result = str(solve(oprt2, oprdA, oprdB))
                else:
                    oprdA  = float(entry2)
                    oprdB  = float(entry3)
                    # call solve routine
                    result = str(solve(oprt2, oprdA, oprdB))
                    oprdA  = float(entry1)
                    oprdB  = float(result)
                    # call solve routine
                    result = str(solve(oprt, oprdA, oprdB))
                # show answer
                oled.text("= " + result,1,45,1)
                oled.show()
                # clear variables
                entry  = 4
                entry1 = ""
                entry2 = ""
                entry3 = ""
                
            # display entries
            if entry < 4:
                oled.fill_rect(0, 6 + (entry *10), 128, 64, 0) # clear part of screen               
            if (entry0 != '' or entry1 != '') and entry == 1:    
                if entry0 != '':
                    oled.text("  " + entry0,1,16,1)
                else:
                    oled.text("  " + entry1,1,16,1)
                oled.show()
            elif entry == 2:
                oled.text(oprt + " " + entry0,1,26,1)
                oled.show()
            elif entry == 3:
                oled.text(oprt2 + " " + entry0,1,36,1)
                oled.show()

