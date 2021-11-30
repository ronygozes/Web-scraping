import argparse

from configs import args_parser_config as config


def args_parse(func):
    """
    :param func: the main function to receive command line arguments
    :return: a wrapper function to supply command line arguments to the main function
    """
    def wrapper():
        """
        gives command line arguments to the function supplied
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--duration", help="How many hours back to scrape: 1 - 24",
                            type=int, default=config.DURATION)
        parser.add_argument("-m", "--magnitude", help="Minimum magnitude to scrape from the site",
                            type=float, default=config.MAGNITUDE)
        parser.add_argument("-b", "--batch", help="Number of insertions before committing in MySQL",
                            type=int, default=config.BATCH)
        parser.add_argument("-a", "--attempts", help="Number of attempts to scrape the site",
                            type=int, default=config.ATTEMPTS)

        args = parser.parse_args()
        func(args.batch, args.duration, args.magnitude, args.attempts)

    return wrapper
