from minizinc import Instance, Model, Solver
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
    machinesDiff = len(test1[1]) - len(test2[1])
    if machinesDiff != 0:
        return machinesDiff

    resourcesDiff = -(len(test1[2]) - len(test2[2]))
    if resourcesDiff != 0:
        return resourcesDiff

    return -(test1[0] - test2[0])

tests.sort(key=cmp_to_key(comparator))

durations = []
machines = []
resources = []

for test in tests:
    durations.append(test[0])
    machines.append(test[1])
    resources.append(test[2])

def calculateCombinations(durations):
    possibleSums = {0}

    for i in range(1, len(durations)):
        for combination in itertools.combinations(durations, i):
            possibleSums.add(sum(combination))
        
    return possibleSums

possibleStartTimes = [0, 422]# calculateCombinations(durations)
possibleStartTimes = list(possibleStartTimes)
possibleStartTimes.sort()
print(possibleStartTimes)
print("len: " + str(len(possibleStartTimes)))

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
instance = Instance(gecode, minizincSolver)

instance["nTests"] = numTests
instance["nMachines"] = numMachines
instance["nResources"] = numResources
instance["durations"] = durations
instance["machinesAvailable"] = machines
instance["resourcesRequired"] = resources
instance["possibleStartTimes"] = possibleStartTimes

result = instance.solve()
print("---------------------------------------------------------")
print(result)
print("Makespan: " + str(result["objective"]))