import random

class DNA:
    def __init__(self, data):
        self.data = list(data)

    def __repr__(self):
        return "{0.__class__.__name__}({0.data})".format(self)

    def __iter__(self):
        return iter(self.data)

    def __eq__(self, other):
        return self.data == other.data

    def crossover(self, other):
        new_data = list(random.choice((gene1, gene2))
                        for gene1, gene2 in zip(self, other))
        return DNA(new_data)

#arithmetical average
def average(*args):
    return sum(args) / len(args)

#weighted average
def weighted_average(numbers):
    return sum(k * v for k, v in numbers.items()) / sum(numbers.values())

#random weighted average
def random_weighted_average(*args, points_w=4, points_r=4):
    weights = [round(random.uniform(0.25, 0.75), points)
               for _ in range(len(args))]
    pairs = {k: v for k, v in zip(args, weights)}
    return round(_wavg(pairs), points)

_avg = average
_wavg = weighted_average
_rwavg = random_weighted_average

class NumDNA(DNA):
    def crossover(self, other):
        new_data = list(random_weighted_average(gene1, gene2)
                        for gene1, gene2 in zip(self, other))
        return NumDNA(new_data)

class Specimen:
    def __init__(self, dna, fit_function):
        self.dna = dna
        self.fit_function = fit_function

    def __repr__(self):
        return "{0.__class__.__name__}({0.dna}, {0.fit_function})".format(self)

    @property
    def _astuple(self):
        return (self.dna, self.fit_function)

    def __eq__(self, other):
        return self._astuple == other._astuple
    
    def crossover(self, other):
        return Specimen(self.dna.crossover(other.dna), self.fit_function)

    def get_fitness(self):
        return self.fit_function(self.dna)


if __name__ == "__main__":
    d_one = DNA("1234")
    d_two = DNA("5678")
    one = Specimen(d_one, None)
    two = Specimen(d_two, None)
    for i in range(3):
        print(Specimen.crossover(one, two))
