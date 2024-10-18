from minizinc import Instance, Model, Solver, Status
import argparse
import re
import time
from datetime import timedelta
from functools import cmp_to_key

SOLVER = "highs"

INPUT_COMMENT = "%"
INPUT_TESTS_AMOUNT = "Number of tests"
INPUT_MACHINES_AMOUNT = "Number of machines"
INPUT_RESOURCES_AMOUNT = "Number of resources"
INPUT_TEST = "test("

TIMEOUT = 295 # 5m - 5s de seguranca

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('output')

args = parser.parse_args()

######################################################
#                   Pre-processing                   #
######################################################

def getId(s):
    return int(s.strip()[2:-1])

def getIds(s):
    ids = []
    unformattedList = s.split(",")
    if len(unformattedList) > 0 and len(unformattedList[0]) > 0:
        for element in unformattedList:
            ids.append(getId(element))

    return ids

def fillMachines(machines, n):
    if len(machines) != 0:
        return machines

    for i in range(1, n + 1):
        machines.append(i)

    return machines

######################################################
#                     Comparator                     #
######################################################

def comparator(test1, test2):
    resourcesDiff = -(len(test1[2]) - len(test2[2]))
    if resourcesDiff != 0:
        return resourcesDiff

    machinesDiff = len(test1[1]) - len(test2[1])
    if machinesDiff != 0:
        return machinesDiff

    return -(test1[0] - test2[0])

######################################################
#                Lower Bound Estimate                #
######################################################

def getMinLowerBound(numResources, tests):
    higherLowerBound = 0
    testsDurationSum = 0
    for r in range(1, numResources + 1):
        testsDurationSum = 0
        for test in tests:
            if r in test[2]:
                testsDurationSum += test[0]
        
        if testsDurationSum > higherLowerBound:
            higherLowerBound = testsDurationSum
    
    return higherLowerBound

######################################################
#                       Models                       #
######################################################

def calculateTimeForIteration(lastIterationDuration, startTimeStamp):
    timeLeft = TIMEOUT - (time.time() - startTimeStamp)
    if lastIterationDuration == -1:
        return int(min(TIMEOUT, timeLeft))

    multiplier = 6
    reasonableTime = int(lastIterationDuration * multiplier)

    return int(min(timeLeft, reasonableTime))

def isSolvableForLowerbound(solver, model, numTests, numMachines, numResources, durations, machines, resources, lowerBound, iterationMaxSeconds):
    instance = Instance(solver, model)

    instance["nTests"] = numTests
    instance["nMachines"] = numMachines
    instance["nResources"] = numResources
    instance["durations"] = durations
    instance["machinesAvailable"] = machines
    instance["resourcesRequired"] = resources
    instance["lowerBound"] = lowerBound

    return instance.solve(timeout=timedelta(seconds=iterationMaxSeconds))

def solveWithLowerBoundVar(numTests, numMachines, numResources, durations, machines, resources, tests):
    model = Model("./Solver.mzn")
    solver = Solver.lookup(SOLVER)
    instance = Instance(solver, model)

    instance["nTests"] = numTests
    instance["nMachines"] = numMachines
    instance["nResources"] = numResources

    instance["durations"] = durations
    instance["machinesAvailable"] = machines
    instance["resourcesRequired"] = resources

    result = instance.solve()

    return result["lowerBound"]

def solveWithBinaryLowerBound(numTests, numMachines, numResources, durations, machines, resources, tests, startTimeStamp):
    model = Model("./SolverBinary.mzn")
    solver = Solver.lookup(SOLVER)
    minLowerBound = getMinLowerBound(numResources, tests)
    l = minLowerBound
    r = sum(durations)
    finalResult = None

    while l < r - 1:
        mid = int((l + r) / 2)
        start_time = time.time()
        result = isSolvableForLowerbound(solver, model, numTests, numMachines, numResources, durations, machines, resources, mid, TIMEOUT)
        elapsed_time = time.time() - start_time

        if result.status == Status.SATISFIED:
            r = mid
            finalResult = result
            lowerBound = r
        else:
            l = mid
            finalResult = result
            lowerBound = l

    if l == minLowerBound:
        result = isSolvableForLowerbound(solver, model, numTests, numMachines, numResources, durations, machines, resources, l)
        return (result, l) if result.status == Status.SATISFIED else (finalResult, r)

    return (finalResult, lowerBound)

