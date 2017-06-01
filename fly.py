# -*- coding: utf-8 -*-
import requests

url = "https://www.flyniki.com/ru/booking/flight/vacancy.php?departure=DME" +\
        "&destination=VIE&outboundDate=2017-05-31&returnDate=2017-05-31" +\
        "&oneway=0&openDateOverview=0&adultCount=1&childCount=0&infantCount=0"

ajax = "_ajax%5Btemplates%5D%5B%5D=main" +\
        "&_ajax%5Btemplates%5D%5B%5D=priceoverview&" +\
        "_ajax%5Btemplates%5D%5B%5D=infos" +\
        "&_ajax%5Btemplates%5D%5B%5D=flightinfo&" +\
        "_ajax%5BrequestParams%5D%5Bdeparture%5D=" +\
        "%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0+-+%D0%94%D0%BE%D0%B" +\
        "C%D0%BE%D0%B4%D0%B5%D0%B4%D0%BE%D0%B2%D0%BE&" +\
        "_ajax%5BrequestParams%5D%5Bdestination%5D=" +\
        "%D0%92%D0%B5%D0%BD%D0%B0&" +\
        "_ajax%5BrequestParams%5D%5BreturnDeparture%5D=" +\
        "&_ajax%5BrequestParams%5D%5BreturnDestination%5D=&" +\
        "_ajax%5BrequestParams%5D%5BoutboundDate%5D=2017-05-31&" +\
        "_ajax%5BrequestParams%5D%5BreturnDate%5D=2017-05-31" +\
        "&_ajax%5BrequestParams%5D%5BadultCount%5D=1" +\
        "&_ajax%5BrequestParams%5D%5BchildCount%5D=0" +\
        "&_ajax%5BrequestParams%5D%5BinfantCount%5D=0" +\
        "&_ajax%5BrequestParams%5D%5BopenDateOverview%5D=" +\
        "&_ajax%5BrequestParams%5D%5Boneway%5D="


def make_ajax_dict(ajax):
    ajax_list = ajax.split("&")
    ajax_dict = {}
    for i in ajax_list:
        a, b = i.split("=")
        while True:
            a1_find, a2_find = a.find("%5B"), a.find("%5D")
            if a1_find > 0:
                a = a[:a1_find] + "|" + a[a1_find+3:]
            elif a2_find > 0:
                a = a[:a2_find] + "|" + a[a2_find+3:]
            else:
                break
        ajax_dict[a] = b
    return ajax_dict


s = requests.Session()
r = s.get(url)
print s.cookies.keys()
print r.url
r2 = s.post(r.url, data=ajax)
print len(r2.content)
