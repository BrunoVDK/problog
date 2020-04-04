import re
import os.path
import subprocess
from sys import platform
from WMC import WeightedModelCounter
from vtree_parser import get_vtree_depth

class MiniC2D(WeightedModelCounter):
    """ WMC using the miniC2D package, which does knowledge compilation and model counting based on exhaustive DPLL. """

    def __init__(self, options):
        dir_platform = "darwin" if platform == "darwin" else "linux"
        self.counter_path = os.path.join(os.path.dirname(__file__), "model_counters",
                                         "miniC2D-1.0.0", "bin", dir_platform, "miniC2D")

        if not os.path.exists(self.counter_path):
            raise Exception("Could not find miniC2D installation. Expected location: {}".format(self.counter_path))

        self.options = options

    def create_vtree(self, filename):
        filename = os.path.abspath(filename)
        dir = os.path.dirname(filename)
        vtree_txt = os.path.join(dir, "vtree-minic2d.txt")

        cnf_params = "--cnf {}".format(filename)
        vtree_params = "--vtree_method 3 --vtree_out {}".format(vtree_txt)
        command = "{} {} {} {}".format(self.counter_path, cnf_params, vtree_params, self.options)

        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return vtree_txt

    def do_model_count(self, filename):
        filename = os.path.abspath(filename)

        cnf_params = "--model_counter --cnf {}".format(filename)
        vtree_params = "--vtree_method 3"
        command = "{} {} {} {}".format(self.counter_path, cnf_params, vtree_params, self.options)

        completed_process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = completed_process.stdout.decode()

        # get the model count from the output
        match = re.search(r"Count(/Probability)?\s\t(.*)", output)
        if match is None:
            return None, {}
        return float(match.group(2))

    def get_stats_for_cnf(self, filename):
        filename = os.path.abspath(filename)
        dir = os.path.dirname(filename)
        vtree_txt = os.path.join(dir, "vtree-minic2d.txt")
        vtree_dot = os.path.join(dir, "vtree-minic2d.dot")

        # need to run without --model_counter to generate NNF stats (= SDD nodes and edges)
        nnf_params = "--cnf {}".format(filename)
        vtree_params = "--vtree_method 3 --vtree_out {} --vtree_dot {}".format(vtree_txt, vtree_dot)
        command = "{} {} {} {}".format(self.counter_path, nnf_params, vtree_params, self.options)
        completed_process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = completed_process.stdout.decode()
        # print(output)

        # convert the new vtree.dot file to a png file
        # (graph,) = pydot.graph_from_dot_file(vtree_file + "dot")
        # graph.write_png(vtree_file + "png")

        num_variables = re.search(r"Vars=([0-9]+)", output)
        num_lines = re.search(r"Clauses=([0-9]+)", output)
        num_nodes = re.search(r"\s\sNodes\s+([0-9]+)", output)
        num_edges = re.search(r"\s\sEdges\s+([0-9]+)", output)

        return {
            "Number of variables in the CNF": num_variables.group(1) if num_variables is not None else "MiniC2D segmentation fault",
            "Number of lines in the CNF": num_lines.group(1) if num_lines is not None else "MiniC2D segmentation fault",
            "Depth of the vtree": get_vtree_depth(vtree_txt),
            "Number of nodes in the circuit": num_nodes.group(1) if num_nodes is not None else "MiniC2D segmentation fault",
            "Number of edges in the circuit": num_edges.group(1) if num_edges is not None else "MiniC2D segmentation fault"
        }
