int: testsAmount = 10;
int: maxMakeSpan = 15;

int: t1Size = 2;
int: t2Size = 4;
int: t3Size = 3;
int: t4Size = 4;
int: t5Size = 3;
int: t6Size = 2;
int: t7Size = 1;
int: t8Size = 2;
int: t9Size = 3;
int: t10Size = 5;

array[1..t1Size] of var 1..maxMakeSpan: t1;
array[1..t2Size] of var 1..maxMakeSpan: t2;
array[1..t3Size] of var 1..maxMakeSpan: t3;
array[1..t4Size] of var 1..maxMakeSpan: t4;
array[1..t5Size] of var 1..maxMakeSpan: t5;
array[1..t6Size] of var 1..maxMakeSpan: t6;
array[1..t7Size] of var 1..maxMakeSpan: t7;
array[1..t8Size] of var 1..maxMakeSpan: t8;
array[1..t9Size] of var 1..maxMakeSpan: t9;
array[1..t10Size] of var 1..maxMakeSpan: t10;

array[1..maxMakeSpan] of var 0..testsAmount: m1;
array[1..maxMakeSpan] of var 0..testsAmount: m2;
array[1..maxMakeSpan] of var 0..testsAmount: m3;

array[1..maxMakeSpan] of var 0..testsAmount: r1;

% Constraints

constraint t1[1] = t1[2] - 1;
constraint t2[1] = t2[2] - 1 /\ t2[2] = t2[3] - 1 /\ t2[3] = t2[4] - 1;
constraint t3[1] = t3[2] - 1 /\ t3[2] = t3[3] - 1;
constraint t4[1] = t4[2] - 1 /\ t4[2] = t4[3] - 1 /\ t4[3] = t4[4] - 1;
constraint t5[1] = t5[2] - 1 /\ t5[2] = t5[3] - 1;
constraint t6[1] = t6[2] - 1;
constraint t8[1] = t8[2] - 1;
constraint t9[1] = t9[2] - 1 /\ t9[2] = t9[3] - 1;
constraint t10[1] = t10[2] - 1 /\ t10[2] = t10[3] - 1 /\ t10[3] = t10[4] - 1 /\ t10[4] = t10[5] - 1;

constraint forall(i in 1..maxMakeSpan) (m2[i] != 7 /\ m3[i] != 7);
constraint forall(i in 1..maxMakeSpan) (m1[i] != 8 /\ m3[i] != 8);
constraint forall(i in 1..maxMakeSpan) (m1[i] != 9 /\ m2[i] != 9);
constraint forall(i in 1..maxMakeSpan) (m2[i] != 10);

constraint forall(i in 1..t2Size) (r1[t2[i]] == 2);
constraint forall(i in 1..t3Size) (r1[t3[i]] == 3);
constraint forall(i in 1..t4Size) (r1[t4[i]] == 4);

constraint forall(i in 1..t1Size) (m1[t1[i]] == 1) \/ forall(i in 1..t1Size) (m2[t1[i]] == 1) \/ forall(i in 1..t1Size) (m3[t1[i]] == 1);
constraint forall(i in 1..t2Size) (m1[t2[i]] == 2) \/ forall(i in 1..t2Size) (m2[t2[i]] == 2) \/ forall(i in 1..t2Size) (m3[t2[i]] == 2);
constraint forall(i in 1..t3Size) (m1[t3[i]] == 3) \/ forall(i in 1..t3Size) (m2[t3[i]] == 3) \/ forall(i in 1..t3Size) (m3[t3[i]] == 3);
constraint forall(i in 1..t4Size) (m1[t4[i]] == 4) \/ forall(i in 1..t4Size) (m2[t4[i]] == 4) \/ forall(i in 1..t4Size) (m3[t4[i]] == 4);
constraint forall(i in 1..t5Size) (m1[t5[i]] == 5) \/ forall(i in 1..t5Size) (m2[t5[i]] == 5) \/ forall(i in 1..t5Size) (m3[t5[i]] == 5);
constraint forall(i in 1..t6Size) (m1[t6[i]] == 6) \/ forall(i in 1..t6Size) (m2[t6[i]] == 6) \/ forall(i in 1..t6Size) (m3[t6[i]] == 6);
constraint forall(i in 1..t7Size) (m1[t7[i]] == 7) \/ forall(i in 1..t7Size) (m2[t7[i]] == 7) \/ forall(i in 1..t7Size) (m3[t7[i]] == 7);
constraint forall(i in 1..t8Size) (m1[t8[i]] == 8) \/ forall(i in 1..t8Size) (m2[t8[i]] == 8) \/ forall(i in 1..t8Size) (m3[t8[i]] == 8);
constraint forall(i in 1..t9Size) (m1[t9[i]] == 9) \/ forall(i in 1..t9Size) (m2[t9[i]] == 9) \/ forall(i in 1..t9Size) (m3[t9[i]] == 9);
constraint forall(i in 1..t10Size) (m1[t10[i]] == 10) \/ forall(i in 1..t10Size) (m2[t10[i]] == 10) \/ forall(i in 1..t10Size) (m3[t10[i]] == 10);


solve satisfy;














