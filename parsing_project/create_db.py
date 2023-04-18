import sqlite3 as sq


def main():
    with sq.connect('offers.db') as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE offers (
          offer_id TEXT,
          address TEXT,
          price TEXT,
          square TEXT,
          link TEXT
        )
      """)


if __name__ == '__main__':
    main()
