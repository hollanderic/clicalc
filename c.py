#!/usr/bin/python

import os
import sys,inspect
import ast
import string
import math,cmath

### Base Class for the operation hooks
#     put most of the boilerplate stuff here so the hook
#     implementations can be short
class cli_hook(object):
    def __init__(self,parent):
        self.parent = parent
        self.args = 2 #default, ini should override otherwise
        self.desc = ""
        self.names = [self.__class__.__name__]
        self.ini()
        pass

    def ini(self):
        pass
    def deg2rad(self,angle):
        # if in radians mode, does nothing, if in degree it will convert
        #  angle (assumed to be in degrees) to radians
        if self.parent.radians:
            return angle
        else:
            return math.radians(angle)

    def exe(self,command_position):
        ##TODO - parse the command string to see if it should operate on
        ##        positions of the stack other than previous to the command
        try:
            value = self.run(self.parent.stack[command_position:])
            for i in range(0,self.args):
                self.parent.stack.pop(command_position+1)
            self.parent.stack[command_position] = value
        except:
            self.parent.statstrings.append("Error in command")
            self.parent.error=True
            self.parent.stack.pop(command_position)
        return command_position
    def __str__(self):
        return self.desc

### Implementation for the operation hooks
class add(cli_hook):
    def ini(self):
        self.names.append("+")
        self.desc="Adds previous two arguments in stack"
    def run(self,args):
        return args[1] + args[2]

class sub(cli_hook):
    def ini(self):
        self.names.append("-")
        self.desc="Subtracts previous two arguments in stack"
    def run(self,args):
        return args[2] - args[1]

class mult(cli_hook):
    def ini(self):
        self.names.append("*")
        self.desc="Multiplies previous two arguments in stack"
    def run(self,args):
        return args[2] * args[1]

class div(cli_hook):
    def ini(self):
        self.names.append("/")
        self.desc="Divides previous two arguments in stack"
    def run(self,args):
        return args[2] / args[1]

class sqr(cli_hook):
    def ini(self):
        self.args=1
        self.desc="Squares previous argument in stack"
    def run(self,args):
        return args[1]**2

class pow(cli_hook):
    def ini(self):
        self.names.append("^")
    def run(self,args):
        return args[2]**args[1]

class sqrt(cli_hook):
    def ini(self):
        self.args=1
        self.desc="Square root of previous argument in stack"
    def run(self,args):
        return args[1]**0.5

class sine(cli_hook):
    def ini(self):
        self.args=1
        self.names.append("sin")
        self.desc="Sine of previous argument in stack"
    def run(self,args):
        if type(args[1])==complex:
            return cmath.sin(args[1])
        else:
            return math.sin(self.deg2rad(args[1]))

class cos(cli_hook):
    def ini(self):
        self.args=1
        self.desc="cosine of previous argument in stack"
    def run(self,args):
        if type(args[1])==complex:
            return cmath.cos(args[1])
        else:
            return math.cos(self.deg2rad(args[1]))

class tan(cli_hook):
    def ini(self):
        self.args=1
        self.desc="tangent of previous argument in stack"
    def run(self,args):
        if type(args[1])==complex:
            return cmath.tan(args[1])
        else:
            return math.tan(self.deg2rad(args[1]))

class delete(cli_hook):
    def ini(self):
        self.names.append("del")
        self.args=0
    def exe(self,command_position):
        self.parent.stack=[]
        return 0



