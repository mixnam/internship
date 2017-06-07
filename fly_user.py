# -*- coding: utf-8 -*-
import sys
import datetime


class Scraper():
    def __init__(self, a, b, c, d=0):
        self.departure = a
        self.destination = b
        self.outboundDate = c
        if not d:
            self.returnDate = c
        else:
            self.returnDate = d

    def print_info(self):
        print "Departure: %s" % self.departure
        print "Dectination: %s" % self.destination
        print "Out bound date: %s" % self.outboundDate
        print "Return date: %s" % self.returnDate


def make_date(date_str):
    date_str_list = date_str.split("-")
    date_int_list = [int(i) for i in date_str_list]
    date_int_list.reverse()
    try:
        date = datetime.date(*date_int_list)
        return date
    except TypeError:
        return None


def validation_date(date_high_str, date_low_str=0):
    if not date_low_str:
        date_low = datetime.date.today()
    else:
        date_low = make_date(date_low_str)

    date_high = make_date(date_high_str)

    if date_high is None or date_low is None:
        return False
    else:
        if date_high >= date_low:
            return True
        else:
            return False


def validation_IATA(IATAcode):
    if IATAcode.isalpha() and IATAcode.isupper() and len(IATAcode) == 3:
        return True
    else:
        return False


def validation(departure, destination, outboundDate, returnDate=0):
    if not returnDate:
        returnDate = outboundDate

    if not validation_date(outboundDate):
        print "You should specify outbound date in this sequence " +\
                "'day-month-year' " +\
                "like this : '5-5-2017'\nOr you specifyed a past date" +\
                "\nPlease check that"
        return False
    elif not validation_date(returnDate, outboundDate):
        print "Your return date can't be before outbound date" +\
                "\nPlease check that"
        return False
    elif not validation_IATA(departure):
        print "You specify wrong departure IATA-code"
        return False
    elif not validation_IATA(destination):
        print "You specify wrong destination IATA-code"
        return False
    else:
        return True


def main():
    if len(sys.argv) == 1:
        print "You don't specify argumetns"
    else:
        argumetns = sys.argv[1:]

    if validation(*argumetns):
        scrap = Scraper(*argumetns)
        scrap.print_info()


main()
