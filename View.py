from Apriori import Apriori
import os
print ('{:=^40}'.format(f' Welcome to frequent pattern analysis tools '))

filePath = 'food.csv'
minConfidence = 0.8
minSuppCount = 2

# while True:
#     print('Enter file path (.csv): ')
#     filePath = str(input())
#     if (os.path.exists(filePath)):
#         break
#     else:
#         print('File does not exits')

# while True:
#     print('Enter confidence threshold: (0.0 - 1.0):')
#     minConfidence = float(input())
#     if (minConfidence > 0.0 and minConfidence <= 1.0):
#         break
#     else:
#         print('Confidence threshold must be greater than 0 and less than 1')

# while True:
#     print('Enter minimum support count:')
#     minSuppCount = int(input())
#     if (minSuppCount > 0):
#         break
#     else:
#         print('Minimum support count must be greater than 0')

# print('Select a method to analyze the frequent pattern')
# print('1) Apriori')
# print('2) FP-Growth')

while True:
    print('Enter your choice:')
    choice = int(input())
    if (choice >= 1 and choice <= 2):
        break
    else:
        print('Invalid choice!')


ap = Apriori(minSuppCount,minConfidence)
ap.process(filePath)
