'''
Created on Apr 15, 2018

@author: peipei
'''
from calRex import encodeList
from videoRegex import infos_file
import subprocess
import csv
import pickle
import codecs
import os
import sys
from itertools import count

ws_repo="/home/peipei/RepoReaper/"
ws_video="/home/peipei/RepoReaper/videoRegex/v2/"

SyntaxTestPath="/home/peipei/workspace/RegexSimilarity/bin:/home/peipei/workspace/RegexSimilarity/commons-text-1.3.jar"
LevenshteinDistanceFile="GetLevenshteinDistance"

def getLevenshteinDistance(regex_new,regex_old):
    cmd=["java", "-cp", SyntaxTestPath, LevenshteinDistanceFile, regex_new,regex_old]
    print("cmd: ",encodeList(cmd))
    try:
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        p.stdout.close()
                        
        if p.returncode>0:
            print("ret:",p.returncode,"new regex :",repr(regex_new.encode("utf-8")),"old regex: ",repr(regex_old.encode("utf-8")))
            return -2
        else:
            stdoutdata=stdoutdata.decode('utf-8')
            distance=int(stdoutdata)
            return distance
    except subprocess.TimeoutExpired:
        print("TimeoutExpired:",p.returncode,"new regex :",repr(regex_new.encode("utf-8")),"old regex: ",repr(regex_old.encode("utf-8")))
        return -2

SyntaxTestPath2="/home/peipei/workspace/RegexSimilarity/bin:/home/peipei/workspace/RegexSimilarity/pcre.jar:/home/peipei/workspace/RegexSimilarity/antlr-runtime-3.5.2.jar";
FeatureCounts="GetFeatureCounts"
def getFeatureCounts(regex):
    cmd=["java", "-cp", SyntaxTestPath2, FeatureCounts, regex]
    print("cmd: ",encodeList(cmd))
    try:
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        p.stdout.close()
        
        print(stdoutdata)              
        if p.returncode>0:
            print("ret:",p.returncode,"regex :",repr(regex.encode("utf-8")))
            return None
        else:
            if stdoutdata==b'invalid regex\n':
                print("invalid regex: ",repr(regex.encode("utf-8")))
                return None
            elif stdoutdata==b'parsing error\n':
                print("parsing error regex: ",repr(regex.encode("utf-8")))
                return None
            
            stdoutdata=stdoutdata.decode('utf-8')
            featureCounts=stdoutdata.strip().split(" ")
            return featureCounts
    except subprocess.TimeoutExpired:
        print("TimeoutExpired:",p.returncode,"regex :",repr(regex.encode("utf-8")))
        return None
    
