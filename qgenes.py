import random

from genetics import NumDNA, Specimen, percent_chance, \
                     NOFITNESS, weighted_average

from qutils import get_possible_outcomes

def _top_nonempty(column):
    result = 0
    for i, block in enumerate(reversed(column)):
        if not block.empty:
            result = i + 1
    return result

def agg_height(board, top_nonempty_list=None):
    if top_nonempty_list is None:
        top_nonempty_list = [_top_nonempty(col) for col in board.columns]
    return sum(top_nonempty_list)

def complete_lines(board):
    count = 0
    for row in board.mask:
        if not any(e for e in row):
            count += 1
    return count

def count_holes(board):
    count = 0
    for col in board.columns:
        found_empty = 0
        for block in reversed(col):
            if block.empty:
                found_empty += 1
            if not block.empty and found_empty:
                count += found_empty
                break
    return count

def _pairs01(seq):
    last = seq[0]
    for item in seq[1:]:
        yield last, item
        last = item

def bumpiness(board, top_nonempty_list=None):
    count = 0
    if top_nonempty_list is None:
        top_nonempty_list = [_top_nonempty(col) for col in board.columns]
    for first_top, second_top in _pairs01(top_nonempty_list):
        count += abs(first_top - second_top)
    return count

def fitness_pw(parameters, weights):
    return sum(param * weight for param, weight in zip(parameters, weights))

def get_parameters(board):
    top_nonempty_list = [_top_nonempty(col) for col in board.columns]
    parameters = [agg_height(board, top_nonempty_list),
                  complete_lines(board),
                  count_holes(board),
                  bumpiness(board, top_nonempty_list)]
    return parameters

def fitness(board, weights):
    parameters = get_parameters(board)
    return fitness_pw(parameters, weights)


class qDNA(NumDNA):
    def mutated(self, points=4):
        data = self.data.copy()
        for i, item in enumerate(data):
            if percent_chance(10):
                part = round(random.uniform(-0.25, 0.25) * item, points)
                data[i] = item + part
        return qDNA(data)
                
    def mutate(self):
        self.data = self.mutated().data


class qSpecimen(Specimen):
    def crossover(self, other, autocalc=False, points=4):
        if not autocalc:
            _definedfitness = lambda o: o._fitness is not NOFITNESS
            msg = "Fitness was not yet calculated"
            assert _definedfitness(self) and _definedfitness(other), msg
        diff = self.fitness - other.fitness
        if diff < 0:
            w1, w2 = 0, -diff
        elif diff > 0:
            w1, w2 = 0, diff
        else:
            w1 = w2 = 0
        w1 += 1; w2 += 1
        data1, data2 = self.dna.data, other.dna.data
        rdata = []
        for item1, item2 in zip(data1, data2):
            rdata.append(round(weighted_average({item1: w1, item2: w2}),
                               points))
        return qSpecimen(qDNA(rdata), self.fit_function)
