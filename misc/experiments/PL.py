from problog.program import PrologFile, Term
from problog.formula import LogicFormula
from problog.sdd_formula import SDD
import random
import sys
import copy

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
                dict_inter[Term(line[2:])] = value
            else:
                dict_inter[Term(line)] = value
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
    new_weights = dict.fromkeys(query_keys, 0)


    while not converged and iters < 100:
        converged = True

        weight_sums = dict.fromkeys(query_keys, 0)
        for interpretation in interpretations:
            for name, value in interpretation.items():

                term = copy.deepcopy(name)
                term = str(term)
                term = term.split('(')
                term1 = term[0]
                term2 = term[1].split(')')[0]

                program.add_evidence(name, program.get_node_by_name(Term(term1,Term(term2))), value)

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
#ground_progam = file_to_string("test_learn.pl")

# Assign to each tunable parameter a random initialization value
#ground_progam_tunable = init_tunable(ground_progam)

# Write back the prolog file with random initialized tunable probabilities
#f = open('test_learn_tunable.pl', 'w')
#f.write(ground_progam_tunable)


pf = PrologFile("test_learn_tunable.pl")
formula = LogicFormula.create_from(pf)
sdd = SDD.create_from(formula)

queries = [Term('stress',Term('a')), Term('stress',Term('b')), Term('stress',Term('c')), Term('smokes',Term('a')), Term('smokes',Term('b')), Term('smokes',Term('c'))]

# File which holds all the evidence examples
examples = file_to_string('data.pl')

# Retrieve the amount of interpretations that has been specified
interpretations_100 = get_interpretations(examples, 100)

# Format the interpretations in a dictionary form: e.g. 'evidence(\+stress(a))' is translated to {stress(a): False}, ...
resulting_interpretations_100 = parse_interpretations(interpretations_100)


print('Parameter learning in order: ' + str(queries))

param_100, iter_1 = learn_parameters(sdd, resulting_interpretations_100, queries)
print('Convergence after: ' + str(iter_1) + ' iterations')
print('Parameters after learning with 100 examples: ' + str(param_100))


interpretations_500 = get_interpretations(examples, 500)
resulting_interpretations_500 = parse_interpretations(interpretations_500)

param_500, iter_1 = learn_parameters(sdd, resulting_interpretations_500, queries)
print('Convergence after: ' + str(iter_1) + ' iterations')
print('Parameters after learning with 500 examples: ' + str(param_500))


interpretations_1000 = get_interpretations(examples, 1000)
resulting_interpretations_1000 = parse_interpretations(interpretations_1000)

param_1000, iter_1 = learn_parameters(sdd, resulting_interpretations_1000, queries)
print('Convergence after: ' + str(iter_1) + ' iterations')
print('Parameters after learning with 1000 examples: ' + str(param_1000))


interpretations_2000 = get_interpretations(examples, 1999)
resulting_interpretations_2000 = parse_interpretations(interpretations_2000)

param_2000, iter_1 = learn_parameters(sdd, resulting_interpretations_2000, queries)
print('Convergence after: ' + str(iter_1) + ' iterations')
print('Parameters after learning with 2000 examples: ' + str(param_2000))




