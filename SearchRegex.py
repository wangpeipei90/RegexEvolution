'''
Created on Mar 27, 2018

@author: peipei
'''
import csv
import os
import subprocess
import re
import pickle


valid_repos_path="/home/peipei/ISSTA/data/valid_repos_csv.csv"
valid_repo_pom="/home/peipei/ISSTA/data/select_reporeaper/valid_repo_pom/"
workspace="/home/peipei/RepoReaper/"

def download_repo(i,r,string_url):
    if os.path.exists(str(i)+"_"+str(r)):
        return
    ##add username:password for https://github.com
#     string_url="https://wangpeipei90:jiangzhen123456@"+string_url[8:]
    cmd_git="git clone "+string_url+".git "+str(i)+"_"+str(r)    
    print("git command: "+cmd_git)

    status_git=os.system(cmd_git)
    print("git status: "+str(status_git))

def download(page,row):
    pom_path=valid_repo_pom+str(page)+"_pom.csv"
    with open(pom_path, mode='r') as pomfile:
        reader = csv.reader(pomfile)
        for rowinfo in reader:
            num_row=int(rowinfo[0])
            if num_row==row:
                valid_url,string_url=rowinfo[2:4]
                valid_url= valid_url=='True'
                if valid_url:
                    download_repo(page,row,string_url)
                    return True
    return False

def run_grep(cmd,repo_path):
    try:
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
        stdoutdata, stderrdata=p.communicate(timeout=3600)
        p.stdout.close()
                        
        if p.returncode>0:
            print("ret:",p.returncode,"repo:",repo_path,"cmd: ",cmd)
            return None
        else:
            return stdoutdata           
    except subprocess.TimeoutExpired:
        print("TimeoutExpired:",p.returncode,"repo:",repo_path,"cmd: ",cmd)
        return None

def extractFileLineNumber(stdout):
    output_regex=stdout.strip().decode('utf-8')
    output_regex=output_regex.splitlines()
    
    re_pattern='^(.*):([0-9]+):\s+.*Pattern.compile\("(.*)"\);(//.*)?$'
    file_line_check=re.compile(re_pattern,re.DOTALL)
    
    regex_info=[]
    for line in output_regex:
        result = file_line_check.match(line)
        if result:
            file_name=result.group(1)
            line_number=result.group(2)
            regex_str=result.group(3)
            print("regex_str: ",regex_str)
            if '"' in regex_str and '\"' not in regex_str:
                print("not literal regex: ",line)
            elif '"+' in regex_str or '" +' in regex_str:
                print("not literal regex: ",line)                
            else:
                regex_info.append((file_name,line_number,regex_str))
        else:
            print("not match regex: ",line)
            
    return regex_info    

