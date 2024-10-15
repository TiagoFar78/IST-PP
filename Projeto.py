from minizinc import Instance, Model, Solver, Status
import argparse
import re
import time
from functools import cmp_to_key
import itertools

SOLVER = "highs"

INPUT_COMMENT = "%"
INPUT_TESTS_AMOUNT = "Number of tests"
INPUT_MACHINES_AMOUNT = "Number of machines"
INPUT_RESOURCES_AMOUNT = "Number of resources"
INPUT_TEST = "test("

parser = argparse.ArgumentParser()
parser.add_argument('input')

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

    return set(ids)

def fillMachines(machines, n):
    if len(machines) != 0:
        return machines

    for i in range(1, n + 1):
        machines.add(i)

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

def isCompleteForLowerbound(solver, model, numTests, numMachines, numResources, durations, machines, resources, lowerBound):
    instance = Instance(solver, model)

    instance["nTests"] = numTests
    instance["nMachines"] = numMachines
    instance["nResources"] = numResources
    instance["durations"] = durations
    instance["machinesAvailable"] = machines
    instance["resourcesRequired"] = resources
    instance["lowerBound"] = lowerBound

    result = instance.solve()

    return result.status == Status.SATISFIED

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

def solveWithBinaryLowerBound(numTests, numMachines, numResources, durations, machines, resources, tests):
    model = Model("./SolverBinary.mzn")
    solver = Solver.lookup(SOLVER)
    print("O maximo lowerBound é " + str(sum(durations)))
    minLowerBound = getMinLowerBound(numResources, tests)
    l = minLowerBound
    r = sum(durations)
    satisfiedLast = False

    while l < r - 1:
        mid = int((l + r) / 2)

        print("Vai tentar o lowerbound " + str(mid))

        start_time = time.time()
        isComplete = isCompleteForLowerbound(solver, model, numTests, numMachines, numResources, durations, machines, resources, mid)
        elapsed_time = time.time() - start_time

        if isComplete:
            print("Satisfez: " + str(mid) + f" em: {elapsed_time:.4f}")
            r = mid
            satisfiedLast = True
        else:
            print("Não satisfez: " + str(mid) + f" em: {elapsed_time:.4f}")
            l = mid
            satisfiedLast = False

    if l == minLowerBound:
        return l if isCompleteForLowerbound(solver, model, numTests, numMachines, numResources, durations, machines, resources, l) else r

    if not satisfiedLast:
        return l

    return r

######################################################
#                      Solution                      #
######################################################

def solve(input):
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

                tests.append((int(duration), fillMachines(getIds(unformattedMachines), numMachines), getIds(unformattedResources)))
    
    tests.sort(key=cmp_to_key(comparator))

    durations = []
    machines = []
    resources = []

    for test in tests:
        durations.append(test[0])
        machines.append(test[1])
        resources.append(test[2])

    print("Input:")
    print("Tests: " + str(numTests))
    print("Machines: " + str(numMachines))
    print("Resources: " + str(numResources))
    print("Durations:")
    print(durations)
    print("Machines:")
    print(machines)
    print("Resources:")
    print(resources)

    makespan = solveWithBinaryLowerBound(numTests, numMachines, numResources, durations, machines, resources, tests)
    print("Makespan: " + str(makespan))

solve(args.input)