def solveWithStepLowerBound(numTests, numMachines, numResources, durations, machines, resources, tests, startTimeStamp):
    model = Model("./SolverBinary.mzn")
    solver = Solver.lookup(SOLVER)
    minLowerBound = getMinLowerBound(numResources, tests)
    current = sum(durations)
    divisor = 2
    step = (current + minLowerBound) // divisor
    prevStep = step
    finalResult = None
    finalLowerBound = current
    lastIterationDuration = -1

    while True:
        iterationMaxDuration = calculateTimeForIteration(lastIterationDuration, startTimeStamp)
        if iterationMaxDuration <= 0:
            return (finalResult, finalLowerBound)

        start_time = time.time()
        result = isSolvableForLowerbound(solver, model, numTests, numMachines, numResources, durations, machines, resources, current, iterationMaxDuration)
        elapsed_time = time.time() - start_time

        if result.status == Status.SATISFIED:
            lastIterationDuration = max(elapsed_time, lastIterationDuration)
            if current == minLowerBound:
                return (result, current)

            finalResult = result
            finalLowerBound = current
        else:
            if step == 1 and prevStep == 1:
                break

            minLowerBound = current + 1

            current += prevStep
            step = prevStep // divisor

        while current - step < minLowerBound and step > divisor - 1:
            step = step // divisor

        current -= step
        prevStep = step
        if step > divisor - 1:
            step = step // divisor

    return (finalResult, current + 1)

######################################################
#                      Solution                      #
######################################################

def getObviousSolution(tests):
    makespan = 0
    startTimes = []
    tasksMachine = []
    for test in tests:
        startTimes.append(makespan)
        makespan += test[0]
        tasksMachine.append(test[1][0])

    return (makespan, startTimes, tasksMachine)

def writeSolutionToFile(output, result, lowerBound, ids, numTests, numMachines, tests):
    if result != None:
        startTimes = result["startTimes"]
        tasksMachine = result["tasksMachine"]
    else:
        lowerBound, startTimes, tasksMachine = getObviousSolution(tests)

    machinesSchedule = []
    for i in range(0, numMachines):
        machinesSchedule.append([])

    for i in range(0, numTests):
        machinesSchedule[tasksMachine[i] - 1].append((ids[i], startTimes[i], tests[i][2]))

    with open(output, "w") as file:
        file.write(f"% Makespan : {lowerBound}\n")

        for i in range(0, numMachines):
            length = len(machinesSchedule[i])
            startTimesString = []
            for j in range(0, length):
                resourcesListString = []
                for resource in machinesSchedule[i][j][2]:
                    resourcesListString.append(f"'r{resource}'")

                if len(resourcesListString) != 0:
                    resourcesString = f",[{','.join(resourcesListString)}]"
                else:
                    resourcesString = ""

                startTimesString.append(f"('t{machinesSchedule[i][j][0]}',{machinesSchedule[i][j][1]}{resourcesString})")

            file.write(f"machine( 'm{i+1}', {length}, [{','.join(startTimesString)}])\n")

def solve(input, output):
    tests = []
    with open(input, 'r') as file:
        testPattern = re.compile(r"test\( 't(\d+)', (\d+), \[(.*?)\], \[(.*?)\]\)")

        for line in file:
            if line.startswith(INPUT_COMMENT):
                value = int(line.split(':')[1].strip())
                if INPUT_TESTS_AMOUNT in line:
                    numTests = value
                elif INPUT_MACHINES_AMOUNT in line:
                    numMachines = value
                elif INPUT_RESOURCES_AMOUNT in line:
                    numResources = value
            
            elif line.startswith(INPUT_TEST):
                match = testPattern.search(line)
                id, duration, unformattedMachines, unformattedResources = match.groups()

                tests.append((int(duration), fillMachines(getIds(unformattedMachines), numMachines), getIds(unformattedResources), id))
    
    tests.sort(key=cmp_to_key(comparator))

    ids = []
    durations = []
    machines = []
    resources = []

    for test in tests:
        ids.append(test[3])
        durations.append(test[0])
        machines.append(set(test[1]))
        resources.append(set(test[2]))

    writeSolutionToFile(output, None, 0, ids, numTests, numMachines, tests) # Makes sure there is at least the obvious solution
    solution = solveWithStepLowerBound(numTests, numMachines, numResources, durations, machines, resources, tests, time.time())
    writeSolutionToFile(output, solution[0], solution[1], ids, numTests, numMachines, tests)

solve(args.input, args.output)