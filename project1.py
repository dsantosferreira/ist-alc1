#!/usr/bin/python3
# alc25 - 6 - project1 
# DO NOT remove or edit the lines above. Thank you.

# PROBLEM VARIABLES
# D - Number of days
# S - Number of shifts in each day. E.g. if S = 4 then there are 4 shifts each day, each one during 6 hours
# R(s, d) - Minimum number of nurses necessary to work in shift s (1 <= s <= S) of day d (1 <= d <= D)
# N/Nk - Set of all nurses / kth nurse
# M - Set of nurses that have managerial qualification (N contains M)
# L(k)min/L(k)max - Minimum/Maximum number of shifts nurse k can do each day
# Hk - Maximum number of shifts that each nurse can do during the D days
# P(k,s,d) - cost of assigning nurse k to shift s in day d

# RESTRICTIONS
# [X] Each shift has a minimum number of necessary nurses to be present
# [X] Work schedule of a nurse in each day must be continuous, that is, there cannot exist a pause between two shifts in a single day
# [X] Each nurse has a minimum and maximum number of shifts it can do each day
# [X] Each nurse can only do Hk shifts throughout the D days
# [X] Each shift must have a nurse with managerial qualifications
# [X] A nurse is never assigned to a shift in which she said she was unavailable
# [X] The cost of assignment is minimized


from sys import stdin
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.card import CardEnc, EncType

cutoff = 6

# Reads the problem specification from the standard input
def load_input():
    input = {"nurses_managerial": [], "min_nurses": [], "nurse_shifts": [], "costs": [], "vars": []}

    input["days"], input["shifts"] = map(int, stdin.readline().split())

    for _ in range(input["days"]):
        input["min_nurses"].append([int(n) for n in stdin.readline().split()])
    
    input["nurses"] = int(stdin.readline().split()[0])

    input["vars"] = [[[d*input["shifts"]*input["nurses"] + s*input["nurses"] + n + 1 for n in range(input["nurses"])] for s in range(input["shifts"])] for d in range(input["days"])]

    input["top_id"] = input["days"] * input["shifts"] * input["nurses"]

    for _ in range(input["nurses"]):
        line = stdin.readline().split()
        input["nurses_managerial"].append(1 if line[0] == "Y" else 0)
        input["nurse_shifts"].append((int(line[1]), int(line[2]), int(line[3])))
    
    for _ in range(input["days"]):
        input["costs"].append([[int(c) for c in stdin.readline().split()] for _ in range(input["shifts"])])
    
    return input

# Each variable x_k,s,d tells us if nurse k is assigned to shift s in day d

# Negate shifts that are impossible for a nurse to work on due to the L_min restriction
def precompute(input):
    shifts = input["shifts"]
    for d in range(input["days"]):
        for n in range(input["nurses"]):
            p1 = 0
            
            while p1 < shifts:
                while p1 < shifts and input["costs"][d][p1][n] == -1:
                    p1 += 1

                p2 = p1
                while p2 < shifts and input["costs"][d][p2][n] != -1:
                    p2 += 1
                
                if p2 - p1 < input["nurse_shifts"][n][0]:
                    while p1 != p2:
                        input["costs"][d][p1][n] = -1
                        p1 += 1
                    p1 += 1
                else:
                    p1 = p2 + 1

# Each shift has a minimum number of necessary nurses to be present
def encode_min_nurses(input, enc):
    for d in range(input["days"]):
        for s in range(input["shifts"]):
            # Get list of available nurses
            available = []

            for n in range(input["nurses"]):
                if input["costs"][d][s][n] != -1:
                    available.append(input["vars"][d][s][n])
            
            encoding = EncType.totalizer if len(available) > cutoff or input["min_nurses"][d][s] > cutoff else EncType.seqcounter
            # Create cardinality constraint
            card_enc = CardEnc.atleast(lits=available, bound=input["min_nurses"][d][s], top_id=input["top_id"], encoding=encoding)
            for clause in card_enc:
                enc.add_clause(clause)
            
            if card_enc.nv > 0:
                input["top_id"] = card_enc.nv
    return enc

