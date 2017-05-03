# ripe_atlas_eyeball_coverage
Produce a list of Eyeball networks with low or none RIPE Atlas probe coverage





Run python find_asns.py

usage: find_asns.py [-h] -c CONNECTED -n NUMBER_OF_ASNS


Find Eyeball Networks missing RIPE ATLAS probe coverage

optional arguments:
  -h, --help            show this help message and exit
  -c CONNECTED, --connected CONNECTED
                        Number of connected probes to use as a threshold to
                        assume a network is covered
  -n NUMBER_OF_ASNS, --number_of_asns NUMBER_OF_ASNS
                        Number of ASNs to return
