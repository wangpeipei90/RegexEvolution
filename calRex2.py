import csv
import hashlib
import os
import pickle
import re
import subprocess
from sys import stdout
import sys
import time
import traceback
import codecs
import platform


ws_win="F:\\" ##workspace
ws_unix="/home/peipei/RepoReaper/"
rex_path="E:\\Rex"

java_path_win="C:\\Java\\jre1.8.161\\bin\\java"
java_path_unix="java"
cp_path="F:\\"
test_file="TestStringMatch"

def encodeList(cmd):
    return [x.encode("utf-8") for x in cmd]
def validateRegex(regex):
    cmd=[java_path,"-cp",cp_path,test_file,regex]
#     cmd=["java","-cp",ws,test_file,regex]
    print("cmd: ",repr(encodeList(cmd)))
    try:
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        if p.returncode>0: ###error not valid regex
            print("could not validate for pattern: ",repr(regex.encode("utf-8")))
            return -1  
        stdoutdata=stdoutdata.strip()
        print(stdoutdata)
        if stdoutdata==b"valid regex":
            return 1
        else:
            return 0   
    except subprocess.TimeoutExpired:
        print("time out of validating pattern: ",repr(regex.encode("utf-8")))
        return -1
    except UnicodeEncodeError:
        print("unicode encode error of validating pattern: ",repr(regex.encode("utf-8")))
        print("Regex String Unicode error:", sys.exc_info()[0])
        traceback.print_exc()
        return -1
    except:
        print("Error in validating for pattern: ",repr(regex.encode("utf-8")))
        traceback.print_exc()
        return -1

def testStringRegex(regex,str):
    cmd=[java_path,"-cp",cp_path,test_file,regex,str]
#     cmd=[b"C:\\Java\\jre1.8.161\\bin\\java",b"TestStringMatch",regex.encode("utf-8"),str]
#     cmd=[java_path,'''-cp .''',test_file,regex,str]
#     print("cmd: ",repr(encodeList(cmd)))
    try:
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        if p.returncode>0: ###error not valid regex
            print("could not test for pattern: ",repr(regex.encode("utf-8")), "and str: ",repr(str.encode("utf-8")))
            return -1  
        stdoutdata=stdoutdata.strip()
#         print(stdoutdata)
        if stdoutdata==b"valid regex: true":
            return 1
        elif stdoutdata==b"valid regex: false":
            return 0
        else:
            return -1
    except subprocess.TimeoutExpired:
        print("time out of validating pattern: ",repr(regex.encode("utf-8")), "and str: ",repr(str.encode("utf-8")))
        return -1
    except UnicodeEncodeError:
        print("unicode encode error of validating pattern: ",repr(regex.encode("utf-8")), "and str: ",repr(str.encode("utf-8")))
        print("Regex String Unicode error:", sys.exc_info()[0])
        traceback.print_exc()
        return -1
    except:
        print("Error in validating for pattern: ",repr(regex.encode("utf-8")), "and str: ",repr(str.encode("utf-8")))
        traceback.print_exc()
        return -1

