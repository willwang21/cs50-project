Flakeless runs on Flask and can be used in the CS50 codespaces app. The application allows users to register an account and log in. Their account must use a unique username. After logging in, a user can upload an iCalendar file exported from Google Calendar on the Upload page. 

(iCalendar files are standardized ways of representing event data. To export an ics file from Google Calendar, log into the desktop app. Hover over the calendar name in the lower left corner, then click the three dots > Settings and Sharing. An "Export Calendar" button is midway down the page. Clicking it will download a zipped iCalendar file, which can then be unzipped. In addition to this manual effort, test ics files are provided in the project/calendars folder.

Note that even though the ics format is standardized, Apple iCalendar files are exported with an "error" according to the documentation. So, they aren't supported here.)

When two users agree to schedule an event, they must enter each other's usernames on the Schedule page. When the second user does so, they will be redirected to a Scheduling page to input their preferences for the meeting: the approximate time (morning, lunch, afternoon, dinner, evening) and the length (in 15-minute increments).

Then, the user is sent to a page showing the meeting times fitting both users' schedules and the selected preferences. If no such meeting times exist within the next 4 weeks, the app reports that fact.

Still incomplete.
