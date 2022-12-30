import json
import random
import numpy as np
import math 
from random import choice
import statistics 

class AI:

    def __init__(self):
        pass

    def solve(self, problem):
        problem_data = json.load(problem)
        solutionFound = 0
        sudoku=AI.arrayify(problem_data)
        while (solutionFound == 0):
            decreaseFactor = 0.99
            stuckCount = 0
            fixedSudoku = np.copy(sudoku)
            AI.PrintSudoku(sudoku)
            AI.FixSudokuValues(fixedSudoku)
            listOfBlocks = AI.CreateList3x3Blocks()
            tmpSudoku = AI.RandomlyFill3x3Blocks(sudoku, listOfBlocks)
            sigma = AI.Initial(sudoku, fixedSudoku, listOfBlocks)
            score = AI.Errors(tmpSudoku)
            itterations = AI.Itterations(fixedSudoku)
            if score <= 0:
                solutionFound = 1

            while solutionFound == 0:
                previousScore = score
                for i in range (0, itterations):
                    newState = AI.ChooseNewState(tmpSudoku, fixedSudoku, listOfBlocks, sigma)
                    tmpSudoku = newState[0]
                    scoreDiff = newState[1]
                    score += scoreDiff
                    if score <= 0:
                        solutionFound = 1
                        break

                sigma *= decreaseFactor
                if score <= 0:
                    solutionFound = 1
                    break
                if score >= previousScore:
                    stuckCount += 1
                else:
                    stuckCount = 0
                if (stuckCount > 80):
                    sigma += 2
                if(AI.Errors(tmpSudoku)==0):
                    AI.PrintSudoku(tmpSudoku)
                    break
        finished=tmpSudoku
        AI.PrintSudoku(finished)
        return finished

    def arrayify(jsonfile):
        resultList = list(jsonfile.values())
        x=np.array(resultList)
        sudoku=x.reshape(-1,9)
        return sudoku
    
    def PrintSudoku(sudoku):
        print("\n")
        for i in range(len(sudoku)):
            line = ""
            if i == 3 or i == 6:
                print("---------------------")
            for j in range(len(sudoku[i])):
                if j == 3 or j == 6:
                    line += "| "
                line += str(sudoku[i,j])+" "
            print(line)

    def FixSudokuValues(sudoku):
        for i in range (0,9):
            for j in range (0,9):
                if sudoku[i,j] != 0:
                    sudoku[i,j] = 1
        return(sudoku)

    def ErrorsRowColumn(row, column, sudoku):
        numberOfErrors = (9 - len(np.unique(sudoku[:,column]))) + (9 - len(np.unique(sudoku[row,:])))
        return(numberOfErrors)

    def Errors(sudoku):
        numberOfErrors = 0 
        for i in range (0,9):
            numberOfErrors += AI.ErrorsRowColumn(i ,i ,sudoku)
        return(numberOfErrors)
    
    def CreateList3x3Blocks ():
        finalListOfBlocks = []
        for r in range (0,9):
            tmpList = []
            block1 = [i + 3*((r)%3) for i in range(0,3)]
            block2 = [i + 3*math.trunc((r)/3) for i in range(0,3)]
            for x in block1:
                for y in block2:
                    tmpList.append([x,y])
            finalListOfBlocks.append(tmpList)
        return(finalListOfBlocks)
    
    def RandomlyFill3x3Blocks(sudoku, listOfBlocks):
        for block in listOfBlocks:
            for box in block:
                if sudoku[box[0],box[1]] == 0:
                    currentBlock = sudoku[block[0][0]:(block[-1][0]+1),block[0][1]:(block[-1][1]+1)]
                    sudoku[box[0],box[1]] = choice([i for i in range(1,10) if i not in currentBlock])
        return sudoku

    def SumOfOneBlock (sudoku, oneBlock):
        finalSum = 0
        for box in oneBlock:
            finalSum += sudoku[box[0], box[1]]
        return(finalSum)

    def TwoRandomBoxesWithinBlock(fixedSudoku, block):
        while (1):
            firstBox = random.choice(block)
            secondBox = choice([box for box in block if box is not firstBox ])
            if fixedSudoku[firstBox[0], firstBox[1]] != 1 and fixedSudoku[secondBox[0], secondBox[1]] != 1:
                return([firstBox, secondBox])

    def FlipBoxes(sudoku, boxesToFlip):
        proposedSudoku = np.copy(sudoku)
        placeHolder = proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]]
        proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]]
        proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
        return(proposedSudoku)

    def ProposedState (sudoku, fixedSudoku, listOfBlocks):
        randomBlock = random.choice(listOfBlocks)
        if AI.SumOfOneBlock(fixedSudoku, randomBlock) > 6:  
            return(sudoku, 1, 1)
        boxesToFlip = AI.TwoRandomBoxesWithinBlock(fixedSudoku, randomBlock)
        proposedSudoku = AI.FlipBoxes(sudoku,  boxesToFlip)
        return([proposedSudoku, boxesToFlip])

    def ChooseNewState (currentSudoku, fixedSudoku, listOfBlocks, sigma):
        proposal = AI.ProposedState(currentSudoku, fixedSudoku, listOfBlocks)
        newSudoku = proposal[0]
        boxesToCheck = proposal[1]
        currentCost = AI.ErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], currentSudoku) + AI.ErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], currentSudoku)
        newCost = AI.ErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], newSudoku) + AI.ErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], newSudoku)
        costDifference = newCost - currentCost
        rho = math.exp(-costDifference/sigma)
        if(np.random.uniform(1,0,1) < rho):
            return([newSudoku, costDifference])
        return([currentSudoku, 0])

    def Itterations(fixed_sudoku):
        Itterations = 0
        for i in range (0,9):
            for j in range (0,9):
                if fixed_sudoku[i,j] != 0:
                    Itterations += 1
        return Itterations
    
    def Initial (sudoku, fixedSudoku, listOfBlocks):
        Differences = []
        tmpSudoku = sudoku
        for i in range(1,10):
            tmpSudoku = AI.ProposedState(tmpSudoku, fixedSudoku, listOfBlocks)[0]
            Differences.append(AI.Errors(tmpSudoku))
        return (statistics.pstdev(Differences))


def main():
    f=open('problem.json')
    x=(AI.solve(AI,f))
    list=x.tolist()
    dic={"Solved Sudoku":list}
    solution=open("solution.json","w")
    json.dump(dic,solution)
    f.close()

if __name__=="__main__":
    main()