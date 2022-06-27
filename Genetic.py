import random

from function_selection import cross_types
from algorithems import algortithem
from settings import *
from sys import maxsize
import numpy
import math


""" to generalize the problem we created a class that given a population calculates the solution"""




def adaptive_decrease(p, rate, generation):
    return 2 * (p ** 2) * math.exp(rate * generation) / (p + p * math.exp(rate * generation))


class C_genetic_algorithem(algortithem):
    Distance_hash = {}

    def __init__(self, target, tar_size, pop_size, problem_spec,problem_spec2, crosstype, fitnesstype, selection,
                 serviving_mechanizem, mutation, gene_dist, max_iter,mutation_probability=0):
        algortithem.__init__(self, target, tar_size, pop_size, problem_spec, fitnesstype, selection,max_iter)
        self.cross_func = cross_types().select
        self.cross_type=crosstype
        self.serviving = serviving_mechanizem
        self.mutation_type = mutation
        self.set_fitness = self.prob_spec().fitnesstype[gene_dist]
        self.fitness_func= self.prob_spec().fitnesstype
        self.selection_pressure = self.pop_diversity = 0
        self.hyper_mutaion = mutation_probability
        self.trigger_mutation = False
        self.elite_rate=GA_ELITRATE
        self.sorting_networks=[]
        self.problem_spec2=problem_spec2

        #todo:T define below sol
        self.num_networks=300

        self.options=self.create_options()
        temp = problem_spec2()
        temp.create_object(self.target_size, self.target, self.options)
        self.buffer2 = [temp]*self.num_networks
        # todo: add options to send to problem creation , we don't have to create it over and over again'
    def create_options(self):
        options=[]
        for k in range(1,self.target_size+1):
            for j in range(k+1,self.target_size+1):
                options.append([k,j])
        return options

    def init_population(self):
        super(C_genetic_algorithem, self).init_population()
        self.init_networks()
        self.populations=[self.population,self.sorting_networks]
    def init_networks(self):
        # todo:T initiate networks here
        #  1.T update self.sorting_networks
        #  2.T defin new target and targetsize
        for i in range(self.num_networks):
            temp=self.problem_spec2()
            temp.create_object( self.target_size, self.target,self.options)
            self.sorting_networks.append(temp)


    def fitness(self):
        new_sets = self.selection_methods.method["tour2"](self.population, self.fitness_array)
        for network in self.sorting_networks:
            # todo :T change selection scheme of which ones to check
            # todo:T apply should sort each set and update the sets fitness and the networks fitness
            network.apply(new_sets,self.target_size,self.target)
        for set in self.population:
            set.fitness=100*set.diversity/set.networks_tested if set.networks_tested else set.fitness

    def propablities_rank_based(self,pop_size,population):

        # depending on the selection scheme get propabilities from ranking system !
        multiplier = 1 if self.selection == SUS or RWS else 0.5  # for now keep it like this
        # scale fitness values with linear ranking for sus and RWS
        fitness_array=[]
        if self.selection == SUS:

            mio = pop_size
            fitness_array = numpy.array([p_linear_rank(mio, int(i)) for i in range(pop_size - 1, -1, -1)])
        # get accumulative sum of above values
        elif self.selection == RWS:
            mean = numpy.mean(fitness_array)
            std = numpy.std(fitness_array)
            # linear scale
            fitness_array = numpy.array([i for i in range((pop_size + 1) * 10, 10, -10)])
            # sigma scale
            fitness_array = numpy.array(
                [max((f - mean) / (2 * std), 1) if std > 0 else 1 for f in fitness_array])
            sum = fitness_array.sum()
            fitness_array = numpy.array([i / sum for i in fitness_array])

        else:
            # fps  for tournament selection
            fitness_array = numpy.array([pop.fitness for pop in population])
            sumof_fit = fitness_array.sum()
            sumof_fit = sumof_fit if sumof_fit else 1
            fitness_array = numpy.array([(pop.fitness + 1) / sumof_fit for pop in population])

        return fitness_array

    def mutate(self, member,type,fitnessType):
        member.mutate(self.target_size, member, type,self.options)

        self.fitness_func[fitnessType](member, self.target, self.target_size,self.sorting_networks,self.population)


    def age_based(self,population):
        age_based_population = [citizen for citizen in population if 2 <= citizen.age <= 20]
        self.buffer[:len(age_based_population)] = age_based_population[:]
        return len(age_based_population)

    # selection of the servivng mechanizem
    def serviving_genes(self,gen,population):
        esize = math.floor(len(population) *self.elite_rate)
        if self.serviving == ELITIZEM:
            self.buffer[:esize] = population[:esize]
        # age
        elif self.serviving == AGE:
            esize = self.age_based(population)
        return esize

    # this function returns an array for each spiecy , how many are elite
    # so that we can choose the appropriate ammount of genes from speciy and so that the population size stayes the same

    def mate(self, gen,fitnesstype,mut_type,prob_spec,population):
        esize = self.serviving_genes(gen,population)
        # cross function for intial GA algo
        self.cross(esize, gen,population, len(population) - esize,fitnesstype,mut_type,prob_spec)

    def cross(self, esize, gen, population, birth_count,fitnesstype,mut_type,prob_spec):
        for i in range(esize, esize + birth_count):
            self.buffer[i] = prob_spec()
            citizen1 = prob_spec()
            citizen2 = prob_spec()
            # condition = True
            i1, i2 = self.selection_methods.method[self.selection](population, self.fitness_array)
            # counter+=1
            citizen1.object, citizen2.object = self.cross_func[self.cross_type if not fitnesstype else CROSS1 ](i1, i2)


            # mutation
            mutation = GA_MUTATION if (
                        (not self.hyper_mutaion) and self.trigger_mutation) else maxsize * adaptive_decrease(0.75, 1,
                                                                                                             gen)
            if random.randint(0, maxsize) < mutation:
                self.mutate(citizen1,mut_type,fitnesstype)
                self.mutate(citizen2,mut_type,fitnesstype)
            # select best of the two
            self.buffer[i] = citizen1 if citizen1.fitness < citizen2.fitness else citizen2

    def algo(self, i):


        self.fitness_array=self.propablities_rank_based(len(self.population)-1,self.population)
        fitnesstype=0
        mut_type=2
        self.fitness()
        self.population=self.sort_by_fitness(self.population)
        self.sorting_networks= self.sort_by_fitness(self.sorting_networks)
        self.mate(i,fitnesstype,mut_type,self.prob_spec,self.population )  # mate the population together
        self.population, self.buffer = self.buffer, self.population  # // swap buffers
        self.swap_buffers()
        self.fitness_array = self.propablities_rank_based(len(self.population), self.population)
        fitnesstype = 1
        mut_type = 1
        self.mate(i, fitnesstype, mut_type, self.problem_spec2,self.sorting_networks)  # mate the population together
        self.solution = self.sorting_networks[0]
        array=numpy.array([i.fitness for i in self.population])
        self.solution2.fitness=array.mean()

        self.sorting_networks, self.buffer = self.buffer, self.sorting_networks  # // swap buffers

        self.swap_buffers()
    def swap_buffers(self):
        self.buffer,self.buffer2=self.buffer2,self.buffer


linear_scale = lambda x: x[0] * x[1] + x[2]


# (s,mio,i)
def p_linear_rank(mio, i, s=1.5):
    if mio > 1:
        return (2 - s) / mio + 2 * i * (s - 1) / (mio * (mio - 1))
    else:
        return 1

# the general idea is to create 2 genetic algorithims one that works on a given population and given elite members
# the second one uses the first class to work on each spiecy and then adds the solutions together
