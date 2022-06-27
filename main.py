import matplotlib.pyplot as plt
from Genetic import C_genetic_algorithem
from create_problem_sets import Sorting,network
from settings import *
import time

algo = {1: C_genetic_algorithem}
tags = {1: "GA_CX_SWAP", 2: "ACO", 3: "simulated_annealing", 4: "tabu"}
heuristics = {0: "", 1: "NN", 2: "C&W"}
mutation_index = {1: "rand", 2: "SWAP", 3: "INSERT"}
problem_sets_GA = {1: Sorting,2:network}
inputs_for_testing = ["6 numbers","16 numbers"]


def plot(fitness, iter, tag, names):
    for i in range(len(fitness)):
        plt.plot(iter[i], fitness[i], label=names[i])
    plt.ylabel('fitness')
    plt.xlabel('iterations')
    plt.title(inputs_for_testing[tag])
    plt.legend()
    # plt.show()
    plt.savefig(f"outputs\{inputs_for_testing[tag]}\{inputs_for_testing[tag]}-iter{len(iter[0])}.png")
    plt.close()

def sort_for_drawing(depth):
    curr=depth[0]
    dep2=[[depth[0]]]
    d=0
    for next in depth[1:]:
        if next[0]<=curr[0]<=next[1] or curr[0] <=next[1]<=curr[1] or next[0]<=curr[1]<=next[1] or curr[0] <=next[0]<=curr[1]:
            dep2.append([next])
            curr=next
            d=d+1
        else:
            dep2[d].append(next)
            curr=next


    return dep2
def plot_network(network,k,name,i):
    index=len(network)
    count=0
    plt.figure(figsize=(10, 7))
    i=0
    j=0
    for depth in network:
        dep=sort_for_drawing(depth)
        for d in dep:
            for item in d:
                plt.vlines(x=count,ymin=item[0],ymax=item[1],label=str(count))
            count+=1
    # replace 6 with k
    for i in range(1,k+1):
        plt.axhline(y=i, color='r', linestyle='-')

    plt.ylabel('comparators')

    plt.xlabel('depth')
    plt.title("network")
    # plt.legend()
    # plt.show()
    plt.savefig(f"outputs\{name}_{i}.png")
    plt.close()

def border():
    print("----------------------------------")

def main():
    process = True


    border()
    while process:
        mutation = 1
        border()
        max_iter = int(input("number of iterations:"))
        border()
        target_size= int(input("enter length of input"))
        depth= int(input("enter optimal depth"))
        comp_num= int(input("enter optimal number of comparitors"))
        problem_set = problem_sets_GA[1]

        border()

        GA_POPSIZE = 100
        GA_TARGET=[target_size,comp_num,depth]
        solution = C_genetic_algorithem(GA_TARGET, target_size, GA_POPSIZE, problem_set,problem_sets_GA[2],CX_, 0, 3,
                           1, mutation, 1, max_iter=max_iter)

        overall_time = time.perf_counter()
        yo,iter,solution,output2,solution2=solution.solve()
        plot_network(solution.get_depth(),GA_TARGET[1],"general",0)
        overall_time = time.perf_counter() - overall_time
        border()
        print("Overall runtime :", overall_time)
        border()

        print("\n run again ? press y for yes n for no ")
        if input() == "n":
            process = False
def automatic():
    iterations=[]
    fitness=[]
    mutation = 1
    border()
    max_iter =100
    border()
    # todo: change this one
    #  1. send in target:  k(input) and optimal size of network
    problem_set = problem_sets_GA[1]

    border()
    # target_size = int(input("number of items to sort"))
    # GA_POPSIZE = int(input("set population size:"))
    GA_POPSIZE = 100
    tag=0
    networks=[]
    populations=[]
    for index,GA_TARGET in enumerate([[6, 12, 5],[16, 61, 9]]):
    # for index,GA_TARGET in enumerate([[16, 61, 9]]):
        target_size = GA_TARGET[0]

        solution = C_genetic_algorithem(GA_TARGET, target_size, GA_POPSIZE, problem_set, problem_sets_GA[2], CX_, 0, 3,
                                        1, mutation, 1, max_iter=max_iter)

        overall_time = time.perf_counter()
        output, iter, solution, output2, solution2 ,network,population= solution.solve()
        networks.append(network)
        populations.append(population)
        iterations.append(iter)
        fitness.append(output)
        iterations.append(iter)
        fitness.append(output2)
        plot_network(solution.get_depth(),GA_TARGET[0],inputs_for_testing[index],0)
        for net in range(10):
            plot_network(network[net].get_depth(), GA_TARGET[0],inputs_for_testing[index]+str(net),0)
        f = open(fr"outputs\Results_{inputs_for_testing[index]}.txt", "a")
        for i in range(10):
            f.write(network[i].__str__())
            f.write("\n")

        print(fitness,iterations)
        plot(fitness, iterations, tag,["network","parasite"])
        tag+=1


    overall_time = time.perf_counter() - overall_time
    border()
    print("Overall runtime :", overall_time)
    border()

if __name__ == "__main__":
    aotomatic=input("select an automatic test or a manual one \n 1. automatic  2.manual")
    if aotomatic=="1":
        automatic()
    else:
        main()



