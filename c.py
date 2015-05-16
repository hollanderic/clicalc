#!/usr/bin/python

import os
import sys
import ast
import string


def printstack(stack):
    for i in range(0,len(stack)):
        print "%d%020s"%(len(stack)-i-1,str(stack[i]))

def pushargs(args,stack):

    for a in args:
        stack.append(ast.literal_eval(string.strip(a)))

stackfd = open(os.getenv('HOME')+'/.clicalc',"rw+")
stack=[]
# Load the stack state from file
data=stackfd.readlines()
for line in data:
    if string.strip(line):
        stack.append(ast.literal_eval(string.strip(line)))



if len(sys.argv)==1:
    printstack(stack)
    sys.exit(0)
else:

    pushargs(sys.argv[1:],stack)
    printstack(stack)
    sys.exit(0)

#    vals = sys.argv[1:]
#    for x in vals:
#        stack=stack + x.split(',')

    for y in stack:
        print str(type(y))+'--'+str(y)
#    stackfd.seek(0,2)
#    print 'writing '+sys.argv[1]
#    stackfd.write(sys.argv[1])

stackfd.close()




