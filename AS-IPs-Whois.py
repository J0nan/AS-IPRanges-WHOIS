import requests
import csv
import argparse
import ipaddress
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
    description = ""
    inetnum = ""
    if objects:
        attributes = objects[0].get("attributes", [])
        inetnum = objects[0].get("key") if objects[0].get("type") == "inetnum" else ""
        for attr in attributes:
            if attr.get("attribute") == "descr":
                description = attr.get("value")
                break
    elif suggestions:
        attributes = suggestions[0].get("attributes", [])
        inetnum = suggestions[0].get("key") if suggestions[0].get("type") == "inetnum" else ""
        for attr in attributes:
            if attr.get("attribute") == "descr":
                description = attr.get("value")
                break
    if inetnum:
        ipNetwork = range_to_cidr(inetnum)
        if len(ipNetwork) == 1:
            return (ipNetwork[0], description)
    return (ipRange, description)

def range_to_cidr(ipRange):
    startIpStr, endIpStr = [ip.strip() for ip in ipRange.split('-')]
    startIp = ipaddress.IPv4Address(startIpStr)
    endIp = ipaddress.IPv4Address(endIpStr)
    return [str(cidr) for cidr in ipaddress.summarize_address_range(startIp, endIp)]

def clean_results(results):
    cleaned_results = []
    # Inverse sort by the mask
    results_sorted = sorted(results, key=lambda x: ipaddress.ip_network(x[0]).prefixlen, reverse=True)

    for i, (ip_inner, descr_inner) in enumerate(results_sorted):
        inner_network = ipaddress.ip_network(ip_inner)
        remove = False

        for ip_outer, descr_outer in results_sorted[i + 1:]:
            outer_network = ipaddress.ip_network(ip_outer)
            
            # Check if inner network is inside outer network
            if inner_network.subnet_of(outer_network):
                # Same description - remove inner network
                if descr_inner == descr_outer:
                    remove = True
                    break
                # Inner has no description, outer has one - remove inner network
                elif descr_inner == "" and descr_outer != "":
                    remove = True
                    break

        if not remove:
            cleaned_results.append((ip_inner, descr_inner))

    return sorted(cleaned_results, key=lambda x: ipaddress.ip_network(x[0]))

def save_to_csv(results, filename, headerRow):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headerRow)
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save AS descriptions of IP ranges using RIPE.")
    parser.add_argument("--saveIPs", required=False, default=False, action='store_true', help="Save all the IP ranges from the AS in a file")
    parser.add_argument("--noDescription", required=False, default=False, action='store_true', help="Do not save the IP ranges description from the AS in a file")
    parser.add_argument("-AS", required=True, help="Autonomous System (AS) number to query.")
    parser.add_argument("-o", required=True, help="Output CSV file name.")
    args = parser.parse_args()

    asNumber = args.AS
    outputFile = args.o

    ipRanges = get_ipRanges(asNumber)
    if args.saveIPs:
        save_to_csv([(ip,) for ip in ipRanges], "IPs_" + outputFile, ["IP Range"])
        print(f"Results saved to IPs_{outputFile}")

    if not args.noDescription:
        results = [get_whois_data(ip) for ip in tqdm(ipRanges, desc="Fetching WHOIS data from RIPE")]
        print("Cleaning up results.")
        results = clean_results(results)

        save_to_csv(results, outputFile, ["IP Range", "Description"])
        print(f"Results saved to {outputFile}")
