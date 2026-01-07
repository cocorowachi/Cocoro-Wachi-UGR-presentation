import csv
import io
import re
import warnings
import numpy as np
import pandas as pd

class Data:
    def __init__(self, csv_path):

        # Read file into memory
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            stringio = io.StringIO(f.read())
            reader = csv.reader(stringio)

        # --- Detect number of header lines ---
        num_header_lines = 0
        next(reader, None)  # skip first line (often a title or junk)
        for line in reader:
            if re.search('[A-Za-z]{2,}', str(line)):
                num_header_lines += 1
            else:
                break
        
        # If no header rows → simple CSV
        if num_header_lines == 0:
            # Just load normally
            df = pd.read_csv(csv_path, parse_dates=[0])
            df = df.set_index(df.columns[0]).apply(pd.to_numeric, errors="coerce").ffill()
            self.data = df
            return

        # --- Extract header rows ---
        stringio.seek(0)
        reader = csv.reader(stringio)
        head_lines = list(reader)[1:num_header_lines+1]

        # Collapse header rows (col-wise concatenation)
        heads = ["".join(col) for col in zip(*head_lines)]
        # Detect blank trailing columns
        blank_cols = 0
        for h in reversed(heads):
            if not re.search('[A-Za-z0-9]', h):
                blank_cols += 1
            else:
                break
        if blank_cols > 0:
            del heads[-blank_cols:]

        # --- Backfill blank cells within multi-row header ---
        if num_header_lines > 1:
            for line_idx in range(len(head_lines)):
                line = head_lines[line_idx]
                last_val = ""
                for cell_idx in range(len(line)):
                    cell_val = line[cell_idx]
                    if not re.search('[A-Za-z0-9]', cell_val): #if cell is blank
                        head_lines[line_idx][cell_idx] = last_val
                    else:
                        last_val = cell_val
            heads = ["".join(i) for i in zip(*head_lines)]
            if blank_cols > 0:
                del heads[-blank_cols:] #delete blank headers from list

        # if second column has "date" or "time" in header assume there are 2 datetime columns, otherwise assume only 1
        if re.search('date|time', heads[1], re.IGNORECASE):
            num_dt_cols = 2
        else:
            num_dt_cols = 1

        # create DataFrame
        stringio.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            df = pd.read_csv(stringio,
                            header=None,
                            skiprows=num_header_lines,
                            parse_dates={'datetime': [i for i in range(num_dt_cols)]}, #combines if 2 dt columns
                            #parse_dates results in DeprecationWarning as of pandas 2.2
                            thousands=',',
                )
        # drop blank trailing columns if any
        if blank_cols > 0:
            tot_cols = len(df.columns)
            col_idxs_to_drop = list(np.arange(tot_cols-blank_cols, tot_cols))
            df = df.drop(columns=df.columns[col_idxs_to_drop]) #drop last columns


        # set datetime column as index
        df.set_index('datetime', inplace=True)
        df = df.drop(index="Date")
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric, errors='coerce')
        # --- Forward-fill ---
        df = df.mask(df < 0, None)
        df = df.ffill()

        # Save final DataFrame
        df.columns = heads[1:]
        self.data = df

    def read(self, col):
        return self.data[col]