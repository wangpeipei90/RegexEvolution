'''
Created on Apr 11, 2018

@author: peipei
'''
import os
import csv
import glob
import pickle
import codecs
import platform
from calRex import addAnchors, generateValidStrings, flags_re, testStringRegex
ws_unix="/home/peipei/RepoReaper/videoRegex/v2/"
ws_win="F:\\videoRegex\\v2\\"
infos_file="video.info"

def replaceQuotes(regex):
    if regex[0]=='"' and regex[-1]=='"':
        regex=regex[1:-1]
        regex=regex.replace('""',' ')
    return regex

def getPersonTask(filename):
    res=filename.split("_")
    person,task=int(res[0][3:]),res[1]
    return person,task

def readFile(filename):
    ptask_dict={"time":[],"regex":[],"op":[]}
    with open(filename,mode="r") as personTask:
        reader = csv.reader(personTask,quotechar='"', delimiter=',',quoting=csv.QUOTE_NONE, skipinitialspace=False)
        #reader = csv.reader(personTask,quotechar='"', delimiter=',',quoting=csv.QUOTE_ALL, skipinitialspace=True)
        #reader = csv.reader(personTask,dialect='excel') 
        next(reader, None) ##skip header
        for row in reader:
            print(row)
            time,op=row[0],row[-1]
            regex=''.join(row[1:-1])
            if time!='' and regex!='' and op!='':
                print("time: ",time,"regex: ",regex,"op: ",op)
                print("changed regex: ",replaceQuotes(regex))
                
                ptask_dict["time"].append(time)
                ptask_dict["regex"].append(replaceQuotes(regex))
                if op=="cp":
                    ptask_dict["op"].append(0)
                elif op=="direct":
                    ptask_dict["op"].append(1)
                else:
                    ptask_dict["op"].append(-1)
            elif regex=='' and time!='':
                print("skip empty regex: ",)
#             print()
#     print(ptask_dict["time"])
#     print(ptask_dict["regex"])
#     print(ptask_dict["op"])
    return ptask_dict

