import os.path
import factory as CounterFactory
from WMC import WeightedModelCounter
from pysdd.sdd import SddManager, Vtree


def get_weights_from_cnf_file(filename):
    weights = []
    with open(os.path.abspath(filename), "r") as f:
        output = f.readlines()

    for line in output:
        if "weight" in line:
            splitted = line.strip("\n").split(" ")
            weights = splitted[2:]
            weights = [w for w in weights if len(w) > 0]
            weights = [float(w) for w in weights]
            break

    return weights


class SDD(WeightedModelCounter):
    """ WMC using the SDD package, which allows users to construct, manipulate, and optimize SDDs. """

    def __init__(self):
        pass

    # Based on http://pysdd.readthedocs.io/en/latest/examples/model_counting.html
    def do_model_count(self, filename):
        # create vtree
        vtree_path = CounterFactory.create("minic2d").create_vtree(filename)
        vtree = Vtree.from_file(bytes(vtree_path.encode()))

        sdd = SddManager.from_vtree(vtree)

        # read CNF
        root = sdd.read_cnf_file(bytes(filename.encode()))

        # do model counting
        wmc = root.wmc(log_mode=False)

        # add weights
        weights = get_weights_from_cnf_file(filename)
        lits = [sdd.literal(i) for i in range(1, sdd.var_count() + 1)]
        assert len(weights) == 2 * len(lits), \
            "Unexpected len {} for weights, got {}. Weights:\n{}".format(len(weights), 2 * len(lits), weights)

        for i in range(len(lits)):
            wmc.set_literal_weight(lits[i], weights[2 * i])
            wmc.set_literal_weight(-lits[i], weights[2 * i + 1])

        # write visualisation of SDD and Vtree to files
        sdd_file = os.path.abspath(os.path.join(os.path.dirname(filename), "sdd."))
        vtree_file = os.path.abspath(os.path.join(os.path.dirname(filename), "vtree-sdd."))

        with open(sdd_file + "dot", "w") as out:
            out.write(sdd.dot())
        with open(vtree_file + "dot", "w") as out:
            out.write(vtree.dot())


        return wmc.propagate()

    def get_stats_for_cnf(self, cnf):
        return {"More stats with SDD as model counter": "not supported"}
