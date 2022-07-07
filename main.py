import os

import matplotlib.pyplot as plt
from Genetic import C_genetic_algorithem
from create_problem_sets import RPS
from settings import *
import time
from Dummies import *
from greenberg import player
from iocaine import iocaine_agent
algo = {1: C_genetic_algorithem}
tags = {1: "GA_CX_SWAP", 2: "ACO", 3: "simulated_annealing", 4: "tabu"}
heuristics = {0: "", 1: "NN", 2: "C&W"}
mutation_index = {1: "rand", 2: "SWAP", 3: "INSERT"}
problem_sets_GA = {1: 2,2:3}
# inputs_for_testing = ["10","20","30"]
inputs_for_testing = ["10"]


class Rashembo_Match:
    def __init__(self):
        self.dummies = [AntiFlat(), Copy(), Freq(), Flat(), Foxtrot(), Bruijn81(), Pi(), Play226(), RndPlayer(),
                        Rotate(), Switch(),
                        SwitchALot()]
        self.experts = [player, iocaine_agent]

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
        for i in range(len(civilian.object)):
            next = agent.nextMove()
            score += self.Winner(civilian.object[i], next)
            agent.storeMove(civilian.object[i], score)

        return score, score >= 0

    def match_Agent_greenberg(self, civilian, agent):
        rps_to_text = ('rock', 'paper', 'scissors')
        rps_to_num = {'rock': 0, 'paper': 1, 'scissors': 2}
        score = 0
        greenberg_moves = []
        my_moves = [rps_to_text[civilian.object[i]] for i in range(len(civilian.object))]
        for i in range(len(civilian.object)):
            move = player(my_moves[:i], greenberg_moves)
            score += self.Winner(civilian.object[i], rps_to_num[move])
            greenberg_moves.append(move)
        return score, score >= 0

    def match_Agent_iocain(self, civilian, agent):
        score = 0
        for i in range(len(civilian.object)):
            move = iocaine_agent(i, civilian.object[i - 1])
            score += self.Winner(civilian.object[i], move)
        return score, score >= 0
    def match_dummies_iocain(self):
        score = 0
        last_move=None
        iocan=[]
        dummy_history=[]
        for dummy in self.dummies:
            for i in range(1000):
                move = iocaine_agent(i,last_move)
                last_move=dummy.nextMove()
                score += self.Winner(move,last_move)
                dummy.storeMove(move, score)
            iocan.append((score >= 0,dummy.getName(),score))
            dummy_history.append((score < 0,"iocaine",-score))
        return iocan,dummy_history
    def match_dummies_greenberg(self):
        rps_to_text = ('rock', 'paper', 'scissors')
        rps_to_num = {'rock': 0, 'paper': 1, 'scissors': 2}
        score = 0

        green_=[]
        dummy_history=[]
        for dummy in self.dummies:
            score = 0
            greenberg_moves = []
            my_moves = []
            for i in range(1000):
                move = player(my_moves[:i], greenberg_moves)
                next=dummy.nextMove()
                my_moves.append( rps_to_text[next])
                score += self.Winner(rps_to_num[move],next)
                greenberg_moves.append(move)
            green_.append((score >= 0, dummy.getName(), score))
            dummy_history.append((score < 0, "greenberg", -score))
        return green_,dummy_history

    def init_dummies(self):
        for dummy in self.dummies:
            dummy.newGame(None)
    def dummies_vs_dummies(self):
        array=[[0]*len(self.dummies)]*len(self.dummies)
        for i in range(len(self.dummies)):
            for j in range(i,len(self.dummies)):
                score=0
                for _ in range(1000):
                    score += self.Winner(self.dummies[i].nextMove(), self.dummies[j].nextMove())
                array[i][j] =(score >= 0,self.dummies[j].getName(), score)
                array[j][i] =(score < 0, self.dummies[i].getName(), -score)

        return array

    def Start_match(self, individual):

        wins = 0
        robots = []
        self.init_dummies()
        for dummy in self.dummies:
            score, winner = self.rashembo_match(individual, dummy)
            wins += winner
            robots.append((winner, dummy.getName(), score))
        score, winner = self.match_Agent_greenberg(individual, agent=None)
        wins += winner
        robots.append((winner, "greenberg", score))
        score, winner = self.match_Agent_iocain(individual, agent=None)
        wins += winner
        robots.append((winner, "iocaine", score))
        individual.fitness = wins / (len(self.dummies) + 2)
        individual.robots_score = robots
        return individual

    def all_out_war(self,individual):
        agent=self.Start_match(individual)
        reslts=agent.robots_score
        all_results=[[] for _ in range(len(self.dummies)+len(self.experts)+1)]
        all_scores=[[] for _ in range(len(self.dummies)+len(self.experts)+1)]
        iocane, dummies1 = self.match_dummies_iocain()
        dvd=self.dummies_vs_dummies()
        greenberg, dummies2 = self.match_dummies_greenberg()

        #dummies:
        for i in range(12):
            all_results[i]=[score[0] for score in dvd[i]]+[dummies1[i][0]]+[dummies2[i][0]]+[reslts[i][0]]
            all_scores[i]=[score[2] for score in dvd[i]]+[dummies1[i][2] ]+[dummies2[i][2]]+[reslts[i][2]]
        all_results[12]=[green[0] for green in greenberg ]+[reslts[12][0]]
        all_results[13]=[ioc[0] for ioc in iocane]+[reslts[13][0]]
        all_results[14]=[res[0] for res in reslts]

        all_scores[12]=[green[2] for green in greenberg ]+[reslts[12][0]]
        all_scores[13]=[ioc[2] for ioc in iocane]+[reslts[13][0]]
        all_scores[14]=[res[2] for res in reslts]

        final_results=[sum(res)/len(res) for res in all_results]
        final_score=[sum(score)/len(score) for score in all_scores]
        return final_results,final_score




