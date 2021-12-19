# -*- coding: utf-8 -*-
import csv
import glob
import shutil
import random

def random_sale_unit_price():
    # min: 20, max: 100
    return random.randrange(20, 101)

if __name__ == "__main__":
    files = glob.glob("进销存报表（无多余SKU）_*月.csv")
    files.sort()

    for f in files:
        fr = open(f, "r", encoding='utf-8-sig')
        csv_reader = csv.reader(fr, delimiter=",")
        fw = open(f+".tmp", "w", encoding='utf-8-sig')
        csv_writer = csv.writer(fw, delimiter=",")

        line = 0
        for row in csv_reader:
            if line > 0:
                row.append(random_sale_unit_price())
            else:
                row.append("销售单价")
            csv_writer.writerow(row)
            line += 1

        fw.close()
        fr.close()
        shutil.move(f+".tmp", f)
