import pandas as pd
import numpy as np
from collections import defaultdict

class ARule:
    def __init__(self,s,l,sn=0,ln=0):
        self.s = s
        self.l = l
        self.sn = sn
        self.ln = ln
        
    def getConfidence(self):
        return self.ln/self.sn

class Apriori:
    def __init__(self,minSuppCount = 2,minConfidence=0.5):
        self.df = None
        self.file = None
        self.basicItem = None
        self.rawSet = None
        self.minSuppCount = minSuppCount
        self.minConfidence = minConfidence * 100
        
    def read_csv(self,file):
        #https://stackoverflow.com/questions/27020216/import-csv-with-different-number-of-columns-per-row-using-pandas
        df = pd.read_fwf(file, header=None)
        df = df[0].str.split(',', expand=True)
        self.df = df
#         print(df)
        #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_numpy.html
    
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
    
    def getNextItemset(self,itemset, k):
        basicItem = itemset
        newBasicItem = []
        for n,item in enumerate(basicItem):
            for j in range(n+1,len(basicItem)):
                item1 = item
                item2 = basicItem[j]
                itemSet = np.union1d(item1,item2)
                if(len(itemSet) == k):
                    newBasicItem.append(np.array(itemSet))
            uniqueBasicItem = np.unique(np.array(newBasicItem),axis=0)
            uniqueBasicItem.astype(object)
        return uniqueBasicItem
    
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
    
    def getKey(self,basicItem):
        if(type(basicItem) == np.str):
            return basicItem
        elif(type(basicItem) == np.str_):
            return basicItem
        elif(type(basicItem) == np.ndarray):
            return basicItem.tobytes()
        else:
            print('key error! line 83')
    
    def getMinSupportItemset(self,basicItemSet):
        suppCountDict = {}
        for basicItem in basicItemSet:
            suppCountDict[self.getKey(basicItem)] = self.calculateMinSuppCount(basicItem)
        return suppCountDict
    
    def filterItemsetwithCount(self,itemset,suppCountDict):
        minSuppCount = self.minSuppCount
        newItemset = []
        counter = 1
        for item in itemset:
            count = suppCountDict[self.getKey(item)]
            if(count >= minSuppCount):
                newItemset.append(item)
        return np.array(newItemset)

    # https://www.youtube.com/watch?v=9oPNGofa1pI&t=32s
    def powerset(self,originalSet):
        subSets = []
        numberOfCombinations = 2 ** len(originalSet) - 1
        for combinationIndex in range(1,numberOfCombinations):
            subSet = []
            for setElementIndex in range(0, len(originalSet)):
                if combinationIndex & 1 << setElementIndex:
                    subSet.append(originalSet[setElementIndex])
            subSets.append(subSet)
        return subSets    

    def associationRule(self):
        threeItemsetAbove = []
        for fp in self.frequentPattern[2:]:
            threeItemsetAbove.append(fp[0])
            rulesSet = self.generateRules(threeItemsetAbove)
        return threeItemsetAbove,rulesSet

    def generateRules(self,threeItemsetAbove):
        rulesSet = defaultdict(list)
        for itemsets in threeItemsetAbove:
            for itemset in itemsets:
                subsets = self.powerset(itemset)
                for n,subset1 in enumerate(subsets):
                    for subset2 in subsets:
                        sn = 0
                        ln = 0
                        mask = np.isin(subset1,subset2)
                        numberOfConflict = mask.sum()
                        if(numberOfConflict == 0):
                            if(len(subset1) != len(subset2)):
                                sn = self.calculateMinSuppCount(subset1)
                                ln = self.calculateMinSuppCount(subset2+subset1)
                                percentage = (ln/sn) * 100
                                if (percentage >= self.minConfidence):
                                    rulesSet[self.getKey(itemset)].append(ARule(subset1,subset2,sn,ln))
            return rulesSet

    def displayItemsetCount(self,itemset,suppCountDict):
        minSuppCount = self.minSuppCount
        try:
            k = itemset.shape[1]
        except:
            k = 1
        counter = 1
        for item in itemset:
            print(f'{counter}: {item}: {suppCountDict[self.getKey(item)]}')        
            counter = counter + 1

    def displayStartDivider(self,counter):
        print('\n')
        print ('{:-^40}'.format(f' {counter}-itemset '))
        print('\n')
    
    def displayMinSuppCountMsg(self):
        print('\n')
        print ('{:*^40}'.format(f' Item that sastify min support count ({self.minSuppCount}) '))
        print('\n')
        
    def displayFrequentPattern(self):
        print ('{:.^40}'.format(f' Frequent Patterns '))
        for fp in self.frequentPattern:
            itemset = fp[0]
            itemdict = fp[1]
            self.displayItemsetCount(itemset,itemdict)            

    def displayRules(self,threeItemsetAbove,rulesSet):
        for itemsets in threeItemsetAbove:
            for itemset in itemsets:
                rules = rulesSet[self.getKey(itemset)]
                if(len(rules) <= 0):
                    continue
                # print ('{:^40}'.format(f' {itemset} '))
                print(itemset)
                print('')
                for rule in rules:
                    percentage = (rule.ln/rule.sn) * 100
                    print(f'{rule.s} => {rule.l} confidence={rule.ln}/{rule.sn} = {percentage}\n')    
                print('\n')
        print ('{:-^40}'.format(f' End strong rule'))

    def generateRules(self):
        strongRules = []
        for frequentPattern in self.frequentPattern[2:]:
            itemset = frequentPattern[0]
            itemsetCount = frequentPattern[1]
            for item in itemset:
                if(len(item) < 2):
                    continue
                ln = itemsetCount[self.getKey(item)]
