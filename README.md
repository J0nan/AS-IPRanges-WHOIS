# AS-IPRanges-WHOIS
Fetch and save AS descriptions of IP ranges using RIPE

## How it works

It uses [Maxmind Geo Lite Announced By AS](https://stat.ripe.net/docs/02.data-api/maxmind-geo-lite-announced-by-as.html) API in order to retrive all the IP ranges of an autonomous system. For all those IP ranges, it uses [Historical Whois](https://stat.ripe.net/docs/02.data-api/historical-whois.html) API in order to retrive the description asosited to thoses IPs.

## Requirements

Install dependancies found on the requirements.txt file.

```shell
git clone https://github.com/J0nan/AS-IPRanges-WHOIS.git
cd AS-IPRanges-WHOIS
python -m venv .
source ./bin/activate #For linux/macOS
pip install -r requirements.txt
```

To exit the Python Virtual Environment:

```shell
deactivate
```

## Usage

```shell
python AS-IPs-Whois.py -AS AS3333 -o AS3333.csv
```

`-AS AS3333` sets the autonomous system.

`-o AS3333.csv` sets the filename of the output.

`--saveIPs` when added an extra file is saved, with all the IP ranges from the autonomous system.

`--noDescription` when added it will not save the IP ranges description from the AS in a file, it will only retrieve all the IP ranges of the autonomous system.
