import csv
import io
import re
import pandas as pd

class Data:
    def __init__(self, csv_path):
        # Read file into memory
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            stringio = io.StringIO(f.read())
            reader = csv.reader(stringio)

        # detect header
        string_pattern = re.compile(r'[A-Za-z]{2,}')
        
        num_header = 0
        next(reader, None)
        for line in reader:
            if string_pattern.search(str(line)):
                num_header += 1
            else:
                break
        
        # If no header rows -> simple CSV
        if num_header == 0:
            # Just load normally
            df = pd.read_csv(csv_path, parse_dates=[0])
            df = df.set_index(df.columns[0]).apply(pd.to_numeric, errors="coerce").ffill()
            self.data = df
            return
        
        # else:
        # collapse header rows (col-wise concatenation)
        stringio.seek(0)
        reader = csv.reader(stringio)
        heads = ["".join(col) for col in zip(*list(reader)[1:num_header+1])]

        # make df
        stringio.seek(0)
        df = pd.read_csv(stringio, header=None, skiprows=num_header, parse_dates={'datetime': [0]}, thousands=',')

        # set index, align data types
        df.set_index('datetime', inplace=True)
        df = df.drop(index="Date")
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric, errors='coerce')
        # ffill negative values
        df = df.mask(df < 0, None)
        df = df.ffill()

        df.columns = heads[1:]
        self.data = df

    def read(self, col):
        return self.data[col]