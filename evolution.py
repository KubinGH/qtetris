import random
import multiprocessing
import time
import functools
from queue import Queue
from ast import literal_eval

from app_ai import App
from qgenes import qDNA as DNA, qSpecimen as Specimen

#POOL_SIZE, DESTROY_NUM, RANDADD_NUM, MATE_NUM = 200, 100, 25, 75
#POOL_SIZE, DESTROY_NUM, RANDADD_NUM, MATE_NUM = 100, 60, 15, 25
#POOL_SIZE, DESTROY_NUM, RANDADD_NUM, MATE_NUM = 40, 20, 5, 15
#POOL_SIZE, DESTROY_NUM, RANDADD_NUM, MATE_NUM = 10, 5, 1, 4
POOL_SIZE, DESTROY_NUM, RANDADD_NUM, MATE_NUM = 5, 3, 1, 2
BOUNDS = (1, 1000)

T_LIMIT = 10000
T_TRIES = 5
POOL_WORKERS = 4

def n_min(sequence, n, key=lambda x: x):
    return sorted(sequence, key=key)[:n]

def choose_two_unique(sequence):
    first = second = None
    while first == second or first == second == None:
        first, second = [random.choice(sequence) for _ in range(2)]
    return first, second

def random_positive():
    return random.randint(*BOUNDS)

def random_negative():
    return -random_positive()

def random_data():
    rn, rp = random_negative, random_positive
    return [rn(), rp(), rn(), rn()]

def specimen_fitness(specimen, limit):
    weights = specimen.dna.data
    session = App(tetrimino_limit=limit, weights=weights)
    session.run()
    return session.score

def one_random_specimen():
    return Specimen(DNA(random_data()), specimen_fitness)

def random_specimen_pool(pool_size=POOL_SIZE):
    return [one_random_specimen() for _ in range(pool_size)]

def read_from_file(filename="savedevo_in.txt"):
    result = []
    with open(filename) as file:
        for i, line in enumerate(file.readlines(), 1):
            this = literal_eval(line.strip())
            try:
                assert isinstance(this, list), "Input DNA not a list"
                assert len(this) == 4, "Input DNA not of length 4"
            except AssertionError as e:
                print("Malformed input '{0}' at line no. {1}".format(this, i))
                print("Error: {0}".format(e))
            result.append(this)
    return result

def save_to_file(lst, filename="savedevo_out.txt"):
    with open(filename, "w") as file:
        for item in lst:
            file.write(str(item.dna.data) + "\n")

def calc_fitness(limit, weights):
    scores = []
    for s in range(T_TRIES):
        session = App(tetrimino_limit=limit, weights=weights)
        session.run()
        scores.append(session.score)
    return sum(scores) / len(scores)

def calc_all(specimen_list, limit):
    func = functools.partial(calc_fitness, limit)
    weights_list = [s.dna.data for s in specimen_list]
    with multiprocessing.Pool(POOL_WORKERS) as pool:
        fit_list = pool.map(func, weights_list)
    return fit_list

def generation(specimen_list, limit=T_LIMIT):
    start = time.time()
    print("Calculate scores")
    fit_list = calc_all(specimen_list, limit)
    end = time.time()
    print("Calculated in {0}".format(round(end - start, 3)))
    
    print("(Set fitness to specimen)")
    for specimen, fitness in zip(specimen_list, fit_list):
        specimen._fitness = fitness
    print("Sort specimen")
    specimen_list.sort(key=lambda x: x.fitness)
    best = specimen_list[-1]
    average = sum(s.fitness for s in specimen_list) / len(specimen_list)
    print("Destroy the unworthy")
    specimen_list = specimen_list[DESTROY_NUM:]
    
    print("-Repopulate")
    print("Mate best")
    mate_results = []
    for i in range(MATE_NUM):
        first, second = choose_two_unique(specimen_list)
        mate_results.append(first.crossover(second))
    specimen_list.extend(mate_results)
    print("Random specimen")
    for i in range(RANDADD_NUM):
        specimen_list.append(one_random_specimen())      
    print("Mutation")
    for specimen in specimen_list:
        specimen.mutate()
    print("-----")
    print("THIS GENERATION STATS:")
    print("BEST: {0}; DNA: {1}".format(best.fitness, best.dna.data))
    print("AVERAGE: {0}".format(average))

    return specimen_list
    
if __name__ == "__main__":
    specimen_list = random_specimen_pool()
    for g in range(7):
        print("=====")
        print("Generation {0}".format(g))
        nxt = generation(specimen_list)
    save_to_file(specimen_list)
