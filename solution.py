import sys
import logging
import re
from datetime import datetime

#GLOBALS
level = logging.DEBUG
SUCCESS_RESPONSE = '200'

def main():
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    try:
        with open(sys.argv[1], 'r') as f:
            lines = f.read().splitlines()
            f.close()
            process_data(lines)

    except IOError:
        logging.error("error reading the file") 


# Takes an array of strings and finds the number of unique IP addreses,
# top three most active IP addreses and top three most vistied URLs
def process_data(lines):
    ip_dict = {}
    url_dict = {}

    for line in lines:
        line_dict = process_line(line)
        try:
            if line_dict['ip'] not in ip_dict.keys():
                ip_dict[line_dict['ip']] = 1
            else:
                ip_dict[line_dict['ip']] += 1

            if line_dict['res_code']==SUCCESS_RESPONSE:
                if line_dict['url'] not in url_dict.keys():
                    url_dict[line_dict['url']] = 1
                else:
                    url_dict[line_dict['url']] += 1
        except KeyError:
            logging.warn("Regex error in line: %s", line)
    
    unique_ips = len(ip_dict.keys())
    sorted_ips = sorted(ip_dict.items(), key=lambda tup:tup[1], reverse=True)
    sorted_urls = sorted(url_dict.items(), key=lambda tup:tup[1], reverse=True)

    # write the results to an output file
    f = open(sys.argv[2], "w")
    f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S\n"))
    f.write("Input file: %s\n" %(sys.argv[1]))
    f.write("The number of unique IP Addresses is %s\n" %(unique_ips))
    f.write("The top three active IP addresses are:\n")
    get_top_three(sorted_ips, f)
    f.write("The top three visited urls are:\n")
    get_top_three(sorted_urls, f)
    f.close()

# Parses a line from the log file and returns a dictionary
# containing the IP address, URL and response code
def process_line(line):
    line_dict = {}

    # find the IP
    try:
        ip = re.search('^\S*', line).group(0)
        if ip:
            line_dict['ip'] = ip
            #logging.debug(ip)
    except AttributeError:
        logging.warn("Regex error for IP in line: %s", line)

    try:
        # find the URL
        url = re.search('(?<=GET )\S*', line).group(0)
        if url:
            line_dict['url'] = url
            #logging.debug(url)
    except AttributeError:
        logging.warn("Regex error for URL in line: %s", line)  

    # get the response code
    try:
        res_code = re.search('(?<=" )\d*', line).group(0)
        if res_code:
            line_dict['res_code'] = res_code
            #logging.debug(res_code)
    except AttributeError:
        logging.warn("Regex error in res code in line: %s", line)

    return line_dict

# takes a sorted list and writes the top 3 to a file
def get_top_three(list, f):
        
    for i in range(3):
        try:
            f.write("    - %s (%s times)\n" %(list[i][0],list[i][1]))
        except IndexError:
            logging.error("Regex error - no value found")

    # this solution takes into account that there are elements tied
    # for certain places and therefore top three might actually have
    # more than three values    
    # count = 0
    # prev = -1
    # for i in list:
    #     if i[1] != prev:
    #         if count >= 3:
    #             break
    #         count+=1
    #         prev=i[1]
    #         f.write("    - %s (%s times)\n" %(i[0],i[1]))
    #     else:
    #         count+=1
    #         f.write("    - %s (equal %s times)\n" %(i[0],i[1]))

if __name__ == "__main__":
    main()