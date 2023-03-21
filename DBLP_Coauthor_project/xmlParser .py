
import re



fileName="dblp.xml"
confNameDict={"SDM":1, "ICDM":1, "SIGMOD":1, "SIGKDD":1, "VLDB":1, "ICDE":1, "CVPR":1, "ICML":1, "ICCV":1, "COLT":1, "SIGIR":1, "ECCV":1,"AAAI":1,"IJCAI":1}
fromYear="2010"
allList=[] #"confName    \t    year    \t    title    \t    author1|author2|..|authorn"
authorDict={} #author: [frequence, yearStart, yearEnd]



def XmlLineParser(fileName):
    rf=open(fileName,"r")
    for line in rf:
        #print "line [1]", line
        if line.startswith("<inproceedings"):
            print ("line [1]", line)
            booktitle=""
            year=""

            authorList=""
            for line in rf:
                print ("line [2]", line)
                if line.startswith("<author"):
                    authorList+=line
                elif line.startswith("<year"):
                    year=line[6:10]
                    if year<fromYear:
                        break
                elif line.startswith("<booktitle"):
                    booktitle=((line[11:]).split("</")[0]).split(" ")[0]
                    if booktitle not in confNameDict:
                        break

                elif line.startswith("</inproceedings"):
                    #tranList=[] #"confName    \t    year    \t    title    \t    author1|author2|..|authorn"
                    localTran =""
                    for authorLine in authorList.split("\n"):
                        for author in re.findall(re.compile(r'<author>(.*)</author>', re.S), authorLine):
                            localTran+=author+","
                    wf=open("tranDB.txt","a")
                    wf.write(localTran[:-1]+"\n")
                    wf.close()
                    break
    rf.close()

if __name__=="__main__":

    XmlLineParser(fileName)