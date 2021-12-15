# -*- coding: utf-8 -*-
import csv
import random

def random_st():
    # min: 500, max: 1000
    return random.randrange(500, 1001)

def random_purchase():
    # min: 100, max: 500
    return random.randrange(100, 501)

def random_sale(max):
    if random.randrange(1, 7) == 2:
        return max
    return random.randrange(0, max+1)

def broken():
    n = random.randrange(1, 7)
    return n == 3

if __name__ == "__main__":
    fr = open("进销存报表（无多余SKU）.csv", "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw_01 = open("进销存报表（无多余SKU）_01月.csv", "w", encoding='utf-8-sig')
    csv_writer_01 = csv.writer(fw_01, delimiter=",")
    fw_02 = open("进销存报表（无多余SKU）_02月.csv", "w", encoding='utf-8-sig')
    csv_writer_02 = csv.writer(fw_02, delimiter=",")
    fw_03 = open("进销存报表（无多余SKU）_03月.csv", "w", encoding='utf-8-sig')
    csv_writer_03 = csv.writer(fw_03, delimiter=",")
    fw_04 = open("进销存报表（无多余SKU）_04月.csv", "w", encoding='utf-8-sig')
    csv_writer_04 = csv.writer(fw_04, delimiter=",")
    fw_05 = open("进销存报表（无多余SKU）_05月.csv", "w", encoding='utf-8-sig')
    csv_writer_05 = csv.writer(fw_05, delimiter=",")
    fw_06 = open("进销存报表（无多余SKU）_06月.csv", "w", encoding='utf-8-sig')
    csv_writer_06 = csv.writer(fw_06, delimiter=",")
    fw_07 = open("进销存报表（无多余SKU）_07月.csv", "w", encoding='utf-8-sig')
    csv_writer_07 = csv.writer(fw_07, delimiter=",")
    fw_08 = open("进销存报表（无多余SKU）_08月.csv", "w", encoding='utf-8-sig')
    csv_writer_08 = csv.writer(fw_08, delimiter=",")
    fw_09 = open("进销存报表（无多余SKU）_09月.csv", "w", encoding='utf-8-sig')
    csv_writer_09 = csv.writer(fw_09, delimiter=",")
    fw_10 = open("进销存报表（无多余SKU）_10月.csv", "w", encoding='utf-8-sig')
    csv_writer_10 = csv.writer(fw_10, delimiter=",")
    fw_11 = open("进销存报表（无多余SKU）_11月.csv", "w", encoding='utf-8-sig')
    csv_writer_11 = csv.writer(fw_11, delimiter=",")
    fw_12 = open("进销存报表（无多余SKU）_12月.csv", "w", encoding='utf-8-sig')
    csv_writer_12 = csv.writer(fw_12, delimiter=",")

    line = 0
    st_inventory = 0
    purchase = 0
    sale = 0
    ed_inventory = 0
    csv_writer_list = [
        csv_writer_02,
        csv_writer_03,
        csv_writer_04,
        csv_writer_05,
        csv_writer_06,
        csv_writer_07,
        csv_writer_08,
        csv_writer_09,
        csv_writer_10,
        csv_writer_11,
        csv_writer_12,
    ]
    for row in csv_reader:
        if line > 0:
            # 01
            row[4] = random_st()
            row[6] = 0
            row[10] = random_sale(row[4])
            if row[4] - row[10] <= 0:
                row[16] = 0
            else:
                row[16] = row[4] - row[10]
            st_inventory = row[16]
            csv_writer_01.writerow(row)
            if line == 1:
                print(row[4], row[6], row[10], row[16])

            # 02-12
            for i in range(11):
                if st_inventory == 0:
                    row[4] = 0
                    if broken():
                        row[6] = 0
                        row[10] = 0
                        row[16] = 0
                    else:
                        row[6] = random_purchase()
                        row[10] = random_sale(row[6])
                        if row[6] - row[10] <= 0:
                            row[16] = 0
                        else:
                            row[16] = row[6] - row[10]
                else:
                    row[4] = st_inventory
                    row[6] = 0
                    row[10] = random_sale(row[4])
                    if row[4] - row[10] <= 0:
                        row[16] = 0
                    else:
                        row[16] = row[4] - row[10]
                st_inventory = row[16]
                csv_writer_list[i].writerow(row)
                if line == 1:
                    print(row[4], row[6], row[10], row[16])

        else:
            csv_writer_01.writerow(row)
            csv_writer_02.writerow(row)
            csv_writer_03.writerow(row)
            csv_writer_04.writerow(row)
            csv_writer_05.writerow(row)
            csv_writer_06.writerow(row)
            csv_writer_07.writerow(row)
            csv_writer_08.writerow(row)
            csv_writer_09.writerow(row)
            csv_writer_10.writerow(row)
            csv_writer_11.writerow(row)
            csv_writer_12.writerow(row)
        line += 1

    fw_01.close()
    fw_02.close()
    fw_03.close()
    fw_04.close()
    fw_05.close()
    fw_06.close()
    fw_07.close()
    fw_08.close()
    fw_09.close()
    fw_10.close()
    fw_11.close()
    fw_12.close()
    fr.close()
