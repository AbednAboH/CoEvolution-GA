import random

from function_selection import cross_types
from algorithems import algortithem
from settings import *
from sys import maxsize
import numpy
import math
from Dummies import *
from greenberg import player
from iocaine import iocaine_agent

""" to generalize the problem we created a class that given a population calculates the solution"""


def adaptive_decrease(p, rate, generation):
    return 2 * (p ** 2) * math.exp(rate * generation) / (p + p * math.exp(rate * generation))


class C_genetic_algorithem(algortithem):
    Distance_hash = {}

    def __init__(self, target, tar_size, pop_size, problem_spec, problem_spec2, crosstype, fitnesstype, selection,
                 serviving_mechanizem, mutation, gene_dist, max_iter,check, mutation_probability=0):
        algortithem.__init__(self, target, tar_size, pop_size, problem_spec, fitnesstype, selection, max_iter)
        self.cross_func = cross_types().select
        self.cross_type = crosstype
        self.serviving = serviving_mechanizem
        self.mutation_type = mutation
        self.set_fitness = self.prob_spec().fitnesstype[gene_dist]
        self.fitness_func = self.prob_spec().fitnesstype
        self.selection_pressure = self.pop_diversity = 0
        self.hyper_mutaion = mutation_probability
        self.trigger_mutation = False
        self.elite_rate = GA_ELITRATE
        self.dummies = [AntiFlat, Copy, Freq, Flat, Foxtrot, Bruijn81, Pi, Play226, RndPlayer, Rotate, Switch,
                        SwitchALot]
        self.experts = [iocaine_agent, player]
        self.problem_spec2 = problem_spec2
        self.check_experts=check
        self.options = self.create_options()
        temp = problem_spec2()
        temp.create_object(self.target_size, self.target, self.options)
        # todo: add options to send to problem creation , we don't have to create it over and over again'

    def create_options(self):
        options = []
        for k in range(1, self.target_size + 1):
            for j in range(k + 1, self.target_size + 1):
                options.append([k, j])
        return options

    def init_population(self):
        super(C_genetic_algorithem, self).init_population()
        self.init_dummies()
        self.fitness()
        self.population = self.sort_by_fitness(self.population)
        self.solution = self.population[0]
        self.output.append(self.solution.fitness)
        self.iter.append(0)
        print(self.solution.fitness)

    def init_dummies(self):
        self.dummies = [AntiFlat(), Copy(), Freq(), Flat(), Foxtrot(), Bruijn81(), Pi(), Play226(), RndPlayer(),
                        Rotate(), Switch(),
                        SwitchALot()]
        for dummy in self.dummies:
            dummy.newGame(None)

    def init_experts(self):
        pass

    def Winner(self, move1, move2):
        if move1 == 0 and move2 == 2:
            return 1
        elif move1 == 2 and move2 == 0:
            return -1
        else:
            return 1 if move1 > move2 else -1 if move2 > move1 else 0

    def rashembo_match(self, civilian, agent):

        score = 0
        rps_to_text = ('rock', 'paper', 'scissors')
        for i in range(1000):
            next = agent.nextMove()
            score += self.Winner(civilian.object[i], next)
            agent.storeMove(civilian.object[i], score)

        return score, score >= 0

    def rashembo_match2(self, civilian, agent):
        rps_to_text = ('rock', 'paper', 'scissors')
        rps_to_num = {'rock': 0, 'paper': 1, 'scissors': 2}
        score = 0
        greenberg_moves = []
        my_moves = [rps_to_text[civilian.object[i]] for i in range(len(civilian.object))]
        for i in range(1000):
            move = player(my_moves[:i], greenberg_moves)
            score += self.Winner(civilian.object[i], rps_to_num[move])
            greenberg_moves.append(move)
        return score, score >= 0

    def rashembo_match3(self, civilian, agent):
        score = 0
        for i in range(1000):
            move = iocaine_agent(i, civilian.object[i - 1])
            score += self.Winner(civilian.object[i], move)
        return score, score >= 0

    def fit_dummies(self, population, dummies):

        for index, pop in enumerate(population):
            wins = 0
            robots = []
            self.init_dummies()
            for dummy in dummies:
                score, winner = self.rashembo_match(pop, dummy)
                wins += winner
                robots.append((winner, dummy.getName(), score))
            if self.check_experts:
                score, winner = self.rashembo_match2(pop, agent=None)
                wins += winner
                robots.append((winner, "greenberg", score))
                score, winner = self.rashembo_match3(pop, agent=None)
                wins += winner
                robots.append((winner, "iocaine", score))
                population[index].fitness = wins / (len(dummies) + 2)
            else:
                population[index].fitness = wins / (len(dummies) )
            population[index].robots_score = robots

            # print(pop.fitness)

    def fitness(self):
        self.fit_dummies(self.population, self.dummies)

    def propablities_rank_based(self, pop_size, population):

        # depending on the selection scheme get propabilities from ranking system !
        multiplier = 1 if self.selection == SUS or RWS else 0.5  # for now keep it like this
        # scale fitness values with linear ranking for sus and RWS
        fitness_array = []
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

    def mutate(self, member, type, fitnessType):
        member.mutate(self.target_size, member, type, self.options)
        self.fit_dummies([member], self.dummies)

    def age_based(self, population):
        age_based_population = [citizen for citizen in population if 2 <= citizen.age <= 20]
        self.buffer[:len(age_based_population)] = age_based_population[:]
        return len(age_based_population)

    # selection of the servivng mechanizem
    def serviving_genes(self, gen, population):
        esize = math.floor(len(population) * self.elite_rate)
        if self.serviving == ELITIZEM:
            self.buffer[:esize] = population[:esize]
        # age
        elif self.serviving == AGE:
            esize = self.age_based(population)
        return esize

    # this function returns an array for each spiecy , how many are elite
    # so that we can choose the appropriate ammount of genes from speciy and so that the population size stayes the same
    def Update_Org_fit(self, i, organizm_i_new):
        new_organizm = self.prob_spec()
        new_organizm.object = organizm_i_new
        self.fit_dummies([new_organizm], self.dummies)
        self.population[i] = self.population[i] if new_organizm.fitness < self.population[i].fitness else new_organizm

    def select_XJ(self, i):
        organizm = random.choice([random.randint(0, i), random.randint(i + 1, len(self.population) - 1) if i != len(
            self.population) - 1 else random.randint(0, i)])
        organizm_i, organizm_j = self.population[i].object, self.population[organizm].object
        return organizm, organizm_i, organizm_j

    def mutualism(self):
        print("------Mutualism phase-----------")
        for i in range(len(self.population)):
            organizm, organizm_i, organizm_j = self.select_XJ(i)
            BF = [random.randint(1, 2), random.randint(1, 2)]
            Mutual_vectors = [(x_i + x_j) // 2 for x_i, x_j in zip(organizm_i, organizm_j)]
            organizmz = [organizm_i, organizm_j]
            best = self.solution.object
            index_to_update = [i, organizm]
            for org in range(2):
                zipped = zip(organizmz[org], Mutual_vectors)
                item = [(x_i + int(random.uniform(0, 1) * abs(best[index] - mv * BF[org]))) % 3 for index, (x_i, mv) in
                        enumerate(zipped)]
                self.Update_Org_fit(index_to_update[org], item)

    def communalism(self, esize, birth_count):
        print("------Communalism phase-----------")

        for i in range(esize, esize + birth_count):
            organizm, organizm_i, organizm_j = self.select_XJ(i)
            best = self.solution.object
            zipped = zip(organizm_i, organizm_j, best)
            organizm_i_new = [x_i + random.uniform(-1, 1) * abs(x_best - x_j) for x_i, x_j, x_best in zipped]
            organizm_i_new = [int(xi) % 3 for xi in organizm_i_new]
            self.Update_Org_fit(i, organizm_i_new)

    def parasitism(self, esize, birth_count, gen):
        print("------Parasitism faze-----------")
        for i in range(esize, esize + birth_count):
            mutation = GA_MUTATION if (
                    (not self.hyper_mutaion) and self.trigger_mutation) \
                else maxsize * adaptive_decrease(0.75, 1, gen)
            organizm, organizm_i, organizm_j = self.select_XJ(i)
            Parasite_vector = [organizm_i[index] if random.uniform(0, 1) >= mutation else
                               random.randint(0, 2) for index in range(len(organizm_i))]
            self.Update_Org_fit(i, Parasite_vector)
           # print(self.population[i].fitness)

    def mate(self, gen, fitnesstype, mut_type, prob_spec, population):
        esize = self.serviving_genes(gen, population)
        self.cross(esize, gen, population, len(population) - esize, fitnesstype, mut_type, prob_spec)

    def cross(self, esize, gen, population, birth_count, fitnesstype, mut_type, prob_spec):
        self.mutualism()
        self.communalism(esize, birth_count)
        self.parasitism(esize, birth_count, gen)
    def algo(self, i):
        self.fitness_array = self.propablities_rank_based(len(self.population) - 1, self.population)
        self.mate(i, 0, 0, self.prob_spec, self.population)  # mate the population together
        self.population = self.sort_by_fitness(self.population)
        self.solution = self.population[0]
    def stopage(self,i):
        return i==self.iteration or self.solution.fitness==1


linear_scale = lambda x: x[0] * x[1] + x[2]


# (s,mio,i)
def p_linear_rank(mio, i, s=1.5):
    if mio > 1:
        return (2 - s) / mio + 2 * i * (s - 1) / (mio * (mio - 1))
    else:
        return 1

# the general idea is to create 2 genetic algorithims one that works on a given population and given elite members
# the second one uses the first class to work on each spiecy and then adds the solutions together
