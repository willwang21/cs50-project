I designed this project using the Flask framework and used Python to do the "behind the scenes" work. 

On the backend, I used a Python module called "icalevents" to parse ics files. It allows for easy import and reading of calendars, and it represents events using Python's native datetime objects. To work with these lists of events, I decided to think of days as being split into 15-minute chunks, and events as taking up a certain number of those chunks. Thus, the AvailableTimes class "translates" calendars by taking an evenly-spaced set of datetimes, representing the total amount of time available, and dropping the datetimes covered by an event.

This implementation meant that I needed to focus on a finite amount of "free time" in each calendar: otherwise, I'd have an infinite set. I chose to have the original datetime set cover 4 weeks, which makes practical sense, too: If two people don't have any common time in a month, it might be good to wait and schedule again, or clear up some time manually.

Then, finding free time is a simple matter of taking set intersections. The preferences about meeting times and lengths are implemented by further dropping datetimes (for the morning, lunch, etc.) and by counting contiguous blocks of time.

On the frontend, I used Flask to implement the website, storing user information in SQL. The project is still incomplete, but if I were to continue, I would simply allow users to submit their preferences, then report the results of the time search to them.
