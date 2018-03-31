import csv
import pickle
import re
import os
import sys
import traceback
import subprocess
ws="G:\\regex" ##workspace
# ws="/home/peipei/ISSTA2018/data/regex/"
rex_path="E:\\Rex"
 
def generateStrings(regex,count,filename):    
    cmd=[rex_path,"/k:"+str(count),"/file:"+filename,"/encoding:ASCII","^"+regex+"$"]
    print("cmd: ",cmd)                        
    try:
        p=subprocess.Popen(cmd)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        if p.returncode>0: ###error not valid regex
            print("could not generate for pattern: ",regex," count: ",count)
            return        
    except subprocess.TimeoutExpired:
        print("time out of generating strings for pattern: ",regex," count: ",count)
        return
    except UnicodeEncodeError:
        print("unicode encode error of generating strings for pattern: ",regex," count: ",count)
        print("Regex String Unicode error:", sys.exc_info()[0])
        traceback.print_exc()
        return
    except:
        print("Error in generate for pattern: ",regex," count: ",count)
        traceback.print_exc()


def getInputs():    
    a=["",56]
    b=["",50]
    a_regex=["\\|DATE\\[([a-zA-Z0-9:\\- /]*)\\]\\|","\\|DATE\\[([a-zA-Z0-9_]*)\\]\\|"]
    b_regex=["\\{(DIRS|DIR|LINKS)(\\[([a-zA-Z0-9_./-]+)\\])?:([a-zA-Z/][a-zA-Z0-9_./-]+)\\}",
             "\\{(DIRS|DIR|FILES)(\\[([a-zA-Z0-9_./-]+)\\])?:([a-zA-Z/][a-zA-Z0-9_./-]+)\\}",
             "\\{(DIRS|DIR)(\\[([a-zA-Z0-9_./-]+)\\])?:([a-zA-Z/][a-zA-Z0-9_./-]+)\\}"]
    
    for k in [100,200,500]:
        count=0
        for regex in a_regex:
            count+=1
            filename=str(a[1])+"_"+str(count)+"_"+str(k)
            generateStrings(regex, k, filename)
            
        count=0
        for regex in b_regex:
            count+=1
            filename=str(b[1])+"_"+str(count)+"_"+str(k)
            generateStrings(regex, k, filename)
                                                       
if __name__== '__main__':
    os.chdir(ws)
    getInputs()
