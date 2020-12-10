#!/bin/python3
from hydra.hydra import hydra_api as hydra
from datetime import date, time, datetime, timedelta
import json
import os 
import sys
import subprocess

HYDRA_USERNAME=os.environ.get('HYDRA_USERNAME')
HYDRA_PASSWORD=os.environ.get('HYDRA_PASSWORD')
SEARCH_KEYWORDS=os.environ.get('SEARCH_KEYWORDS')
SEARCH_VERSIONS=os.environ.get('SEARCH_VERSIONS')
TELEMETRY_URL=os.environ.get('TELEMETRY_URL')
CASE_URL=os.environ.get('CASE_URL')
OC_USERNAME=os.environ.get('OC_USERNAME')
OC_PASSWORD=os.environ.get('OC_PASSWORD')
OC_PROJECT=os.environ.get('OC_PROJECT')
OC_POD_LABEL=os.environ.get('OC_POD_LABEL')
OC_API_URL=os.environ.get('OC_API_URL')

if HYDRA_USERNAME == None or \
    HYDRA_PASSWORD == None or \
    CASE_URL == None or \
    OC_USERNAME == None or \
    OC_PASSWORD == None or \
    OC_PROJECT == None or \
    OC_POD_LABEL == None or \
    OC_API_URL == None or \
    TELEMETRY_URL == None:    
    print("Unable to start.  The following environment variables must be defined: \n - HYDRA_USERNAME\n - HYDRA_PASSWORD\n - TELEMETRY_URL\n - CASE_URL\n - OC_USERNAME\n - OC_PASSWORD\n - OC_PROJECT\n - OC_POD_LABEL\n - OC_API_URL")
    sys.exit(1)

if SEARCH_KEYWORDS == None:
    SEARCH_KEYWORDS = 'vmware,vsphere,vcenter,azure'

if SEARCH_VERSIONS == None:
    SEARCH_VERSIONS = '4.4,4.5,4.6'

hapi = hydra(username=HYDRA_USERNAME, password=HYDRA_PASSWORD)

keywords = SEARCH_KEYWORDS.split(',')
version = SEARCH_VERSIONS.split(',')

end_date = date.today()
start_date = end_date -  timedelta(days=7)

def getCaseLink(result):
    if 'case_number' not in result:
        return ''
    caseNo = result['case_number']
    return '<a href="'+CASE_URL.format(caseNo=caseNo)+'">'+caseNo+'</a>'
 
def getTelemetryLink(result):
    if 'case_openshift_cluster_id' not in result:
        return '--'
    clusterUid = result['case_openshift_cluster_id']
    if clusterUid == 'null':
        return '--'
    return '<a href="'+TELEMETRY_URL.format(clusterUid=clusterUid)+'">'+clusterUid+'</a>'

def getCaseDate(result):
    if 'case_createdDate' not in result:
        return ''
    return result['case_createdDate']

def getCaseSummary(result):
    if 'case_summary' not in result:
        return ''
    return result['case_summary']

def getHtmlLine(result):
    return "<tr><td>"+getCaseDate(result)+"</td>"+ \
    "<td>"+getCaseLink(result)+"</td>"+ \
    "<td>"+getTelemetryLink(result)+"</td>"+ \
    "<td>"+getCaseSummary(result)+"</td></tr>"

def getHtmlDoc(doc):
    outdoc = '<html>\n<head> <style>table, th, td {    border: 1px solid black;    border-collapse: collapse;}th, td {    padding: 5px;}</style></head>\n<body style="font-family: sans-serif;">\n'+ \
    '<h3>Cases from the last 7 days</h3>\n'+ \
    'Collected at: ' + str(datetime.now()) + \
    '<table>\n'+ \
    '<tr style="font-weight: bolder;background-color: black;border-color: black;color: white;"><td>Opened</td><td>Case</td><td>Telemetry</td><td>Description</td></tr>\n'
    for result in doc:
        summary = getCaseSummary(result).lower()        
        for keyword in keywords:
            if keyword in summary:
                outdoc = outdoc + getHtmlLine(result) + "\n"
                break    
    return outdoc + '</table></body></html>'

def pushCaseSummary():
    result = subprocess.run(["oc", "login", OC_API_URL, "-u", OC_USERNAME, "-p", OC_PASSWORD])
    result.check_returncode()
    print("Getting hosting pod")
    result = subprocess.run(["oc", "get", "pods", "-l", OC_POD_LABEL, "-n", OC_PROJECT, "-o=jsonpath='{.items[0].metadata.name}'"], capture_output=True)
    result.check_returncode()

    podName = result.stdout.decode("utf-8")
    podName = podName.replace("'","")

    print("Pushing report to " + podName)

    result = subprocess.run(["oc", "cp", "case_report.html", podName+":index.html"])
    result.check_returncode()
    
call_list = \
{
    'case_product': ['OpenShift Container Platform'], 
    'case_version': version, 
    'fl': ['case_number', 'case_summary', 'case_createdDate', 'case_openshift_cluster_id'], 
    'case_createdDate': '['+start_date.isoformat()+'T00:00:00Z TO '+end_date.isoformat()+'T00:00:00Z]', 
    'start': 0, 
    'rows': 10000
}

print("Collecting case data")
results = hapi.search_cases(**call_list)

if "response" in results:
    response = results["response"]
    if "docs" in response:        
        with open("case_report.html", "w") as outfile:
            outfile.write(getHtmlDoc(response["docs"]))
            print("Wrote case_report.html")
            print("Pushing case report")
        pushCaseSummary()
else:
    print("Received invalid response")        



