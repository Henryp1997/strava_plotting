from datetime import datetime
import os

def read_config(string):
    with open(f'{os.path.dirname(os.path.realpath(__file__))}/config.txt', 'r') as f:
        params = f.readlines()
    
    return [i.split(" = ")[1] for i in params if string in i][0].strip("\n")

def get_weekly_averaged_data(data_list, dates):
    """ get data as a list of weekly totals """

    data_list = list(data_list)
    dates = list(dates)
    
    data_list.reverse()
    dates.reverse()
    last_run_date = dates[-1]

    # get list of all mondays since first run
    mondays = ['2022-04-18']
    month_dict = {
    '01': 31, '02': 28, '03': 31, '04': 30, '05': 31, '06': 30, '07': 31, '08': 31, '09': 30, '10': 31, '11': 30, '12': 31
    }
    year = '2022'
    for i in range(1, 200):
        month = mondays[i-1].split("-")[1]
        day = int(mondays[i-1].split("-")[2])

        if 3 < day < 10:
            day = f'0{day + 7}'
        else:
            day = f'{day + 7}'
        date = f'{year}-{month}-{day}'
    
        max_day = month_dict[date.split("-")[1]]
        day = int(date.split("-")[2])
        if day > max_day:
            if month == '12':
                offset = -11
                year = f'{int(year) + 1}'
            else:
                offset = 1
            month = list(month_dict.keys())[list(month_dict.keys()).index(date.split("-")[1]) + offset]
            day = f'0{day - max_day}'
            date = f'{year}-{month}-{day}'

        if date.split("-")[2][0] == '0' and int(date.split("-")[2].split("0")[1]) > 9:
            day = date.split("-")[2].split("0")[1]
            date = f'{year}-{month}-{day}'
            
        mondays.append(date)
    
    for i, monday in enumerate(mondays):
        if datetime.strptime(monday, "%Y-%m-%d") > last_run_date:
            last_monday_idx = i
            break
    
    mondays = [datetime.strptime(i, "%Y-%m-%d") for i in mondays[:last_monday_idx+1]]

    data_weekly = [0 for i in range(len(mondays))]
    for i, val in enumerate(data_list):
        for j, monday in enumerate(mondays):
            if dates[i] < mondays[0] and j == 0:
                data_weekly[j] += val
            else:
                if mondays[j-1] < dates[i] < monday:
                    data_weekly[j] += val

    data_list.reverse()
    dates.reverse()
    return data_weekly