# Work schedule of a nurse in each day must be continuous, that is, there cannot exist a pause between two shifts in a single day
def encode_continous_shifts(input, enc):
    for d in range(input["days"]):
        for n in range(input["nurses"]):
            for s1 in range(0, input["shifts"]-2):
                if input["costs"][d][s1][n] == -1:
                    continue
                for s2 in range(s1 + 2, input["shifts"]):
                    if input["costs"][d][s2][n] == -1:
                        continue
                    enc.add_clause([-input["vars"][d][s1][n], input["vars"][d][s1+1][n], -input["vars"][d][s2][n] ])
    return enc


# Each nurse has a minimum and maximum number of shifts it can do each day
def encode_shifts_per_day(input, enc):
    for d in range(input["days"]):
        for n in range(input["nurses"]):
            lits = [input["vars"][d][s][n] for s in range(input["shifts"]) if input["costs"][d][s][n] != -1]
            encoding = EncType.totalizer if len(lits) > cutoff or input["nurse_shifts"][n][0] > cutoff else EncType.seqcounter
            card_enc = CardEnc.atleast(lits=lits, bound=input["nurse_shifts"][n][0], top_id = input["top_id"], encoding=encoding)
            for clause in card_enc.clauses:
                enc.add_clause(clause)

            if card_enc.nv > 0:
                input["top_id"] = card_enc.nv

            encoding = EncType.totalizer if len(lits) > cutoff or input["nurse_shifts"][n][1] > cutoff else EncType.seqcounter
            card_enc = CardEnc.atmost(lits=lits, bound=input["nurse_shifts"][n][1], top_id = input["top_id"], encoding=encoding)
            for clause in card_enc.clauses:
                enc.add_clause(clause)
            
            if card_enc.nv > 0:
                input["top_id"] = card_enc.nv
    return enc

# Each nurse can only do Hk shifts throughout the D days
def encode_max_shifts(input, enc):
    for n in range(input["nurses"]):
        lits = [input["vars"][d][s][n] for d in range(input["days"]) for s in range(input["shifts"]) if input["costs"][d][s][n] != -1]
        encoding = EncType.totalizer if len(lits) > cutoff or input["nurse_shifts"][n][2] > cutoff else EncType.seqcounter
        card_enc = CardEnc.atmost(lits=lits, bound=input["nurse_shifts"][n][2], top_id=input["top_id"], encoding=encoding)
        for clause in card_enc:
            enc.add_clause(clause)
        
        if card_enc.nv > 0:
            input["top_id"] = card_enc.nv
    return enc

# Each shift must have at least one nurse with managerial qualifications
def encode_min_managerial(input, enc):
    for d in range(input["days"]):
        for s in range(input["shifts"]):
            enc.add_clause([input["vars"][d][s][n] for n in range(input["nurses"]) if input["costs"][d][s][n] != -1 and input["nurses_managerial"][n]])
    return enc

# A nurse is never assigned to a shift in which she said she was unavailable
# The cost of assignment is minimized
def encode_costs(input, enc):
    for d in range(input["days"]):
        for s in range(input["shifts"]):
            for n in range(input["nurses"]):
                if input["costs"][d][s][n] == -1:
                    enc.add_clause([-input["vars"][d][s][n]])
                else:
                    enc.add_clause([-input["vars"][d][s][n]], weight=input["costs"][d][s][n])
    return enc

def print_output(enc, D, S, N):
    model = [l for l in enc.compute() if l <= D*S*N and l > 0]
    print(enc.cost)
    for d in range(D):
        for s in range(S):
            shift_nurses = [n+1 for n in range(N) if d*S*N + s*N + n + 1 in model]
            print(len(shift_nurses), end='')
            for nurse in shift_nurses:
                print(" " + str(nurse), end='')
            print()


def main():
    input = load_input()
    enc = RC2(WCNF(), solver='cd19')

    precompute(input)
    enc = encode_min_nurses(input, enc)
    enc = encode_continous_shifts(input, enc)
    enc = encode_shifts_per_day(input, enc)
    enc = encode_max_shifts(input, enc)
    enc = encode_min_managerial(input, enc)
    enc = encode_costs(input, enc)

    print_output(enc, input["days"], input["shifts"], input["nurses"])

if __name__ == "__main__":
    main()