def readAllFiles():
    infos=dict()
    lens=[]
    for filename in glob.glob("par*.csv"):
        print("file: ",filename)
    
        person,task=getPersonTask(filename)
        info=readFile(filename)
        
        if task not in infos:
            infos[task]=dict()
        infos[task][person]=info
        lens.append([task,person,len(info['regex'])])
        
    output=open(infos_file,'wb')
    pickle.dump(infos, output,protocol=2)
    output.close()
    
    filename="info.csv"
    with open(filename,'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["task","person","chainLen"])
        wr2.writerows(lens)

def mkDirs(k=100):
    infos=pickle.load(open(infos_file,"rb"))
    
    for task in infos:
        if not os.path.exists(task):
            os.mkdir(task)
        for person in infos[task]:
            p_dir=task+"/"+str(person)
            if not os.path.exists(p_dir):
                os.mkdir(p_dir)
            k_dir=p_dir+"/"+str(k)
            if not os.path.exists(k_dir):
                os.mkdir(k_dir)
             
            
def generateStrings(k=100): 
    infos=pickle.load(open(infos_file,"rb"))
    
    for task in infos:
        print("task: ",task,)
        for person in infos[task]: 
            print("task: ",task,"person: ",person,"k: ",k)
            k_dir=task+"/"+str(person)+"/"+str(k)
            for idx,regex in enumerate(infos[task][person]['regex']):
                filename=k_dir+"/"+str(idx)
                
                regex2=regex
                if r'''\\''' in regex:
                    try:
                        regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
                    except UnicodeEncodeError:
                        pass
                print("task: ",task,"person: ",person,"idx: ",idx,"regex: ",repr(regex.encode("utf-8")))
                print("regex2: ",repr(regex2.encode("utf-8")))
                regex3=addAnchors(regex2, flags_re)
                print("regex3: ",repr(regex3.encode("utf-8")))
                
                strs=generateValidStrings(regex2, regex3, k)
                if strs is None:
                    print("Invalid Regex: ",repr(regex.encode("utf-8"))," task: ",task," person: ",person," idx: ",idx," k: ",k)
                    continue
                elif len(strs)==0:
                    print("Rex no valid strings Regex: ",repr(regex.encode("utf-8"))," task: ",task," person: ",person," idx: ",idx," k: ",k,)
                    continue
                elif len(strs)<k:
                    print("Rex no enough strings Regex: ",repr(regex.encode("utf-8"))," size: ",len(strs)," task: ",task," person: ",person," idx: ",idx," k: ",k,)
                
                output=open(filename,'wb')
                pickle.dump(strs, output,protocol=2)
                output.close()
                                 
                with open(filename+".csv",'w') as resultFile:
                    wr2 = csv.writer(resultFile, dialect='excel')
                    for rexStr in strs:
                        wr2.writerow(list(rexStr))
                           
def calSimilarity(k=100,step=1):
    infos=pickle.load(open(infos_file,"rb"))
    res=dict()
    skipRegex=skipChain=0
    validChain=validChainRegex=0
    validRegex=0
    for task in infos:
        print("task: ",task,)
        if task not in res:
            res[task]=dict()
        for person in infos[task]: 
            print("task: ",task,"person: ",person,"k: ",k)
            
                
            k_dir=task+"/"+str(person)+"/"+str(k)
            
            regex_strs=[]
            for idx,regex in enumerate(infos[task][person]['regex']):
                filename=k_dir+"/"+str(idx)
                
                regex2=regex
                if r'''\\''' in regex:
                    try:
                        regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
                    except UnicodeEncodeError:
                        pass
                print("task: ",task,"person: ",person,"idx: ",idx,"regex: ",repr(regex.encode("utf-8")))
                print("regex2: ",repr(regex2.encode("utf-8")))
                regex3=addAnchors(regex2, flags_re)
                print("regex3: ",repr(regex3.encode("utf-8")))
                
                if os.path.exists(filename) and os.path.getsize(filename)>0:
                    try:
                        strs=pickle.load(open(filename,"rb"))
                        if len(strs)>0:
                            regex_strs.append([regex2,strs])
                            validRegex+=1
                        else:
                            regex_strs.append([regex2,None])
                            skipRegex+=1
                    except:
                        print("Error! could not pickle file: ",filename)
                        regex_strs.append([regex2,None])
                        skipRegex+=1
                else:
                    regex_strs.append([regex2,None])
                    skipRegex+=1
            
            
            n=len(regex_strs)
            if person not in res[task]:
                res[task][person]=[]
             
            pertask=[]   
            for i in range(n-step):
                j=i+step
                if regex_strs[i][1] is None or regex_strs[j][1] is None:
                    continue
                
                new_regex,old_regex=regex_strs[j][0],regex_strs[i][0]            
                union_strs=set(regex_strs[j][1]).union(set(regex_strs[i][1]))
                
                succ_strs=[None,None]
                for idx,regex in enumerate([old_regex,new_regex]):
                    succ_strs[idx]=[]                   
                    for strRex in union_strs:
                        matchRes=testStringRegex(regex,strRex)
                        if matchRes==1:
                            succ_strs[idx].append(strRex)
                overlaps=list(set(succ_strs[0])&set(succ_strs[1]))
                additions=list(set(succ_strs[1])-set(succ_strs[0]))
                reductions=list(set(succ_strs[0])-set(succ_strs[1]))
                ele=[n,j,i,len(additions),len(overlaps),len(reductions),len(succ_strs[1]),len(succ_strs[0]),len(union_strs)]
                pertask.append(ele)  
            
            if len(pertask)>0:      
                res[task][person]=pertask
                validChain+=1
                
                validIDs1=[perRes[1] for perRes in pertask] #new
                validIDs2=[perRes[2] for perRes in pertask] #old
                validIDs=set(validIDs1).union(set(validIDs2))
                validChainRegex+=len(validIDs)                            
                print("validChain Regexes: ",validIDs) 
            else:
                skipChain+=1
                
    print("skipChain: ",skipChain," skipRegex: ",skipRegex," validRegex: ",validRegex," validChain: ",validChain," validChainRegex: ",validChainRegex)
    
    output=open("video_sim_enforce1."+str(k)+"_"+str(step),'wb')
    pickle.dump(res, output, protocol=2)
    output.close()          
    
    with open("video_sim_enforce1_"+str(k)+"_"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","Task","Person","ChainLen","NewRID","OldRID","Addition","Overlap","Reduction","Tnew","Told","Union"])
        idx=0
        for task in res:
            for person in res[task]:                
                idx+=1
                for comp in res[task][person]:
                    temp=[idx,task,person]
                    temp.extend(comp)
                    wr2.writerow(temp) 
                            
if __name__ == '__main__':
    if platform.system()=="Windows":
        os.chdir(ws_win)
    else:
        os.chdir(ws_unix)
        
#     generateStrings(100)
    print("K: 100")    
    calSimilarity(100,1)
    print("K: 200")
    calSimilarity(200,1)
    print("K: 500")
    calSimilarity(500,1)
#     filename="par10_HasSoyIngredient_v2.csv"
#     readFile(filename)
#     filename="par10_ValidEmail_v2.csv"
#     filename="par24_RepeatedWords_v2.csv"
#     print(readFile(filename))
    readAllFiles()
#     mkDirs(500)
    pass
