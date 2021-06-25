import random
from random import randint
import scheduleData as data
import copy


def hemming_distance(chromosome1, chromosome2):
    distance = 0
    for i in range(len(chromosome1)):
        if chromosome1[i]['day'] != chromosome2[i]['day']:
            distance += 1
        if chromosome1[i]['lesson'] != chromosome2[i]['lesson']:
            distance += 1
    return distance


def outbreeding(population):
    length = len(population)
    index1 = randint(0, length - 1)
    index2 = 0
    chromosome1 = population[index1]
    population.remove(chromosome1)
    hemming = []
    for chromosome2 in population:
        hemming.append(hemming_distance(chromosome1, chromosome2))
    maxnum = 0
    j = 0
    for i in hemming:
        if i > maxnum:
            maxnum = i
            index2 = j
        j += 1
    chr2 = population[index2]
    population.remove(chr2)
    indexes = [index1, index2]
    return indexes


def mutation(offsprings):
    mutOffsprings = []
    for schedule in offsprings:
        lenOffOne = len(schedule)
        currentNotEmpty = data.all_positions(schedule, None, 0, 0, 1, 0, 0, 0)[0]
        indexGeneralNotSorted = []
        for off in range(lenOffOne):
            lesson1 = currentNotEmpty[off]
            index = [off]
            for off1 in range(lenOffOne):
                lesson2 = currentNotEmpty[off1]
                if off != off1 and lesson1[0] == lesson2[0] and lesson1[1] == lesson2[1] and (
                        lesson1[2] in lesson2[2] or lesson2[2] in lesson1[2] or [x for x in lesson1[2] if
                                                                                 x in lesson2[2]]):
                    index.append(off1)
            indexGeneralNotSorted.append(index)
        indexGeneralSorted = []
        for i in indexGeneralNotSorted:
            iS = sorted(i)
            if iS not in indexGeneralSorted and len(iS) > 1:
                indexGeneralSorted.append(i)
        for ind in indexGeneralSorted:
            whoChangesPosition = random.choice(ind)
            ind.remove(whoChangesPosition)
            discWhoChange = schedule[whoChangesPosition]['discipline']
            groupWhoChange = []
            for dC in discWhoChange:
                groupWhoChange.append(data.disciplines[dC - 1][3])
            currentEmptyWithGroup = data.all_positions(schedule, groupWhoChange, 0, 0, 0, 0, 0, 1)[0]
            if len(currentEmptyWithGroup)<1:
                break
            hit = random.choice(currentEmptyWithGroup)
            schedule[whoChangesPosition]['day'] = hit[0]
            schedule[whoChangesPosition]['lesson'] = hit[1]
        mutOffsprings.append(schedule)
    for off in range(len(offsprings)):
        offsprings[off] = mutOffsprings[off]
    return offsprings


def crossover(chromosome1, chromosome2, offsprings):
    chromosomemask1,chromosomemask2 = [],[]
    offspring1,offspring2=copy.copy(chromosome1), copy.copy(chromosome2)
    for i in range(len(chromosome1)):
        chromosomemask1.append(random.choice([0, 1]))
        chromosomemask2.append(random.choice([0, 1]))
    points = ['day', 'lesson']
    for i in range(len(chromosome1)):
        p = random.choice(points)
        if chromosomemask1[i] == 0:
            offspring1[i][p] = chromosome2[i][p]
        if chromosomemask2[i] == 0:
            offspring2[i][p] = chromosome1[i][p]
    offsprings.append(offspring1)
    offsprings.append(offspring2)


def evolution(iteration_num, begin_num):
    population = data.create_population(begin_num)  # початкова популяція з 20 розкладів
    for i in range(iteration_num):
        parent_pool = copy.copy(population)
        offsprings = []
        flag = True
        j = 0
        while flag:
            if len(parent_pool) == 0:
                flag = False
            else:
                indexes = outbreeding(parent_pool)
                ind1 = indexes[0]
                ind2 = indexes[1]
                crossover(population[ind1], population[ind2], offsprings)
            j += 1
        for row in population:
            offsprings.append(row)
        flag = True
        population = []
        offsprings = mutation(offsprings)
        while flag:
            if len(offsprings) == 0:
                flag = False
            else:
                ind1 = 0
                if len(offsprings) != 1:
                    ind1 = randint(0, len(offsprings) - 1)
                chromosome1 = offsprings[ind1]
                offsprings.remove(chromosome1)
                ind2 = 0
                d = len(offsprings)
                if d != 1:
                    ind2 = randint(0, d - 1)
                chromosome2 = offsprings[ind2]
                offsprings.remove(chromosome2)
                chromosome11 = data.sort_chromosome(chromosome1)
                chromosome21 = data.sort_chromosome(chromosome2)
                fitness1 = data.aim_limitation(chromosome11)
                fitness2 = data.aim_limitation(chromosome21)
                if fitness1 > fitness2:
                    population.append(chromosome1)
                else:
                    population.append(chromosome2)
    return population
