# -*- coding: utf-8 -*-
import datetime
import argparse
from scraper import Scraper


def validation_date_str(date_str):
    try:
        date = datetime.datetime.strptime(date_str, "%d-%m-%Y")
        return date
    except ValueError:
        msg = ("\nYou should specify date like this: DD-MM-YYYY " +
               "\nNot like this : {0}").format(date_str)
        raise argparse.ArgumentTypeError(msg)


def validation_date(date_high, date_low=0):
    if date_high >= (date_low or datetime.datetime.now()):
        return True
    else:
        return False


def validation_IATA(IATAcode):
    if IATAcode.isalpha() and IATAcode.isupper() and len(IATAcode) == 3:
        return IATAcode
    else:
        msg = "\nYou specify wrong IATA-code, it should be like this : 'AAA'"
        raise argparse.ArgumentTypeError(msg)


def validation(outboundDate, returnDate=0):
    if not returnDate:
        returnDate = outboundDate

    if not validation_date(outboundDate):
        print ("You can't spesify outbound date erlier than {0}\n" +
               "Please check that"
               ).format(datetime.datetime.now().strftime("%d-%m-%Y"))
        return False
    elif not validation_date(returnDate, outboundDate):
        print "Your return date can't be before outbound date" +\
                "\nPlease check that"
        return False
    else:
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("departureIATA",
                        type=validation_IATA,
                        help="Specify IATA-code of your departure airport")
    parser.add_argument("destinationIATA",
                        type=validation_IATA,
                        help="Specify IATA-code of your destination airport")
    parser.add_argument("outboundDate",
                        type=validation_date_str,
                        help="Specify outbound date")
    parser.add_argument("returnDate",
                        nargs="?",
                        default=0,
                        type=validation_date_str,
                        help=("If you don't want fly oneway," +
                              " specify return date"))
    args = parser.parse_args()

    if validation(args.outboundDate, args.returnDate):
        s = Scraper(args.departureIATA,
                    args.destinationIATA,
                    args.outboundDate,
                    args.returnDate)
        s.print_info()
    else:
        print "Something wrong"


if __name__ == "__main__":
    main()
