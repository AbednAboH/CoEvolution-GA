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


class RPS(DNA):
    def __init__(self):
        DNA.__init__(self)
        self.robots_score=[]
    def character_creation(self, target_size):
        return random.randint(0, 2)


