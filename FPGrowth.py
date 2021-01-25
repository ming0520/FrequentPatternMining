import pandas as pd
import numpy as np
from collections import defaultdict
from anytree import Node, RenderTree, find, Walker
from collections import OrderedDict

class AssociationRule:
    def __init__(self,s,l,sn=0,ln=0):
        self.s = s
        self.l = l
        self.sn = sn
        self.ln = ln

class CPB:
    def __init__(self,path,count):
        self.path = path
        self.count = count

class BasicItem:
    def __init__(self,name,count):
        self.name = name
        self.count = count

class ItemTable:
    def __init__(self,name=None,count=None,idxs=None):
        self.name = name
        self.count = count
        self.idxs = idxs
        self.head = []
        self.CPBase = []
        self.CFPTree = []
        self.CFPTreeTable = []
        self.CFP=[]
        self.FP = []
        self.StrongRule = []

class FPGrowth:
    def __init__(self,minSuppCount=2,minConfidence=0.5):
        self.minSuppCount = minSuppCount
        self.df = None
        self.basicItem = None
        self.rawSet = None
        self.minConfidence = minConfidence
        
    def read_csv(self,file):
        df = pd.read_fwf(file, header=None)
        df = df[0].str.split(',', expand=True)
        self.df = df
        
    def resolveDuplicated(self):
        rawSet = self.df.to_numpy()
        for nRow,row in enumerate(rawSet):
            counter = 1
            for nCol,col in enumerate(row):
                if col == None:
                    continue
                for restN in range(nCol+1,len(row)):
                    if(col == row[restN]):
                        row[restN] = str(col) + str(counter)
                        counter = counter + 1
        self.basicItem = np.unique(rawSet[rawSet != np.array(None)])
        self.rawSet = rawSet.astype('object')
        return self.basicItem
    
    def generateItemTable(self):
        itemTbl = []
        for basicItem in self.basicItem:
            mask = np.isin(self.rawSet,basicItem)
            vec_mask = np.isin(mask.sum(axis=1), [1])
            idxs = np.where(vec_mask)
            count = len(idxs[0])
            itemTbl.append(ItemTable(basicItem,count,idxs[0]))
        return itemTbl
    def reverseName(self,itemTables):
        alphaDsc = sorted(itemTables, key=lambda x: x.name,reverse=True)
        return sorted(alphaDsc, key=lambda x: x.count)

    def getAscItemTable(self,itemTables):
#         https://stackoverflow.com/questions/48727337/python-how-to-sort-list-of-object
         return sorted(itemTables, key=lambda x: (x.count))
        
    def getDscItemTable(self,itemTables):
#         https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects
#         return sorted(itemTables, key=lambda x: x.count,reverse=True)
        alphaAsc = sorted(itemTables, key=lambda x: x.name)
        return sorted(alphaAsc, key=lambda x: x.count,reverse=True)

    def filterItemTable(self,itemTables):
