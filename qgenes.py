import random

from genetics import NumDNA, Specimen, percent_chance, \
                     NOFITNESS, weighted_average


def _top_nonempty(column):
    result = 0
    for i, block in enumerate(reversed(column)):
        if not block.empty:
            result = i + 1
    return result

def agg_height(board):
    for i, row in enumerate(reversed(board.rows)):
        if any(not e.empty for e in row):
            continue
        else:
            #the first empty row
            return i
    return len(board.rows)

def complete_lines(board):
    count = 0
    for row in board.rows:
        if all(not e.empty for e in row):
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

def bumpiness(board):
    count = 0
    for first, second in _pairs01(board.columns):
        first_top, second_top = _top_nonempty(first), _top_nonempty(second)
        count += abs(first_top - second_top)
    return count

def get_parameters(board):
    return [agg_height(board),
            complete_lines(board),
            count_holes(board),
            bumpiness(board)]

def fitness_wp(parameters, weights):
    return sum(a * b for param, weight in zip(parameters, weights))

def fitness(board, weights):
    return fitness_wp(get_parameters(board), weights)


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
        print(w1, w2)
        data1, data2 = self.dna.data, other.dna.data
        rdata = []
        for item1, item2 in zip(data1, data2):
            rdata.append(round(weighted_average({item1: w1, item2: w2}),
                               points))
        return qSpecimen(qDNA(rdata), self.fit_function)
