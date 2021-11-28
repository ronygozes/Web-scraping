import argparse


def args_parse(func):
    def wrapper():
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--duration", help="How many hours back to scrape: 1 - 24",
                            type=int, default=24)
        parser.add_argument("-m", "--magnitude", help="Minimum magnitude to scrape from the site",
                            type=float, default=0)
        parser.add_argument("-b", "--batch", help="Number of insertions before committing in MySQL",
                            type=int, default=1)
        parser.add_argument("-a", "--attempts", help="Number of attempts to scrape the site",
                            type=int, default=50)

        args = parser.parse_args()
        func(args.batch, args.duration, args.magnitude, args.attempts)

    return wrapper
#
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-d", "--duration", help="How many hours back to scrape: 1 - 24")
#     parser.add_argument("-m", "--magnitude", help="Minimum magnitude to scrape from the site")
#     parser.add_argument("-m", "--magnitude", help="Minimum magnitude to scrape from the site")
#
#     args = parser.parse_args()
#
#
# if __name__ == '__main__':
#     main()
