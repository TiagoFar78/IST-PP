from minizinc import Instance, Model, Solver
import argparse
import re

INPUT_COMMENT = "%"
INPUT_TESTS_AMOUNT = "Number of tests"
INPUT_MACHINES_AMOUNT = "Number of machines"
INPUT_RESOURCES_AMOUNT = "Number of resources"
INPUT_MAKESPAN = "Maximum makespan"
INPUT_TEST = "test("

parser = argparse.ArgumentParser()
parser.add_argument('input')

args = parser.parse_args()

tests = []

def getId(s):
    return int(s.strip()[2:-1])


def getIds(s):
    ids = []
    unformattedList = s.split(",")
    if len(unformattedList) > 0 and len(unformattedList[0]) > 0:
        for element in unformattedList:
            ids.append(getId(element))

    return ids

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
            elif INPUT_MAKESPAN in line:
                maxMakespan = value
        
        elif line.startswith(INPUT_TEST):
            match = testPattern.search(line)
            id, duration, unformattedMachines, unformattedResources = match.groups()

            tests.append({ 'id': id, 'duration': duration, 'machines': getIds(unformattedMachines), 'resources': getIds(unformattedResources) })

print("Input:")
print("Tests: " + str(numTests))
print("Machines: " + str(numMachines))
print("Resources: " + str(numResources))
print("Maximum makespan: " + str(maxMakespan))

for test in tests:
    print(test)

# Load n-Queens model from file
nqueens = Model("./nqueens.mzn")
# Find the MiniZinc solver configuration for Gecode
gecode = Solver.lookup("gecode")
# Create an Instance of the n-Queens model for Gecode
instance = Instance(gecode, nqueens)
# Assign 4 to n
instance["n"] = 4
result = instance.solve()
# Output the array q
print(result["q"])