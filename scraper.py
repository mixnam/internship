# -*- coding: utf-8 -*-
import requests
import itertools
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
        self.currency = self.tree.get_element_by_id("flight-table-" +
                                                    "header-price-" +
                                                    "ECO_COMF").text

        tr = path.getchildren()
        count = len(tr) / 2
        results = {}
        for i in range(count):
            price_comf = path.get_element_by_id("priceLabelIdCOMFFi_" + str(i))
            price_comf = price_comf.xpath(".//div[@class='current']/span")[0]
            price_comf = Decimal(price_comf.text.split(",")[0])

            price_prem = path.get_element_by_id("priceLabelIdPREMFi_" + str(i))
            price_prem = price_prem.xpath(".//div[@class='lowest']/span")[0]
            price_prem = Decimal(price_prem.text.split(",")[0])

            departure = path.get_element_by_id("flightDepartureFi_" + str(i))
            departure_time = [j.text for j in departure.getchildren()]
            departure_time = "-".join(departure_time)

            duration = path.get_element_by_id("flightDurationFi_" + str(i))
            duration = duration.text

            results[i + 1] = {"Light": {"price": price_comf,
                                        "duration": duration,
                                        "departure": departure_time},
                              "Flex": {"price": price_prem,
                                       "duration": duration,
                                       "departure": departure_time}}

            try:
                price_bus = path.get_element_by_id("priceLabelIdFLEXFi_" +
                                                   str(i))
                price_bus = price_bus.xpath(".//div[@class='lowest']/span")[0]
                price_bus = Decimal(price_bus.text.split(",")[0])
                results[i + 1].setdefault("Busines", {"price": price_bus,
                                                      "duration": duration,
                                                      "departure": departure_time})
            except KeyError:
                pass

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

        self.outbound_vacancy = self.get_vacancy("outbound block")
        self.return_vacancy = self.get_vacancy("return block")

        if self.return_vacancy is None:
            self.print_results()
        else:
            self.print_mixed_results(self.sort_mixed_results(self.mix_results()))

    def mix_results(self):
        mixed_results = {}
        vacancy_num = 1
        for i, j in itertools.product(self.outbound_vacancy,
                                      self.return_vacancy):
            for k, l in itertools.product(self.outbound_vacancy[i],
                                          self.return_vacancy[j]):
                mixed_results[vacancy_num] = {"price": str(self.outbound_vacancy[i][k]["price"] +
                                                           self.return_vacancy[j][l]["price"]),
                                              "outbound duration": self.outbound_vacancy[i][k]["duration"],
                                              "outbound departure": self.outbound_vacancy[i][k]["departure"],
                                              "return duration": self.return_vacancy[j][l]["duration"],
                                              "return departure": self.return_vacancy[j][l]["departure"],
                                              "classes": "-".join([k, l])}
                vacancy_num += 1
        return mixed_results

    def print_results(self):
        val = self.outbound_vacancy
        for i in val:
            print ("Вариант номер {0}:\n\tвремя вылета-прилета {1}\n" +
                   "\tдлилетльность перелета - {2}\n\tцена " +
                   "'econom light' - {3}" +
                   "\n\tцена 'econom flex' - " +
                   "{4}").format(i,
                                 val[i]["Light"]["departure"],
                                 val[i]["Light"]["duration"],
                                 str(val[i]["Light"]["price"]) + self.currency,
                                 str(val[i]["Flex"]["price"]) + self.currency)
            try:
                print "\tцена 'busines'" + str(val[i]["Busines"]["price"]) + self.currency
            except KeyError:
                pass

    def print_mixed_results(self, val):
        for i in val:
            print ("Вариант номер: {6}\n"
                   "\tВремя вылета/прилета в приямом направлении: {0}\n" +
                   "\tВремя в пути: {1}\n" +
                   "\tВремя вылета/прилета в обратном напревлении: {2}\n" +
                   "\tвремя в пути: {3}\n" +
                   "\tКлассы : {4}\n" +
                   "\tЦена: {5}").format(i[1]["outbound departure"],
                                         i[1]["outbound duration"],
                                         i[1]["return departure"],
                                         i[1]["return duration"],
                                         i[1]["classes"],
                                         i[1]["price"] + self.currency,
                                         i[0])

    def sort_mixed_results(self, val):
        return sorted(val.items(), key=lambda (k, v): v["price"])
