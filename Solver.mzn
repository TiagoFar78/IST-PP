int: nTests;
int: nMachines;
int: nResources;
%int: lowerBound;

array[1..nTests] of int: durations;
array[1..nTests] of set of int: machinesAvailable;
array[1..nTests] of set of int: resourcesRequired;

array[1..nTests] of var 0..nMachines: tasksMachine;
array[1..nTests] of var 0..sum(durations) - min(durations): startTimes;

var max(durations)..sum(durations): lowerBound;

constraint forall(t in 1..nTests) (
    startTimes[t] + durations[t] <= lowerBound
);

constraint forall(r in 1..nResources, t1 in 1..nTests, t2 in 1..nTests) (
    if t1 != t2 /\ r in resourcesRequired[t1] /\ r in resourcesRequired[t2] then
        startTimes[t1] + durations[t1] <= startTimes[t2] \/ startTimes[t2] + durations[t2] <= startTimes[t1] 
    endif
);

constraint forall(t in 1..nTests) (
    tasksMachine[t] in machinesAvailable[t]
);

constraint forall(t1 in 1..nTests, t2 in 1..nTests) (
    if t1 != t2 /\ tasksMachine[t1] == tasksMachine[t2] then 
        startTimes[t1] + durations[t1] <= startTimes[t2] \/ startTimes[t2] + durations[t2] <= startTimes[t1] 
    endif
);

solve
:: int_search([lowerBound], input_order, indomain_min, complete)
satisfy;