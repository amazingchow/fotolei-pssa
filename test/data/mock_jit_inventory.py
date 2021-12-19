# -*- coding: utf-8 -*-
import csv

if __name__ == "__main__":
    fr = open("进销存报表（无多余SKU）_12月.csv", "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    line = 0
    jit_inventory = {}
    for row in csv_reader:
        if line > 0:
            jit_inventory[row[2]] = (row[2], row[16])
            # csv_writer.writerow(new_row)
        # else:
        #     csv_writer.writerow(["规格编码", "实际库存"])
        line += 1
    fr.close()


    fr = open("产品目录.csv", "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open("实时库存.csv", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")

    for row in csv_reader:
        if line > 0:
            new_row = ["", ""]
            new_row[0] = row[1]
            if row[1] in jit_inventory.keys():
                new_row[1] = jit_inventory[row[1]][1]
            else:
                new_row[1] = 100
            csv_writer.writerow(new_row)
        else:
            csv_writer.writerow(["规格编码", "实际库存"])
        line += 1

    fw.close()
    fr.close()
