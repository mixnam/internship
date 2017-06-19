# -*- coding: utf-8 -*-
import requests
from lxml import html
from decimal import Decimal


def try_KeyError(f):
    def wrap(self, *args):
        try:
            return f(self, *args)
        except KeyError:
            raise ScraperError("что-то не так в make_results")
    return wrap


class ScraperError(Exception):
    def __init__(self, value):
        self.value = value


class Scraper(object):
    def __init__(self, departure, destination, outbound_date, return_date=0):
        self.departure = departure
        self.destination = destination
        self.outbound_date = outbound_date.strftime("%Y-%m-%d")
        if not return_date:
            self.oneway_bool_ajax = "on"
            self.oneway_bool_url = 1
            self.return_date = outbound_date.strftime("%Y-%m-%d")
        else:
            self.oneway_bool_ajax = ""
            self.oneway_bool_url = 0
            self.return_date = return_date.strftime("%Y-%m-%d")

        self.make_search()

    def print_info(self):
        print "Departure: %s" % self.departure
        print "Destination: %s" % self.destination
        print "Outbound date: %s" % self.outbound_date
        print "Return date: %s" % self.return_date

    def get_json(self):
        ajax_dict = {"_ajax[templates][]": ["main",
                                            "priceoverview",
                                            "infos",
                                            "flightinfo"],
                     "_ajax[requestParams][openDateOverview]": "",
                     "_ajax[requestParams][departure]": self.departure,
                     "_ajax[requestParams][childCount]": 0,
                     "_ajax[requestParams][returnDate]": self.return_date,
                     "_ajax[requestParams]" +
                     "[outboundDate]": self.outbound_date,
                     "_ajax[requestParams][oneway]": self.oneway_bool_ajax,
                     "_ajax[requestParams][adultCount]": 1,
                     "_ajax[requestParams]" +
                     "[destination]": self.destination,
                     "_ajax[requestParams][infantCount]": 0,
                     "_ajax[requestParams][returnDestination]": "",
                     "_ajax[requestParams][returnDeparture]": ""}

        url = ("https://www.flyniki.com/ru/booking/" +
               "flight/vacancy.php?departure={0}" +
               "&destination={1}&outboundDate={2}&returnDate={3}" +
               "&oneway={4}&openDateOverview=0&adultCount=1&" +
               "childCount=0&infantCount=0").format(self.departure,
                                                    self.destination,
                                                    self.outbound_date,
                                                    self.return_date,
                                                    self.oneway_bool_url)

        with requests.Session() as s:
            request_get = s.get(url)
            request_post = s.post(request_get.url, data=ajax_dict)
            if request_post.json():
                return request_post.json()
            else:
                raise ScraperError("No json")

    @try_KeyError
    def make_results(self, path):
        tr = path.getchildren()
        count = len(tr)/2
        results = {}
        for i in range(count):
            currency_comf = self.tree.get_element_by_id("flight-table-" +
                                                        "header-price-" +
                                                        "ECO_COMF")
            currency_prem = self.tree.get_element_by_id("flight-table-" +
                                                        "header-price-" +
                                                        "ECO_PREM")

            price_comf = path.get_element_by_id("priceLabelIdCOMFFi_" + str(i))
            price_comf = price_comf.xpath(".//div[@class='current']/span")[0]
            price_comf = (Decimal(price_comf.text.split(",")[0]),
                          currency_comf)

            price_prem = path.get_element_by_id("priceLabelIdPREMFi_" + str(i))
            price_prem = price_prem.xpath(".//div[@class='lowest']/span")[0]
            price_prem = (Decimal(price_prem.text.split(",")[0]),
                          currency_prem)

            try:
                currency_bus = self.tree.get_element_by_id("flight-table-" +
                                                           "header-price-" +
                                                           "BUS_FLEX")
                price_bus = path.get_element_by_id("priceLabelIdFLEXFi_" +
                                                   str(i))
                price_bus = price_bus.xpath(".//div[@class='lowest']/span")[0]
                price_bus = (Decimal(price_bus.text.split(",")[0]),
                             currency_bus)
            except KeyError:
                price_bus = "нет доступных мест"

            departure = path.get_element_by_id("flightDepartureFi_" + str(i))
            departure_time = [j.text for j in departure.getchildren()]
            departure_time = "-".join(departure_time)

            duration = path.get_element_by_id("flightDurationFi_"+str(i))
            duration = duration.text

            results[i] = {"price comfort": price_comf,
                          "price premium": price_prem,
                          "price busines": price_bus,
                          "departure": departure_time,
                          "duration": duration}

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
            raise ScraperError(error.text + "\n")

    def get_vacancy(self, block):
        try:
            flight_tables = self.tree.get_element_by_id("flighttables")
            tbody = flight_tables.xpath(("//div[@class='{0}']" +
                                         "/div[@class='tablebackground']" +
                                         "/table[@class='flighttable']" +
                                         "/tbody").format(block))[0]
            return self.make_results(tbody)
        except KeyError:
            raise ScraperError("Не удалось найти рейсов " +
                               "на запрошенные даты\n")
        except IndexError:
            return None

    def make_search(self):
        self.json = self.get_json()
        self.tree = self.make_tree()

        outbound_vacancy = self.get_vacancy("outbound block")
        return_vacancy = self.get_vacancy("return block")

        self.print_results(outbound_vacancy)
        self.print_results(return_vacancy)

    # def sort_results(self, val, val2):
    #     k = ["EL","EF","BS"]
    #     k = ["-".join(i) for i in itertools.product(k,k)]
    #     v = [0]*10
    #     sorted_results = dict(zip(k,v))
    #     if type(val) and type(val2) == dict:
    #         for i in sorted_results.keys():
    #             for j in val:
    #                 for k in val2:
    #                     sorted_results[i] = {j+k: }

    def print_results(self, val):
        if type(val) == dict:
            for i in val.keys():
                print ("{0} вариант:\nвремя вылета-прилета {1}, " +
                       "длилетльность перелета - {2}\nцена " +
                       "'econom light' - {3}" +
                       "\nцена 'econom flex' - {4}" +
                       "\nцена 'busines' - " +
                       "{5}").format(i + 1,
                                     val[i]["departure"],
                                     val[i]["duration"],
                                     str(val[i]["price comfort"][0]),
                                     str(val[i]["price premium"][0]),
                                     str(val[i]["price busines"][0]))
        else:
            pass
