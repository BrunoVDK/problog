from problog.program import PrologFile, Term
from problog.formula import LogicFormula
from problog.sdd_formula import SDD
import random
import sys


def get_interpretations(file, n):

    interpretations = file.split("\n----------------\n")

    if n > 1999:
        print("There are no more than 2000 examples, please request a smaller amount of examples")
        sys.exit(1)

    interpretations = interpretations[:n]

    return interpretations

def parse_interpretations(interpretations):

    interpretations_list = []

    for interpretation in interpretations:
        dict_inter = {}

        for line in interpretation.split():
            line = line[9:-2]

            value = False if line[0:2] == "\+" else True
            if value == False:
                dict_inter[line[2:]] = value
            else:
                dict_inter[line] = value
        interpretations_list.append(dict_inter)

    return interpretations_list



def file_to_string(filename):
    with open(filename) as input_file:
        return input_file.read()


def init_tunable(filename):
    for i in range(len(filename)):
        if filename[i] == '_':
            filename = filename[:i] + str(random.uniform(0, 1)) + filename[i + 1:]
        else:
            continue
    return filename


def learn_parameters(program, interpretations, queries):
    iters = 0
    converged = False

    query_keys = [program.get_node_by_name(q) for q in queries]
    #print(queries)
    new_weights = dict.fromkeys(query_keys, 0)

    while not converged and iters < 100:
        converged = True

        weight_sums = dict.fromkeys(query_keys, 0)
        for interpretation in interpretations:
            for name, value in interpretation.items():
                program.add_evidence(name, program.get_node_by_name(Term(str(name))), value)

            evaluation = program.evaluate()
            for query, result in evaluation.items():
                if query in queries:
                    weight_sums[program.get_node_by_name(query)] += result

            program.clear_evidence()
        for key, sum in weight_sums.items():
            new_weight = sum / len(interpretations)

            if abs(new_weights[key] - new_weight) > 0.000005:
                converged = False
            new_weights[key] = new_weight

        program.set_weights(new_weights)
        iters += 1

    return new_weights, iters


# Read in the progam with tunable parameters
ground_progam = file_to_string("test_learn.pl")

# Assign to each tunable parameter a random initialization value
ground_progam_tunable = init_tunable(ground_progam)

# Write back the prolog file with assigned tunable probabilities
f = open('test_learn_tunable.pl', 'w')
f.write(ground_progam_tunable)


pf = PrologFile("test_learn_tunable.pl")
formula = LogicFormula.create_from(pf)
sdd = SDD.create_from(formula)


queries = [Term("stress","a"), Term("stress", "b"), Term("stress", "c"), Term("smokes", "a"), Term("smokes", "b"), Term("smokes", "c")]

# File which holds all the evidence examples
examples = file_to_string('data.pl')

# Retrieve the amount of interpretations that has been specified
interpretations_100 = get_interpretations(examples, 100)

# Format the interpretations in a dictionary form: e.g. 'evidence(\+stress(a))' is translated to {stress(a): False}, ...
resulting_interpretations = parse_interpretations(interpretations_100)



#param_100, iter_1 = learn_parameters(sdd, resulting_interpretations, queries)
# print('Convergence after: ' + str(iter_1) + ' iterations')
# print('Parameters: ' + str(param_100))









