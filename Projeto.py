from minizinc import Instance, Model, Solver
import argparse
import re

INPUT_COMMENT = "%"
INPUT_TESTS_AMOUNT = "Number of tests"
INPUT_MACHINES_AMOUNT = "Number of machines"
INPUT_RESOURCES_AMOUNT = "Number of resources"
INPUT_TEST = "test("

parser = argparse.ArgumentParser()
parser.add_argument('input')

args = parser.parse_args()

durations = []
machines = []
resources = []

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

            durations.append(int(duration))
            machines.append(fillMachines(getIds(unformattedMachines)))
            resources.append(getIds(unformattedResources))

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

result = instance.solve()
print("---------------------------------------------------------")
print(result)
print("Makespan: " + str(result["objective"]))