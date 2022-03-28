# -*- coding: utf -*-
import argparse
import glob
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


def do_batch_upload_inventories(session, url, year_and_month, csvfile):
    mp_encoder = MultipartEncoder(
        fields={
            "import_date": year_and_month,
            "file": (os.path.basename(csvfile), open(csvfile, "rb"), "text/plain"),
        }
    )
    resp = session.post(
        url,
        data=mp_encoder,
        headers={"Content-Type": mp_encoder.content_type}
    )
    print("上传{}, 返回码: {}, 返回状态: {}".format(csvfile, resp.status_code, resp.json()["message"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_ip", required=True, type=str, help="服务器IP地址")
    parser.add_argument("--dir", required=True, type=str, help="N个进销存报表所在目录")
    args = parser.parse_args()
    csvfiles = glob.glob("{}/*.csv".format(args.dir))
    csvfiles.sort()

    with requests.Session() as session:
        api_url = "http://{}:15555/api/v1/users/login".format(args.server_ip)
        session.post(api_url, json={"username": "fotolei", "password": "asdf5678"})

        api_url = "http://{}:15555/api/v1/inventories/upload".format(args.server_ip)
        for csvfile in csvfiles:
            year_and_month = os.path.basename(csvfile)[0:7]
            year_and_month = year_and_month.replace(".", "-")
            do_batch_upload_inventories(session, api_url, year_and_month, csvfile)

        api_url = "http://{}:15555/api/v1/users/logout".format(args.server_ip)
        session.delete(api_url)