#                 print(f'------{item}: {itemsetCount[self.getKey(item)]}-----')
                subsets = self.powerset(item)
                for subset in subsets:
                    sn = self.calculateMinSuppCount(subset)
                    s=subset
                    l=np.setdiff1d(item,subset)
#                     print(f'{subset}=>{l}')
                    associationRule = ARule(s,l,sn,ln)
                    strongRules.append(associationRule)
        self.strongRules = strongRules
        
    def displayAllRules(self):        
        for strongRule in self.strongRules:
            print(f'{strongRule.s}=>{strongRule.l} confidence={strongRule.ln}/{strongRule.sn}={strongRule.getConfidence():.2f} support count = {strongRule.ln}')
            
    def displayStrongRules(self):        
        for strongRule in self.strongRules:
            if(strongRule.ln >= self.minSuppCount and strongRule.getConfidence()*100 >= self.minConfidence):
                print(f'{strongRule.s}=>{strongRule.l} confidence={strongRule.ln}/{strongRule.sn}={strongRule.getConfidence()*100:.2f} support count = {strongRule.ln}')
    
    def process(self,file):
        print ('{:=^40}'.format(f' Start of apriori '))
        self.file = file
        self.read_csv(file)
        self.resolveDuplicated()
        frequentPattern = []

        basicItem = self.basicItem
        itemDict = self.getMinSupportItemset(basicItem)
        self.itemDict = itemDict
        self.displayStartDivider(1)
        self.displayItemsetCount(basicItem,itemDict)
        ItemFiltered = self.filterItemsetwithCount(basicItem,itemDict)
        self.displayMinSuppCountMsg()
        self.displayItemsetCount(ItemFiltered,itemDict)
        frequentPattern.append([ItemFiltered,itemDict])
        counter = 2
        while ItemFiltered.size > 2:
            self.displayStartDivider(counter)
            nextItemset = self.getNextItemset(ItemFiltered,counter)
            nextItemsetCount = self.getMinSupportItemset(nextItemset)
            self.displayItemsetCount(nextItemset,nextItemsetCount)
            ItemFiltered = self.filterItemsetwithCount(nextItemset,nextItemsetCount)
            if(ItemFiltered.size != 0):
                self.displayMinSuppCountMsg()
            self.displayItemsetCount(ItemFiltered,nextItemsetCount)
            counter = counter+1
            if(ItemFiltered.size != 0):
                frequentPattern.append([ItemFiltered,nextItemsetCount])
        self.frequentPattern = frequentPattern
        self.displayFrequentPattern()
        print('')
        print ('{:-^40}'.format(f' Strong Rule '))
        print('')
        self.generateRules()
        self.displayStrongRules()
        try:
            self.generateRules()
            self.displayStrongRules()
        except:
            print('\nNo strong rule\n')
        # try:
        #     rulesSet = self.associationRule()
        #     threeItemsetAbove, rulesSet = self.associationRule()
        #     self.displayRules(threeItemsetAbove,rulesSet)
        # except:
        #     print('\nNo strong rule\n')
        print('\n')
        print ('{:=^40}'.format(f' End of apriori '))