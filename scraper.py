# -*- coding: utf-8 -*-
import requests
from lxml import html


class Scraper():
    def __init__(self, departure, destination, outboundDate, returnDate=0):
        self.departure = departure
        self.destination = destination
        self.outboundDate = outboundDate.strftime("%Y-%m-%d")
        if not returnDate:
            self.oneway_ajax = "on"
            self.oneway_url = 1
            self.returnDate = outboundDate.strftime("%Y-%m-%d")
        else:
            self.oneway_ajax = "off"
            self.oneway_url = 0
            self.returnDate = returnDate.strftime("%Y-%m-%d")

        self.ajax_dict = {"_ajax[templates][]": ["main",
                                                 "priceoverview",
                                                 "infos",
                                                 "flightinfo"],
                          "_ajax[requestParams][openDateOverview]": "",
                          "_ajax[requestParams][departure]": self.departure,
                          "_ajax[requestParams][childCount]": 0,
                          "_ajax[requestParams][returnDate]": self.returnDate,
                          "_ajax[requestParams]" +
                          "[outboundDate]": self.outboundDate,
                          "_ajax[requestParams][oneway]": self.oneway_ajax,
                          "_ajax[requestParams][adultCount]": 1,
                          "_ajax[requestParams]" +
                          "[destination]": self.destination,
                          "_ajax[requestParams][infantCount]": 0,
                          "_ajax[requestParams][returnDestination]": "",
                          "_ajax[requestParams][returnDeparture]": ""}

        self.url = ("https://www.flyniki.com/ru/booking/" +
                    "flight/vacancy.php?departure={0}" +
                    "&destination={1}&outboundDate={2}&returnDate={3}" +
                    "&oneway={4}&openDateOverview=0&adultCount=1&" +
                    "childCount=0&infantCount=0").format(self.departure,
                                                         self.destination,
                                                         self.outboundDate,
                                                         self.returnDate,
                                                         self.oneway_url)

    def print_info(self):
        print "Departure: %s" % self.departure
        print "Destination: %s" % self.destination
        print "Out bound date: %s" % self.outboundDate
        print "Return date: %s" % self.returnDate

    def get_json(self):
        with requests.Session() as s:
            request_get = s.get(self.url)
            request_post = s.post(request_get.url, data=self.ajax_dict)
            if request_post.json():
                main = request_post.json()["templates"]["main"]
                self.tree = html.fromstring(main)
                flight_tables = self.tree.get_element_by_id("flighttables")
                tbody = flight_tables.xpath("//div[@class='outbound block']" +
                                            "/div[@class='tablebackground']" +
                                            "/table[@class='flighttable']" +
                                            "/tbody")[0]
                tr = tbody.getchildren()
                self.vacancy_number = len(tr)/2
                self.make_results()
            else:
                print "No json"

    def make_results(self):
        self.results = {}
        for i in range(self.vacancy_number):
            price_comf = self.tree.get_element_by_id("priceLabelIdCOMFFi_" +
                                                     str(i))
            price_comf = price_comf.xpath(".//div[@class='current']/span")[0]

            price_prem = self.tree.get_element_by_id("priceLabelIdPREMFi_" +
                                                     str(i))
            price_prem = price_prem.xpath(".//div[@class='current']/span")[0]

            departure = self.tree.get_element_by_id("flightDepartureFi_" +
                                                    str(i))
            departure_time = [j.text for j in departure.getchildren()]
            departure_time = "-".join(departure_time)

            duration = self.tree.get_element_by_id("flightDurationFi_"+str(i))

            self.results[i] = {"price comfort": price_comf.text,
                               "price premium": price_prem.text,
                               "departure": departure_time,
                               "duration": duration.text}

        for i in self.results.keys():
            print i, self.results[i]
