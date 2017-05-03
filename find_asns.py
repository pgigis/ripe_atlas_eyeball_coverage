#!/usr/bin/env python
import os
import csv
import sys
import json
import argparse
from ripe.atlas.cousteau import ProbeRequest

### Initializing paths

sys.path.append("%s/lib" % ( os.path.dirname(os.path.realpath(__file__) ) ) )
curr_dict = os.path.dirname(os.path.realpath(__file__))

from Atlas import Measure

json_of_results = list()

number_of_users_cover = 0
count_ASNs = 0


# Args
parser = argparse.ArgumentParser(description="Find Eyeball Networks missing RIPE ATLAS probe coverage")
parser.add_argument('-c', '--connected', dest='connected', type=int, help="Number of connected probes to use as a threshold to assume a network is covered", required=True)
parser.add_argument('-n', '--number_of_asns', dest='number_of_asns', type=int, help="Number of ASNs to return", required=True)
#parser.add_argument('-a', '--apnic_filename', dest='apnic_filename', type=str, help="Provide the apnic filename", required=True)
args = parser.parse_args()


def check_if_asn_covered(asns, threshold_connected_probes, saved_asns):
	
	#Case asns is a list of asns
	for asn in asns:
		
		print "Processing " + str(asn["ASN"])

		asn_n = asn["ASN"].split("AS")[1]
		filters = {"asn_v4": asn_n}
		probes = ProbeRequest(**filters)

		probes_dict = dict()
		count_connected = 0
		count_disconnected = 0
		count_abandoned = 0
		count_never_connected = 0

		detail_dict = dict()

		for probe in probes:
			if(probe['status']['name'] == "Connected"):
				count_connected = count_connected + 1
			
			elif(probe['status']['name'] == "Never Connected"):
				count_never_connected = count_never_connected + 1

			elif(probe['status']['name'] == "Disconnected"):
				count_disconnected = count_disconnected + 1

			elif(probe['status']['name'] == "Abandoned"):
				count_never_connected = count_never_connected + 1
		
		detail_dict["AS_name"] = asn["AS Name"]
		detail_dict["connected"] = count_connected
		detail_dict["disconnected"] = count_disconnected
		detail_dict["abandoned"] = count_abandoned
		detail_dict["never_connected"] = count_never_connected
		detail_dict["estimated_users"] = asn['Users (est.)']
		detail_dict["apnic_obj"] = asn

		if(count_connected <= threshold_connected_probes):
			json_of_results.append( (asn["ASN"], detail_dict) )
			return True

		return False



#Load APNIC Data
with open("dataset.json", 'r') as data:
	asns_apnic = json.load(data)


values_list = asns_apnic.keys()
values_list = [int(x) for x in values_list]
values_list.sort(reverse=True)


for i in values_list:

	if(args.number_of_asns == count_ASNs):
		break

	if(check_if_asn_covered(asns_apnic[str(i)], args.connected, json_of_results)):
		count_ASNs = count_ASNs + 1
		number_of_users_cover = number_of_users_cover + i

print "Total Users:" + str(number_of_users_cover)

with open('json_results.json', 'w') as outfile:
    json.dump(json_of_results, outfile)


#Provide .csv (comma seperated) file

results_csv = open("results_csv.csv", 'a+')
results_csv.write("ASN,  Name, Connected, Disconnected, Abandoned, Never Connected, Estimated Number of Users \n")


for asn in json_of_results:

	results_csv.write( str(asn[0]) + ", " + str(asn[1]["apnic_obj"]["AS Name"]) + ", " + str(asn[1]["connected"]) + ", " + str(asn[1]["disconnected"]) + ", " + str(asn[1]["abandoned"]) + ", " + str(asn[1]["never_connected"]) + ", " + str(asn[1]["estimated_users"]) + "\n")


results_csv.close()



