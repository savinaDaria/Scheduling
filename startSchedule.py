from qtconsole.mainwindow import background

import scheduleData as data
import genetic
import annealing
import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QStyle
num_of_start_population = 20
iterations = 1000

max_lesson = 4
max_day = 5

def fill_table(chromosome, title,flag):
    app = QApplication(sys.argv)
    table = QTableWidget()
    table.setWindowTitle(title)
    table.resize(2000, 2000)
    table.setRowCount(max_day*(max_lesson+1)+2)
    list_begin = [2, 7, 12, 17, 22]
    table.setColumnCount(data.group_amount + 1)
    for i in range(1,max_day*(max_lesson+1)+1):
        for j in range(1, data.group_amount+1):
            if i+1 not in list_begin:
                table.setRowHeight(i, 170)
            table.setColumnWidth(j, 300)
    for i in range(data.group_amount):
        table.setItem(0, i + 1, QTableWidgetItem(data.groupsData[i][2]))
    table.setItem(0, 0, QTableWidgetItem("Група"))

    days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
    k = 0
    for i in list_begin:
        table.setItem(i - 1, 1, QTableWidgetItem(days[k]))
        table.setItem(i, 0, QTableWidgetItem("Пара 1"))
        table.setItem(i + 1, 0, QTableWidgetItem("Пара 2"))
        table.setItem(i + 2, 0, QTableWidgetItem("Пара 3"))
        table.setItem(i + 3, 0, QTableWidgetItem("Пара 4"))
        k += 1
    for grp in data.groupsData:
        for fragment in chromosome:
            indexes = []
            for ind in range(len(fragment['discipline'])):
                indexes.append(fragment['discipline'][ind] - 1)
            for ind in indexes:
                if data.disciplines[ind][3] == data.groupsData[grp[0] - 1][0]:
                    day = fragment['day']
                    lesson = fragment['lesson']
                    discipline_ind = data.disciplines[ind][1] - 1
                    discipline = data.discipline_names[discipline_ind][1]
                    d_type_ind = data.disciplines[ind][2] - 1
                    d_type = data.discipline_types[d_type_ind][1]
                    teacher_ind = data.disciplines[ind][6] - 1
                    teacher = data.teachers[teacher_ind][1]
                    teacher_position_ind = data.teachers[teacher_ind][2] - 1
                    teacher_position = data.teacher_positions[teacher_position_ind][1]
                    item = QTableWidgetItem(discipline + "\n" + d_type + "\n" + teacher + "\n" + teacher_position + "\n")
                    table.setItem(5 * day + 1 - 1 - (4 - lesson), grp[0],item)
                    if(flag==1):table.setStyleSheet("background-color: #d3e0ce")
                    else: table.setStyleSheet("background-color: #b8e3ea")

    table.show()
    return app.exec_()


populationlastSA, best = annealing.annealing(iterations, num_of_start_population)
populationlastGA = genetic.evolution(100, num_of_start_population)

GA = fill_table(populationlastGA[0], "Розклад за генетичним алгоритмом",1)
SA = fill_table(best, "Розклад за імітацією відпалу",2)

