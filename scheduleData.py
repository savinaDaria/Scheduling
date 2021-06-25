import copy
import random
import sqlite3 as sq

max_lesson = 4
max_day = 5
connection = sq.connect('ScheduleUniv1.db')
with connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Discipline_List")
    disciplines = cursor.fetchall()
    cursor.execute("SELECT * FROM Disciplines")
    discipline_names = cursor.fetchall()
    cursor.execute("SELECT * FROM Discipline_Type")
    discipline_types = cursor.fetchall()
    cursor.execute("SELECT * FROM Teachers")
    teachers = cursor.fetchall()
    cursor.execute("SELECT * FROM Teacher_Position")
    teacher_positions = cursor.fetchall()
    cursor.execute("SELECT * FROM Specialties")
    specialties = cursor.fetchall()
    cursor.execute("SELECT * FROM Student_Groups")
    groupsData = cursor.fetchall()
    group_amount = len(groupsData)
    groups = []
    for gr in groupsData:
        groups.append(gr[0])


def DisciplineListCreation():
    with connection:
        cursor.execute(
            "SELECT Student_Groups.Group_ID, Student_Groups.Flow, Student_Groups.Flow_Number, Student_Flow.Year,"
            " Student_Flow.Specialty, Student_Groups.Amount_Of_Students, Specialties.Abbreviation FROM Student_Groups,"
            " Student_Flow, Specialties WHERE Student_Groups.Flow=Student_Flow.Flow_ID and "
            "Student_Flow.Specialty=Specialties.Specialty_ID")
        rows = cursor.fetchall()
        if len(rows) == 0:
            print('There are no groups in DB')
            return 0
        cursor.execute(
            "SELECT Disciplines.Discipline_ID, Disciplines.Discipline, Disciplines.Specialty, Disciplines.Year,"
            " Disciplines.Classes_Type, Disciplines.Classes_Amount, Disciplines.Teacher, Teachers.Teacher_Name FROM "
            "Disciplines, Teachers WHERE Disciplines.Teacher=Teachers.Teacher_ID")
        if len(disciplines) == 0:
            print('There is no academic plan in DB')
        i = 0
        for row in rows:
            for discipline in disciplines:
                if discipline[2] == row[4] and discipline[3] == row[3]:
                    hours_per_week = int(discipline[5] / 17)
                    while hours_per_week:
                        i += 1
                        params = (
                            i, discipline[0], discipline[1], discipline[4], row[1], row[2], row[0], row[5],
                            discipline[2],
                            row[6], discipline[3], discipline[6], discipline[7])
                        cursor.execute("INSERT INTO Discipline_List VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", params)
                        hours_per_week = hours_per_week - 1
    if connection:
        connection.close()


def all_positions(chromosome, groupsNeeded, all_generated, all_generatedWithGroups,
                  current_notEmpty, current_notEmptyWithGroups, current_Empty, current_EmptyWithGroups):
    result = []
    all_positions_generated = position_struct()
    all_generatedWithGroupsList = []
    if groupsNeeded is not None:
        for p in all_positions_generated:
            if p[2] == groupsNeeded:
                all_generatedWithGroupsList.append(p)
    if chromosome is not None:
        current_notEmptyList = []
        for ch in chromosome:
            disc = ch['discipline']
            group = []
            for d in disc:
                group.append(disciplines[d - 1][3])
            current_notEmptyList.append([ch['day'], ch['lesson'], group])

        current_emptyList = copy.copy(all_positions_generated)  # стануть пустими після очистки зайнятих
        for h in current_notEmptyList:
            groupCurrent=h[2]
            if h in current_emptyList :
                current_emptyList.remove(h)
                for a in current_emptyList:
                    if a[0]==h[0] and a[1]==h[1] and [x for x in groupCurrent if x in a[2]]:
                        current_emptyList.remove(a)

        if groupsNeeded is not None:
            current_emptyWithGroupsList = []
            current_notEmptyWithGroupsList = []
            for p in current_emptyList:
                if p[2] == groupsNeeded:
                    current_emptyWithGroupsList.append(p)
            for p in current_notEmptyList:
                if p[2] == groupsNeeded:
                    current_notEmptyWithGroupsList.append(p)

    if all_generated:
        result.append(all_positions_generated)
    if all_generatedWithGroups:
        result.append(all_generatedWithGroupsList)
    if current_notEmpty:
        result.append(current_notEmptyList)
    if current_notEmptyWithGroups:
        result.append(current_notEmptyWithGroupsList)
    if current_Empty:
        result.append(current_emptyList)
    if current_EmptyWithGroups:
        result.append(current_emptyWithGroupsList)
    return result


