import random

from fitness_functions import fitness_selector
from mutations import mutations
import math
import numpy


# have to fill hash table with different keys when getting the command from main


# basic class for all problem sets because fittness and the member of the population are problem specific
# ,and we have to eliminate problem specifc parameters from the Genetic algorithem
# might dd mutate !
def city_dist(city, neighbor):
    # calculates euclidean distance between two cities
    dx = city.x - neighbor.x
    dy = city.y - neighbor.y
    distance = math.sqrt(dx ** 2 + dy ** 2)
    return distance


class Agent:
    fitnesstype = fitness_selector().select

    def __init__(self):
        self.object = []
        # self.learning_fitness = 0
        # self.algo_huristic = None
        self.age = 0
        self.fitness = 15
        self.solution = ""

    # creates a member of the population
    def create_object(self, target_size, target, options=None):
        return self.object

    def character_creation(self, target_size):
        pass

    def Learning_fitness(self, target, target_size, huristic):
        self.learning_fitness = self.fitnesstype[huristic](self, target, target_size)
        return self.learning_fitness

    # function to calculate the fitness for this specific problem

    def calculate_fittness(self, target, target_size, select_fitness, age_update=True):
        self.fitness = self.fitnesstype[select_fitness](self, target, target_size)
        self.age += 1 if age_update else 0
        return self.fitness

    def create_special_parameter(self, target_size):
        pass

    # for sorting purposes
    def __lt__(self, other):
        return self.fitness < other.fitness

    def __str__(self):
        bstr = ""
        for i in self.object:
            bstr += str(i) + ","
        bstr += self.solution
        return bstr

    def __repr__(self):
        bstr = ""
        for i in self.object:
            bstr += str(i) + " "
        return bstr

    # def __eq__(self, other):
    #     self.fitness = other.fitness
    #     self.object = other.object
    # age !
    def hash(self, other):
        return self.object


# class for first problem
class DNA(Agent):
    mutation = mutations()

    def __init__(self):
        Agent.__init__(self)
        self.diversity = 0
        # self.spiecy = 0
        self.networks_tested = 0

    def create_object(self, target_size, target, options=None):
        self.object = []
        for j in range(target_size):
            self.object += [self.character_creation(target_size)]
        self.create_special_parameter(target_size)
        return self.object

    def character_creation(self, target_size):
        return chr((random.randint(0, 90)) + 32)

    def mutate(self, target_size, member, mutation_type, options):
        self.mutation.select[mutation_type](target_size, member, options)

    def hash(self, other):
        return ''.join(self.object + other.object)


class Sorting(DNA):
    def __init__(self):
        super(Sorting, self).__init__()

    def create_object(self, target_size, target, options=None):
        self.object = [i for i in range(1, target_size + 1)]
        random.shuffle(self.object)


class network(DNA):
    def __init__(self):
        super(network, self).__init__()
        depth = 0

    def create_object(self, target_size, target, options=None):
        # todo: V define how to create the network'
        optimal_network_size = target[1]
        for i in range(round(optimal_network_size)):
            op = self.valid_insertion(i, options) if i > 0 else options
            self.object.append(self.character_create(len(op), op))

    def character_create(self, target_size, options):
        return random.choice(options)

    def solve_network(self, set, target_size):
        new_set = [i for i in set.object]
        for index, comperator in enumerate(self.object):
            self.compare(comperator[0] - 1, comperator[1] - 1, new_set)

        # if the solution is valid update diversity
        set.diversity += 1 if self.check_solution(new_set, target_size) else 0
        set.networks_tested += 1
        return new_set

    def check_solution(self, set, target_size):
        for i in range(1, target_size + 1):
            if i != set[i - 1]:
                return False
        return True

    def apply(self, sets, target_size, target):
        all_sets_sorted = []
        for set in sets:
            set.diversity = 0
            set.networks_tested = 0
            all_sets_sorted.append(self.solve_network(set, target_size))
        sum_of_sets = 0
        for set in sets:
            sum_of_sets += set.diversity
        # we want the lower number
        depth = self.get_depth()
        factor = len(depth) / target[2]
        if factor != 1.0:
            factor = 100 * factor
        else:
            factor = 0
        self.fitness = factor + 100 * (1 - sum_of_sets / len(sets))
        return all_sets_sorted

    def compare(self, first, second, set):
        if set[first] <= set[second]:
            return
        else:
            set[first], set[second] = set[second], set[first]

    def get_depth(self):
        depth = [[]]
        d = 0
        for i in range(len(self.object)):
            if not i:
                depth[d].append(self.object[0])
            else:
                flag = self.depth_check(depth[d], self.object[i])
                d = d + 1 if flag else d
                depth.append([self.object[i]]) if flag else depth[d].append(self.object[i])
        return depth

    def get_depth_at_index(self, i):
        depth = self.get_depth()
        count = 0
        depth_of_currnet = []
        newdepth = 0
        for d in depth:
            newdepth += 1
            for _ in depth:
                count += 1
                if count == i + 1:
                    depth_of_currnet.append(newdepth)

        return depth, newdepth - 1

    def __str__(self):
        bst = ""
        depth = self.get_depth()
        for index, i in enumerate(depth):
            bst += "depth " + str(index + 1) + ": "
            for j in i:
                bst += "(" + str(j[0]) + "," + str(j[1]) + ")"
            bst += " \n "

        return bst

    def depth_check(self, lista, items):
        [i1, i2] = items
        for list in lista:
            if i1 not in list and i2 not in list:
                continue
            else:
                return True
        return False

    def valid_insertion(self, ipos, options):
        depth, index = self.get_depth_at_index(ipos)
        tabu = depth[index]
        index_minus = index - 1 > 0 and len(depth) > 0
        index_plus = len(depth) - 1 >= index + 1
        if index_minus:
            for i in depth[index - 1]:
                tabu.append(i)
        if index_plus:
            for i in depth[index + 1]:
                tabu.append(i)

        new_options = [opt for opt in options if opt not in tabu]
        return new_options
