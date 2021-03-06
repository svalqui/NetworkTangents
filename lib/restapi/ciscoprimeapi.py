# "https://server/webacs/api/v2/data/ClientSessions.json?.full=true&userName=tommyblue",
# "https://server/webacs/api/v1/data/RadioDetails?.full=true&operStatus=\"DOWN\"&slotId=\"0\"",
# "https://server/webacs/api/v1/data/RadioDetails?.full=true&operStatus=\"DOWN\"",
# "https://server/webacs/api/v1/data/RadioDetails?.full=true&operStatus=\"DOWN\"&slotId=\"0\"&apName=contains(\"EXT\")"
# "https://server/webacs/api/v2/data/ClientSessions/59036754\"
# "https://server/webacs/api/v2/data\"
#  reachabilityStatus - D_Content : str Value : Reachable
# url = "https://server/webacs/api/v2/data/ClientSessions.json?.full=true&userName=" # Check Working
# url = "https://server/webacs/api/v1/data/Alarms.json?.condition.value=AP_DISASSOCIATED&severity=MAJOR"
# url = "https://server/webacs/api/v1/data/Alarms.json?.full=true"
# url = "https://server/webacs/api/v2/data/AccessPointDetails/587698.json?.full=true" # Checked working
# Pagination = 99

import requests
import json
from requests.auth import HTTPBasicAuth
import lib.restapimaster
import time


class CiscoPrimeApi(lib.restapimaster.RestApi):
    def __init__(self, user_name, password, url_prime):
        super(CiscoPrimeApi, self).__init__()
        self.user_name = user_name
        self.password = password
        self.urlbase = url_prime  # "https://pi.mydomain.net"
        self.url_unreachable = self.urlbase + "/webacs/api/v2/data/AccessPointDetails.json?.full=true" \
                   "&reachabilityStatus=UNREACHABLE"
        self.url_paged = ""
        self.list_content = []
        self.page = ""
        self.page_decoded = ""
        self.reach_page_end = False
        self.page_counter = 0
        self.first_result = 0
        self.max_result = 0
        self.current_page = ""

    def read_page(self, url, debug=False):
        self.url_paged = url
        if debug:
            print("read_page reading ...",self.url_paged)
        self.page = requests.get(self.url_paged, headers=self.header_json, verify=False,
                                 auth=HTTPBasicAuth(self.user_name, self.password))
        time.sleep(0.1)
        if debug:
            print("Querying :  ", self.url_paged)
            print(self.page.status_code)
        self.page_decoded = json.loads(self.page.text)
        return self.page_decoded

    def page_handler(self, url, debug=False):
        self.reach_page_end = False
        self.page_counter = 0
        self.first_result = 0
        self.max_result = 99
        self.url_paged = ""
        self.list_content = []
        if debug:
            print("page_handler initiating while")
        while not self.reach_page_end:
            self.url_paged = url + "&.maxResults=" + str(self.max_result) + \
                             "&.firstResult=" + str(self.first_result)
            if debug:
                print("requesting current page  ", self.url_paged)
            self.current_page = self.read_page(self.url_paged)
            # self.navigate_json(self.current_page)
            self.list_content.append(self.current_page)
            self.page_counter = self.current_page['queryResponse']["@count"]
            if debug:
                print("page_counter", self.page_counter)
                print("returning last...", self.current_page['queryResponse']["@last"])
            if self.current_page['queryResponse']["@last"] > self.page_counter:
                self.first_result += 100
            else:
                self.reach_page_end = True
        return self.list_content

    def read_unreachable(self, debug=False):
        if debug:
            print("calling page_handler")
        self.list_content = self.page_handler(self.url_unreachable)
        return

    def list_unreachable_neighbors(self, debug=False):
        list_ap_neighbor = []
        list_ap_no_neighbor = []
        if debug:
            print("calling read_unreachable...")
        self.read_unreachable()
        if debug:
            print("received unreachable")
        for item in self.list_content:
            for entity in item['queryResponse']['entity']:
                # print(i['@url'])
                if debug:
                    print(entity['accessPointDetailsDTO']['name'])
                if 'cdpNeighbors' in entity['accessPointDetailsDTO'] :
                    # print(type(i['accessPointDetailsDTO']['cdpNeighbors']))
                    for neighbor in entity['accessPointDetailsDTO']['cdpNeighbors'].keys():
                        # print(type(i['accessPointDetailsDTO']['cdpNeighbors'][j]))
                        for detail in entity['accessPointDetailsDTO']['cdpNeighbors'][neighbor]:
                            if debug:
                                print(detail["neighborName"])
                                print(detail["neighborPort"])
                                print()
                            list_ap_neighbor.append([entity['accessPointDetailsDTO']['name'], detail["neighborName"],
                                                     detail["neighborPort"]])
                else:
                    if debug:
                        print("No cdpNeighbors on this device\n")
                    list_ap_no_neighbor.append(entity['accessPointDetailsDTO']['name'])
        return list_ap_neighbor, list_ap_no_neighbor

