#!/usr/bin/python

import os
import sys
import ast
import string

class rpn:
    def __init__(self,fname=None):
        self.stack=[]
        self.fname = fname
        self.error=False
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
                    self.stack.insert(0,value)

        self.commands= {    "drop":self.drop   ,   "add":self.add  , "sub":self.sub    ,   "mult":self.mult    ,
                            "div":self.div }
                    
    def __str__(self):
        s=""
        for i in range(len(self.stack)-1,-1,-1):
            s= s + "%3d%030s\n"%(i,str(self.stack[i]))
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
                if command in self.commands.keys():
                    position=self.commands[command](position)
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

            for i in range(len(self.stack)-1,-1,-1):
                stackfd.write("%s\n"%str(self.stack[i]))



            stackfd.close()
            
##  Commands
##      Commands are responsible for checking for errors, executing, stack reordering, and
##          returning a stack position where processing can continue after command execution.

    def drop(self,command_position=0,value_position=-1):  #position contains position of this command within stack
        if len(self.stack)==1:
            self.stack.pop(command_position)
            return command_position

        if value_position == command_position:
            self.stack.pop(command_position)            #Handle case of user explicitly dropping the drop
            return command_position
        
        elif value_position==-1:                        #typical case
            self.stack.pop(0)
            self.stack.pop(0)
            return command_position
        
        else:
            self.stack.pop(value_position)
            self.stack.pop(command_position)
            return command_position

    def add(self,command_position):
        try:
            value=self.stack[command_position+1] + self.stack[command_position+2]
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value    
            return command_position
        except:
            self.statstrings.append("Bad additition attempted, dropping command")
            self.error=True
            self.stack.pop(command_position)
            return command_position
        pass
    
 
    def sub(self,command_position):
        try:
            value=self.stack[command_position+2] - self.stack[command_position+1]
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value    
            return command_position
        except:
            self.statstrings.append("Bad subtraction attempted, dropping command")
            self.error=True
            self.stack.pop(command_position)
            return command_position
        pass
 
    def mult(self,command_position):
        try:
            value=self.stack[command_position+1] * self.stack[command_position+2]
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value    
            return command_position
        except:
            self.statstrings.append("Bad multiplication attempted, dropping command")
            self.error=True
            self.stack.pop(command_position)
            return command_position
        pass

    def div(self,command_position):
        try:
            value=self.stack[command_position+2] / float(self.stack[command_position+1])
            self.stack.pop(command_position+1)
            self.stack.pop(command_position+1)
            self.stack[command_position]=value    
            return command_position
        except:
            self.statstrings.append("Bad division attempted, dropping command")
            self.error=True
            self.stack.pop(command_position)
            return command_position
        pass
  
    

clicalc = rpn(os.getenv('HOME')+'/.clicalc')

if len(sys.argv)>1:
    clicalc.pushargs(sys.argv[1:])

    clicalc.process()



print clicalc
clicalc.save()




sys.exit(0)

