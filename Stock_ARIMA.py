# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 13:13:56 2019

@author: Mati
"""

#Clear all variables
# =============================================================================
# from IPython import get_ipython
# get_ipython().magic('reset -sf')
# =============================================================================
import matplotlib.pyplot as plt
import matplotlib.style as stl

import numpy as np
import os
import datetime as dt
import pandas_datareader.data as web
import easygui
import pandas as pd
from tkinter import *
import pmdarima as pmd


# =============================================================================
# Firmy, które możemy wybrać to m.in.:
#
# TSLA - Tesla
# MSFT - Microsoft
# EBAY - eBay
# TWTR - Twitter
# AMZN - Amazon
# INTC - Intel
# SBUX - Starbucks
# AAPL - Apple Inc.
# KO   - Coca-Cola
# F    - Ford Motor 
# FB   - Facebook
# GM   - General Motors
#
# =============================================================================

#IMPORTANT! Provide the working directory

os.chdir('C:\\Users\\Mati\\Desktop\\Python\\Projekty')

#Auxiliary function to set a date x months and x yeras ago

def monthdelta(date, delta):
    m, y = (date.month-delta) % 12, date.year + ((date.month)-delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

def yeardelta(date, delta):
    y = date.year - delta
    return date.replace(year = y)


#We can use different styles of graphs
    
#print(plt.style.available)
stl.use('ggplot')
#stl.use('grayscale')
#stl.use('fivethirtyeight')

#Input the company name you want to examine
sStock = str(easygui.enterbox("Podaj nazwę firmy"))

#Determine for how many periods the forecast is necessary
iPeriodsNumber = int(easygui.enterbox("Ile dni chcesz przewidzieć?"))

#Display a window with possible data periods to choose

root = Tk()
root.title("Przedział czasu")

v = IntVar()
v.set(1)

def mmm():
    return(v.get())

Label(root, text = "Wybierz przedział czasu dla którego \nprzedstawione zostaną dane",
      padx = 25, justify = LEFT).pack(anchor = W)
Radiobutton(root, text = "2W", variable = v, value = 1, command = mmm).pack(anchor = W)
Radiobutton(root, text = "1M", variable = v, value = 2, command = mmm).pack(anchor = W)
Radiobutton(root, text = "3M", variable = v, value = 3, command = mmm).pack(anchor = W)
Radiobutton(root, text = "6M", variable = v, value = 4, command = mmm).pack(anchor = W)
Radiobutton(root, text = "1Y", variable = v, value = 5, command = mmm).pack(anchor = W)
Radiobutton(root, text = "3Y", variable = v, value = 6, command = mmm).pack(anchor = W)

root.mainloop()

Period = mmm()

sEnd = dt.datetime.today()

if Period == 1:
    sStart = sEnd - dt.timedelta(weeks = 2)
    sPeriod = "2W"
elif Period == 2:
    sStart = monthdelta(sEnd, 1)
    sPeriod = "1M"
elif Period == 3:
    sStart = monthdelta(sEnd, 3)
    sPeriod = "3M"
elif Period == 4:
    sStart = monthdelta(sEnd, 6)
    sPeriod = "6M"
elif Period == 5:
    sStart = yeardelta(sEnd, 1)
    sPeriod = "1Y"
elif Period == 6:
    sStart = yeardelta(sEnd, 3)
    sPeriod = "3Y"

#Download data for chosen company and period of time

dfData = web.DataReader(sStock, 'yahoo', sStart , sEnd)

#Check if directory exist, create relevant folders and write a csv file

sDirectory = os.getcwd() + "\\Stock_Data"
if not os.path.exists(sDirectory):
    os.makedirs(sDirectory)
    
sStockDirectory = sDirectory + '\\' + sStock
if not os.path.exists(sStockDirectory):
    os.makedirs(sStockDirectory)  

dfData.to_csv(sStockDirectory + '\\Dane_' + sStock + '_' + sPeriod + '.csv', sep = ',')

#Read data to data frame

dfData = pd.read_csv(sStockDirectory + '\\Dane_' + sStock + '_' + sPeriod + '.csv', parse_dates = True, index_col = 0)

vStockDate = dfData.index
vStockClose = dfData.Close
vMA100 = vStockClose.rolling(window = 20, min_periods = 0).mean()

def FigPlot(vDate, vClose):
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    ax1.plot(vDate, vClose, '-', color = 'b', label = 'Cena zamknięcia', linewidth = 1.4)
    #ax1.plot(vDate, vOpen, '-', color = 'c', label = 'Cena otwarcia')
    ax1.plot(vDate, vMA100, '-', color = 'c', label = 'Średnia ruchoma', linewidth = 1.4)
    
    
    ax1.plot([], [], color = 'g', alpha = 0.5, label = 'Zysk', linewidth = 1.4)
    ax1.plot([], [], color = 'r', alpha = 0.5, label = 'Strata', linewidth = 1.4)
    
    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax1.grid(True, linestyle = '-')
    ax1.fill_between(vDate, vClose, vClose[0], 
                     where = (vClose > vClose[0]), 
                     facecolor = 'g', alpha=0.3)
    ax1.fill_between(vDate, vClose, vClose[0], 
                     where = (vClose < vClose[0]), 
                     facecolor = 'r', alpha=0.3)
    
    ax1.annotate(str(round(vClose[0],2)), (vDate[0], vClose[0]))
    ax1.annotate(str(round(vClose[-1],2)), (vDate[-1], vClose[-1]))
    
    plt.xlabel = "Data"
    plt.ylabel = "Cena zamknięcia"
    plt.legend()
    plt.title('Wykres cen akcji firmy ' + sStock + '\nPrzedział czasu równy ' + sPeriod)
    
    plt.show()
    
FigPlot(vStockDate, vStockClose)

modArima = pmd.auto_arima(vStockClose, start_p=0, start_q=0,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=5, max_q=5, # maximum p and q
                      m=1,              # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=False,   # No Seasonality
                      start_P=0, 
                      D=0, 
                      trace=True,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)

#Summary of the Arima model
modSummary = modArima.summary()
print(modSummary)

#Few graphs to check the correctness of model
modArima.plot_diagnostics(figsize=(8,8))
plt.show()


modForecast, modConfInt = modArima.predict(n_periods = iPeriodsNumber, return_conf_int=True, alpha=0.5)

vForecastIndex = np.arange(len(vStockClose), len(vStockClose) + iPeriodsNumber)

# make series for plotting purpose
seriesForecast = pd.Series(modForecast, index = vForecastIndex)
seriesLower = pd.Series(modConfInt[:, 0], index = vForecastIndex)
seriesUpper = pd.Series(modConfInt[:, 1], index = vForecastIndex)

vDatesForecast = pd.bdate_range(pd.datetime.today(), periods = iPeriodsNumber).tolist()
seriesForecast.index = vDatesForecast
seriesLower.index = vDatesForecast

# Plot

plt.plot(vStockClose, label = 'Cena zamknięcia', linewidth = 1.4)
plt.plot(seriesForecast, color='darkgreen', label = 'Prognozowana cena', linewidth = 1.4)
plt.fill_between(seriesLower.index, 
                 seriesLower, 
                 seriesUpper, 
                 color='k', alpha=.15,
                 label = 'Przedział ufnosci')

plt.xticks(rotation = 45)

plt.legend()
plt.title("Forecast for " + str(iPeriodsNumber) + " days of a stock price for " + sStock)
plt.savefig(sStockDirectory + '\\' + sStock + '_Forecast_' + sPeriod + '.png')
plt.show()


