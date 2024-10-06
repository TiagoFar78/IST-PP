from minizinc import Instance, Model, Solver, Status
import argparse
import re
from functools import cmp_to_key
import itertools

INPUT_COMMENT = "%"
INPUT_TESTS_AMOUNT = "Number of tests"
INPUT_MACHINES_AMOUNT = "Number of machines"
INPUT_RESOURCES_AMOUNT = "Number of resources"
INPUT_TEST = "test("

parser = argparse.ArgumentParser()
parser.add_argument('input')

args = parser.parse_args()

def getId(s):
    return int(s.strip()[2:-1])


def getIds(s):
    ids = []
    unformattedList = s.split(",")
    if len(unformattedList) > 0 and len(unformattedList[0]) > 0:
        for element in unformattedList:
            ids.append(getId(element))

    return set(ids)

def fillMachines(machines):
    if len(machines) != 0:
        return machines

    for i in range(1, numMachines + 1):
        machines.add(i)

    return machines

tests = []
with open(args.input, 'r') as file:
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

            tests.append((int(duration), fillMachines(getIds(unformattedMachines)), getIds(unformattedResources)))

def comparator(test1, test2):
    resourcesDiff = -(len(test1[2]) - len(test2[2]))
    if resourcesDiff != 0:
        return resourcesDiff

    machinesDiff = len(test1[1]) - len(test2[1])
    if machinesDiff != 0:
        return machinesDiff

    return -(test1[0] - test2[0])

tests.sort(key=cmp_to_key(comparator))

durations = []
machines = []
resources = []

for test in tests:
    durations.append(test[0])
    machines.append(test[1])
    resources.append(test[2])

def calculatePossibleMakespans(durations):
    minDuration = max(durations)
    possibleMakespans = {minDuration}

    for i in range(2, len(durations)):
        for combination in itertools.combinations(durations, i):
            currentDuration = sum(combination)
            if currentDuration > minDuration:
                possibleMakespans.add(currentDuration)

    uniqueMakespans = list(possibleMakespans)
    uniqueMakespans.sort()
    uniqueMakespans.append(sum(durations))
    return uniqueMakespans

def calculateCombinations(durations):
    possibleSums = {0}

    for i in range(1, len(durations)):
        for combination in itertools.combinations(durations, i):
            possibleSums.add(sum(combination))
        
    return possibleSums

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

minizincSolver = Model("./Solver.mzn")
gecode = Solver.lookup("gecode")

def solveWithLowerBoundVar():
    instance = Instance(gecode, minizincSolver)

    instance["nTests"] = numTests
    instance["nMachines"] = numMachines
    instance["nResources"] = numResources

    instance["durations"] = durations
    instance["machinesAvailable"] = machines
    instance["resourcesRequired"] = resources

    result = instance.solve()

    print("makespan: " + str(result["lowerBound"]))


def solveWithLinearLowerBound():
    print("O maximo lowerBound é " + str(sum(durations)))
    for i in range(max(durations), sum(durations) + 1):
        instance = Instance(gecode, minizincSolver)

        instance["nTests"] = numTests
        instance["nMachines"] = numMachines
        instance["nResources"] = numResources
        instance["durations"] = durations
        instance["machinesAvailable"] = machines
        instance["resourcesRequired"] = resources
        instance["lowerBound"] = i

        print("Vai tentar o lowerbound " + str(i))
        result = instance.solve()

        if result.status == Status.SATISFIED:
            print("makespan: " + str(i))
            break

def solveWithBinaryLowerBound():
    print("O maximo lowerBound é " + str(sum(durations)))
    l = max(durations)
    r = sum(durations)

    while l < r - 1:
        mid = int((l + r) / 2)

        instance = Instance(gecode, minizincSolver)

        instance["nTests"] = numTests
        instance["nMachines"] = numMachines
        instance["nResources"] = numResources
        instance["durations"] = durations
        instance["machinesAvailable"] = machines
        instance["resourcesRequired"] = resources
        instance["lowerBound"] = mid

        print("Vai tentar o lowerbound " + str(mid))
        result = instance.solve()

        lastStatus = result.status
        if result.status == Status.SATISFIED:
            print("Satisfez: " + str(mid))
            r = mid
        else:
            print("Não satisfez: " + str(mid))
            l = mid

    if lastStatus == Status.SATISFIED:
        makespan = l
    else:
        makespan = r

    print("Makespan: " + str(makespan))

solveWithBinaryLowerBound()