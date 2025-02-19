import requests
import csv
import argparse
from tqdm import tqdm

def get_ipRanges(asNumber):
    url = f"https://stat.ripe.net/data/maxmind-geo-lite-announced-by-as/data.json?resource={asNumber}"
    response = requests.get(url)
    data = response.json()
    locations = [entry.get("locations", []) for entry in data.get("data", {}).get("located_resources", [])]
    ipRanges = []
    for location in locations:
        ipRanges.extend(location[0].get("resources", []))
    return ipRanges

def get_whois_data(ipRange):
    url = f"https://stat.ripe.net/data/historical-whois/data.json?resource={ipRange}"
    response = requests.get(url)
    data = response.json()
    messages = data.get("messages", [])
    objects = data.get("data", {}).get("objects", [])
    suggestions = data.get("data", {}).get("suggestions", [])
    if objects:
        attributes = objects[0].get("attributes", [])
        for attr in attributes:
            if attr.get("attribute") == "descr":
                return attr.get("value")
    elif messages or suggestions:
        return -1
    return ""

def save_to_csv(results, filename, headerRow):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=',',)
        writer.writerow(headerRow)
        for result in results:
            if result[1] != -1:
                writer.writerow([result] if type(result) == str else result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save AS descriptions of IP ranges using RIPE.")
    parser.add_argument("--saveIPs", required=False, default=False, action='store_true', help="Save all the IP ranges from the AS in a file")
    parser.add_argument("-AS", required=True, help="Autonomous System (AS) number to query.")
    parser.add_argument("-o", required=True, help="Output CSV file name.")
    args = parser.parse_args()
    
    asNumber = args.AS
    outputFile = args.o
    
    ipRanges = get_ipRanges(asNumber)
    if args.saveIPs:
        save_to_csv(ipRanges, "IPs" + outputFile, ["IP Range"]) 
        print(f"Results saved to {"IPs" + outputFile}")
    results = [(ip, get_whois_data(ip)) for ip in tqdm(ipRanges, desc="Fetching WHOIS data from RIPE")]
    save_to_csv(results, outputFile, ["IP Range", "Description"])
    print(f"Results saved to {outputFile}")
