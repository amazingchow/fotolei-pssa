# -*- coding: utf -*-
import argparse
import glob
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


def do_batch_upload_jit_inventory_file(session, url, csvfile):
    mp_encoder = MultipartEncoder(
        fields={
            "file": (os.path.basename(csvfile), open(csvfile, "rb"), "text/plain"),
        }
    )
    resp = session.post(url, data=mp_encoder, headers={"Content-Type": mp_encoder.content_type})
    print("上传{}, 返回码: {}, 返回状态: {}".format(csvfile, resp.status_code, resp.json()["message"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_ip", required=True, type=str, help="服务器IP地址")
    parser.add_argument("--dir", required=True, type=str, help="N个实时库存表所在目录")
    args = parser.parse_args()
    csvfiles = glob.glob("{}/*.csv".format(args.dir))
    csvfiles.sort()

    api_url = "http://{}:15555/api/v1/jitinventory/upload".format(args.server_ip)
    with requests.Session() as session:
        for csvfile in csvfiles:
            do_batch_upload_jit_inventory_file(session, api_url, csvfile)
