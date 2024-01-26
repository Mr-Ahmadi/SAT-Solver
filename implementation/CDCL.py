import random
from typing import List


class RetVal:
    r_satisfied = 0
    r_unsatisfied = 1
    r_normal = 2


class SATSolverCDCL:
    def __init__(self):
        self.literals = []
        self.literal_list_per_clause = []
        self.literal_frequency = []
        self.literal_polarity = []
        self.original_literal_frequency = []
        self.literal_count = 0
        self.clause_count = 0
        self.kappa_antecedent = 0
        self.literal_decision_level = []
        self.literal_antecedent = []
        self.assigned_literal_count = 0
        self.already_unsatisfied = False
        self.pick_counter = 0
        self.random_generator = random.Random()
        self.generator = random.Random()

    def initialize(self):
        self.literal_count = int(input("number of variables: "))
        self.clause_count = int(input("number of clauses: "))
        self.assigned_literal_count = 0
        self.kappa_antecedent = -1
        self.pick_counter = 0
        self.already_unsatisfied = False
        self.literals = [-1] * self.literal_count
        self.literal_frequency = [0] * self.literal_count
        self.literal_polarity = [0] * self.literal_count
        self.literal_list_per_clause = [[] for _ in range(self.clause_count)]
        self.literal_antecedent = [-1] * self.literal_count
        self.literal_decision_level = [-1] * self.literal_count
        literal_count_in_clause = 0
        for i in range(self.clause_count):
            literal_count_in_clause = 0
            while True:
                literal = int(input("literal (0 to start new clause): "))
                if literal > 0:
                    self.literal_list_per_clause[i].append(literal)
                    self.literal_frequency[literal - 1] += 1
                    self.literal_polarity[literal - 1] += 1
                elif literal < 0:
                    self.literal_list_per_clause[i].append(literal)
                    self.literal_frequency[-1 - literal] += 1
                    self.literal_polarity[-1 - literal] -= 1
                else:
                    if literal_count_in_clause == 0:
                        self.already_unsatisfied = True
                    break
                literal_count_in_clause += 1
        self.original_literal_frequency = self.literal_frequency[:]

    def CDCL(self):
        decision_level = 0
        if self.already_unsatisfied:
            return RetVal.r_unsatisfied
        unit_propagate_result = self.unit_propagate(decision_level)
        if unit_propagate_result == RetVal.r_unsatisfied:
            return unit_propagate_result
        while not self.all_variables_assigned():
            picked_variable = self.pick_branching_variable()
            decision_level += 1
            self.assign_literal(picked_variable, decision_level, -1)
            while True:
                unit_propagate_result = self.unit_propagate(decision_level)
                if unit_propagate_result == RetVal.r_unsatisfied:
                    if decision_level == 0:
                        return unit_propagate_result
                    decision_level = self.conflict_analysis_and_backtrack(
                        decision_level
                    )
                else:
                    break
        return RetVal.r_satisfied

    def unit_propagate(self, decision_level):
        unit_clause_found = False
        false_count = 0
        unset_count = 0
        literal_index = 0
        satisfied_flag = False
        last_unset_literal = -1
        while True:
            unit_clause_found = False
            for i in range(len(self.literal_list_per_clause)):
                false_count = 0
                unset_count = 0
                satisfied_flag = False
                for j in range(len(self.literal_list_per_clause[i])):
                    literal_index = self.literal_to_variable_index(
                        self.literal_list_per_clause[i][j]
                    )
                    if self.literals[literal_index] == -1:
                        unset_count += 1
                        last_unset_literal = j
                    elif (
                        self.literals[literal_index] == 0
                        and self.literal_list_per_clause[i][j] > 0
                    ) or (
                        self.literals[literal_index] == 1
                        and self.literal_list_per_clause[i][j] < 0
                    ):
                        false_count += 1
                    else:
                        satisfied_flag = True
                        break
                if satisfied_flag:
                    continue
                if unset_count == 1:
                    self.assign_literal(
                        self.literal_list_per_clause[i][last_unset_literal],
                        decision_level,
                        i,
                    )
                    unit_clause_found = True
                    break
                elif false_count == len(self.literal_list_per_clause[i]):
                    self.kappa_antecedent = i
                    return RetVal.r_unsatisfied
            if not unit_clause_found:
                break
        self.kappa_antecedent = -1
        return RetVal.r_normal

    def assign_literal(self, variable, decision_level, antecedent):
        literal = self.literal_to_variable_index(variable)
        value = 1 if variable > 0 else 0
        self.literals[literal] = value
        self.literal_decision_level[literal] = decision_level
        self.literal_antecedent[literal] = antecedent
        self.literal_frequency[literal] = -1
        self.assigned_literal_count += 1

    def unassign_literal(self, literal_index):
        self.literals[literal_index] = -1
        self.literal_decision_level[literal_index] = -1
        self.literal_antecedent[literal_index] = -1
        self.literal_frequency[literal_index] = self.original_literal_frequency[
            literal_index
        ]
        self.assigned_literal_count -= 1

    def literal_to_variable_index(self, variable):
        return variable - 1 if variable > 0 else -variable - 1

    def conflict_analysis_and_backtrack(self, decision_level):
        learnt_clause = self.literal_list_per_clause[self.kappa_antecedent][:]
        conflict_decision_level = decision_level
        this_level_count = 0
        resolver_literal = 0
        literal = 0
        while True:
            this_level_count = 0
            for i in range(len(learnt_clause)):
                literal = self.literal_to_variable_index(learnt_clause[i])
                if self.literal_decision_level[literal] == conflict_decision_level:
                    this_level_count += 1
                if (
                    self.literal_decision_level[literal] == conflict_decision_level
                    and self.literal_antecedent[literal] != -1
                ):
                    resolver_literal = literal
            if this_level_count == 1:
                break
            learnt_clause = self.resolve(learnt_clause, resolver_literal)
        self.literal_list_per_clause.append(learnt_clause)
        for i in range(len(learnt_clause)):
            literal_index = self.literal_to_variable_index(learnt_clause[i])
            update = 1 if learnt_clause[i] > 0 else -1
            self.literal_polarity[literal_index] += update
            if self.literal_frequency[literal_index] != -1:
                self.literal_frequency[literal_index] += 1
            self.original_literal_frequency[literal_index] += 1
        self.clause_count += 1
        backtracked_decision_level = 0
        for i in range(len(learnt_clause)):
            literal_index = self.literal_to_variable_index(learnt_clause[i])
            decision_level_here = self.literal_decision_level[literal_index]
            if (
                decision_level_here != conflict_decision_level
                and decision_level_here > backtracked_decision_level
            ):
                backtracked_decision_level = decision_level_here
        for i in range(len(self.literals)):
            if self.literal_decision_level[i] > backtracked_decision_level:
                self.unassign_literal(i)
        return backtracked_decision_level

    def resolve(self, input_clause, literal):
        second_input = self.literal_list_per_clause[self.literal_antecedent[literal]][:]
        input_clause.extend(second_input)
        i = 0
        while i < len(input_clause):
            if input_clause[i] == literal + 1 or input_clause[i] == -literal - 1:
                input_clause.pop(i)
            else:
                i += 1
        input_clause.sort()
        input_clause = list(set(input_clause))
        return input_clause

    def pick_branching_variable(self):
        random_value = random.randint(1, 10)
        too_many_attempts = False
        attempt_counter = 0
        while True:
            if (
                random_value > 4
                or self.assigned_literal_count < self.literal_count / 2
                or too_many_attempts
            ):
                self.pick_counter += 1
                if self.pick_counter == 20 * self.literal_count:
                    for i in range(len(self.literals)):
                        self.original_literal_frequency[i] //= 2
                        if self.literal_frequency[i] != -1:
                            self.literal_frequency[i] //= 2
                    self.pick_counter = 0
                variable = self.literal_frequency.index(max(self.literal_frequency))
                if self.literal_polarity[variable] >= 0:
                    return variable + 1
                return -variable - 1
            else:
                while attempt_counter < 10 * self.literal_count:
                    variable = random.randint(0, self.literal_count - 1)
                    if self.literal_frequency[variable] != -1:
                        if self.literal_polarity[variable] >= 0:
                            return variable + 1
                        return -variable - 1
                    attempt_counter += 1
                too_many_attempts = True

    def all_variables_assigned(self):
        return self.literal_count == self.assigned_literal_count

    def show_result(self, result_status):
        if result_status == RetVal.r_satisfied:
            print("SAT")
            for i in range(len(self.literals)):
                if i != 0:
                    print(" ", end="")
                if self.literals[i] != -1:
                    print(pow(-1, (self.literals[i] + 1)) * (i + 1), end="")
                else:
                    print(i + 1, end="")
        else:
            print("UNSAT")

    def solve(self):
        result_status = self.CDCL()
        self.show_result(result_status)


solver = SATSolverCDCL()
solver.initialize()
solver.solve()
