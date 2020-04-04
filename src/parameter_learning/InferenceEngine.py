import copy

from timeit import default_timer as timer
from CNF import CNF
from FOLTheory import FOLTheory
from GroundProblogParser import GroundProblogParser
from factory import create as create_weighted_model_counter


class InferenceEngine:
    def __init__(self, counter="minic2d"):
        self.problog_parser = GroundProblogParser()
        self.weighted_model_counter = create_weighted_model_counter(counter)

    def ground_problog_evaluate(self, ground_program, print_steps=False):
        """ Evaluates a problog program and returns the results. """
        start = timer()
        ttime = timer()
        # parse the ground program to the internal representation of ground problog
        problog_program = self.problog_parser.program_to_problog(ground_program)
        if print_steps:
            print("GROUND PROGRAM:")
            print(problog_program)
            print("====================================================")
        time_parsed_ground_problog = str(round(timer() - ttime, 3)) + "s"
        ttime = timer()

        # convert the GroundProblog to a FOLTheory
        fol_theory = FOLTheory.create_from_problog(problog_program)
        if print_steps:
            print("FOL theory:")
            print(fol_theory)
            print("----------------------------------------------------")
        time_converted_to_fol = str(round(timer() - ttime, 3)) + "s"
        ttime = timer()

        # convert the FOLTheory to its CNF representation
        cnf = CNF.create_from_fol_theory(fol_theory)
        if print_steps:
            print("CNF:")
            print(cnf)
            print("====================================================")

            # convert the CNF to dimacs format for the weighted model counter
            print("DIMACS:")
            print(cnf.to_dimacs())
            print("====================================================")
        time_converted_to_cnf = str(round(timer() - ttime, 3)) + "s"
        ttime = timer()

        # do the model counting
        results, stats = self.weighted_model_counter.evaluate_cnf(cnf, return_stats=True, print_steps=print_steps)
        time_model_counting = str(round(timer() - ttime, 3)) + "s"
        time_total = str(round(timer() - start, 3)) + "s"

        stats["Time to parse ground problog"] = time_parsed_ground_problog
        stats["Time to convert ground problog to first order logic"] = time_converted_to_fol
        stats["Time to convert first order logic to CNF"] = time_converted_to_cnf
        stats["Time for all model counting"] = time_model_counting
        stats["Total runtime"] = time_total
        if print_steps:
            print("====================================================")
            print("EVALUATION:")
            query_str_len = max([len(q) for q, _ in results]) if results else None
            for query, probability in results:
                print("{:<{}}: {}".format(query, query_str_len, probability))

            print("----------------------------------------------------")
            print("STATS:")
            for stat in stats:
                print("\t" + stat + ": ", stats[stat])

        return results

    def interpretation_to_cnf_evidence(self, interpretation):
        """ Converts a ProbLog interpretation to a list of CNF evidence. """
        problog_program = self.problog_parser.program_to_problog(interpretation)
        fol_theory = FOLTheory.create_from_problog(problog_program)
        cnf = CNF.create_from_fol_theory(fol_theory)
        return cnf.get_evidence()

    def ground_problog_learn_parameters(self, ground_program, interpretations, print_steps=False):
        """ Learns parameters in a ground_problog file using Expectation Maximization. """
        start = timer()

        # initial values for the probabilities to be learned have already been set during parsing

        # parse the ground program to the internal representation of ground problog
        problog_program = self.problog_parser.program_to_problog(ground_program)
        if print_steps:
            print("GROUND PROGRAM:")
            print(problog_program)
            print("====================================================")

        # convert the GroundProblog to a FOLTheory
        fol_theory = FOLTheory.create_from_problog(problog_program)
        fol_theory.delete_queries()

        if print_steps:
            print("FOL theory:")
            print(fol_theory)
            print("----------------------------------------------------")

        # convert the FOLTheory to its CNF representation
        cnf = CNF.create_from_fol_theory(fol_theory)

        # get the probabilities that need to be learned/tuned and add them as queries in the CNF
        tunable_literals = cnf.get_tunable_literals_as_dict()
        for tunable_lit_name in tunable_literals:
            cnf.add_query(tunable_literals[tunable_lit_name])

        if print_steps:
            print("CNF:")
            print(cnf)
            print("====================================================")
            # convert the CNF to dimacs format for the weighted model counter
            print("DIMACS:")
            print(cnf.to_dimacs())
            print("====================================================")
            print("INITIAL TUNABLE PROBABILITIES:")
            print([(name, lit.weight_true) for name, lit in tunable_literals.items()])
            print("====================================================")

        iteration = 0
        converged = False
        while not converged and iteration < 100:
            iteration += 1

            # update the weights of the tunable probabilities in the CNF at every iteration
            for name, lit in tunable_literals.items():
                cnf.set_literal_weights(name, lit.weight_true, 1 if lit.weight_false == 1 else 1 - lit.weight_true)

            # add each interpretation as evidence to the CNF and sum up the results of the queries
            literal_weight_sums = dict.fromkeys(tunable_literals.keys(), 0)
            for interpretation in interpretations:
                # add the interpretation as evidence in a copy of the CNF
                cnf_copy = copy.deepcopy(cnf)
                for evidence in self.interpretation_to_cnf_evidence(interpretation):
                    cnf_copy.add_evidence(evidence)

                # do model counting with the evidence
                results = self.weighted_model_counter.evaluate_cnf(cnf_copy, return_stats=False, print_steps=False)
                for query, prob in results:
                    literal_weight_sums[query] += prob

            # update the tunable probabilities and determine whether or not convergence has been reached
            all_converged = True
            for name, summ in literal_weight_sums.items():
                new_weight = summ / len(interpretations)
                tunable_lit = tunable_literals[name]

                if abs(tunable_lit.weight_true - new_weight) > 0.005:
                    all_converged = False

                tunable_lit.weight_true = new_weight
                tunable_literals[name] = tunable_lit

            converged = all_converged
            print("probabilities after iteration {}: {}".format(iteration, [(name, lit.weight_true) for name, lit in tunable_literals.items()]))

        if print_steps:
            print("====================================================")
            print("FINAL LEARNED PARAMETERS:")
            query_str_len = max([len(k) for k in tunable_literals.keys()])
            for query, literal in tunable_literals.items():
                print("{:<{}}: {}".format(query, query_str_len, literal.weight_true))

        print("Total runtime:", str(round(timer() - start, 3)) + "s")
        return tunable_literals
