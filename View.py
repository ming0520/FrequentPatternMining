from Apriori import Apriori
from FPGrowth import FPGrowth
import os
import pandas as pd
import numpy as np
import csv

def call_apriori(filePath,minSuppCount,minConfidence):
    ap = Apriori(minSuppCount,minConfidence)
    ap.process(filePath)

def call_fpGrowth(filePath,minSuppCount,minConfidence):
    fp = FPGrowth(minSuppCount,minConfidence)
    df = fp.process(filePath)
    while True:
        print('Do you want to save as output.csv at here? (y/n)')
        choice = str(input())
        choice = choice[0].lower() 
        if (choice =='y'):
            print('Saved to output.csv')
            df.to_csv('output.csv')
            break
        elif (choice == 'n'):
            break
        else:
            print('Invalid choice!')

def getInput():
    temp = ""
    transRecord = []
    print('Please enter the transaction records (enter ''''quit'''' to stop the input)')
    while True:
        temp = input()
        if temp == 'quit':
            break
        transRecord.append(temp)
    return transRecord

def saveInput(transRecord):
    transArray = []
    for row in transRecord:
    #     print(row.split(','))
        transArray.append(np.asarray(row.split(',')))
    a = np.asarray(transArray,dtype=object)
    # a.shape
    while True:
        print('Enter file name to save (.csv): ')
        filePath = str(input())
        if (not os.path.exists(filePath)):
            break
        else:
            print('File exits! Please try another name')    
    with open(filePath, "w", encoding = "utf-8") as f:
        w = csv.writer(f)
        w.writerows(transArray)
    return filePath

print ('{:=^40}'.format(f' Welcome to frequent pattern analysis tools '))

filePath = 'monkey.csv'
minConfidence = 0.5
minSuppCount = 2
# call_apriori(filePath,minSuppCount,minConfidence)
# call_fpGrowth(filePath,minSuppCount,minConfidence)
while True:
    while True:
        print('Select a input method')
        print('1) File (.csv)')
        print('2) Manual')
        choice = int(input())
        if (choice >= 1 and choice <= 2):
            break
        else:
            print('Invalid choice!')       

    if choice == 1:
        while True:
            print('Enter file path (.csv): ')
            filePath = str(input())
            if (os.path.exists(filePath)):
                break
            else:
                print('File does not exits')
    elif choice == 2:
        transRecord = getInput()
        filePath = saveInput(transRecord)     
        

    while True:
        print('Enter confidence threshold: (0.0 - 1.0):')
        minConfidence = float(input())
        if (minConfidence > 0.0 and minConfidence <= 1.0):
            break
        else:
            print('Confidence threshold must be greater than 0 and less than 1')

    while True:
        print('Enter minimum support count:')
        minSuppCount = int(input())
        if (minSuppCount > 0):
            break
        else:
            print('Minimum support count must be greater than 0')

    print('Select a method to analyze the frequent pattern')
    print('1) Apriori')
    print('2) FP-Growth')

    while True:
        print('Enter your choice:')
        choice = int(input())
        if (choice >= 1 and choice <= 2):
            break
        else:
            print('Invalid choice!')

    if(choice == 1):
        call_apriori(filePath,minSuppCount,minConfidence)
    elif(choice == 2):
        call_fpGrowth(filePath,minSuppCount,minConfidence)
    else:
        print('Invalid choice! Exit program')


    print('Do you want exit program? (y/n)')
    choice = str(input())
    choice = choice[0].lower() 
    if (choice =='y'):
        break
    elif (choice == 'n'):
        continue
    else:
        print('Invalid choice!')