#         https://stackoverflow.com/questions/7623715/deleting-list-elements-based-on-condition
        return [item for item in itemTables if item.count >= self.minSuppCount]

    def getItemTable(self):
        itemTbl = self.generateItemTable()
        itemTbl = self.getDscItemTable(itemTbl)
        return itemTbl
    
    def displayData(self):
        print(self.df)
        
    def updateItemTable(self,basicItem,currentNode):
        basicItem.head.append(currentNode)
        return basicItem
    
    def updateTree(self,currentNode,basicItem,maxDepth,count=None):
        if count == None:
            count = 1
            
        if currentNode.depth < maxDepth:
            if currentNode.is_leaf:
                newNode = Node(basicItem.name,parent=currentNode,count=count)
                currentNode = newNode
                basicItem = self.updateItemTable(basicItem,currentNode)
            else:
                found = False
                for child in currentNode.children:
                    if child.name == basicItem.name:
                        if count == None:
                            child.count +=1
                        else:
                            child.count += count
                        currentNode = child
                        found=True
                if not found:
                    newNode = Node(basicItem.name,parent=currentNode,count=count)
                    currentNode = newNode
                    basicItem = self.updateItemTable(basicItem,currentNode)
        return currentNode,basicItem
    
    def getFPTree(self,itemTbl):
        root = Node('null')
        currentNode = root
        for i,row in enumerate(self.rawSet):
            currentNode = root
            maxDepth = len(row[row != None])
            for basicItem in itemTbl:
                mask = np.isin(basicItem.idxs,i)
                occurance = mask.sum()
                if(occurance >= 1):
                    currentNode,basicItem = self.updateTree(currentNode,basicItem,maxDepth)
        return root,itemTbl
    
    def filterCPBase(self,itemTbl):
        newItemTbl = []
        for item in itemTbl:
            nodes = item.head
            totalCount = 0
            for node in nodes:
                totalCount += node.count
            if(totalCount >= self.minSuppCount):
                newItemTbl.append(item)
        return newItemTbl
    
    def generateCPBase(self,itemTbl):
        for item in itemTbl:
            pathList = []
            nodes = item.head
            for node in nodes:
                paths = []
                for path in node.path:
                    if(path.name != 'null' and path.name!=item.name):
                        paths.append(path.name)
                if(len(paths) > 0):
                    pathList.append(CPB(paths,path.count))
            item.CPBase = pathList
        return itemTbl

    def searchBasicItemTable(self,basicItemTable, itemName):
        counter = 0
        for basicItem in basicItemTable:
            if basicItem.name == itemName:
                return counter
            counter+=1
        return -99
    
    def generateCFPTree(self,itemTbl):
        for item in itemTbl:
            root = Node('null')
            currentNode = root
            CFPTreeTable = []
            cpbs = item.CPBase
            basicItemTable = []
            for cpb in cpbs:
                currentNode = root
                maxDepth = len(cpb.path)
                for itemName in cpb.path:
                    index = self.searchBasicItemTable(basicItemTable,itemName)
                    if(index == -99):
                        basicItem = ItemTable(itemName,cpb.count)
                    else:
                        basicItem = basicItemTable[index]

                    currentNode,basicItem = self.updateTree(currentNode,basicItem,maxDepth,cpb.count)

                    if(index == -99):
                        basicItemTable.append(basicItem)
                    else:
                        basicItemTable[index] = basicItem
            item.CFPTreeTable = basicItemTable
            item.CFPTree = root
        return itemTbl
    def pruneBranchTree(self,itemTbl):
        # prune branch that doesnt meet min supprt count
        # https://buildmedia.readthedocs.org/media/pdf/anytree/latest/anytree.pdf
        # 2.3 Detach/Attach Protocol page 8
        # c.parent=None
        for item in itemTbl:
            for node in item.CFPTree.descendants:
                if node.count < self.minSuppCount:
                    node.parent = None
        return itemTbl

    def removeBranchTable(self,itemTbl):

        # remove the nodeLink if prunned
        # https://stackabuse.com/remove-element-from-an-array-in-python/
        # Using del
        # del array[index]
        for item in itemTbl:
            for basicItem in item.CFPTreeTable: 
                for index,nodeLink in enumerate(basicItem.head):
                    if(nodeLink.root != item.CFPTree.root):
                        del basicItem.head[index]
        return itemTbl

    def generateConditionalPattern(self,itemTbl):
    # generate frequent pattern
        for item in itemTbl:
            condPats = []
            for basicItem in item.CFPTreeTable:
                if(len(basicItem.head) <= 0):
                    continue
                for index,nodeLink in enumerate(basicItem.head):
                    condPatsItem = {}
                    currentNode = nodeLink
                    if(not nodeLink.is_leaf):
                        continue
                    while(currentNode.parent):
                        condPatsItem[currentNode.name] = currentNode.count
                        currentNode = currentNode.parent
                    if condPatsItem:
                        condPats.append(condPatsItem)
            item.CFP = condPats
        return itemTbl

    # https://www.youtube.com/watch?v=9oPNGofa1pI&t=32s
    def powerset(self,originalSet,maxLength=0):
        subSets = []
        numberOfCombinations = 2 ** len(originalSet)-maxLength
        for combinationIndex in range(1,numberOfCombinations):
            subSet = []
            for setElementIndex in range(0, len(originalSet)):
                if combinationIndex & 1 << setElementIndex:
                    subSet.append(originalSet[setElementIndex])
            subSets.append(subSet)
        return subSets

    def generateFrequentPattern(self,cfp,baseItem):
        frequentPatterns = []
        CFPItems = []
        cfp = OrderedDict(reversed(list(cfp.items()))) 
        for key,value in cfp.items():
            CFPItems.append(key)

        subsets = self.powerset(CFPItems)

        for subset in subsets:
            frequentPattern = ((subset+[baseItem],cfp[subset[-1]]))
            frequentPatterns.append(frequentPattern)
        return frequentPatterns

    def generateFrequentPatternTable(self,itemTbl):
        # generate frequent pattern table
        for item in itemTbl:
            if(len(item.CFP) <= 0):
                continue
            frequentPatterns = []
            for cfp in item.CFP:
                frequentPatterns+=(self.generateFrequentPattern(cfp,item.name))
            for i,frequentPattern1 in enumerate(frequentPatterns):
                for j in range(i+1,len(frequentPatterns)-1):
                    frequentPattern2 = frequentPatterns[j]
                    if(frequentPattern1[0] == frequentPattern2[0]):
                        newCount = frequentPattern1[1] + frequentPattern2[1]
                        newName = frequentPattern1[0]
                        newTup = (newName,newCount)
                        frequentPatterns[i] = newTup
                        del frequentPatterns[j]
            item.FP = frequentPatterns
        return itemTbl
    
    def calculateMinSuppCount(self,basicItem):
        #https://stackoverflow.com/questions/56419519/selecting-rows-of-numpy-array-that-contains-all-the-given-values
        item = basicItem
        if(type(item) == np.str):
            k = 1
        elif(type(item) == np.ndarray):
            k = len(item)
        else:
            k = len(item)
        mask = np.isin(self.rawSet,item)
        vec_mask = np.isin(mask.sum(axis=1), [k])
        ids = np.where(vec_mask)
        minSuppCount = len(ids[0])
        return minSuppCount
    
    def generateStrongRule(self,itemTbl,isLargestK=True):
        largestK = 0
        if isLargestK:
            for item in itemTbl:
                frequentPatterns=item.FP
                for frequentPattern in frequentPatterns:
                    largestK = max(largestK,len(frequentPattern[0]))
            print(f'Largest k is {largestK}')

        for item in itemTbl:
            frequentPatterns = item.FP
            for frequentPattern in frequentPatterns:
                itemset = frequentPattern[0]
                ln = frequentPattern[1]
                if(len(itemset)!=largestK and isLargestK):
                    continue
                subsets = self.powerset(itemset,1)
                item
                for subset in subsets:
                    s = subset
                    l = np.setdiff1d(itemset,subset)
                    sn = self.calculateMinSuppCount(s)
                    associationRule = AssociationRule(s,l,sn,ln)
                    item.StrongRule.append(associationRule)
        return itemTbl
    
    def displayItemTable(self,itemTbl):
        for item in itemTbl:
            print(f'{item.name}:{item.count}')
    
    def displayFPTree(self,root):
        print(RenderTree(root))
        
    def displayConditionalPatternBase(self,itemTbl):
        for item in itemTbl:
            print(f'==={item.name}===')
            for cpb in item.CPBase:
                print(f'{cpb.path} : {cpb.count}')
                
    def displayConditionalFPTreeTable(self,itemTbl):
        for item in itemTbl:
            print(f'{item.name}',end=':')
            print(item.CFP)
            
    def displayConditionalFPTree(self,itemTbl):            
        for item in itemTbl:
            print(f'==={item.name}===')
            print(RenderTree(item.CFPTree))
            print('\n')
            
    def displayFrequentPatternGenerated(self,itemTbl):      
        for item in itemTbl:
            if(len(item.CFP) <= 0):
                continue
            print(f'{item.name}:',end='')
            for fp in item.FP:
                print(f'{fp}',end=', ')
            print('\n')
            
    def displayAllFrequentPattern(self,itemTbl):
        for item in itemTbl:
            print(f"(['{item.name}'], {item.count})")
            
        for item in itemTbl:
            for frequentPattern in item.FP:
                print(frequentPattern)

    def displayStrongRule(self,itemTbl):
        print(f'Minimum confidence threshold is {self.minConfidence}')
        for item in itemTbl:
            if(len(item.StrongRule) <= 0):
                continue

            print(item.name)
            for strongRule in item.StrongRule:
                s = strongRule.s
                l = strongRule.l
                sn = strongRule.sn
                ln = strongRule.ln
                confidence = ln/sn
                if confidence < self.minConfidence:
                    continue
                print(f'{s}=>{l} confidence = {ln}/{sn} = {confidence}')
                
    def to_df(self,itemTbl):          
        data = {}
        data['Item'] = []
        data['CPB'] = []
        data['CFP'] = []
        data['FP'] = []
        for item in itemTbl:
            data['Item'].append(item.name)
            conditionalPatternBase = []
            for cpb in item.CPBase:
                dicted = (cpb.path,cpb.count)
                conditionalPatternBase.append(dicted)

            conditionalFPTree = []
            for cfp in item.CFP:
                conditionalFPTree.append(cfp)
            data['FP'].append(item.FP)
            data['CFP'].append(conditionalFPTree)
            data['CPB'].append(conditionalPatternBase)
        df = pd.DataFrame(data)
        return df
    
    def process(self,file):
        self.read_csv(file)
        self.resolveDuplicated()
        print('Transaction:')
        self.displayData()
        print('\n')
        itemTbl = self.getItemTable()
        print('Rearranged Item:')
        self.displayItemTable(itemTbl)
        print('\n')
        fptree,itemTbl = self.getFPTree(itemTbl)
        print('Frequent Pattern Tree:')
        self.displayFPTree(fptree)
        print('\n')
        itemTbl = self.reverseName(itemTbl)
        itemTbl = self.filterCPBase(itemTbl)
        itemTbl = self.generateCPBase(itemTbl)
        print('Conditional Pattern Base:')
        self.displayConditionalPatternBase(itemTbl)
        print('\n')
        itemTbl = self.generateCFPTree(itemTbl)
        print('Conditional FP Tree before prune:')
        self.displayConditionalFPTree(itemTbl)
        print('\n')
        itemTbl = self.pruneBranchTree(itemTbl)
        itemTbl = self.removeBranchTable(itemTbl)
        itemTbl = self.generateConditionalPattern(itemTbl)
        print('Conditional FP Tree Result:')
        self.displayConditionalFPTreeTable(itemTbl)
        print('\n')
        itemTbl = self.generateFrequentPatternTable(itemTbl)
        print('Frequent Pattern Generated:')
        self.displayFrequentPatternGenerated(itemTbl)
        print('\n')
        print('All Frequent Pattern:')
        self.displayAllFrequentPattern(itemTbl)
        print('\n')
        itemTbl = self.generateStrongRule(itemTbl)
        print('\nStrong Rule:')
        self.displayStrongRule(itemTbl)
        print('========================================================================')
        df = self.to_df(itemTbl)
        return df