#!/usr/bin/python

import os
import sys
import ast
import string
import math,cmath

class rpn:
    def __init__(self,fname=None):
        self.stack=[]
        self.fname = fname
        self.error=False
        self.hex=False
        self.options=""
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
                            self.options=value
                    else:
                        self.stack.insert(0,value)

        self.commands= {    "drop":self.drop,   "add":self.add,
                            "sub":self.sub,     "mult":self.mult,
                            "div":self.div,     "sqrt":self.sqrt,
                            "sqr":self.sqr,     "copy":self.copy,
                            "sin":self.sin,     "cos":self.cos,
                            "tan":self.tan,     "asin":self.asin,
                            "acos":self.acos,   "atan":self.atan,
                            "hex":self.hexadec, "+":self.add,
                        }

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
            #print "%d   %s"%(position,str(command))
            if type(command) == str:
                command=command.split(":")
                if command[0] in self.commands.keys():
                    position=self.commands[command[0]](position,command[1:])
                else:
                    position = position + 1
            else:
                position=position+1

    def pushargs(self,args):
        for a in args:
            try:
                value=ast.literal_eval(string.strip(a))
            except:
                value=string.strip(a)
            self.stack.insert(0,value)

    def save(self,fname=None):
        if self.error:
            return(0)       #safety lock - if there was an error in command line, don't overwrite stack
        if self.fname:
            stackfd = open(self.fname,"w+")
            stackfd.write("%s\n"%str(self.options))

            for i in range(len(self.stack)-1,-1,-1):
                stackfd.write("%s\n"%str(self.stack[i]))
            stackfd.close()

##  Commands
##      Commands are responsible for checking for errors, executing,
##          stack reordering, and returning a stack position where processing
##          can continue after command execution.

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
            self.statstrings.append("Bad drop attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def add(self,command_position,args):
        try:
            value=self.stack[command_position+1] + self.stack[command_position+2]
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad additition attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def sub(self,command_position,args):
        try:
            value=self.stack[command_position+2] - self.stack[command_position+1]
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad subtraction attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def mult(self,command_position,args):
        try:
            value=self.stack[command_position+1] * self.stack[command_position+2]
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad multiplication attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def div(self,command_position,args):
        try:
            value=self.stack[command_position+2] / float(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad division attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def sqrt(self,command_position,args):
        try:
            if type(self.stack[command_position+1])==complex:
                value=cmath.sqrt(self.stack[command_position+1])
            else:
                value=math.sqrt(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad square root attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def sqr(self,command_position,args):
        try:
            value=(self.stack[command_position+1])**2
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad square attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def copy(self,command_position,args):
        try:
            self.stack[command_position]=self.stack[command_position+1]
            return command_position
        except:
            self.stack.pop(command_position)
            return command_position

    def sin(self,command_position,args):
        try:
            if type(self.stack[command_position+1])==complex:
                value=cmath.sin(self.stack[command_position+1])
            else:
                value=math.sin(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad sine attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def cos(self,command_position,args):
        try:
            if type(self.stack[command_position+1])==complex:
                value=cmath.cos(self.stack[command_position+1])
            else:
                value=math.cos(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad cosine attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

    def tan(self,command_position,args):
        try:
            if type(self.stack[command_position+1])==complex:
                value=cmath.tan(self.stack[command_position+1])
            else:
                value=math.tan(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack[command_position]=value
            return command_position
        except:
            self.statstrings.append("Bad tangent attempted, ignoring command")
            self.error=True
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
            self.statstrings.append("Bad arc sine attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

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
            self.statstrings.append("Bad arc cosine attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position

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
            self.statstrings.append("Bad arc tangent attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position
    def hexadec(self,command_position,args):
        try:
            self.hex=True
            self.stack.pop(command_position)
            return command_position
        except:
            self.statstrings.append("failed hex mode attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position
    def options(self,command_position,args):
        try:
            self.hex=True
            self.stack.pop(command_position)
            return command_position
        except:
            self.statstrings.append("failed hex mode attempted, ignoring command")
            self.error=True
            self.stack.pop(command_position)
            return command_position
clicalc = rpn(os.getenv('HOME')+'/.clicalc')

if len(sys.argv)>1:
    clicalc.pushargs(sys.argv[1:])
    clicalc.process()

print clicalc
clicalc.save()

sys.exit(0)

