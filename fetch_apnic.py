import os
import sys
import json
import time
import urllib2
import argparse
import subprocess
from ripe.atlas.cousteau import ProbeRequest
from threading import Thread, Lock


# Initializing paths
sys.path.append("%s/lib" % ( os.path.dirname(os.path.realpath(__file__) ) ) )
root_path = os.path.dirname(os.path.realpath(__file__))

parallel_threads = 8


# parse command line arguments
parser = argparse.ArgumentParser(description="Fetch the APNIC estimates per country")
parser.add_argument("-c", "--country", dest="country", type=str, help="Country code to study (default = all)", default="all")
parser.add_argument("-p", "--cumulative_percent", dest="cumulative_percent", type=float, help="Threshold of cumulative percentage for population being covered (default = 95)", default=95)
parser.add_argument("-t", "--threshold_of_marketshare", dest="threshold_of_marketshare", type=float, help="Threshold to consider a network as eyeball (default = 0.1)", default=0.1)

args = parser.parse_args()


def save_networks(country, list_of_eyeballs):
    file_name = root_path + "/apnic_" + str(args.cumulative_percent) + "_" + str(args.threshold_of_marketshare) + "/" + country + ".json"
    with open( file_name , "w") as outfile:
        json.dump(list_of_eyeballs, outfile)


def fetch_data(country, cumulative_percent, threshold_of_marketshare):
    APNIC_ECON_URL = "http://v6data.data.labs.apnic.net/ipv6-measurement/Economies/%s/%s.asns.json?m=%s" % (country, country, threshold_of_marketshare)
    RIPESTAT_NAME_URL = "https://stat.ripe.net/data/whois/data.json?resource="
    econ_data = []
    list_of_eyeballs = list()

    try:
        req = urllib2.Request( APNIC_ECON_URL )
        conn = urllib2.urlopen( req )
        econ_data = json.load( conn )
    except:
        print "data URL unavailable, exiting (URL:%s)" % APNIC_ECON_URL

    if len(econ_data) == 0:
        print "data URL returned 0 ASNs for this economy (URL:%s)" % APNIC_ECON_URL
        return False

    else:
        for entry in econ_data:
            ripestat_response = None
            try:
                req = urllib2.Request(RIPESTAT_NAME_URL + str(entry["as"]))
                conn = urllib2.urlopen(req)
                ripestat_response = json.load(conn)
                if "data" in ripestat_response:
                    if "records" in ripestat_response["data"] and len(ripestat_response["data"]["records"]) > 0:
                        for record in ripestat_response["data"]["records"][0]:
                            if "key" in record and record["key"] == "as-name":
                                entry["autnum"] = record["value"]
                                break
            except:
                print "Failed to call RIPEStat" % RIPESTAT_NAME_URL + str(entry["as"])
                entry["autnum"] = "Not resolved" 

            del entry['cc']

            list_of_eyeballs.append(entry)

            if entry["cumulative"] >= cumulative_percent:
                break
    save_networks(country, list_of_eyeballs)


def fetch_country_codes(root_path):
    file_path = root_path + "/data/countries.txt"
    with open( file_path ) as f:
        lines = f.readlines()
    return  [(line.strip("\n")) for line in lines]


def main():
    
    file_path = root_path + "/apnic_" + str(args.cumulative_percent) + "_" + str(args.threshold_of_marketshare)
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if(args.country == "all"):

        list_of_threads = list()
        list_of_countries = fetch_country_codes(root_path)

        for country in list_of_countries:
            list_of_threads.append(Thread(target=fetch_data, args=( ( country, args.cumulative_percent, args.threshold_of_marketshare ))))

        for (i,thread) in enumerate(list_of_threads):
            thread.start()

            if(i % parallel_threads == 0):
                time.sleep(5)

        for thread in list_of_threads:
            thread.join()

    else:
        fetch_data(args.country, args.cumulative_percent, args.threshold_of_marketshare)


main()