def plot(fitness, iter, tag):
    for i in range(len(fitness)):
        plt.plot(iter, fitness,label="fitness" )
    plt.ylabel('fitness')
    plt.xlabel('iterations')
    plt.title(tag)
    plt.legend()
    # plt.show()
    CHECK_FOLDER = os.path.isdir(f"outputs\{tag}")
    if not CHECK_FOLDER:
        os.makedirs(f"outputs\{tag}")
    plt.savefig(f"outputs\{tag}\{tag}.png")
    plt.close()

#get array of stats against robots
def spacer(lines,f):
    d="-"*lines
    f.write(f"{d}\n")
def create_results_file(name,results,streak):
    f = open(fr"outputs\{name}\Results_{name}.txt", "a")
    spaceforfirst=15
    fitnes=23
    all_lines=fitnes*3+spaceforfirst
    for _ in range(all_lines-2):f.write("-")
    mid=23*7
    f.write("\n")
    for _ in range(mid):f.write(" ")
    f.write(f"|Results:|")
    f.write("\n")
    len_line=21
    space=23*15
    spacer(space, f)
    our_Robot="Our Agent's win Ratio"
    lenofR=len_line-len(our_Robot)
    f.write(our_Robot)
    for i in range(lenofR):f.write(" ")




    f.write("|")


    for robot in results[0]:
        len_space=len_line-len(robot[1])
        f.write(f" {robot[1]}")
        for i in range(len_space):f.write(" ")
        f.write("|")
    f.write("\n")

    spacer(space, f)

    for i in range(len_line):f.write(" ")
    f.write("|")
    for robot in results[0]:
        len_space=10-len("winer")
        num = len_space // 2
        num = num * 2 + len(robot[1])
        f.write(f" winer")
        for i in range(len_space):f.write(" ")
        f.write("|")
        len_space=10-len("score")
        f.write(f"score")
        for i in range(len_space):f.write(" ")
        f.write("|")
    f.write("\n")

    for row ,percentage in zip(results,streak):

        spacer(space, f)
        win_perc = int(percentage * 100)

        f.write(f"{win_perc}%")
        for i in range(len_line-len(str(win_perc))-1): f.write(" ")
        f.write("|")


        for item in row:
            (lenth,val)=(len("True"),"True") if item[0] else (len("False"),"False")
            len_space = 10 -lenth
            f.write(f" {item[0]}")
            for i in range(len_space): f.write(" ")
            f.write("|")
            len_space = 10 -len(str(item[2]))
            f.write(f"{item[2]}")
            for i in range(len_space): f.write(" ")
            f.write("|")

        f.write("\n")
    print(results)
    output=[[] for i in range(len(results[0]))]
    for i in range(len(results[0])):
        for row in results:
            output[i].append(row[i][0])

    spacer(space, f)
    averages = [int(100*sum(array) / len(array)) for array in output]
    lenofR = len_line - len(our_Robot)
    f.write(our_Robot)
    f.write("|")

    for i in range(lenofR): f.write(" ")
    for robot in results[0]:
        len_space=len_line-len(robot[1])
        f.write(f" {robot[1]}")
        for i in range(len_space):f.write(" ")
        f.write("|")
    f.write("\n")

    spacer(space, f)
    avrg_win_ratio = sum(streak) / len(streak)
    win_perc = int(avrg_win_ratio * 100)

    f.write(f"{win_perc}%")
    for i in range(len_line - len(str(win_perc)) - 1): f.write(" ")
    f.write("|")

    for average in averages:
        len_space=len_line-len(str(average))
        f.write(f" {str(average)}")
        for i in range(len_space):f.write(" ")
        f.write("|")
    f.write("\n")

