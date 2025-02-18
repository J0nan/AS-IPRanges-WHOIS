# AS-IPRanges-WHOIS
Fetch and save AS descriptions of IP ranges using RIPE

## How it works

It uses [Maxmind Geo Lite Announced By AS](https://stat.ripe.net/docs/02.data-api/maxmind-geo-lite-announced-by-as.html) API in order to retrive all the IP ranges of an autonomous system. For all those IP ranges, it uses [Historical Whois](https://stat.ripe.net/docs/02.data-api/historical-whois.html) API in order to retrive the description asosited to thoses IPs. If the API call returns a message or does not have an exact match it will not be saved on the csv. On the other hand if it finds an exact match it will be saved on the csv with the description if it is founded.

## Requirements

Install dependancies found on the requirements.txt file.

```shell
pip install -r requirements.txt
```

## Usage

```shell
python AS-IPs-Whois.py -AS AS3333 -o AS3333.csv
```

`-AS AS3333` sets the autonomous system.

`-o AS3333.csv` sets the filename of the output.