def limitation_importantBeginDay(chromosome):
    result = 0
    for day in range(1, max_day + 1):
        for ch in chromosome:
            if ch['day'] == day:
                if ch['lesson'] in range(1, 3) and disciplines[ch['discipline'][0]][2] == 1:
                    result += 1
                elif ch['lesson'] in range(1, 3) and disciplines[ch['discipline'][0]][2] != 1:
                    result -= 1
    return result


def limitation_windows(chromosome):
    result = 0
    for day in range(1, max_day + 1):
        lesson_sort = []
        i = 0
        for ch in chromosome:
            if ch['day'] == day:
                lesson_sort.append(chromosome[i]['lesson'])
            i += 1
        if len(lesson_sort) == 0:
            continue
        serial = list(range(min(lesson_sort), max(lesson_sort) + 1))
        result += 1
        for i in serial:
            if i not in lesson_sort:
                result -= 2
                break
    return result


def aim_limitation(chromosome):
    chromosome = sort_chromosome(chromosome)
    aim_func = limitation_windows(chromosome) + limitation_importantBeginDay(chromosome)
    return aim_func


def sort_chromosome(chromosome):
    for fragment in range(len(chromosome)):
        for fragment_next in range(len(chromosome)):
            if chromosome[fragment]['day'] < chromosome[fragment_next]['day']:
                chromosome[fragment], chromosome[fragment_next] = chromosome[fragment_next], chromosome[fragment]

            if chromosome[fragment]['day'] == chromosome[fragment_next]['day'] and chromosome[fragment]['lesson'] < \
                    chromosome[fragment_next]['lesson']:
                chromosome[fragment], chromosome[fragment_next] = chromosome[fragment_next], chromosome[fragment]
    return chromosome


def position_struct():
    positions = []
    for i in range(max_day):
        for j in range(max_lesson):
            for g in groups:
                positions.append([i + 1, j + 1, [g]])
            positions.append([i + 1, j + 1, groups])
    return positions


def create_chromosome():
    chromosome = []
    i = 0
    disciplines1 = copy.copy(disciplines)
    disciplines_left = len(disciplines1)
    while disciplines_left:
        discipline_row = disciplines1[0]
        disciplines1.remove(discipline_row)
        group1 = discipline_row[3]
        group2 = -1
        discipline_list = [discipline_row[0]]
        for row in disciplines1:
            if row[1] == discipline_row[1] and row[2] == discipline_row[2] \
                    and row[4] == discipline_row[4] and row[5] == discipline_row[5] \
                    and row[3] != discipline_row[3] and row[6] == discipline_row[6]:
                discipline_list.append(row[0])
                group2 = row[3]
                disciplines1.remove(row)
                break
        group_list = [group1]
        if group2 != -1:
            group_list.append(group2)

        if i == 0:
            allPositionsWithGroups = all_positions(None, group_list, 0, 1, 0, 0, 0, 0)[0]
            currentChosen = random.choice(allPositionsWithGroups)
        else:
            get_positions = all_positions(chromosome, group_list, 0, 0, 1, 0, 0, 1)
            currentNotEmpty = get_positions[0]
            currentEmptyWithGroups = get_positions[1]
            while True:
                flag = True
                if len(currentEmptyWithGroups)<1:
                    return chromosome
                currentChosen = random.choice(currentEmptyWithGroups)
                teacher = discipline_row[6]
                j=0
                for elem in currentNotEmpty:
                    teacher_part=chromosome[j]['discipline'][0]
                    teacher_elem=disciplines[teacher_part][6]
                    if elem[0] == currentChosen[0] and elem[1] == currentChosen[1] \
                            and teacher == teacher_elem:
                        currentEmptyWithGroups.remove(currentChosen)
                        currentChosen = random.choice(currentEmptyWithGroups)
                        flag = False
                    j+=1
                if flag:
                    break

        chromosome.append({'day': 0, 'lesson': 0, 'discipline': 0})
        chromosome[i]['day'] = currentChosen[0]
        chromosome[i]['lesson'] = currentChosen[1]
        chromosome[i]['discipline'] = discipline_list
        i += 1
        disciplines_left = len(disciplines1)
    return chromosome


def create_population(population_size):
    population = []
    for i in range(population_size):
        population.append(create_chromosome())
    return population
