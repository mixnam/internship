# -*- coding: utf-8 -*-
"""main module"""
import datetime
import argparse
import sys
from scraper import Scraper, ScraperError


class ValidationError(Exception):
    """My new validation exeption"""
    def __init__(self, value):
        super(ValidationError, self).__init__()
        self.value = value


def validation_date_str(date_str):
    """Check the format of date-string"""
    try:
        date = datetime.datetime.strptime(date_str, "%d-%m-%Y")
        return date
    except ValueError:
        msg = "\nYou should specify date like this: DD-MM-YYYY " \
              "\nNot like this : {0}\n".format(date_str)
        raise ValidationError(msg)


def date_is_valid(date_high, date_low=0):
    """Compare the date"""
    return bool(date_high >= (date_low or datetime.datetime.now()))


def validation_iata(iata_code):
    """Check the format of IATA-string"""
    if iata_code.isalpha() and iata_code.isupper() and len(iata_code) == 3:
        return iata_code
    else:
        msg = "\nYou specify wrong IATA-code, it should be like this : 'AAA'\n"
        raise ValidationError(msg)


def check_dates(outbound_date, return_date=0):
    """Check the dates"""
    date_limit = datetime.datetime.now() + datetime.timedelta(360)

    if not return_date:
        return_date = outbound_date

    if not date_is_valid(outbound_date):
        msg = "You can't spesify outbound date erlier than {0}\n" \
              "Please check that\n".format(datetime.datetime.now().strftime("%d-%m-%Y"))
        raise ValidationError(msg)
    elif not date_is_valid(return_date, outbound_date):
        msg = "Your return date can't be before outbound date" \
              "\nPlease check that\n"
        raise ValidationError(msg)
    elif not date_is_valid(date_limit, (outbound_date and return_date)):
        msg = "You can't specify outbound or return date latter than {0}\n" \
              "Please check that\n".format(date_limit.strftime("%d-%m-%Y"))
        raise ValidationError(msg)
    else:
        return True


def main():
    """main function"""
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("departure_IATA",
                            type=validation_iata,
                            help="Specify IATA-code of your departure airport")
        parser.add_argument("destination_IATA",
                            type=validation_iata,
                            help="Specify IATA of your destination airport")
        parser.add_argument("outbound_date",
                            type=validation_date_str,
                            help="Specify outbound date")
        parser.add_argument("return_date",
                            nargs="?",
                            default=0,
                            type=validation_date_str,
                            help="If you don't want fly oneway," \
                                 " specify return date")
        args = parser.parse_args()

        if check_dates(args.outbound_date, args.return_date):
            srap = Scraper(args.departure_IATA,
                           args.destination_IATA,
                           args.outbound_date,
                           args.return_date)
            srap.make_search()

        return 0
    except (ScraperError, ValidationError) as err:
        sys.stderr.write(err.value)
        return 1


if __name__ == "__main__":
    sys.exit(main())