class rpn:
    def __init__(self,fname=None):
        self.stack=[]
        self.hooks=[]
        self.fname = fname
        self.error=False
        self.hex=False
        self.options=""
        self.radians=False
        self.statstrings=[]

        if self.fname:
            stackfd = open(self.fname,"a+")
            stackfd.seek(0)
            data=stackfd.readlines()
            for line in data:
                if string.strip(line):
                    try:
                        value=ast.literal_eval(string.strip(line))
                    except:
                        value=string.strip(line)
                    if type(value) == str:
                        if value[0:4] == "opt:":
                            #print "Options = %s"%value
                            self.options=value.split(":")[1]
                    else:
                        self.stack.insert(0,value)

        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj):
                if (len(obj.__bases__)>0):
                    if obj.__bases__[0].__name__ == "cli_hook":
                        self.hooks.append(obj(self))

    def __str__(self):
        s="Options: %s\n"%self.options
        for i in range(len(self.stack)-1,-1,-1):
            optstr=""
            if self.hex:
                try:
                    if type(self.stack[i])==str:
                        for c in self.stack[i]:
                            optstr=optstr+"%02X "%ord(c)
                    else:
                        optstr="0x%X"%self.stack[i]
                except:
                    optstr="----"
            s= s + "%3d:%040s    %s\n"%(i,str(self.stack[i]),optstr)
        if self.statstrings:
            s=s+"-----------------------"
        for item in self.statstrings:
            s=s+item+"\n"
        return s

    def process(self):  # processes the stack
        position = 0
        while position < len(self.stack):
            command = self.stack[position]
            if type(command) == str:
                command=command.split(":")

                for op in self.hooks:
                    if command[0] in op.names:
                        position = op.exe(position)
                        break

            position=position+1

    def pushargs(self,args):
        for a in args:
            try:
                value=ast.literal_eval(string.strip(a))
            except:
                value=string.strip(a)
            if type(value) == str:
                if value[0:4] == "opt:":
                    self.options=value.split(":")[1]
                else:
                    self.stack.insert(0,value)
            else:
                self.stack.insert(0,value)

    def save(self,fname=None):
        if self.error:
            return(0)       #safety lock - if there was an error in command line, don't overwrite stack
        if self.fname:
            stackfd = open(self.fname,"w+")
            stackfd.write("opt:%s\n"%str(self.options))

            for i in range(len(self.stack)-1,-1,-1):
                stackfd.write("%s\n"%str(self.stack[i]))
            stackfd.close()

##  Commands
##      Commands are responsible for checking for errors, executing,
##          stack reordering, and returning a stack position where processing
##          can continue after command execution.
    def err_handler(self,command_position,message):
        self.statstrings.append(message)
        self.error=True
        self.stack.pop(command_position)
        return command_position

    def drop(self,command_position,args):  #position contains position of this command within stack
        if args:
            try:
                value_position=int(args[0])+1   # add one to account for fact the command is on the stack now
            except:
                value_position=-1
        else:
            value_position=-1
        try:
            if len(self.stack)==1:
                self.stack.pop(command_position)
                return command_position

            if value_position==-1:                        #typical case
                self.stack.pop(0)
                self.stack.pop(0)
                return command_position

            else:
                self.stack.pop(value_position)
                self.stack.pop(command_position)
                return command_position
        except:
            return err_handler(command_position,"Bad drop attempted, ignoring command")

    def copy(self,command_position,args):
        try:
            self.stack[command_position]=self.stack[command_position+1]
            return command_position
        except:
            self.stack.pop(command_position)
            return command_position

    def asin(self,command_position,args):
        try:
            if ((type(self.stack[command_position+1])==complex) or (self.stack[command_position+1]>1)):
                value=cmath.asin(self.stack[command_position+1])
            else:
                value=math.asin(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            return self.err_handler(command_position,"Bad arc sine attempted, ignoring command")

    def acos(self,command_position,args):
        try:
            if ((type(self.stack[command_position+1])==complex) or (self.stack[command_position+1]>1)):
                value=cmath.acos(self.stack[command_position+1])
            else:
                value=math.acos(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            return self.err_handler(command_position,"Bad arc cosine attempted, ignoring command")

    def atan(self,command_position,args):
        try:
            if type(self.stack[command_position+1])==complex:
                value=cmath.atan(self.stack[command_position+1])
            else:
                value=math.atan(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            return self.err_handler(command_position,"Bad arc tangent attempted, ignoring command")

    def hexadec(self,command_position,args):
        try:
            self.hex=True
            self.stack.pop(command_position)
            return command_position
        except:
            return self.err_handler(command_position,"failed hex mode attempted, ignoring command")

    def options(self,command_position,args):
        try:
            self.hex=True
            self.stack.pop(command_position)
            return command_position
        except:
            return self.err_handler(command_position,"failed hex mode attempted, ignoring command")

clicalc = rpn(os.getenv('HOME')+'/.clicalc')

if len(sys.argv)>1:
    clicalc.pushargs(sys.argv[1:])
    clicalc.process()

print clicalc
clicalc.save()

sys.exit(0)

