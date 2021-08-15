"""
functions to support the dashboard i/o
"""
import os
import datetime
import pandas as pd
import numpy as np


def get_file_name_for_date(search_folder, date_=None):
    """
    Finds the file name for the todays date
    :param search_folder: The destination folder to search
    :return: str, file_name
    """
    if date_ is None:
        today_date = datetime.datetime.today().strftime('%d-%m-%Y')
    else:
        today_date = date_

    files_ = [file for file in os.listdir(search_folder) if today_date in file]
    if len(files_) == 1:
        return files_[0]
    else:
        raise FileNotFoundError(f"Unable to find a unique file for {today_date} in {search_folder}")


def get_site_options(destination):
    """
    Extract the Site options to show on the dashboard from Real-> file containing actual solar values

    :param destination: The folder to search
    :return: dict of value:label for these options
    :rtype: dict
    """
    file_name = get_file_name_for_date(search_folder=destination, date_=None)
    file_ = pd.read_csv(os.path.join(destination, file_name))
    cols = sorted([col for col in file_.columns if 'Time' not in col])
    return [dict(label=t, value=t) for t in cols]


def get_today_date(date_or_str='date'):
    if 'date' in date_or_str:
        return datetime.datetime.today().date()
    else:
        return datetime.datetime.today().date().strftime('%d-%m-%Y')


def get_dates_in_dir(destination):
    return [file.split('.')[0] for file in os.listdir(destination) if os.path.isfile(os.path.join(destination, file))]


def get_min_max_dates(verbose=False, *args):
    """
    Extract minimum and maximum date available for dashboard
    :param args: *args are the destination to search for files to search the min date
    :return: tuple(minimum_date, maximum_date)
    """
    dirs = [dest for dest in args]

    all_files = []
    for one_dir in dirs:
        files_ = get_dates_in_dir(one_dir)
        all_files.append(files_)

    flat_list = [item for sublist in all_files for item in sublist]
    dates_ = []
    for item in flat_list:
        if 'log' not in item and 'scaled' not in item and len(item) > 1 and 'copy' not in item:
            try:
                date_date = datetime.datetime.strptime(item, '%d-%m-%Y')
                dates_.append(date_date)
            except ValueError as ve:
                if verbose:
                    print(f"Unable to parse {item}, {ve}")

    dates_ = list(set(dates_))
    return min(dates_).date(), max(dates_).date()


def get_outputs_to_show():
    vals = ['Actual', 'Day Ahead Ensemble', 'Satellite', 'IntraDay', 'Logs']
    return [dict(label=t, value=t) for t in vals]


def read_csv_data(destination, date, site=None):
    file_name = get_file_name_for_date(search_folder=destination, date_=date)
    data = pd.read_csv(os.path.join(destination, file_name))
    if site is not None:
        data = data[site][:95]

    return data


def read_excel_sheets(destination, date, site):
    file_name = get_file_name_for_date(search_folder=destination, date_=date)
    data = pd.read_excel(os.path.join(destination, file_name), engine='openpyxl', sheet_name=None)
    site_data = data.get(site).iloc[:, -2:]
    site_data.columns = [col[-8:] for col in site_data.columns]
    return site_data


def read_all_data_for_date_site(real_path,
                                intra_day_path,
                                day_ahead_ensemble_path,
                                satellite_forecast_path,
                                log_path,
                                date,
                                site):

    time_axis = pd.date_range(start='1/1/2018', periods=96, freq='15T').time

    try:
        real = read_csv_data(destination=real_path, date=date, site=site)

    except FileNotFoundError:
        real = pd.Series(np.repeat(np.nan, 96))

    try:
        intraday = read_csv_data(destination=intra_day_path, date=date, site=site)
    except FileNotFoundError:
        intraday = pd.Series(np.repeat(np.nan, 96))

    try:
        da_ensemble = read_csv_data(destination=day_ahead_ensemble_path, date=date, site=site)
    except FileNotFoundError:
        da_ensemble = pd.Series(np.repeat(np.nan, 96))

    try:
        satellite = read_csv_data(destination=satellite_forecast_path, date=date, site=site)
    except FileNotFoundError:
        satellite = pd.Series(np.repeat(np.nan, 96))

    try:
        log_data = read_excel_sheets(destination=log_path, date=date, site=site)
    except FileNotFoundError:
        log_data = pd.Series(np.repeat(np.nan, 96))


    intraday.name = 'IntraDay'
    real.name = 'Actual'
    da_ensemble.name = 'Day Ahead Ensemble'
    satellite.name = 'Satellite'
    log_data.name = 'Logs'

    temp_1 = pd.merge(left=intraday, right=da_ensemble, left_index=True, right_index=True, how='outer')
    temp_2 = pd.merge(left=temp_1, right=satellite, left_index=True, right_index=True, how='outer')
    temp_3 = pd.merge(left=temp_2, right=log_data, left_index=True, right_index=True, how='outer')
    temp_4 = pd.merge(left=temp_3, right=real, left_index=True, right_index=True, how='outer')
    temp_4 = temp_4.fillna(np.nan)

    def map_index_fun(x): return x.strftime('%H:%M')
    time_axis = [map_index_fun(x) for x in time_axis]
    temp_4.index = time_axis
    temp_4 = temp_4.round(2)
    return temp_4


def get_current_time(form='%d %B %Y %H:%M:%S'):
    return datetime.datetime.now().strftime(form)