def generateStrings2(regex,count,seed):
    cmd=[rex_path,"/k:"+str(count),"/seed:"+str(seed),"/encoding:ASCII",regex]
    print("cmd: ",repr(encodeList(cmd)))                        
    try:
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        if p.returncode>0: ###error not valid regex
            print("could not generate for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
            print(stderrdata)
            print(stdoutdata)
            return -1  
         
        print(stdoutdata)
        stdoutdata=stdoutdata.strip().decode("utf-8").splitlines()
        print(stdoutdata)
        return stdoutdata
            
    except subprocess.TimeoutExpired:
        print("time out of generating strings for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
        return -1
    except UnicodeEncodeError:
        print("unicode encode error of generating strings for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
        print("Regex String Unicode error:", sys.exc_info()[0])
        traceback.print_exc()
        return -1
    except:
        print("Error in generate for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
        traceback.print_exc()
        return -1

def generateValidStrings(regex,regex_rex,count): ##regex type byte
    if validateRegex(regex)!=1:
#         print("invalid regex")
        return None
    
    valid_strs=list()
    for tries in range(5): 
        if len(valid_strs)>=count:
            break
        
        seed=int(time.time())
        strs=generateStrings2(regex_rex, count-len(valid_strs),seed)
        if strs is None or strs==-1:
            continue
        
        for str in strs:
            str=str[1:-1]
            if str not in valid_strs and testStringRegex(regex, str)==1:
                valid_strs.append(str)
                if len(valid_strs)>=count:
                    break
    return valid_strs
                
        
def generateStrings(regex,count,filename):    
    cmd=[rex_path,"/k:"+str(count),"/file:"+filename,"/encoding:ASCII",regex]
    print("cmd: ",repr(repr(encodeList(cmd))))                        
    try:
        p=subprocess.Popen(cmd)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        if p.returncode>0: ###error not valid regex
            print("could not generate for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
            return        
    except subprocess.TimeoutExpired:
        print("time out of generating strings for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
        return
    except UnicodeEncodeError:
        print("unicode encode error of generating strings for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
        print("Regex String Unicode error:", sys.exc_info()[0])
        traceback.print_exc()
        return
    except:
        print("Error in generate for pattern: ",repr(regex.encode("utf-8"))," count: ",count)
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

flags_re=re.compile("(\(\?(?!.{0,2}(.).{0,2}\\2)[imsU]{1,4}\))(.*)",re.DOTALL)
def addAnchors(regexStr,flags_re):
    flags=None
    ##remove start ^
    if len(regexStr)>0 and regexStr[0]=='^':
        regexStr=regexStr[1:]
    ###start with flags:
    if len(regexStr)>4 and regexStr[0]=="(":
        res=flags_re.match(regexStr)
        if res:
            flags,regexStr=res.group(1),res.group(3)
    ###add ^
    if len(regexStr)>0 and regexStr[0]!='^':
        regexStr='^'+regexStr
    ## add $
    if len(regexStr)>0 and regexStr[-1]!='$':
        regexStr=regexStr+'$'
    ###add falgs
    if flags is not None:
        regexStr=flags+regexStr
#     regexStr=regexStr.encode('utf-8')  ##print not utf8 cause unicode error
#     regexStr=regexStr.decode("utf-8")    
    return regexStr

def getHash(file_name):
    return hashlib.md5(file_name.encode()).hexdigest()

def readGenRegex(k, enforce=False):
    ### read searched_repos.csv to get all valid repos
    with open("searched_repos.csv",mode="r") as searchedRepos:
        reader = csv.reader(searchedRepos)        
        for repo in reader:
            page,row=int(repo[0]),int(repo[1])
            repo_path=str(page)+"_"+str(row)
            
#             if repo_path!="3128_406" and repo_path!="3020_282":
# #                 print(repo_path)
#                 continue
            print(repo_path)
            ### load committed regex
            os.chdir(repo_path)
            regex_hist=pickle.load(open("regex.hist",'rb'))
            
                        
            if not os.path.exists(str(k)):
                os.mkdir(str(k))
#             else:
#                 fileList = os.listdir(str(k))
#                 for fileName in fileList:
#                     os.remove(str(k)+"/"+fileName)            
            
            os.chdir(str(k))
            for key,value in regex_hist.items():
                file_name,line_number=key
#                 if file_name!="src/main/java/com/rarchives/ripme/ripper/rippers/EHentaiRipper.java" or int(line_number)!=82:
#                     print(file_name,line_number)
#                     continue
                    
                regexes=value[0]
                if len(regexes)>1:
                    for idx,regex in enumerate(regexes):
                        if enforce:
                            filename=repo_path+"_"+str(getHash(file_name))+"_"+line_number+"."+str(idx)
                        else:                            
                            filename=repo_path+"_"+str(getHash(file_name))+"_"+line_number+"_"+str(idx)
                        
                        print("repo: ",repo_path," k: ",k," file: ",file_name," line: ",line_number," idx: ",idx, "genstr: ",filename)
                        
                        regex2=regex
                        if r'''\\''' in regex:
                            try:
                                regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
                            except UnicodeEncodeError:
                                pass
                        
                        print("regex2: ",repr(regex2.encode("utf-8")))
                        regex3=addAnchors(regex2, flags_re)
                        print("regex3: ",repr(regex3.encode("utf-8")))
                        
                        if not enforce:
                            generateStrings(regex3, k,filename)
                        else:                            
                            strs=generateValidStrings(regex2, regex3, k)
                            if strs is None:
                                print("Invalid Regex: ",repr(regex.encode("utf-8"))," repo: ",repo_path," k: ",k," file: ",file_name," line: ",line_number," idx: ",idx, "genstr: ",filename)
                                continue
                            elif len(strs)==0:
                                print("Rex no valid strings Regex: ",repr(regex.encode("utf-8"))," repo: ",repo_path," k: ",k," file: ",file_name," line: ",line_number," idx: ",idx, "genstr: ",filename)
                                continue
                            elif len(strs)<k:
                                print("Rex no enough strings Regex: ",repr(regex.encode("utf-8"))," size: ",len(strs)," repo: ",repo_path," k: ",k," file: ",file_name," line: ",line_number," idx: ",idx, "genstr: ",filename)
                            output=open(filename,'wb')
                            pickle.dump(strs, output,protocol=2)
                            output.close()
                             
                            filename=repo_path+"_"+str(getHash(file_name))+"_"+line_number+"_"+str(idx)+".csv"
                            with open(filename,'w') as resultFile:
                                wr2 = csv.writer(resultFile, dialect='excel')
                                for info in strs:
                                    wr2.writerow(list(info))
                        
            os.chdir("../..")                                     

SemanticTestPath="/home/peipei/workspace/RegexSimilarity/bin"
SemanticTestFile="TestSimilarity"


def getEnforcedMatchResults(regexes,files):
    clean_strs=[]
    clean_regexes=[]
    enforcedRes=[]
    for idx,file in enumerate(files):
            try:
                res=pickle.load(open(file,"rb"))
                if len(res)>0:
                    clean_strs.append(res)
                    clean_regexes.append(regexes[idx])
            except:
                print("Error! could not pickle file: ",file)
                continue
                
                
    if len(clean_regexes)<2:
        return enforcedRes
    
    print("clean length: ",len(clean_regexes))
    for i,regex in enumerate(clean_regexes):
        ele=[i,regex]
        for j,strs in enumerate(clean_strs):
            succ=fail=err=0
            for str in strs:
                matchRes=testStringRegex(regex,str)
                if matchRes==1:
                    succ+=1
                elif matchRes==0:
                    fail+=1
                else:
                    err+=1
            ele.extend([succ,fail,err])
        print(ele)        
        enforcedRes.append(ele)       
    return enforcedRes  

def getEnforcedSimilarityRegex(k,enforce=True):
    skipRegex=skipChain=0
    validChain=validChainRegex=0
    validRegex=0
    
    res_sim=dict()
    with open("searched_repos.csv",mode="r") as searchedRepos:
        reader = csv.reader(searchedRepos)        
        for repo in reader:
            page,row=int(repo[0]),int(repo[1])
            repo_path=str(page)+"_"+str(row)
            
#             if repo_path!="3017_466":
#                 continue
            ### load committed regex
            os.chdir(repo_path)    
            
            regex_hist=pickle.load(open("regex.hist",'rb'))
            os.chdir(str(k))
            for key,value in regex_hist.items():
                file_name,line_number=key
                regexes=value[0]
                
                if len(regexes)<=1: ##skip if chain length is 1
                    continue
                
                p_regex=list()
                p_files=list()
                print("repo path: ",repo_path," file: ",file_name," line: ",line_number)
                
                for idx,regex in enumerate(regexes):
                    if enforce:
                        filename=repo_path+"_"+str(getHash(file_name))+"_"+line_number+"."+str(idx)
                    else:
                        filename=repo_path+"_"+str(getHash(file_name))+"_"+line_number+"_"+str(idx)
                        
                    regex2=regex
                    if r'''\\''' in regex:
                        try:                            
                            regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
                        except UnicodeEncodeError:
                            pass 
                    
                    if os.path.exists(filename) and os.path.getsize(filename)>0:
                        p_regex.append(regex2)
                        p_files.append(filename)
                        validRegex+=1
                    else:
                        print("invalid regex syntax or fail to generate string for idx: ",idx," regex: ", regex)
                        skipRegex+=1
                
#                 if len(p_regex)<len(regexes):
                if len(p_regex)<len(regexes): ### select chains no invalid no rex failure
                    print("skip regex commit chain after dropping invalid syntax or failures in generate strings in Rex")
                    skipChain+=1
                    continue
                
                res=getEnforcedMatchResults(p_regex,p_files)
                if len(res)==0: ##no elements in file or only one file has valid strings
                    print("skip regex commit chain after string match regex Rex")
                    skipChain+=1
                    continue
                
                res_sim[(repo_path,file_name,line_number)]=dict()
                for perRes in res:
                    print("add: ",perRes)
                    idx,regex=perRes[0],perRes[1]
                    validChainRegex+=1
                    res_sim[(repo_path,file_name,line_number)][idx]=perRes
                validChain+=1
                
                
            os.chdir("../..")   
    
    print("skipChain: ",skipChain," skipRegex: ",skipRegex," validRegex: ",validRegex," validChain: ",validChain," validChainRegex: ",validChainRegex)  
    
    output=open("res_sim_enforce."+str(k),'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()
                    
                    
                           
def readSimilarityRegex(k,enforce=False):
    ### read searched_repos.csv to get all valid repos
    countRegex=validRegex=invalidRegex=chainRegex=0 ##vRegex is chain uRegex is number
    succ_fail=re.compile("\nregex: .*? file: [a-z0-9_]+ k: [125]00 succ: ([0-9]+) fail: ([0-9]+)\n?",re.DOTALL)
    invalid_syntax=re.compile("\nregex: .*? is skipped because of invalid syntax\n?",re.DOTALL)
    
    res_sim=dict()
    with open("searched_repos.csv",mode="r") as searchedRepos:
        reader = csv.reader(searchedRepos)        
        for repo in reader:
            page,row=int(repo[0]),int(repo[1])
            repo_path=str(page)+"_"+str(row)
            
#             if repo_path!="3017_466":
#                 continue
            ### load committed regex
            os.chdir(repo_path)    
            
            regex_hist=pickle.load(open("regex.hist",'rb'))
            os.chdir(str(k))
            for key,value in regex_hist.items():
                file_name,line_number=key
                regexes=value[0]
                
                if len(regexes)<=1:
                    continue
                
                p_regex=list()
                p_files=list()
                print("repo path: ",repo_path," filename: ",file_name," line: ",line_number)
                
                for idx,regex in enumerate(regexes):
                    if enforce:
                        filename=repo_path+"_"+str(getHash(file_name))+"_"+line_number+"."+str(idx)
                    else:
                        filename=repo_path+"_"+str(getHash(file_name))+"_"+line_number+"_"+str(idx)
                        
                    regex2=regex
                    if '''\\''' in regex:
                        try:                            
                            regex2=codecs.escape_decode(bytes(regex2, "utf-8"))[0].decode("utf-8")
                        except UnicodeEncodeError:
                            pass 
                    
                    if os.path.exists(filename) and os.path.getsize(filename)>0:
                        p_regex.append(regex2)
                        p_files.append(filename)
                        countRegex+=1
                    else:
                        print("fail to generate string for idx: ",idx," regex: ", regex)
                
                if len(p_regex)<len(regexes):
                    print("skip regex commit chain because at least one regex fails to generate strings in Rex")
                    continue
                
                chainRegex+=1
                  
                parameters=[str(len(p_regex))]
                parameters.extend(p_regex)
                parameters.extend(p_files)
                parameters.append(str(k))
               
                cmd=["java", "-cp", SemanticTestPath, SemanticTestFile]
                cmd.extend(parameters)
                
                print("cmd: ",encodeList(cmd))
                
                try:
                    p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
                    stdoutdata, stderrdata=p.communicate(timeout=3600)
                    p.stdout.close()
                                    
                    if p.returncode>0:
                        print("ret:",p.returncode,"repo:",repo_path,"cmd: ",cmd)
                        return None
                    else:
                        stdoutdata=stdoutdata.decode('utf-8')
#                         lines=stdoutdata.splitlines()
#                         i=1
                        print("stdout:",stdoutdata)
                        res_sim[(repo_path,file_name,line_number)]=dict()
                        for regex in range(len(p_regex)):
                            res_sim[(repo_path,file_name,line_number)][regex]=[regexes[regex],p_regex[regex]]
                            for file in range(len(p_files)):
                                res=succ_fail.search(stdoutdata)
                                if res is None:
                                    res2=invalid_syntax.search(stdoutdata)##drop invalid regex
                                    if res2 is None:
                                        print("Error stdout: ",stdoutdata)
                                    else:
                                        invalidRegex+=1
                                        print("Drop invalid regex:",repr(regexes[regex].encode("utf-8"))," id: ",regex, "repo: ",repo_path," file: ",file_name," line:",line_number)                                
                                    break
                                        
                                        
#                                 print("group 0: ",res.group(0))
                                succ,fail=res.group(1),res.group(2)
#                                 print("regex: ",regex,"file: ",file,"succ: ",succ,"fail: ",fail)                                
                                res_sim[(repo_path,file_name,line_number)][regex].append(int(succ))
                                res_sim[(repo_path,file_name,line_number)][regex].append(int(fail))
                                pos=res.end(2)
#                                 print(stdoutdata[:pos+1])
                                stdoutdata=stdoutdata[pos:]
                            print(res_sim[(repo_path,file_name,line_number)][regex])
#                         for line in stdoutdata.splitlines():
#                             print(line)
                except subprocess.TimeoutExpired:
                    print("TimeoutExpired:",p.returncode,"repo:",repo_path,"cmd: ",cmd)
                    return None
                    
            os.chdir("../..")   
    print("chainRegex: ",chainRegex," countRegex: ",countRegex," invalid: ",invalidRegex)  
    
    output=open("res_sim."+str(k),'wb')
    pickle.dump(res_sim, output, protocol=2)
    output.close()

def generatePortion(k,step=1):
    comps=[]
    length_chain=[0]*10
    res_sim=pickle.load(open("res_sim."+str(k),'rb'))
#     res_sim.sort()
    for chain,comp in res_sim.items():
        print(list(chain))
        length_chain[len(comp)]+=1
#         if chain!=('1398_334','lib/commons-core/src/main/java/org/apache/olingo/commons/core/edm/primitivetype/AbstractGeospatialType.java','47'):
#             continue
        for idx in range(len(comp)-step):
            ## check both idx and old are valid regex
            print("len idx: ",len(comp[idx]))
            if len(comp[idx])<3:
                print("com idx: ",comp[idx])
                continue
            
            old=idx+step
            while old<len(comp) and len(comp[old])<3:
                old+=1
            if old==len(comp):
                break
            
            regex10,regex11=comp[idx][:2]
            regex20,regex21=comp[old][:2]
            
            print("idx: ",idx,comp[idx])
            s11,f11=comp[idx][idx*2+2:idx*2+4]
            s12,f12=comp[idx][old*2+2:old*2+4]
            
            
            print("old: ",old,comp[old])
            s21,f21=comp[old][idx*2+2:idx*2+4]
            s22,f22=comp[old][old*2+2:old*2+4]
            
            ele=list(chain)
            if s21==f21==s22==f22==0:
                s12,f12=0,0
                a,b,c=s11,0,0
                t1=s11+f11
                t2=s22+f22
                t=t1
                
                ele2=[idx,old,regex10,regex20,a,b,c,t,t1,t2,repr(regex11),repr(regex21)]
                ele.extend(ele2)
                print("add ",tuple(ele)," to comps")
                comps.append(tuple(ele))
                print("Invalid regex occurs---:",chain," idx: ",idx,"old: ",old)
            else:                
                t1,t2=s11+f11,s22+f22
                a,c=t1+t2-s21-s22,t1+t2-s11-s12
                b=t1+t2-a-c
                t=a+b+c
                if a<0 or b<0 or c<0:
                    print("Error: Math fails---:",chain," idx: ",idx,"old: ",old)
                    b=t1+t2-a if a>c else t1+t2-c
#                     sys.exit(1)
#                 else:
                ele2=[idx,old,regex10,regex20,a,b,c,t,t1,t2,repr(regex11),repr(regex21)]
                ele.extend(ele2)
                print("add ",tuple(ele)," to comps")
                comps.append(tuple(ele))
                
#     comps.sort(key=lambda x:(str(x[0]),str(x[1]),str(x[2]),str(x[3]),str(x[4])))

    with open("res_sim_"+str(k)+"_"+str(step)+"_sim.csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","NewRID","OldRID","New-Old","New*Old","Old-New","Total","TotalNew","TotalOld"])
        idx=0
        prev_comp=None
        for comp in comps:
            print(list(comp))
            if prev_comp is None or prev_comp!=tuple(list(comp)[:3]):                
                idx+=1
                prev_comp=tuple(list(comp)[:3])
                print("newly: ",prev_comp)
            
            temp=[idx]
            temp2=list(comp)
            temp.extend(temp2[3:5])
            temp.extend(temp2[7:-2])
            print(temp)
            wr2.writerow(temp)
            
    with open("res_sim_"+str(k)+"_"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","Repo","File","Line","NewRID","OldRID","NewRegex","OldRegex","New-Old","New*Old","Old-New","Total","TotalNew","TotalOld","NewRegex1","OldRegex1"])
        idx=0
        prev_comp=None
        for comp in comps:
            if prev_comp is None or prev_comp!=tuple(list(comp)[:3]):
                idx+=1
                prev_comp=tuple(list(comp)[:3])
            temp=[idx]
            temp.extend(list(comp))
            wr2.writerow(temp)
        
    for idx,ele in enumerate(length_chain):
        if ele>0:
            print("len: ",idx,"num:",ele)

def generateEnforcedPortion(k,step=1):
    comps=[]
    length_chain=[0]*10
    res_sim=pickle.load(open("res_sim_enforce."+str(k),'rb'))
#     res_sim.sort()
    for chain,comp in res_sim.items():
        print(list(chain))
        length_chain[len(comp)]+=1
#         if chain!=('1398_334','lib/commons-core/src/main/java/org/apache/olingo/commons/core/edm/primitivetype/AbstractGeospatialType.java','47'):
#             continue
        print(comp)

#        id_regexes=[None]*len(comp)
#        for regex,perRes in comp.items():
#            id_regexes[perRes[0]]=regex
#        print(id_regexes)
        
        for idx in range(len(comp)-step):
            ## check both idx and old are valid regex
            new_res=comp[idx]
            new_regex=new_res[1]
            
            print("len idx: ",len(new_res))
            if len(new_res)<8:
                print("Res not match idx: ",new_res)
                continue
            
            old=idx+step
            old_res=comp[old]
            old_regex=old_res[0]
                        
            print("new: ",idx,new_res)
            s11,f11,e11=new_res[idx*3+2:idx*3+5]
            s12,f12,e12=new_res[old*3+2:old*3+5]
            if e11>0 or e12>0:
                print("Error new: ",idx,new_res)
            
                
            print("old: ",old,old_res)
            s21,f21,e21=old_res[idx*3+2:idx*3+5]
            s22,f22,e22=old_res[old*3+2:old*3+5]
            if e21>0 or e22>0:
                print("Error old: ",old,old_res)
                
            ele=list(chain)
            if s21==f21==s22==f22==0:
                s12,f12=0,0
                a,b,c=s11,0,0
                t1=s11+f11
                t2=s22+f22
                t=t1
                
                ele2=[idx,old,new_regex,old_regex,a,b,c,t,t1,t2]
                ele.extend(ele2)
                print("add ",tuple(ele)," to comps")
                comps.append(tuple(ele))
                print("Invalid regex occurs---:",ele,new_res,old_res)
            else:                
                t1,t2=s11+f11,s22+f22
                a,c=t1+t2-s21-s22,t1+t2-s11-s12
                b=t1+t2-a-c
                t=a+b+c
                if a<0 or b<0 or c<0:
                    print("Error: Math fails---:",chain," idx: ",new_res,"old: ",old_res)
                    b=t1+t2-a if a>c else t1+t2-c
#                     sys.exit(1)
#                 else:
                ele2=[idx,old,new_regex,old_regex,a,b,c,t,t1,t2]
                ele.extend(ele2)
                print("add ",tuple(ele)," to comps")
                comps.append(tuple(ele))
                
#     comps.sort(key=lambda x:(str(x[0]),str(x[1]),str(x[2]),str(x[3]),str(x[4])))

    with open("res_sim_enforce_"+str(k)+"_"+str(step)+"_sim.csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","NewRID","OldRID","New-Old","New*Old","Old-New","Total","TotalNew","TotalOld"])
        idx=0
        prev_comp=None
        for comp in comps:
            print(list(comp))
            if prev_comp is None or prev_comp!=tuple(list(comp)[:3]):                
                idx+=1
                prev_comp=tuple(list(comp)[:3])
                print("newly: ",prev_comp)
            
            temp=[idx]
            temp2=list(comp)
            temp.extend(temp2[3:5])
            temp.extend(temp2[7:])
            print(temp)
            wr2.writerow(temp)
            
    with open("res_sim_enforce_"+str(k)+"_"+str(step)+".csv",'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        wr2.writerow(["ChainID","Repo","File","Line","NewRID","OldRID","NewRegex","OldRegex","New-Old","New*Old","Old-New","Total","TotalNew","TotalOld","NewRegex1","OldRegex1"])
        idx=0
        prev_comp=None
        for comp in comps:
            if prev_comp is None or prev_comp!=tuple(list(comp)[:3]):
                idx+=1
                prev_comp=tuple(list(comp)[:3])
            temp=[idx]
            temp.extend(list(comp))
            wr2.writerow(temp)
        
    for idx,ele in enumerate(length_chain):
        if ele>0:
            print("len: ",idx,"num:",ele) 
                                                              
if __name__== '__main__':
    if platform.system()=="Windows":
        cp_path=ws_win
        os.chdir(ws_win)
        java_path=java_path_win
    else:
        cp_path=ws_unix
        os.chdir(ws_unix)
        java_path=java_path_unix
#     regex='^https?://e-hentai\\.org/g/([0-9]+)/([a-fA-F0-9]+)/$'
#     regex='^.*g\\.e-hentai\\.org/g/[0-9]+/[a-fA-F0-9]+)/$'
#     print(validateRegex(regex))
#     s=["a*b","[http(s)?:[^\\]]+\\]"]
#     for regex in s:
#         if validateRegex(regex):
#             strs=generateStrings2(regex, 10,int(time.time()))
#             for str in strs:
#                 print("str: ",str)
#                 print(testStringRegex(regex, str)) 
# #         print(validateRegex(regex))
# #         print(testStringRegex(regex, "a"))
# #         print(testStringRegex(regex, "ab"))
# #         print(testStringRegex(regex, "https:\\"))
# #         print(testStringRegex(regex, "https:"))

#     readGenRegex(100,enforce=True)
#     readGenRegex(100,enforce=False)
#     readGenRegex(200)
#     readGenRegex(500)
#    getEnforcedSimilarityRegex(100,enforce=True)
#     readSimilarityRegex(100)
#     readSimilarityRegex(200)
#     readSimilarityRegex(500)
#     generatePortion(100,1)
    generateEnforcedPortion(100,1)
