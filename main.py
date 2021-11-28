import sql
import scraper
from args_parser import args_parse


@args_parse
def main(batch, duration, magnitude, attempts):
    df = scraper.main(attempts)
    if df is None:
        print('No new values available at this time, try again later')
        return
    dicts = []
    for i in range(len(df)):
        dicts.append(df.iloc[i].to_dict())
    # sql.create_db()
    # sql.create_tables()
    # sql.add_batch(dicts, batch)
    print(dicts)


if __name__ == '__main__':
    main()


