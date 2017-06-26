# -*- coding: utf-8 -*-
import requests
import itertools
from lxml import html
from decimal import Decimal


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

        url = "https://www.flyniki.com/ru/booking/" \
              "flight/vacancy.php?departure={0}" \
              "&destination={1}&outboundDate={2}&returnDate={3}" \
              "&oneway={4}&openDateOverview=0&adultCount=1&" \
              "childCount=0&infantCount=0".format(self.departure,
                                                  self.destination,
                                                  self.outbound_date,
                                                  self.return_date,
                                                  self.oneway_bool_url)

        with requests.Session() as s:
            request_get = s.get(url)
            request_post = s.post(request_get.url, data=ajax_dict)
            return request_post.json()

    def make_results(self, path):
        self.currency = self.tree.get_element_by_id("flight-table-" \
                                                    "header-price-" \
                                                    "ECO_COMF").text
        price_str = "//label[@id='priceLabelId{0}Fi_{1}']/" \
                    "div[@class='lowest']/span/text()"
        departure_str = "//span[@id='flightDepartureFi_{0}']/time/text()"
        duration_str = "//span[@id='flightDurationFi_{0}']/text()"

        tr = path.getchildren()
        count = len(tr) / 2
        results = []
        classes = (("COMF", "Econom"), ("PREM", "Flex"), ("FLEX", "Business"))

        for vacancy_num in range(count):
            departure = path.xpath(departure_str.format(vacancy_num))
            departure = "-".join(departure)

            duration = path.xpath(duration_str.format(vacancy_num))[0]

            for class_str, class_val in classes:
                try:
                    price = path.xpath(price_str.format(class_str, vacancy_num))[0]
                    price = Decimal(price.split(",")[0])
                    results.append({"class": class_val,
                                    "price": price,
                                    "departure": departure,
                                    "duration": duration})
                except IndexError:
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
            error = tree.xpath("//div[@class='wrapper']/" \
                               "div[@class='entry formCheck']/p")[0]
            raise ScraperError(error.text + "\n")

    def get_vacancy(self, block):
        try:
            flight_tables = self.tree.get_element_by_id("flighttables")
            tbody = flight_tables.xpath("//div[@class='{0}']" \
                                        "/div[@class='tablebackground']" \
                                        "/table[@class='flighttable']" \
                                        "/tbody".format(block))[0]
            return self.make_results(tbody)
        except KeyError:
            raise ScraperError("Не удалось найти рейсов " \
                               "на запрошенные даты\n")
        except IndexError:
            return None

    def make_search(self):
        self.print_info()

        self.json = self.get_json()
        self.tree = self.make_tree()

        self.outbound_vacancy = self.get_vacancy("outbound block")
        self.return_vacancy = self.get_vacancy("return block")

        if self.return_vacancy is None:
            self.print_results(self.sort_results(self.outbound_vacancy))
        else:
            self.print_mixed_results(self.sort_results(self.mix_results()))

    def mix_results(self):
        mixed_results = []
        num = 1
        for out, ret in itertools.product(self.outbound_vacancy,
                                          self.return_vacancy):
            mixed_results.append({"price": str(out["price"] + ret["price"]),
                                  "outbound duration": out["duration"],
                                  "outbound departure": out["departure"],
                                  "return duration": ret["duration"],
                                  "return departure": ret["departure"],
                                  "classes": "-".join([out["class"], ret["class"]])})
            num += 1
        return mixed_results

    def print_results(self, val):
        for j, i in enumerate(val, 1):
            print "Вариант номер {0}:\n\tВремя вылета-прилета: {1}\n" \
                  "\tДлилетльность перелета: {2}\n\tЦена: {3}\n" \
                  "\tКласс: " \
                  "{4}".format(j,
                               i["departure"],
                               i["duration"],
                               str(i["price"]) + self.currency,
                               i["class"])

    def print_mixed_results(self, val):
        for j, i in enumerate(val, 1):
            print "Вариант номер: {6}\n" \
                  "\tВремя вылета/прилета в прямом направлении: {0}\n" \
                  "\tВремя в пути: {1}\n" \
                  "\tВремя вылета/прилета в обратном напревлении: {2}\n" \
                  "\tвремя в пути: {3}\n" \
                  "\tКлассы : {4}\n" \
                  "\tЦена: {5}".format(i["outbound departure"],
                                       i["outbound duration"],
                                       i["return departure"],
                                       i["return duration"],
                                       i["classes"],
                                       i["price"] + self.currency,
                                       j)

    def sort_results(self, val):
        return sorted(val, key=lambda v: float(v["price"]))
