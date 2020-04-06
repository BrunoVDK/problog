import copy
import os.path


class WeightedModelCounter:
    """ Abstract class for weighted model counters. """

    def evaluate_cnf(self, cnf, return_stats=True, print_steps=False):
        """ Executes queries in a given weighted CNF and returns the results. """
        results = {}

        cnf_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Problog", "files", "cnf{}.dimac"))
        cnf_query_filename = cnf_filename.format("")
        cnf_without_query_filename = cnf_filename.format("_without_query")
        with open(cnf_without_query_filename, "w") as file:
            file.write(cnf.to_dimacs())

        evidence = cnf.get_evidence_with_dimacs_numbers()
        queries = cnf.get_queries_with_dimacs_numbers()

        for literal, number in queries:
            if print_steps:
                print("EVALUATING QUERY '{}', DIMACS NUMBER {}".format(literal, number))

            # add the query as a new clause in the CNF
            cnf_with_query = copy.deepcopy(cnf)
            cnf_with_query.add_clause([literal])

            # write the new CNF to a file so that model counting can be done on it with the selected WMC package
            with open(cnf_query_filename, "w") as file:
                file.write(cnf_with_query.to_dimacs())

            # do model count of (theory + evidence + query)
            probability = self.do_model_count(cnf_query_filename)
            if print_steps:
                print("RESULT: {}".format(probability))

            # if CNF has evidence, then need to do model counts on 2 CNFs per query
            # probability of (theory + evidence + query) by probability of (theory + evidence)
            if len(evidence):
                # do model count of (theory + evidence)
                probability_without_query = self.do_model_count(cnf_without_query_filename)
                if print_steps:
                    print("RESULT WITHOUT QUERY: {}".format(probability_without_query))

                probability = probability / probability_without_query

            results[literal.name] = probability

        results = sorted(results.items(), key=lambda kv: kv[0])

        if return_stats:
            stats = self.get_stats_for_cnf(cnf_without_query_filename)
            return results, stats

        return results

    def do_model_count(self, cnf):
        """ Executes weighted model counting on a given weighted CNF and returns its probability. """
        raise NotImplementedError

    def get_stats_for_cnf(self, cnf):
        """ Returns various weighted model counter stats for a given weighted CNF. """
        raise NotImplementedError
