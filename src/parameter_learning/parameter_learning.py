import math, random, numpy as np, time
from builtins import open, list, len, map

# PySDD imports (known issue with DSharp for macOS ...)
from pysdd.sdd import SddManager, Vtree, WmcManager

DATA_FILE = "data.pl" # DATA_FILE = "custom_data.pl"
NB_EXAMPLES = 1000

# CNF variables
vars =	[
    "stress(a)", "stress(b)", "stress(c)",
    "smokes(a)", "smokes(b)", "smokes(c)",
    "friends(a,b)", "friends(a,c)", "friends(b,a)", "friends(b,c)", "friends(c,a)", "friends(c,b)",
    "aux(a,b)", "aux(a,c)", "aux(b,a)", "aux(b,c)", "aux(c,a)", "aux(c,b)",
]
rands = [random.random() for i in range(0,6)]
weights =	[
    0.2, 0.8, 0.2, 0.8, 0.2, 0.8,
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
    # rands[0], 1-rands[0], rands[1], 1-rands[1], rands[2], 1-rands[2], rands[3], 1-rands[3], rands[4], 1-rands[4], rands[5], 1-rands[5],
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
]
# neg_weights = [math.log(weights[i]) for i in range(1,len(weights),2)]
# pos_weights = [math.log(weights[i]) for i in range(0,len(weights),2)]
neg_weights = [weights[i] for i in range(1,len(weights),2)]
pos_weights = [weights[i] for i in range(0,len(weights),2)]
weights_array = np.asarray(list(reversed(neg_weights)) + pos_weights)
def vidx(var):
    return 1 + vars.index(var)

# Parameters to determine
parameters_strings = ["friends(a,b)", "friends(a,c)", "friends(b,a)", "friends(b,c)", "friends(c,a)", "friends(c,b)"]
parameters = list(map(vidx, parameters_strings))

# Process examples
def examples(file, cap=20):
    with open(file) as f:
        example = []
        i = 0
        for line in f:
            if line.strip().startswith('---'):
                yield example
                example = []
                i += 1
                if i >= cap:
                    return
            else:
                evidence = line[9:-3]
                value = False if evidence[0:2] == "\+" else True
                atom = evidence if value else evidence[2:]
                index = vidx(atom)
                example += [index] if value else [-index]

# Creation of base program CNF.
#   This is by no means general, there's little point in doing so since
#   ProbLog already provides the required functionality.
clauses = []
def add_rule1(head, var1, var2, var3, var4, var5):
    # (a <=> (b | (c & d) | (e & f)))
    # ... becomes ...
    # (~a | b | c | e) &
    # (~a | b | c | f) &
    # (~a | b | d | e) &
    # (~a | b | d | f) &
    # (~b | a) &
    # (~c | ~d | a) &
    # (~e | ~f | a)
    clauses.append([-vidx(head), vidx(var1), vidx(var2), vidx(var4)])
    clauses.append([-vidx(head), vidx(var1), vidx(var2), vidx(var5)])
    clauses.append([-vidx(head), vidx(var1), vidx(var3), vidx(var4)])
    clauses.append([-vidx(head), vidx(var1), vidx(var3), vidx(var5)])
    clauses.append([-vidx(var1), vidx(head)])
    clauses.append([-vidx(var2), -vidx(var3), vidx(head)])
    clauses.append([-vidx(var4), -vidx(var5), vidx(head)])
def add_rule2(head, var1, var2, var3):
    # (a <=> b | (c & d))
    # ... becomes ...
    # (~a | b | c) &
    # (~a | b | d) &
    # (~b | a) &
    # (~c | ~d | a)
    clauses.append([-vidx(head), vidx(var1), vidx(var2)])
    clauses.append([-vidx(head), vidx(var1), vidx(var3)])
    clauses.append([-vidx(var1), vidx(head)])
    clauses.append([-vidx(var2), -vidx(var3), vidx(head)])
def tostr(clause):
    output = ""
    for literal in clause:
        output += str(literal) + " "
    return output + "0"
