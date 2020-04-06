import sys
import os.path
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from InferenceEngine import InferenceEngine


def file_to_string(filename):
    with open(filename) as input_file:
        return input_file.read()



def generate_interpretations(file, n):

    interpretations = file.split("\n----------------\n")

    if n > 1999:
        parser.error("There are no more than 2000 examples, please request a smaller amount of examples")
        sys.exit(1)

    interpretations = interpretations[:n]

    return interpretations




parser = argparse.ArgumentParser(description='Arguments for inference')
parser.add_argument("-pl", "--problog_learn", default="/Users/michieljanssen/PycharmProjects/Problog/test_learn.pl", dest="problog_learn", help="Parameter learning on a ground ProbLog file with tunable probabilities")
parser.add_argument("-plt", "--problog_learn_truth", default= "/Users/michieljanssen/PycharmProjects/Problog/test_ground-truth.pl",dest="problog_learn_truth", help="Ground ProbLog file with values probabilities to sample from for parameter learning")
parser.add_argument("-if", "--interpretations_file", default= "/Users/michieljanssen/PycharmProjects/Problog/data.pl", dest="interpretations_file", help="The path to the data examples")
parser.add_argument("-in", "--interpretations_number", default=100, dest="interpretations_number", help="Amount of interpretations that is used during parameter learning")
parser.add_argument("-mc", "--model_counter", dest="model_counter", help="The model counter to use [minic2d, sdd]", default="minic2d")
parser.add_argument("-bn", "--bayesian_network", dest="bn", help="A bayesian network file")

if __name__ == '__main__':
    args = parser.parse_args()


    if args.problog_learn:
        filename = args.problog_learn
    elif args.bn:
        filename = args.bn
    else:
        parser.error("Please provide a problog file (--problog --problog_learn) or a bayesian network (--bayesian_network)")
        sys.exit(1)

    if args.interpretations_file:
        interpretations = args.interpretations_file
    else:
        parser.error("Please provide the interpretations file")
        sys.exit(1)

    if args.model_counter.lower() == "minic2d":
        model_counter = "minic2d"
    elif args.model_counter.lower() == "sdd":
        model_counter = "sdd"
    else:
        parser.error("Given model counter not supported (sdd, minic2d).")
        sys.exit(1)

    engine = InferenceEngine(model_counter)

    if args.problog_learn_truth is None:
        parser.error("Please provide a problog file with ground truth for probabilities filled in for generation of interpretations (--problog_learn_truth).")
        sys.exit(1)

    # if parameter learning, the program expects an already grounded file,
    # as grounding a file without queries would result in an empty program
    ground_program = file_to_string(filename)

    ground_truth_filename = args.problog_learn_truth
    amount_of_interpretations = int(args.interpretations_number)
    examples = file_to_string(interpretations)
    interpretations = generate_interpretations(examples, amount_of_interpretations)
    print(len(interpretations))

    engine.ground_problog_learn_parameters(ground_program, interpretations, print_steps=True)
