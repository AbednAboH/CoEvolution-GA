# class for fitness functions , add your fitness function here !
import math
from settings import BIN, HIGH_PENALTY, PENALTY, LIV_DIST, KINDL_TAU
from numpy import unique
import numpy

hash_table = {}


class fitness_selector:
    def __init__(self):
        self.select = {0: self.sets_fitness,1:self.networks_fitness}

    def sets_fitness(self, object, target, target_size,networks,sets):

        for network in networks:
            network.solve_network(object,target_size)

        object.fitness=100*object.diversity/object.networks_tested

    def networks_fitness(self, object, target, target_size,networks,sets):
        object.apply( sets,target_size,target)
        return object.fitness



