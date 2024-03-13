import queue

class Graph:
    """
    Represents a graph using an adjacency list representation.
    Edges are bidirectional to ensure the graph is undirected.
    """
    def __init__(self):
        self.graph = {}

    def add_edge(self, v, w):
        """Adds an edge between vertices v and w."""
        if v not in self.graph:
            self.graph[v] = []
        if w not in self.graph:
            self.graph[w] = []
        self.graph[v].append(w)
        self.graph[w].append(v)

def read_graph(file_path):
    """
    Reads a graph and the number of colors from a given file.
    Expects a specific format detailed in the problem statement.
    """
    colors = 0
    graph = Graph()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            if line.startswith('colors'):
                colors = int(line.split('=')[1])
                continue
            v, w = map(int, line.split(','))
            graph.add_edge(v, w)
    return graph, colors

class CSP:
    """
    Defines a Constraint Satisfaction Problem (CSP) for graph coloring.
    Variables, domains, and constraints are based on the graph structure.
    """

    def __init__(self, graph, colors):
        self.variables = list(graph.graph.keys())
        self.domains = {var: list(range(1, colors + 1)) for var in self.variables}
        self.neighbors = graph.graph

    def is_consistent(self, var, value, assignment):
        """
        Checks if assigning a value to a variable is consistent with the CSP constraints.
        """
        for neighbor in self.neighbors.get(var, []):
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True

    def select_unassigned_variable(self, assignment):
        """Selects the next unassigned variable using the Minimum Remaining Values (MRV) heuristic."""
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]), default=None)

    def order_domain_values(self, var, assignment):
        """Returns the ordered list of domain values for a variable."""
        return self.domains[var]

def ac3(csp):
    """
    Applies the AC3 algorithm to enforce arc consistency.
    Returns False if an inconsistency is found, True otherwise.
    """
    q = queue.Queue()
    for xi in csp.variables:
        for xj in csp.neighbors[xi]:
            q.put((xi, xj))
    while not q.empty():
        (xi, xj) = q.get()
        if revise(csp, xi, xj):
            if len(csp.domains[xi]) == 0:
                return False
    return True

def revise(csp, xi, xj):
    """Revises the domain of xi to satisfy the constraint between xi and xj."""
    revised = False
    for x in csp.domains[xi][:]:
        if all(not csp.is_consistent(xi, x, {xj: y}) for y in csp.domains[xj]):
            csp.domains[xi].remove(x)
            revised = True
    return revised

def backtrack(csp, assignment={}):
    """
    Implements the backtracking search algorithm.
    Returns a solution as a variable-value assignment if one exists.
    """
    if len(assignment) == len(csp.variables):
        return assignment
    var = csp.select_unassigned_variable(assignment)
    if var is None:
        return None
    for value in csp.order_domain_values(var, assignment):
        if csp.is_consistent(var, value, assignment):
            local_assignment = assignment.copy()
            local_assignment[var] = value
            result = backtrack(csp, local_assignment)
            if result is not None:
                return result
    return None


# Test Code
# Input file is gc_78317094521100.txt
# Input file and this Python file is in the same directory
file_path = 'gc_78317094521100.txt'
graph, colors = read_graph(file_path)
csp = CSP(graph, colors)

if ac3(csp):
    solution = backtrack(csp)
    if solution:
        for var in sorted(solution.keys()):
            print(f"Vertex {var}: Color {solution[var]}")
    else:
        print("No solution found.")
else:
    print("AC3 failed to reduce domains to a solvable state.")