def calLevenshteinDistanceVideo(step=1):
    skipComp,validComp,totalComp=0,0,0
    res_sim=dict()
    
    infos=pickle.load(open(infos_file,"rb"))
    for task in infos:
        print("task: ",task,)
        if task not in res_sim:
            res_sim[task]=dict()
        for person in infos[task]: 
            print("task: ",task,"person: ",person,"step: ",step)
            
            regex_strs=[]
            for idx,regex in enumerate(infos[task][person]['regex']):                
                regex_strs.append(regex) ###original regex no escape at all
                print("task: ",task,"person: ",person,"idx: ",idx,"regex: ",repr(regex.encode("utf-8")))                
            
            if len(regex_strs)<=step: ##skip if chain length is 1
                    continue  
                          
            n=len(regex_strs)
            res_d=[]                
            totalComp+=(n-step)
            for i in range(n-step):
                j=i+step
                regex_new,regex_old=regex_strs[j],regex_strs[i]
                res=getLevenshteinDistance(regex_new, regex_old)
                if res<0:
                    skipComp+=1
                else:
                    ele=[n,j,i,res,len(regex_new),len(regex_old)]
                    res_d.append(ele)
                    validComp+=1
            res_sim[task][person]=res_d
    
    print("skipComp: ",skipComp," validComp: ",validComp," totalComp: ",totalComp)
    
    output=open("video_syntaxDistance_"+"_"+str(step),'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()          
    
    with open("video_syntaxDistance_"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","Task","Person","ChainLen","NewRID","OldRID","Distance","NewRLen","OldRLen"])
        idx=0
        for task in res_sim:
            for person in res_sim[task]:                
                idx+=1
                for comp in res_sim[task][person]:
                    temp=[idx,task,person]
                    temp.extend(comp)
                    wr2.writerow(temp) 

def calStepsBetweenRegexRepo():
    res_sim=[]
    with open("searched_repos.csv",mode="r") as searchedRepos:
        reader = csv.reader(searchedRepos)        
        for repo in reader:
            page,row=int(repo[0]),int(repo[1])
            repo_path=str(page)+"_"+str(row)
            os.chdir(repo_path)
            
            regex_hist=pickle.load(open("regex.hist",'rb'))
            
            for key,value in regex_hist.items():
                file_name,line_number=key
                regexes=value[0]
                
                if len(regexes)<=1: ##skip if chain length is 1
                    continue                
                               
                n=len(regexes)
                for i in range(n-1,0,-1): ###[1,n-1]
                    for j in range(i-1,-1,-1): ###[0,i-1]
                        if regexes[i]==regexes[j]:
                            count=i-j
                            item=[repo_path,file_name,line_number,i,count]
                            res_sim.append(item)
                            break
                    
            os.chdir("../")
    
    output=open("repo_sameString_count",'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()
    with open("repo_syntaxDistance_count.csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["repo","file","line","RID","count"])
        idx=0
        for item in res_sim:              
            idx+=1
            wr2.writerow(item)
                                  
def calStepsBetweenRegexVideo():
    res_sim=[]
    infos=pickle.load(open(infos_file,"rb"))
    for task in infos:
        print("task: ",task,)
        for person in infos[task]: 
            print("task: ",task,"person: ",person)
            
            regex_strs=[]
            for idx,regex in enumerate(infos[task][person]['regex']):                
                regex_strs.append(regex) ###original regex no escape at all
                print("task: ",task,"person: ",person,"idx: ",idx,"regex: ",repr(regex.encode("utf-8")))                
            
            if len(regex_strs)<=1: ##skip if chain length is 1
                    continue                
                               
            n=len(regex_strs)
            for i in range(n-1): ###[0,n-2]
                for j in range(i+1,n): ##[i+1,n-1]
                    if regex_strs[i]==regex_strs[j]:
                        count=j-i
                        item=[task,person,i,count]
                        res_sim.append(item)
                        break
                    
    
    output=open("video_sameString_count",'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()
    with open("video_syntaxDistance_count.csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["task","person","RID","count"])
        idx=0
        for item in res_sim:              
            idx+=1
            wr2.writerow(item)


def calLevenshteinDistanceRepo(step=1):
    skipComp,validComp,totalComp=0,0,0
    res_sim=dict()
    with open("searched_repos.csv",mode="r") as searchedRepos:
        reader = csv.reader(searchedRepos)        
        for repo in reader:
            page,row=int(repo[0]),int(repo[1])
            repo_path=str(page)+"_"+str(row)
            os.chdir(repo_path)
            
            regex_hist=pickle.load(open("regex.hist",'rb'))
            
            for key,value in regex_hist.items():
                file_name,line_number=key
                regexes=value[0]
                
                if len(regexes)<=step: ##skip if chain length is 1
                    continue
                
#                 escapedRegexes=[]
#                 for regex in regexes:                        
#                     regex2=regex
#                     if r'''\\''' in regex:
#                         try:                            
#                             regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
#                         except UnicodeEncodeError:
#                             pass 
#                     
#                     escapedRegexes.append(regex2)
                
                res_d=[]                
                n=len(regexes)
                totalComp+=(n-step)
                for j in range(n-step):
                    i=j+step
                    regex_new,regex_old=regexes[j],regexes[i]
                    res=getLevenshteinDistance(regex_new, regex_old)
                    if res<0:
                        skipComp+=1
                    else:
                        ele=[n,j,i,res,len(regex_new),len(regex_old)]
                        res_d.append(ele)
                        validComp+=1
                res_sim[(repo_path,file_name,line_number)]=res_d
            os.chdir("../")
    
    print("skipComp: ",skipComp," validComp: ",validComp," totalComp: ",totalComp)  
    
    output=open("repo_syntaxDistance_"+str(step),'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()
    with open("repo_syntaxDistance_"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","repo","file","line","ChainLen","NewRID","OldRID","Distance","NewRLen","OldRLen"])
        idx=0
        for repo,comps in res_sim.items():              
            idx+=1
            for comp in comps:
                temp=[idx]
                temp.extend(list(repo))
                temp.extend(comp)
                wr2.writerow(temp)

def calFeatureCountsRepo():
    skipRegex,validRegex,totalRegex=0,0,0
    res_sim=dict()
    with open("searched_repos.csv",mode="r") as searchedRepos:
        reader = csv.reader(searchedRepos)        
        for repo in reader:
            page,row=int(repo[0]),int(repo[1])
            repo_path=str(page)+"_"+str(row)
#             if repo_path!="951_88":
#                 continue
            os.chdir(repo_path)
            
            regex_hist=pickle.load(open("regex.hist",'rb'))
            
            for key,value in regex_hist.items():
                file_name,line_number=key
                regexes=value[0]
                
                if len(regexes)<=1: ##skip if chain length is 1
                    continue
                
                res_sim[(repo_path,file_name,line_number)]=[]
                totalRegex+=len(regexes)
                for idx,regex in enumerate(regexes):                        
                    regex2=regex
                    if r'''\\''' in regex:
                        try:                            
                            regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
                        except UnicodeEncodeError:
                            pass 
                    print("repo: ",repo_path,"file: ",file_name,"line: ",line_number,"idx: ",idx,"regex: ",repr(regex2.encode("utf-8")))
                    featureCounts=getFeatureCounts(regex2)
                    if featureCounts is None:
                        skipRegex+=1
                    else:
                        validRegex+=1
                    
                    res_sim[(repo_path,file_name,line_number)].append([len(regexes),idx,featureCounts])
                
            os.chdir("../")
    
    print("skipRegex: ",skipRegex," validRegex: ",validRegex," totalRegex: ",totalRegex)  
    
    output=open("repo_features",'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()
    with open("repo_features.csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","repo","file","line","ChainLen","RegexID","Features"])
        idx=0
        for repo,comps in res_sim.items():              
            idx+=1
            for comp in comps:
                temp=[idx]
                temp.extend(list(repo))
                temp.extend(comp[:2])
                if comp[2] is not None:
                    temp.extend(comp[2])
                else:
                    temp.extend([-1]*34)
                wr2.writerow(temp) 

def getvalidFeature(counts):
    dict_count=dict()
    for idx,count in enumerate(counts[2]):
        if int(count)>0:
            dict_count[idx]=int(count)
    return counts[1],dict_count  ## index of regex, and idx_count of features

record_features=[None]*35
def getFeaturDifference(chainLen,j,i,new_dict,old_dict):
    add,remove,change,same=0,0,0,0
    for idx_feature in new_dict:
        if idx_feature not in old_dict:
            add+=1
            record_features[idx_feature][0]+=1
        elif new_dict[idx_feature]==old_dict[idx_feature]:
            same+=1
            record_features[idx_feature][3]+=1
        else:
            change+=1
            record_features[idx_feature][2]+=1
    for idx_feature in old_dict:
        if idx_feature not in new_dict:
            remove+=1
            record_features[idx_feature][1]+=1
    ##add+same+change=len(new)
    ##remove+same+change=len(old)
    return [chainLen,j,i,add,remove,change,same,len(new_dict),len(old_dict)]
                         
def calFeatureDistanceRepo(step=1):
    for i in range(35):
        record_features[i]=[0,0,0,0]
        
    chains,edits,totalRegex=0,0,0
    featureCounts=pickle.load(open("repo_features","rb"))
    feature_sim=dict()
    for chain,counts in featureCounts.items():
        n=len(counts)
        totalRegex+=n
        
        candidates=[]
        for j in range(n-step):
            i=j+step
            if counts[j][2] is None or counts[i][2] is None:
                continue
            new_counts=counts[j]
            old_counts=counts[i]
            new_index,new_dict=getvalidFeature(new_counts)
            old_index,old_dict=getvalidFeature(old_counts)
            candidates.append([new_index,old_index,new_dict,old_dict])
        if len(candidates)==0:
            continue
        edits+=len(candidates)
        chains+=1
        feature_sim[chain]=[]
        for candidate in candidates:
            j,i,new_index,old_index=candidate
            diff=getFeaturDifference(n,j,i,new_index,old_index)
            feature_sim[chain].append(diff)
    
    print("step: ",step,"chains: ",chains," edits: ",edits," totalRegex: ",totalRegex)  
    
    output=open("repo_features.diff"+str(step),'wb')
    pickle.dump(feature_sim, output, protocol=2)
    output.close()
    with open("repo_features_diff"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","repo","file","line","ChainLen","NewRID","OldRID","Add","Remove","Change","Same","NFNew","NFOld"])
        idx=0
        for repo,diffs in feature_sim.items():              
            idx+=1
            for diff in diffs:
                temp=[idx]
                temp.extend(list(repo))
                temp.extend(diff)
                wr2.writerow(temp) 
    
    with open("repo_features_record"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["Feature","Add","Remove","Change","Same"])
        idx=0
        for record in record_features:              
            idx+=1            
            temp=[idx]
            temp.extend(record)
            wr2.writerow(temp) 
def calFeatureCountsVideo():
    skipRegex,validRegex,totalRegex=0,0,0
    res_sim=dict()
    
    infos=pickle.load(open(infos_file,"rb"))
    for task in infos:
        print("task: ",task,)
        if task not in res_sim:
            res_sim[task]=dict()
        for person in infos[task]: 
            print("task: ",task,"person: ",person)
            
            res_sim[task][person]=[]
            n=len(infos[task][person]['regex'])
            totalRegex+=n
            for idx,regex in enumerate(infos[task][person]['regex']):                
                regex2=regex
                if r'''\\''' in regex:
                    try:
                        regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
                    except UnicodeEncodeError:
                        pass
                print("task: ",task,"person: ",person,"idx: ",idx,"regex: ",repr(regex2.encode("utf-8")))    
                featureCounts=getFeatureCounts(regex2)
                if featureCounts is None:
                    skipRegex+=1
                else:
                    validRegex+=1
                    
                res_sim[task][person].append([n,idx,featureCounts])
                
    
    print("skipRegex: ",skipRegex," validRegex: ",validRegex," totalRegex: ",totalRegex)  
    
    output=open("video_features",'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()
    with open("video_features.csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","task","person","ChainLen","RegexID","Features"])
        idx=0
        for task in res_sim:
            for person in res_sim[task]:                
                idx+=1
                for comp in res_sim[task][person]:
                    temp=[idx,task,person]
                    temp.extend(comp[:2])
                    if comp[2] is not None:
                        temp.extend(comp[2])
                    else:
                        temp.extend([-1]*34)
                    wr2.writerow(temp)  

def calFeatureDistanceVideo(step=1):
    for i in range(35):
        record_features[i]=[0,0,0,0]
        
    chains,edits,totalRegex=0,0,0
    featureCounts=pickle.load(open("video_features","rb"))
    feature_sim=dict()
    for task in featureCounts:
        if task not in feature_sim:
            feature_sim[task]=dict()
        for person,counts in featureCounts[task].items():
            chain=(task,person)
            n=len(counts)
            totalRegex+=n
            
            candidates=[]
            for i in range(n-step):
                j=i+step
                if counts[j][2] is None or counts[i][2] is None:
                    continue
                new_counts=counts[j]
                old_counts=counts[i]
                new_index,new_dict=getvalidFeature(new_counts)
                old_index,old_dict=getvalidFeature(old_counts)
                candidates.append([new_index,old_index,new_dict,old_dict])
            if len(candidates)==0:
                continue
            edits+=len(candidates)
            chains+=1
            feature_sim[chain]=[]
            for candidate in candidates:
                j,i,new_index,old_index=candidate
                diff=getFeaturDifference(n,j,i,new_index,old_index)
                feature_sim[chain].append(diff)
    
    print("step: ",step,"chains: ",chains," edits: ",edits," totalRegex: ",totalRegex)  
    
    output=open("video_features.diff"+str(step),'wb')
    pickle.dump(feature_sim, output, protocol=2)
    output.close()
    with open("video_features_diff"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","task","person","ChainLen","NewRID","OldRID","Add","Remove","Change","Same","NFNew","NFOld"])
        idx=0
        for repo,diffs in feature_sim.items():              
            idx+=1
            for diff in diffs:
                temp=[idx]
                temp.extend(list(repo))
                temp.extend(diff)
                wr2.writerow(temp)
    
    with open("video_features_record"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["Feature","Add","Remove","Change","Same"])
        idx=0
        for record in record_features:              
            idx+=1            
            temp=[idx]
            temp.extend(record)
            wr2.writerow(temp)
                                                               
if __name__ == '__main__':
#     type=sys.argv[1]
    type="repo"
    if type=="repo":
        os.chdir(ws_repo)
#         calStepsBetweenRegexRepo()
#         calFeatureCountsRepo()
#         print("step 1")
        calFeatureDistanceRepo(step=1)
#         print("step 2")
#         calFeatureDistanceRepo(step=2)
#         print("step 3")
#         calFeatureDistanceRepo(step=3)
#         calLevenshteinDistanceRepo(step=3)
    elif type=="video":
        os.chdir(ws_video)
#         calStepsBetweenRegexVideo()
#         calFeatureCountsVideo()
#         print("step 1")
        calFeatureDistanceVideo(step=1)
#         print("step 2")
#         calFeatureDistanceVideo(step=2)
#         print("step 3")
#         calFeatureDistanceVideo(step=3)
#         calLevenshteinDistanceVideo(step=3)
    pass