# queryResponse - D_Content : dict found on dict resending
#   @last - D_Content : int Value : 47
#   @count - D_Content : int Value : 48
#   @type - D_Content : str Value : AccessPointDetails
#   @requestUrl - D_Content : str Value : https://server/webacs/api/v2/data/AccessPointDetails?.full=true&amp;reachabilityStatus=UNREACHABLE&amp;.maxResults=99&amp;.firstResult=0
#   @rootUrl - D_Content : str Value : https://server/webacs/api/v2/data
#   @responseType - D_Content : str Value : listEntityInstances
#   @first - D_Content : int Value : 0
#   entity - D_Content : list found on dict resending, len : 48
#     - L-Content : list here
#     - L-Content : dict found on list resending
#     accessPointDetailsDTO - D_Content : dict found on dict resending
#       clientCount_5GHz - D_Content : int Value : 0
#       cdpNeighbors - D_Content : dict found on dict resending
#         cdpNeighbor - D_Content : list found on dict resending, len : 1
#           - L-Content : list here
#           - L-Content : dict found on list resending
#           neighborName - D_Content : str Value : sw-123
#           platform - D_Content : str Value : cisco WS-C3750X-48P
#           duplex - D_Content : str Value : Full Duplex
#           localPort - D_Content : str Value : 2
#           interfaceSpeed - D_Content : str Value : 1Gbps
#           neighborPort - D_Content : str Value : GigabitEthernet2/0/17
#           capabilities - D_Content : str Value : Switch IGMP
#           neighborIpAddress - D_Content : str Value : 172.1.1.26
#         unifiedApInfo - D_Content : dict found on dict resending
#           contryCode - D_Content : str Value : AU
#           iosVersion - D_Content : str Value : 15.3(3)JBB6$
#           wlanProfiles - D_Content : dict found on dict resending
#             wlanProfile - D_Content : list found on dict resending, len : 0
#               - L-Content : list here
#             portNumber - D_Content : int Value : 0
#             apStaticEnabled - D_Content : int Value : 0
#             capwapJoinTakenTime - D_Content : int Value : 10300
#             statisticsTimer - D_Content : int Value : 180
#             bootVersion - D_Content : str Value : 12.4.23.0
#             wlanVlanMappings - D_Content : dict found on dict resending
#               wlanVlanMapping - D_Content : list found on dict resending, len : 0
#                 - L-Content : list here
#               rogueDetectionEnabled - D_Content : int Value : True
#               apMode - D_Content : str Value : 0
#               apGroupName - D_Content : str Value : General
#               poeStatus - D_Content : str Value : 4
#               preStandardState - D_Content : int Value : 0
#               wipsenabled - D_Content : str Value : 0
#               flexConnectMode - D_Content : int Value : False
#               secondaryMwar - D_Content : str Value : wlc-1
#               telnetEnabled - D_Content : int Value : False
#               encryptionEnabled - D_Content : int Value : False
#               linkLatencyEnabled - D_Content : int Value : False
#               sshEnabled - D_Content : int Value : True
#               poeStatusEnum - D_Content : str Value : NORMAL
#               apCertType - D_Content : int Value : 1
#               powerInjectorState - D_Content : int Value : 1
#               primaryMwar - D_Content : str Value : wlc-2
#           apType - D_Content : str Value : AP3600I
#           clientCount_2_4GHz - D_Content : str Value : 0
#           adminStatus - D_Content : str Value : ENABLE
#           name - D_Content : str Value : APf872.ead0.2b18
#           reachabilityStatus - D_Content : str Value : Unreachable
#           @id - D_Content : int Value : 587941
#           locationHeirarchy - D_Content : str Value : Root Area
#           macAddress - D_Content : str Value : 00:00:00:00:12:34
#           @displayName - D_Content : str Value : 587
#           model - D_Content : str Value : AIR-CAP3602I-N-K9
#           softwareVersion - D_Content : str Value : 8.1.131.0
#           ethernetMac - D_Content : str Value : 00:00:00:00:00:18
#           mapLocation - D_Content : str Value : Hiden very well
#           serialNumber - D_Content : str Value : SN1234
#           clientCount - D_Content : str Value : 0
#           type - D_Content : str Value : UnifiedAp
#           status - D_Content : str Value : CLEARED
#           ipAddress - D_Content : str Value : 10.1.1.78
#       @url - D_Content : str Value : https://pi.uni.net.au/webacs/api/v2/data/AccessPointDetails/587
#       @dtoType - D_Content : str Value : accessPointDetailsDTO
#       @type - D_Content : str Value : AccessPointDetails
#     - L-Content : dict found on list resending
#     accessPointDetailsDTO - D_Content : dict found on dict resending

