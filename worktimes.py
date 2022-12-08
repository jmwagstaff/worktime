import pandas as pd
import click
from datetime import datetime


TIMES_FILE = "working-times.csv"


@click.group()
def wt():
    pass


@wt.command()
@click.option("--time", "-t", "time_entry", default=None, help="")
def stop(time_entry):
    # check last entry was 'start'
    lastline = get_last_line(TIMES_FILE).split(",")
    if len(lastline) == 3:
        print("No action taken. Last entry was 'stop', try 'start'")
    elif len(lastline) != 2:
        print(f"Something is wrong with last line: {lastline}")
    else:
        if time_entry is None:
            now = datetime.now()
            time_entry = ", " + now.strftime("%H:%M")
        print(f"Writing time_entry: {time_entry}")
        overwrite_last_line(TIMES_FILE, time_entry)


@wt.command()
@click.option("--time", "-t", "time_entry", default=None, help="")
def start(time_entry):
    # check last entry was 'stop'
    lastline = get_last_line(TIMES_FILE).split(",")
    if len(lastline) == 2:
        print("No action taken. Last entry was 'start', try 'stop'")
    elif len(lastline) != 3:
        print(f"Something is wrong with last line: {lastline}")
    else:
        if time_entry is None:
            now = datetime.now()
            time_entry = now.strftime("%d.%m.%Y, %H:%M")
        else:
            # check time_entry
            # build time_entry with date
            pass
        print(f"Writing time_entry: {time_entry}")
        add_new_line(TIMES_FILE, time_entry)


def add_new_line(filename, text):
    with open(filename, "a") as f:
        f.write(f"\n{text}")


def overwrite_last_line(filename, text):
    with open(filename, "r") as f:
        lines = f.readlines()
        lines[-1] = lines[-1] + text

    with open(filename, "w") as f:
        f.writelines(lines)


def get_last_line(filename):
    with open(filename, "r") as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
    return last_line


@wt.command()
def show():
    # show by default current week, add flag for --all
    df = get_df()
    df["date"] = df["Date"].dt.strftime("%a %d-%m-%Y")
    df["in"] = df["In_datetime"].dt.strftime("%H:%M")
    df["out"] = df["Out_datetime"].dt.strftime("%H:%M")
    print("\n")
    print(df[["date", "in", "out", "duration"]])


@wt.command()
@click.option("--fill", "-f", "fill_missing_entry", is_flag=True, default=False, help="")
def show_tiso(fill_missing_entry):
    df = get_df(fill_missing_entry=fill_missing_entry)

    lunch = pd.Timedelta("30 min")

    per_day_df = df.groupby(df.Date).agg({"In_datetime": "first", "duration": "sum"})
    per_day_df["duration_plus_lunch"] = per_day_df["duration"] + lunch
    per_day_df["eff_end_time"] = per_day_df["In_datetime"] + per_day_df["duration_plus_lunch"]
    per_day_df.reset_index(inplace=True)
    per_day_df["date"] = per_day_df["Date"].dt.strftime("%a %d-%m-%Y")
    per_day_df["in"] = per_day_df["In_datetime"].dt.strftime("%H:%M")
    per_day_df["out"] = per_day_df["eff_end_time"].dt.strftime("%H:%M")
    # per_day_df["worktime"] = per_day_df["duration"].dt.strftime('%H:%M')
    print("\n")
    print(per_day_df[["date", "in", "out", "duration"]])


@wt.command()
@click.option("--ndays", "-n", "n_days", default=1, help="")
def day(n_days):
    df = get_df(fill_missing_entry=True)

    lunch = pd.Timedelta("30 min")

    per_day_df = df.groupby(df.Date).agg({"In_datetime": "first", "duration": "sum"})
    per_day_df["duration_plus_lunch"] = per_day_df["duration"] + lunch
    per_day_df["eff_end_time"] = per_day_df["In_datetime"] + per_day_df["duration_plus_lunch"]
    per_day_df.reset_index(inplace=True)
    per_day_df["date"] = per_day_df["Date"].dt.strftime("%a %d-%m-%Y")
    per_day_df["in"] = per_day_df["In_datetime"].dt.strftime("%H:%M")
    per_day_df["out"] = per_day_df["eff_end_time"].dt.strftime("%H:%M")
    # per_day_df["worktime"] = per_day_df["duration"].dt.strftime('%H:%M')
    print("\n")
    print(per_day_df[["date", "in", "out", "duration"]].tail(n_days))


def get_df(fill_missing_entry=False):
    df = pd.read_csv(TIMES_FILE)
    df["Date"].fillna(method="ffill", inplace=True)

    nans = df.isnull().sum().sum()
    if nans > 1:
        raise Exception("Warning, there are multiple incomplete entries! Check the data!")
    elif nans == 1 and df["Out"].tail(1).notnull().values:
        raise Exception("There is a single entry missing which is not the last Out! Check the data!")
    else:
        if fill_missing_entry and df["Out"].tail(1).isnull().values:
            print("Filling incomplete Out entry with current time!")
            df["Out"] = df["Out"].fillna(datetime.now().strftime("%H:%M"))

        df["In_datetime"] = pd.to_datetime(df["Date"] + " " + df["In"], dayfirst=True)
        df["Out_datetime"] = pd.to_datetime(df["Date"] + " " + df["Out"], dayfirst=True)

        df["duration"] = df["Out_datetime"] - df["In_datetime"]
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
        return df


if __name__ == "__main__":
    wt()