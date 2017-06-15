# -*- coding: utf-8 -*-
import requests
from lxml import html


class MyException(Exception):
    def __init__(self, text):
        print text


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
            self.oneway_ajax = ""
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
        self.json = self.get_json()
        self.tree = self.make_tree()
        self.outbound_vacancy = self.get_vacancy("outbound block")
        self.return_vacancy = self.get_vacancy("return block")

        self.print_results(self.outbound_vacancy)
        self.print_results(self.return_vacancy)

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
                return request_post.json()
            else:
                raise MyException("No json")

    def make_results(self, path):
        tr = path.getchildren()
        count = len(tr)/2
        results = {}
        for i in range(count):
            price_comf = path.get_element_by_id("priceLabelIdCOMFFi_" + str(i))
            price_comf = price_comf.xpath(".//div[@class='current']/span")[0]

            price_prem = path.get_element_by_id("priceLabelIdPREMFi_" + str(i))
            price_prem = price_prem.xpath(".//div[@class='current']/span")[0]

            departure = path.get_element_by_id("flightDepartureFi_" + str(i))
            departure_time = [j.text for j in departure.getchildren()]
            departure_time = "-".join(departure_time)

            duration = path.get_element_by_id("flightDurationFi_"+str(i))

            results[i] = {"price comfort": price_comf.text,
                          "price premium": price_prem.text,
                          "departure": departure_time,
                          "duration": duration.text}
        return results

    def make_tree(self):
        try:
            main = self.json["templates"]["main"]
            tree = html.fromstring(main)
            return tree
        except KeyError:
            main = self.json["error"]
            tree = html.fromstring(main)
            error = tree.xpath("//div[@class='wrapper']/" +
                               "div[@class='entry formCheck']/p")[0]
            raise MyException(error.text)

    def get_vacancy(self, block):
        try:
            flight_tables = self.tree.get_element_by_id("flighttables")
            tbody = flight_tables.xpath(("//div[@class='{0}']" +
                                         "/div[@class='tablebackground']" +
                                         "/table[@class='flighttable']" +
                                         "/tbody").format(block))[0]
            return self.make_results(tbody)
        except KeyError:
                raise MyException("Не удалось найти рейсов " +
                                  "на запрошенные даты")
        except IndexError:
                return None

    def print_results(self, val):
        if type(val) == dict:
            for i in val.keys():
                print i, val[i]
        else:
            pass
