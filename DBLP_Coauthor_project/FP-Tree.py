
import pandas as pd
import numpy as np
from sklearn.externals import joblib



class TREE_NODE:
    def __init__(self, authorName, frequence, parentPointer):
        self.authorName=authorName
        self.frequence=frequence
        self.parentPointer=parentPointer
        self.childrenPointer={}
        self.brotherPointer=None





def CreateHeaderTable(tranDB, minSupport=1):
    headerTable={}
    authorDB={}
    for i, (conf, year, authorList) in enumerate(tranDB):
        authorListSet=set([])
        print("trans", i, "=="*20)
        if conf is np.nan or year is np.nan or authorList is np.nan:
            continue
        for author in authorList.split("|"):
            authorListSet.add(author)
            if author in headerTable:
                headerTable[author][0]+=1
                if year<headerTable[author][2]:
                    headerTable[author][2]=year
                elif year>headerTable[author][3]:
                    headerTable[author][3]=year
            else:
                headerTable[author]=[1, None, year, year]
        if frozenset(authorListSet) in authorDB:
            authorDB[frozenset(authorListSet)]+=1
        else:
            authorDB[frozenset(authorListSet)]=1
    for author in list(headerTable.keys()):
        if headerTable[author][0]<minSupport:
            del headerTable[author]
    return headerTable, authorDB

def UpdateTree(authorsList, treeNode, headerTable, frequence):
    if authorsList[0] in treeNode.childrenPointer:
        treeNode.childrenPointer[authorsList[0]].frequence+=frequence
    else:
        treeNode.childrenPointer[authorsList[0]]=TREE_NODE(authorsList[0], frequence, treeNode)
        if headerTable[authorsList[0]][1]==None:
            headerTable[authorsList[0]][1]=treeNode.childrenPointer[authorsList[0]]
        else:
            firstChildPointer=headerTable[authorsList[0]][1]
            tempAuthorNode=firstChildPointer
            while tempAuthorNode.brotherPointer is not None:
                tempAuthorNode=tempAuthorNode.brotherPointer
            tempAuthorNode.brotherPointer=treeNode.childrenPointer[authorsList[0]]
    if len(authorsList)>1:

        UpdateTree(authorsList[1:], treeNode.childrenPointer[authorsList[0]], headerTable, frequence)


def CreateTree(authorDB, headerTable):
    treeRoot=TREE_NODE("NULL", 0, None)
    for i, (authorListSet, frequence) in enumerate(authorDB.items()):
        print("authorListSet", i, "=="*20)
        tempDict={}
        for author in authorListSet:
            if author in headerTable:
                tempDict[author]=headerTable[author][0]
        if len(tempDict)>0:
            tempList=sorted(tempDict.items(), key=lambda x:x[1], reverse=True)
            authorsList=[author for author, count in tempList]
            UpdateTree(authorsList, treeRoot, headerTable, frequence)
    return treeRoot





def FindParentTreeNodes(baseTreeNode):
    parentTreeNodes=[]
    while baseTreeNode.parentPointer is not None:
        parentTreeNodes.append(baseTreeNode.authorName)
        baseTreeNode=baseTreeNode.parentPointer
    return parentTreeNodes

def FindCondAuthorDB(firstChildPointerTreeNode):
    condAuthorDB={}
    tempTreeNode=firstChildPointerTreeNode
    while tempTreeNode is not None:
        parentTreeNodes=FindParentTreeNodes(tempTreeNode)
        if len(parentTreeNodes)>1:
            condAuthorDB[frozenset(parentTreeNodes[1:])]=tempTreeNode.frequence

        tempTreeNode=tempTreeNode.brotherPointer
    return condAuthorDB

def CreateCondHeaderTable(condAuthorDB, minSupport=1):
    condHeaderTable = {}
    for i, (authorListSet, frequence) in enumerate(condAuthorDB.items()):
        print("cond trans", i, "=="*20)
        for author in authorListSet:
            if author in condHeaderTable:
                condHeaderTable[author][0] += frequence
            else:
                condHeaderTable[author] = [frequence, None]
    for author in list(condHeaderTable):
        if condHeaderTable[author][0] < minSupport:
            del condHeaderTable[author]
    return condHeaderTable



def MineTree(treeRoot, headerTable, minSupport=1, baseFreqAuthorSet=set([]), finalFreqAuthorPattDict={}):
    sortedAuthorsList=[value[0] for value in sorted(headerTable.items(), key=lambda x:x[1][0], reverse=False)]
    for baseAuthor in sortedAuthorsList:
        newFreqAuthorSet=baseFreqAuthorSet.copy()
        newFreqAuthorSet.add(baseAuthor)
        finalFreqAuthorPattDict[frozenset(newFreqAuthorSet)]=headerTable[baseAuthor][0]
        condAuthorDB=FindCondAuthorDB(headerTable[baseAuthor][1])
        condHeaderTable=CreateCondHeaderTable(condAuthorDB, minSupport)
        condTreeRoot=CreateTree(condAuthorDB, condHeaderTable)
        if condHeaderTable is not None:
            MineTree(condTreeRoot, condHeaderTable, minSupport, newFreqAuthorSet, finalFreqAuthorPattDict)







if __name__=="__main__":
    
    minSupport=3
    tranDB=pd.read_csv("tranDB.txt",sep="\t",header=None)
    print(tranDB.shape)
    tranDB = np.array(tranDB.iloc[:, [0, 1, 3]])
    print(tranDB)
    #firstly, create header table(the first pass)
    headerTable, authorDB=CreateHeaderTable(tranDB, minSupport)
    print(len(headerTable))
    print(headerTable)
    # #secondly, create the FP-Tree(the second pass)
    treeRoot=CreateTree(authorDB, headerTable)
    # #finally, mining the FP-Tree
    baseFreqAuthorSet=set([])
    finalFreqAuthorPattDict={}
    MineTree(treeRoot, headerTable, minSupport, baseFreqAuthorSet, finalFreqAuthorPattDict)
    print(len(finalFreqAuthorPattDict))
    maxCoauthors=0
    finalFreqAuthorPattList=sorted(finalFreqAuthorPattDict.items(), key=lambda x:x[1], reverse=True)
    joblib.dump(finalFreqAuthorPattList, 'finalFreqAuthorPattList.pkl')
    wf=open("finalFreqAuthorPattDict.txt","w")
    for freqAuthorSet, support in finalFreqAuthorPattList:
        print("support=", support, "==>freqAuthorSet=", freqAuthorSet)
        wf.write("support="+str(support)+"==>freqAuthorSet="+str(freqAuthorSet)+"\n")
        if len(freqAuthorSet)>maxCoauthors:
            maxCoauthors=len(freqAuthorSet)
    wf.close()
    print("the max number of coauthors is %d " % (maxCoauthors))#7

