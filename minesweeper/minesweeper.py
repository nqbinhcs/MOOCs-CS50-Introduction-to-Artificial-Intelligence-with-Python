import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()
        # Check the condition that if number of cells in a sentence equals count, all cells in the sentences are mines
        if len(self.cells) == self.count:
            for (i, j) in self.cells:
                mines.add((i, j))

        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()
        # Check the condition that if number of cells in a sentence equals 0, all cells in the sentences are safe
        if self.count == 0:
            for (i, j) in self.cells:
                safes.add((i, j))
        return safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Check if cell in cells
        if cell in self.cells:
            # decrease size of cells
            self.count -= 1
            # remove cell in cells
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Check if cell in cells
        if cell in self.cells:
            # remove cell in cells
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1
        self.moves_made.add(cell)
        # 2
        self.mark_safe(cell)
        # 3
        cells = set()
        neighbor_cells = self.neighbor_cell(cell)
        count_cpy = count
        for n_cell in neighbor_cells:
            if n_cell in self.moves_made:
                if n_cell in self.mines:
                    count_cpy -= 1
            else:
                cells.add(n_cell)

        new_sentence = Sentence(cells, count_cpy)
        # Add new sentence
        self.knowledge.append(new_sentence)
        # 4
        self.update_knowledge()
        # 5
        self.conclude_from_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            # check if cell has not been used
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                # check if cell has not been used and are not mine
                if cell not in self.moves_made and cell not in self.mines:
                    return cell
        return None

    def neighbor_cell(self, cell):
        cells = set()
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    cells.add((i, j))
        return cells

    def update_knowledge(self):
        # copy knowledge
        knowledge_cpy = self.knowledge

        # update mines, safes from knowledge base
        for sentence in knowledge_cpy:
            mines = sentence.known_mines()
            safes = sentence.known_safes()

            if mines:
                for mine in mines:
                    self.mark_mine(mine)

            if safes:
                for safe in safes:
                    self.mark_safe(safe)

    def conclude_from_knowledge(self):
        # sentence is not useful needed to be removed
        need_delete = []

        for i in range(0, len(self.knowledge)):
            for j in range(0, i):
                # copy first sentence
                sentence_i = copy.deepcopy(self.knowledge[i])
                # copy second sentence
                sentence_j = copy.deepcopy(self.knowledge[j])
                # second set always is greater than first set
                if sentence_i.count > sentence_j.count:
                    # swap
                    sentence_i, sentence_j = sentence_j, sentence_i
                # check first set is subset of second subset
                if sentence_i.cells.issubset(sentence_j.cells):
                    # new set
                    new_cells = sentence_j.cells - sentence_i.cells
                    # new count
                    new_count = sentence_j.count - sentence_i.count
                    # new sentence which is inferred from two sentences
                    new_sentence = Sentence(new_cells, new_count)
                    self.knowledge.append(new_sentence)
                    # second sentence is not useful, so it is needed to removed
                    need_delete.append(sentence_j)

        # remove sentences from knowledge base
        for no_need_sentence in need_delete:
            if no_need_sentence in self.knowledge:
                self.knowledge.remove(no_need_sentence)

        # update knowledge
        self.update_knowledge()
