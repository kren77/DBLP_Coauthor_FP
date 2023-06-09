class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}
    def inc(self, numOccur):
        self.count += numOccur
    def disp(self, ind=1):
        print('  '*ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind+1)

def createTree(dataSet, minSup=1):
    freqDic = {}

    for trans in dataSet:
        for item in trans:
            freqDic[item] = freqDic.get(item, 0) + dataSet[trans]

    headerTable = {k: v for (k, v) in freqDic.items() if v >= minSup}


    if len(headerTable) == 0: return None, None
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]

    retTree = treeNode('Null Set', 1, None)
    for tranSet, count in dataSet.items():
        localD = {}
        for item in tranSet:
            if headerTable.get(item,0):
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable

def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        inTree.children[items[0]].inc(count)
    else:
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)

def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

def findPrefixPath(basePat, treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0])]
    for basePat in bigL:
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)

        if len(newFreqSet) > 1:
            freqItemList[frozenset(newFreqSet)] = headerTable[basePat][0]
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])

        
        myCondTree, myHead = createTree(condPattBases, minSup)

        if myHead != None:


            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)

def loadSimpDat(inFile):
    dataSet = {}
    for line in inFile:
        line =line.strip().split(',')
        dataLine = [word for word in line if word.isdigit()]
        dataSet[frozenset(dataLine)] = dataSet.get(frozenset(dataLine),0) + 1
            
    return dataSet



if __name__ == "__main__":
    minSup = 100
    print("Reading Source File ... Wait...")
    with open('authors_encoded.txt','r') as f:
        dataSet = loadSimpDat(f)

    print("Constructing FP-tree ... Wait...")
    myFPtree, myHeaderTab = createTree(dataSet, minSup)
    
    print("Mining frequent items ... Wait...")
    myFreqList = {}
    mineTree(myFPtree, myHeaderTab, minSup, set([]), myFreqList)
    print("Totally %d frequent itemsets found ! " %len(myFreqList))
    print("Constructing authors_index... Wait...")

    maxCoauthors = 0
    for freqAuthors in myFreqList.keys():
        if len(freqAuthors) > maxCoauthors:
            maxCoauthors = len(freqAuthors)
    print("the max num of coauthors is %d " % (maxCoauthors))

    
    with open('authors_index.txt','r') as authorsIndex:
        i = 0
        authorsDic = {}
        for name in authorsIndex:
            name = name.strip()
            authorsDic[i] = name
            i = i+1
    
    print("Writing result into result.txt... Wait...")

    with open('result4.txt','w') as result2:
        with open('result3.txt','w') as result:
            result.write("%25s\t%25s\t%15s\t%10s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\n" \
                         %('authorA','authorB','authorC','Sup(A,B,C)','Sup(A)','Sup(B)','Sup(C)',\
                           'Con(A)','Con(B)','Con(C)','MinCon','MaxCon'))
            result2.write("%25s\t%25s\t%15s\t%10s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\n" \
                          %('authorA','authorB','authorC','Sup(A,B,C)','Sup(A)','Sup(B)','Sup(C)',\
                            'Con(A)','Con(B)','Con(C)','MinCon','MaxCon'))
            resultList = sorted(myFreqList.items(), key=lambda p: p[1], reverse=True)
            for itemSet, support in resultList:
                itemList = list(itemSet)
                A = itemList[0]
                authorA = authorsDic.get(int(A),'0')
                B = itemList[1]
                authorB = authorsDic.get(int(B),'0')
                SupAB_C = int(support)
                SupA = int(myHeaderTab.get(A,[0])[0])
                SupB = int(myHeaderTab.get(B,[0])[0])
                ConA = float(SupAB_C) / float(SupA)
                ConB = float(SupAB_C) / float(SupB)
                (C,authorC,SupC,ConC) = ('','',0.0,0.0)
   
                if len(itemList) == 3:
                    C = itemList[2]
                    authorC = authorsDic.get(int(C),'0')
                    SupC = int(myHeaderTab.get(C,[0])[0])
                    ConC = float(SupAB_C) / float(SupC)
                    MinCon = min([ConA, ConB, ConC])
                    MaxCon = max([ConA, ConB, ConC])
                elif len(itemList) == 2:
                    MinCon = min([ConA, ConB])
                    MaxCon = max([ConA, ConB])                


                if MinCon < 0.4 or MaxCon < 0.5 or (MinCon + MaxCon)/2 < 0.5:
                    continue
                result.write("%25s\t%25s\t%15s\t%10.0f\t%6.0f\t%6.0f\t%6.0f\t%6.4f\t%6.4f\t%6.4f\t%6.4f\t%6.4f\n" \
                             %(authorA,authorB,authorC,SupAB_C,\
                               SupA,SupB,SupC,ConA,ConB,ConC,MinCon,MaxCon))
                result2.write("%25s\t%25s\t%15s\t%10.0f\t%6.0f\t%6.0f\t%6.0f\t\%6.4f\t%6.4f\t%6.4f\t%6.4f\t%6.4f\n"\
                              %(A,B,C,SupAB_C,SupA,SupB,SupC,\
                                ConA,ConB,ConC,MinCon,MaxCon))
    print("Finished !")
