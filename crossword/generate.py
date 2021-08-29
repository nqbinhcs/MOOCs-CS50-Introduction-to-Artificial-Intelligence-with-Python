import sys
from typing import AsyncIterable, NoReturn

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # removing the words from list words which do not satisfy the length of variable
        for var in self.domains:
            var_length = var.length
            var_domain = {
                word for word in self.domains[var] if len(word) == var_length}
            self.domains[var] = var_domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # get overlap
        overlap = self.crossword.overlaps[x, y]
        removed_domain = set()
        # check if overlap
        if overlap:
            # position in x
            pos_x = overlap[0]
            # position in y
            pos_y = overlap[1]
            for word_x in self.domains[x]:
                # check if the word from domain of x conflict with doman of y, removing this word from domain of x
                flag = max(word_y[pos_y] == word_x[pos_x]
                           for word_y in self.domains[y])
                if flag:
                    continue
                removed_domain.add(word_x)
            self.domains[x] -= removed_domain
        return len(removed_domain) > 0

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # initial
        if arcs:  # not None
            queue = arcs
        else:  # None
            # all arcs of the problem
            queue = [
                (x, y) for x in self.crossword.variables for y in self.crossword.variables if x != y]
        while len(queue):
            # dequeue
            (x, y) = queue[0]
            queue.pop(0)
            # revise
            if self.revise(x, y):
                # if no choice from domain
                if len(self.domains[x]) == 0:
                    return False
                # related arcs
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        number_variables = len(self.crossword.variables)
        number_assigned_variables = len(assignment)
        # check if set of values equals values
        return number_assigned_variables == number_variables

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if all values are distinct
        assigned_values = list(assignment.values())
        if len(assigned_values) != len(set(assigned_values)):
            return False

        for x in assignment:
            # check if correct length
            if x.length != len(assignment[x]):
                return False
            # check if conflict with neighbors
            for y in self.crossword.neighbors(x):
                if y in assignment:
                    if self.conflict((x, assignment[x]), (y, assignment[y])):
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # list value of domain by constraining values
        values = list()
        for value in self.domains[var]:
            # init counter
            count = 0
            for neighbor in self.crossword.neighbors(var):
                # if neighbor is not assigned
                if neighbor not in assignment:
                    # add to counter if value is also in domain of neighbor
                    count += (value in self.domains[neighbor])
            values.append((value, count))

        # sort by least constraining values
        values.sort(key=lambda x: x[1])
        return [value[0] for value in values]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # unassigned variables list
        unassignment = list()
        for variable in self.crossword.variables:
            if variable not in assignment:
                unassignment.append((variable, len(self.domains[variable])))

        # sort by domain value
        unassignment.sort(key=lambda x: x[1])
        domain_values = set(map(lambda x: x[1], unassignment))

        # grouping elements which has the same domain value
        new_unassignment = [[x[0] for x in unassignment if x[1] == y]
                            for y in domain_values]
        unassignment = new_unassignment

        # sort each group by degree
        for group_domain in unassignment:
            group_domain.sort(key=lambda x: len(
                self.crossword.neighbors(x)), reverse=True)

        # flat list
        unassignment = [x for sublist in unassignment for x in sublist]
        return unassignment[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            # assigning var to value
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            else:
                # removing if not satisfied
                del assignment[var]
        return None

    def conflict(self, assigned_x, assigned_y):
        # check the assigned variable have the confliction with other assigned variable
        (x, word_x) = assigned_x
        (y, word_y) = assigned_y
        (pos_x, pos_y) = self.crossword.overlaps[x, y]
        return word_x[pos_x] != word_y[pos_y]


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    creator.enforce_node_consistency()
    assignment = creator.solve()
    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
