#*******************************************************************************#
#                                                                               #
#     Heroku deployment account:                                                #
#       Email:  ...@gmail.com                                                   #
#       Password:  ...                                                          #
#                                                                               #
#     Hanldes queries to google ngrams, returns a timeseries of the usage       #
#       frequency in the google books corpus from 1800-2019 as a line chart     #
#                                                                               #
#*******************************************************************************#

import json
from pathlib import Path
from matplotlib import pyplot
from urllib.request import urlopen



#*********************************************************#
#                                                         #
#   Frequency data normalization function                 #
#     Input:   raw timeseries data                        #
#     Outputs: data normalized to minimum of 1,           #
#              year in which the data is normalized to,   #
#              year where the global maximum is reached   #
#                                                         #
#*********************************************************#
def normalize(timeseries):
    nozeros = [x for x in timeseries if x != 0]                      # remove zeros from the timeseries
    smallest = min(nozeros)                                          # find minimum value in the timeseries
    norm = [round(value/smallest,5) for value in timeseries]         # normalize the timeseries to the smallest value
    biggest = max(norm)                                              # find the maximum value in the normalized timeseries
    for i in range(len(norm)):
        if norm[i] == 1:
            smallest_year = i+1800                                   # find the year in which the smallest value is reached
        if norm[i] == biggest:
            biggest_year = i+1800                                    # find the year in which the biggest value is reached
    return norm, smallest_year, biggest_year



#*********************************************************#
#                                                         #
#   Main n-gram searching function                        #
#     Input:   query string                               #
#     Outputs: data normalized to minimum of 1,           #
#              year in which the data is normalized to,   #
#              year where the global maximum is reached,  #
#              actual search term, start year, end year   #
#                                                         #
#*********************************************************#
def get(query):
    url, search, start, end = getURL(query)                           # get ngram url
    with urlopen(url) as response:
        datajson = json.loads(response.read())[0]                     # read the json data
    try: timeseries = datajson['timeseries']                          # extract the timeseries
    except Exception as e: print(f"\n>>>  Error:  {e}")
    norm, smallest_year, biggest_year = normalize(timeseries)         # normalize the timeseries
    return norm, smallest_year, biggest_year, search, start, end



#*********************************************************#
#                                                         #
#   URL getter function                                   #
#     Input:   query string, start year,                  #
#              end year, and smoothing amount             #
#     Outputs: google ngram url string,                   #
#              actual search term, star year, end year    #
#                                                         #
#*********************************************************#
def getURL(query, start=1800, end=2019, smoothing=0, **kwargs):
    if ',' in query:
        split_str = query.split(',')                                  # split query into list
        if split_str[0][0] != '.':                                    # only accept queries beginning with '.'
            return
        else:
            search = split_str[0][1:]                                 # take everything from '.' to ',' for search string
        if ' ' in search:
            search = search.replace(' ', '+')                         # spaces need to be '+'s in URL
    
        for i in range(1, len(split_str)):
            if 'start' in split_str[i]:
                try: start = int(split_str[i].split('=')[1])          # get start year as int
                except Exception as e: print(f"\n>>>  {e}")
            if 'end' in split_str[i]:
                try: end = int(split_str[i].split('=')[1])            # get end year as int
                except Exception as e: print(f"\n>>>  {e}")
            if 'smoothing' in split_str[i]:
                try: smoothing = int(split_str[i].split('=')[1])      # get smoothing value as int
                except Exception as e: print(f"\n>>>  {e}")
    else:
        search = query[1:]                                            # search string is everything after '.' in query
        if ' ' in search:
            search = search.replace(' ', '+')                         # spaces need to be '+'s in URL
    
    if start > 2019 or start < 1500:                                  # start year can only be between 1500 and 2019
        start = 1800
    if end > 2019 or end < 1500:                                      # end year can only be between 1500 and 2019
        end = 2019
    if start > end:                                                   # start cannot be greater than end
        start, end = end, start
    if smoothing < 0:                                                 # smoothing cannot be negative
        smoothing = -smoothing
    
    url = (
      'https://books.google.com/ngrams/json?content=' + search +
      '&year_start=' + str(start) + '&year_end=' + str(end) +
      '&corpus=26&smoothing=' + str(smoothing) + '&case_insensitive=true'
    )
    return url, search, start, end





#*********************************************************#
#                                                         #
#   Plot generating function                              #
#     Input:  search string (passed to get function)      #
#     Output: png image file (saves locally for main)     #
#                                                         #
#*********************************************************#
def plot(query, avg=False, span=2):
    x = [i+start for i in range(len(timeseries))]
    timeseries, smallest_year, biggest_year, search, start, end = get(query)
    print(f"\n\n[plot function]>>>  Searching for {search} from {start} to {end}\n\n")

    pyplot.tight_layout()
    pyplot.style.use('ggplot')
    pyplot.rcParams['figure.figsize'] = (17, 10)
    pyplot.subplots_adjust(right=0.93, bottom=0.15)
    pyplot.yticks(font=Path('font/InconsolataRegular.ttf'), fontsize=30, color='white')
    pyplot.xticks(range(start, end, 25), font=Path('font/InconsolataRegular.ttf'), fontsize=30, color='white')
    pyplot.xlabel('year', font=Path('font/JetBrainsMonoMediumItalic.ttf'), fontsize=33, labelpad=41, color='white')
    pyplot.ylabel('frequency', font=Path('font/JetBrainsMonoMediumItalic.ttf'), fontsize=30, labelpad=38, color='white')
    pyplot.title('"'+str(search)+'"', font=Path('font/JetBrainsMonoExtraBold.ttf'), fontsize = 35, pad = 30, color='white')

    pyplot.plot(x,timeseries)
    pyplot.axvline(x=biggest_year, color='#BBBBBB', linestyle='--')
    pyplot.axvline(x=smallest_year, color='#BBBBBB', linestyle='--')
    pyplot.savefig('pic.png', format='png', facecolor='#36393f')
    pyplot.close()
