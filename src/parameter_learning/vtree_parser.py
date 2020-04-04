class VtreeNode:
    def __init__(self, node_id, children):
        self.id = node_id
        self.children = children

    def get_depth(self):
        depths = []
        if len(self.children) == 0:
            return 0

        for c in self.children:
            depths.append(c.get_depth() + 1)
        return max(depths)


def read_vtree(filename):
    f = open(filename, "r")
    lines = f.readlines()
    lines = [line.strip("\n").split(" ") for line in lines]
    nodes = {}
    root = None
    for line in lines:
        if line[0] == "c" or line[0] == "vtree":
            continue
        elif line[0] == "I":
            # Internal node
            parent = line[1]
            left_child = line[2]
            right_child = line[3]
            root = VtreeNode(line[1], [nodes[left_child], nodes[right_child]])
            nodes[line[1]] = root

        elif line[0] == "L":
            # Leaf node
            #new_node = VtreeNode(line[1], [])
            nodes[line[1]] = VtreeNode(line[1], [])

    return root


def get_vtree_depth(filename):
    tree = read_vtree(filename)
    return tree.get_depth() - 1
