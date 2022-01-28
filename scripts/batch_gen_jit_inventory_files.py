# -*- coding: utf -*-
import argparse
import csv
import glob
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, type=str, help="N个进销存报表所在目录")
    parser.add_argument("--dst", required=True, type=str, help="存放N个实时库存表的目录")
    args = parser.parse_args()
    csvfiles = glob.glob("{}/*.csv".format(args.src))
    csvfiles.sort()

    for csvfile in csvfiles:
        year_and_month = os.path.basename(csvfile)[0:7]
        year_and_month = year_and_month.replace(".", "-")
        fn = "{}/实时库存-{}.csv".format(args.dst, year_and_month)
        fw = open(fn, "w", encoding='utf-8-sig')
        csv_writer = csv.writer(fw, delimiter=",")
        csv_writer.writerow(["规格编码", "实时可用库存"])
        with open(csvfile, "r", encoding='utf-8-sig') as fd:
            csv_reader = csv.reader(fd, delimiter=",")
            next(csv_reader, None)  # skip the header line
            for row in csv_reader:
                if len(row[16].strip()) > 0:
                    csv_writer.writerow([row[2], row[16]])
        fw.close()
        print("生成{}".format(fn))
