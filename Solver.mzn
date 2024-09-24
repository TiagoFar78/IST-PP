int: nTests;
int: nMachines;
int: nResources;

array[1..nTests] of int: durations;
array[1..nTests] of set of int: machinesAvailable;
array[1..nTests] of set of int: resourcesRequired;

int: minAvailableMachines = max([card(machinesAvailable[i]) | i in 1..nTests]);
int: minMachinesUsed = min(nTests, minAvailableMachines);

array[1..nTests] of var 0..nMachines: tasksMachine;
array[1..nTests] of var 0..sum(durations) - min(durations): startTimes;
array[1..nMachines] of var 0..nTests: machineUsage;
array[1..nMachines] of var 0..sum(durations): machineEndTime;

constraint forall(t in 1..nTests) (
    tasksMachine[t] in machinesAvailable[t]
);

constraint forall(t1 in 1..nTests, t2 in 1..nTests) (
    if t1 != t2 /\ tasksMachine[t1] == tasksMachine[t2] then 
        startTimes[t1] + durations[t1] <= startTimes[t2] \/ startTimes[t2] + durations[t2] <= startTimes[t1] 
    endif
);

constraint forall(r in 1..nResources, t1 in 1..nTests, t2 in 1..nTests) (
    if t1 != t2 /\ r in resourcesRequired[t1] /\ r in resourcesRequired[t2] then
        startTimes[t1] + durations[t1] <= startTimes[t2] \/ startTimes[t2] + durations[t2] <= startTimes[t1] 
    endif
);

constraint forall(m in 1..nMachines) (
    machineUsage[m] = sum(t in 1..nTests where tasksMachine[t] == m) (1)
);

constraint sum(m in 1..nMachines)(if machineUsage[m] > 0 then 1 else 0 endif) >= minMachinesUsed;

constraint forall(m in 1..nMachines) (
    machineEndTime[m] = sum(t in 1..nTests where tasksMachine[t] == m) (startTimes[t] + durations[t])
);

constraint forall(t in 1..nTests) (
    let {
        array[int] of var int: availableEndTimes = [machineEndTime[m] | m in machinesAvailable[t]],
        var int: minEndTime = min([availableEndTimes[i] | i in index_set(availableEndTimes)])
    } in

    exists(m in machinesAvailable[t]) (
        machineEndTime[m] == minEndTime /\ tasksMachine[t] == m
    )
);

solve minimize max([startTimes[t] + durations[t] | t in 1..nTests]);