add_rule1("smokes(a)", "stress(a)", "friends(a,b)", "aux(a,b)", "friends(a,c)", "aux(a,c)")
add_rule1("smokes(b)", "stress(b)", "friends(b,a)", "aux(b,a)", "friends(b,c)", "aux(b,c)")
add_rule1("smokes(c)", "stress(c)", "friends(c,a)", "aux(c,a)", "friends(c,b)", "aux(c,b)")
add_rule2("aux(a,b)", "stress(b)", "friends(b,c)", "stress(c)")
add_rule2("aux(a,c)", "stress(c)", "friends(c,b)", "stress(b)")
add_rule2("aux(b,a)", "stress(a)", "friends(a,c)", "stress(c)")
add_rule2("aux(b,c)", "stress(c)", "friends(c,a)", "stress(a)")
add_rule2("aux(c,a)", "stress(a)", "friends(a,b)", "stress(b)")
add_rule2("aux(c,b)", "stress(b)", "friends(b,a)", "stress(a)")
# clauses.append([7]) # This adds stress(c) as evidence
cnf = "p cnf " + str(len(vars)) + " " + str(len(clauses)) + "\n" \
    + "c weights " + " ".join([str(weight) for weight in weights]) + "\n" \
    + "\n".join(list(map(tostr, clauses)))
# print(cnf)

# Test : generate SDD and do weighted model counting
(manager, sdd) = SddManager.from_cnf_string(cnf)
# manager.auto_gc_and_minimize_off()
wmc = sdd.wmc(log_mode=False)
wmc.set_literal_weights_from_array(weights_array)
w = wmc.propagate()
print("Weighted model count: " + str(w))

# Get interpretations
interpretations = list(examples(DATA_FILE, cap=NB_EXAMPLES))

# Generate SDD for each example
counters = []
header_cnf = "p cnf " + str(len(vars)) + " " + str(len(clauses) + 6) + "\n" \
    + "\n".join(list(map(tostr, clauses)))
header_query_cnf = "p cnf " + str(len(vars)) + " " + str(len(clauses) + 7) + "\n" \
    + "\n".join(list(map(tostr, clauses)))
for interpretation in interpretations:
    wmcs = dict.fromkeys(parameters)
    for parameter in parameters:
        example_query_cnf = header_query_cnf + "\n" + \
                            "\n".join([str(p) + " 0" for p in interpretation]) + \
                            "\n" + str(parameter) + " 0"
        (_, sdd) = SddManager.from_cnf_string(example_query_cnf)
        wmc = sdd.wmc(log_mode=False)
        wmc.set_literal_weights_from_array(weights_array)
        wmcs[parameter] = wmc
        # print("Model count for example : " + str(wmc.propagate()))
    (_, sdd) = SddManager.from_cnf_string(header_cnf + "\n" + "\n".join([str(p) + " 0" for p in interpretation]))
    wmc = sdd.wmc(log_mode=False)
    wmc.set_literal_weights_from_array(weights_array)
    counters.append((wmc, wmcs))
    # print("Model count for example : " + str(wmc.propagate()))

# EM algorithm
iteration = 1
max_iterations = 2000
weights = dict.fromkeys(parameters, 0.0)
for i in range(0, max_iterations):
    delta = 0 # Maximum update of weights
    totals = dict.fromkeys(parameters, 0.0)
    for (wmc, wmcs) in counters:
        count_evidence = wmc.propagate()
        # print(count_evidence)
        for parameter in parameters:
            count_evidence_query = wmcs[parameter].propagate()
            # print(count_evidence_query)
            marginal = count_evidence_query / count_evidence
            # print(marginal)
            totals[parameter] += marginal
    for parameter in parameters:
        previous = weights[parameter]
        weights[parameter] = totals[parameter] / len(interpretations)
        delta = max(delta, abs(previous - weights[parameter]))
        for (wmc, wmcs) in counters:
            wmc.set_literal_weight(parameter, weights[parameter])
            wmc.set_literal_weight(-parameter, 1.0 - weights[parameter])
            for other in parameters:
               wmcs[other].set_literal_weight(parameter, weights[parameter])
               wmcs[other].set_literal_weight(-parameter, 1.0 - weights[parameter])
    if delta < np.finfo(float).eps:
        break
    iteration += 1
    print("New weights : " + " --- ".join([str(x) for x in weights.values()]))
    print("Starting iteration " + str(iteration) + " ...")

for parameter_string in parameters_strings:
    print(parameter_string + " : " + str(weights[vidx(parameter_string)]))