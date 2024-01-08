def DPLL(cnf):
    if not cnf:
        return True
    if any(not clause for clause in cnf):
        return False
    for clause in cnf:
        if len(clause) == 1:
            literal = clause[0]
            cnf = unitPropagate(cnf, literal)
            return DPLL(cnf)
    literal = cnf[0][0]
    cnf = unitPropagate(cnf, literal)
    if DPLL(cnf):
        return True
    cnf = unitPropagate(cnf, -literal)
    return DPLL(cnf)


def unitPropagate(cnf, literal):
    newCnf = [clause for clause in cnf if literal not in clause]
    newCnf = [list(filter(lambda l: l != -literal, clause)) for clause in newCnf]
    return newCnf


cnf = [
    [-2, 1, 3],
    [-2, 1, 3],
    [2, 1, 3],
]
result = DPLL(cnf)
print(result)