def saveCSV(regex_info,file_name):
    with open(file_name,'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        for info in regex_info:
            wr2.writerow(list(info))

def extractCommits(stdout):    
    output_commits=stdout.strip()
    try:
        output_commits=output_commits.decode('utf-8')
    except UnicodeDecodeError:
        print("ERROR Unicode")
        return [],[],[],[]
    
    output_commits=output_commits.splitlines()
    
#     re_file=re.compile(r"^[+]{3} b/(.*)$\n@",re.DOTALL|re.MULTILINE)
#     for file in re_file.finditer(output_commits):
#         if file.group(1)!=file_name:
#             print("ERR!! file: ",file_name,"line: ",line_number)
#             raise Exception("error of extract Commits! file: ",file_name,"line: ",line_number)
    
    re_regex='^[+]\s+.*Pattern.compile\("(.*)"\);(//.*)?'
    regexes=[]
#     for regex in re.finditer(re_regex, output_commits,re.DOTALL|re.MULTILINE):
#         regexes.append(regex.group(1))
           
    re_version="^commit ([a-zA-Z0-9]+)"    
    commits=[]
#     for commit in re.finditer(re_version, output_commits,re.DOTALL|re.MULTILINE):
#         commits.append(commit.group(1))
    
    re_author="^Author:\s+(.*)\s+<(.*?@.*?)>"
    authors=[]
#     for author in re.finditer(re_author, output_commits, re.DOTALL|re.MULTILINE):
#         authors.append((author.group(1),author.group(2))) ##name, email
    
    re_date="^Date:   ([A-Z][a-z]{2}) ([A-Z][a-z]{2}) ([0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2}) ([0-9]{4}) (.*)"
    dates=[]
#     for date in re.finditer(re_date, output_commits, re.DOTALL|re.MULTILINE):
#         dates.append((date.group(1),date.group(2),date.group(3),date.group(4),date.group(5))) #day, month, date, time, year

    for line in output_commits: 
        
        if len(line)>0 and line[0]=="+":
            res=re.match(re_regex, line, re.DOTALL)
            if res:
                regexes.append(res.group(1))  
            continue
        if len(line)>5 and line[:6]=="commit":
            res=re.match(re_version, line, re.DOTALL)
            if res:
                commits.append(res.group(1))  
            continue 
        if len(line)>5 and line[:6]=="Author":
            res=re.match(re_author, line, re.DOTALL)
            if res:
                authors.append((res.group(1),res.group(2)))  
            continue
        if len(line)>3 and line[:4]=="Date":
            res=re.match(re_date, line, re.DOTALL)
            if res:
                dates.append((res.group(1),res.group(2),res.group(3),res.group(4),res.group(5)))  
            continue
    return regexes,commits,authors,dates

def saveDictCSV(regex_hist,file_name):
    with open(file_name,'w') as resultFile:
        wr2 = csv.writer(resultFile, dialect='excel')
        for info,hist in regex_hist.items():  ###regexes,commits,authors,dates
            t=list(info)
            t.extend(hist[0])
            wr2.writerow(t)
                            
def searchRegex(page,row):
    if not download(page, row):
        print("download file")
        return False
    repo_path=str(page)+"_"+str(row)
    if not os.path.exists(repo_path):
        return -1
    
    os.chdir(repo_path)
    
    ###cmd 1
    regex_info=[]
    
    cmd1=["grep","-nr", "Pattern.compile("]
    print("command1:", cmd1)
    res1=run_grep(cmd1,repo_path)
    if res1 is not None:    
        regex_info=extractFileLineNumber(res1)
    
        saveCSV(regex_info,"regex_info.csv")
        output=open("regex.info",'wb')
        pickle.dump(regex_info, output, pickle.HIGHEST_PROTOCOL)
        output.close() 
    
    ###cmd 2
    ### no follow "--follow", --follow requires exactly one pathspec
    regex_hist=dict()
    for info in regex_info:
        file_name,line_number,regex_str=info
        cmd2=["git", "log", "-L",line_number+","+line_number+":"+file_name]
        print("repo:",repo_path,"command2:", cmd2)
        
        res2=run_grep(cmd2,repo_path)        
        if res2 is not None:
            regexes,commits,authors,dates=extractCommits(res2)
            regex_hist[(file_name,line_number)]=[regexes,commits,authors,dates]
    
    saveDictCSV(regex_hist,"regex_hist.csv")
    output=open("regex.hist",'wb')
    pickle.dump(regex_hist, output, pickle.HIGHEST_PROTOCOL)
    output.close()
    
    os.chdir(workspace) 
    return len(regex_info)
    
def searchValidRepos():
    repos=list()
    with open(valid_repos_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip the headers
        for row in reader:
            page,row=int(row[1]),int(row[2])
            print(page,row)
            len_regex=searchRegex(page, row)
            print(page,row,len_regex)
            if len_regex>0:
                repos.append((page,row))
                                    
    saveCSV(repos,"searched_repos.csv")
    
def changedRegex():
    regex_changeCount=list()
    with open("searched_repos.csv",mode="r") as searchedRepos:
        reader = csv.reader(searchedRepos)        
        for repo in reader:
            page,row=int(repo[0]),int(repo[1])
            repo_path=str(page)+"_"+str(row)
            
            regex_hist=pickle.load(open(repo_path+"/regex.hist",'rb'))
            for key,value in regex_hist.items():
                file_name,line_number=key
                regexes=value[0]
                regex_changeCount.append((repo_path,file_name,line_number,len(regexes)))
    
    ##sort changeCount descending
    regex_changeCount=sorted(regex_changeCount, key=lambda x: x[3])
    saveCSV(regex_changeCount,"change_count.csv")
                
if __name__ == '__main__':
    os.chdir(workspace)
#     searchRegex(1002, 50)
#     searchRegex(1143, 24)
#     searchValidRepos()
    changedRegex()
    pass