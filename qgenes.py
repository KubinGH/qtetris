import random

from genetics import NumDNA, Specimen, percent_chance, \
                     NOFITNESS, weighted_average

from qutils import get_possible_outcomes

from fitfuncs import c_agg_height, c_complete_lines, c_top_nonempty, \
                     c_count_holes, c_bumpiness

top_nonempty = c_top_nonempty
agg_height = c_agg_height
complete_lines = c_complete_lines
count_holes = c_count_holes
bumpiness = c_bumpiness

def fitness_pw(parameters, weights):
    return sum(param * weight for param, weight in zip(parameters, weights))

def get_parameters(board):
    top_nonempty_list = [top_nonempty(col) for col in board.columns]
    parameters = [agg_height(board, top_nonempty_list),
                  complete_lines(board),
                  count_holes(board, top_nonempty_list),
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
