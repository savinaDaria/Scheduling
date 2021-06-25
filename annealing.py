import copy
import numpy as np
from math import *
from random import *
import scheduleData as data


def generate_new_element(scheduleGiven, change_percent):
    schedule = copy.copy(scheduleGiven)
    amount_change = int(round(change_percent * len(schedule) / 100))
    not_used_indexes = list(range(0, len(schedule)))
    while amount_change > 0:
        ind = choice(not_used_indexes)
        not_used_indexes.remove(ind)
        group = []
        for d in schedule[ind]['discipline']:
            group.append(data.disciplines[d - 1][3])
        all_positions_notEmpty, all_positions_notEmptyWithGroups, all_positions_emptyWithGroups\
            = data.all_positions(schedule, group, 0, 0, 1, 1, 0, 1)
        if len(all_positions_emptyWithGroups) > 0:
            empty = choice(all_positions_emptyWithGroups)
            all_positions_emptyWithGroups.remove(empty)
            all_positions_emptyWithGroups.append([schedule[ind]['day'], schedule[ind]['lesson'], group])
            schedule[ind]['day'] = empty[0]
            schedule[ind]['lesson'] = empty[1]
        elif len(all_positions_notEmptyWithGroups) > 0:
            notEmpty = choice(all_positions_notEmptyWithGroups)
            all_positions_notEmptyWithGroups.remove(notEmpty)
            temp = schedule[ind]
            indNotEmpty = all_positions_notEmpty.index(notEmpty)
            schedule[ind]['day'] = notEmpty[0]
            schedule[ind]['lesson'] = notEmpty[1]
            schedule[indNotEmpty]['day'] = temp['day']
            schedule[indNotEmpty]['lesson'] = temp['lesson']
            amount_change -= 1
        else:
            amount_change += 1
        amount_change -= 1
    return schedule


def annealing(iter_num, begin_num):
    T = 1000
    population = data.create_population(begin_num)
    population_limit = []
    for element in population:
        population_limit.append(data.aim_limitation(element))
    for i in range(iter_num):
        if T == 0:
            break
        index = randint(0, begin_num - 1)
        new_schedule = generate_new_element(population[index], randint(0, 101))
        new_schedule_limit = data.aim_limitation(new_schedule)
        if population_limit[index] <= new_schedule_limit:
            population[index] = new_schedule
            population_limit[index] = new_schedule_limit
        else:
            delta = population_limit[index] - new_schedule_limit
            p = exp((-1) * delta / T)
            q = np.random.uniform(0, 1, 1)[0]
            if p > q:
                population[index] = new_schedule
                population_limit[index] = new_schedule_limit
            if i != 0:
                T = T / log(i + 1)
    print("max=", max(population_limit))
    return population, population[population_limit.index(max(population_limit))]
