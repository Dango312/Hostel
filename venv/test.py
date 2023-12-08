from tkinter import *
import tkcalendar
from datetime import timedelta,date,datetime

root = Tk()


def date_range(start, stop):
    global dates  # If you want to use this outside of functions

    dates = []
    diff = (stop - start).days
    for i in range(diff + 1):
        day = start + timedelta(days=i)
        dates.append(day)
    if dates:
        print(dates)  # Print it, or even make it global to access it outside this
    else:
        print('Make sure the end date is later than start date')


date1 = tkcalendar.DateEntry(root, mindate=datetime.now(), maxdate=(datetime.now() + timedelta(days=365)))
date1.pack(padx=10, pady=10)

date2 = tkcalendar.DateEntry(root)
date2.pack(padx=10, pady=10)

Button(root, text='Find range', command=lambda: date_range(date1.get_date(), date2.get_date())).pack()

root.mainloop()