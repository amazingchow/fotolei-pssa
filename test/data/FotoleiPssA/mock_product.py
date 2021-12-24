# -*- coding: utf-8 -*-
import csv
import glob
import shutil
import random

def random_w():
    # min: 100, max: 1000
    return random.randrange(100, 1001)

def random_lwh():
    # min: 5, max: 50
    return random.randrange(5, 51)

def random_moq():
    # min: 1, max: 10
    return random.randrange(1, 11)

if __name__ == "__main__":
    spec_code_2_ed_inventory = {}
    fr = open("2021.11进销存报表.csv", "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    line = 0
    for row in csv_reader:
        if line > 0:
           spec_code_2_ed_inventory[row[2]] = row[16] 
        line += 1    

    fr = open("产品目录-2021-12-21.csv", "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open("产品目录-2021-12-21.csv.tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")

    line = 0
    for row in csv_reader:
        if line > 0:
            row[9] = random_w()
            row[10] = random_lwh()
            row[11] = random_lwh()
            row[12] = random_lwh()
            if row[1] in spec_code_2_ed_inventory.keys():
                row[18] = spec_code_2_ed_inventory[row[1]]
            else:
                row[18] = 100
            row[19] = random_moq()
        csv_writer.writerow(row)
        line += 1

    fw.close()
    fr.close()
    # shutil.move(f+".tmp", f)
