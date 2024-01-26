def DPLL(cnf):
    if not cnf:
        return True
    if any(not clause for clause in cnf):
        return False
    for clause in cnf:
        if len(clause) == 1:
            literal = clause[0]
            cnf = unit_propagate(cnf, literal)
            return DPLL(cnf)
    literal = cnf[0][0]
    cnf = unit_propagate(cnf, literal)
    if DPLL(cnf):
        return True
    cnf = unit_propagate(cnf, -literal)
    return DPLL(cnf)


def unit_propagate(cnf, literal):
    new_cnf = [clause for clause in cnf if literal not in clause]
    new_cnf = [list(filter(lambda l: l != -literal, clause)) for clause in new_cnf]
    return new_cnf


cnf = [
    [-2, 1, 3],
    [-2, 1, 3],
    [2, 1, 3],
]
result = DPLL(cnf)
print(result)
