from datetime import datetime
from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests

# Setup
app = Flask(__name__)


def parse_bucket(url: str = "https://minio-api.cloud.randomds.com/portaleofferte/") -> list:
    """Function to parse a public Minio bucket and create a dictionary
    with file links, names, and sizes
    
    Parameters:
    url (str): url for the Minio Bucket. Need to allow anonymous access for listing files

    Returns:
    file_list (list): list of dictionaries with information about the files in the bucket
    """
    file_list = requests.get(url)
    file_list = BeautifulSoup(file_list.text, features="xml")
    file_list = [
        {
            "file": item.find("Key").get_text().split("_")[-1].split(".")[0],
            "link": "{}{}".format(url, item.find("Key").get_text()),
            "size": "{}kb".format(int(float(item.find("Size").get_text()) / 1024))
        }
        for item in file_list.find_all("Contents")
    ]
    return file_list


@app.route("/", methods=(["GET"]))
def index():
    "Return list of files"
    data_files = parse_bucket("https://minio-api.cloud.randomds.com/portaleofferte/")
    # Order files by date
    ordered_files = sorted(data_files, key=lambda d: d["file"], reverse=True)
    last_run = datetime.now().strftime("%Y-%m-%d %H:%M")
    return render_template("index.html", data_files=ordered_files, last_run=last_run)


@app.route("/details", methods=(["GET"]))
def details():
    "Return static page with data collection details"
    return render_template("details.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