def border():
    print("----------------------------------")


dict={0:"Anti Flat Player",1:"Copy Player",2:"Freq Player", 3:"Flat Player",
       4:"Foxtrot Player" ,5:"Bruijn 81 Player", 6:"Pi Player" ,7:"226 Player",
          8:"Random Player",9:"Rotating Player",10:"Switching Player",
          11:"Switch a Lot Player",12:"greenberg",13:"iocaine" ,14:"Our Agent"}
def main2():
    name=input("enter a name for the results file:\nthe results belong to the tournement between our agent against all other agents , not all participants against each other \n")
    rounds=int(input("enter number of rounds!:"))
    target_size=1000
    problem_set=RPS
    max_iter=int(input("enter number of max iterations !:"))
    GA_POPSIZE=int(input("enter population size:"))
    Check_experts=bool(int(input("check experts during co-evolution : \nnot recommended with high population size ,experts take too much time to think\ntrue: 1 \nfalse: 0")))
    solution = C_genetic_algorithem(GA_TARGET, target_size, GA_POPSIZE, problem_set, problem_set, CX_, 0, 3,
                                    1, 1, 1, max_iter,Check_experts,mutation_probability=1)
    output, iter, sol, output2, sol2, network, population=solution.solve()
    results=[]
    match=Rashembo_Match()
    win_percentage=[]
    print(f"\nPloting graph of fitness and saving to output file named{name}\n")
    plot(output, iter, name)
    print("\nestablishing tournment agent vs all bots\n")
    for round in range(rounds):
        individual=match.Start_match(sol)
        results.append(individual.robots_score)
        win_percentage.append(individual.fitness)
    print(f"\nall rounds are Complete ,fetching results to output file with name {name}:\n")
    create_results_file(name,results,win_percentage)
    print("tournment all against each other\n")
    for j in range(5):
        print(f"tournament #{j}\n")
        win_ratio,points=match.all_out_war(sol)

        for i in range(len(win_ratio)):
            print(f"{dict[i]}'s win ratio is {int(100*win_ratio[i])}% and it's average score is {points[i]}")
        print("\n")
    input("\npress any key to exit ...\n")


if __name__ == "__main__":

    main2()


