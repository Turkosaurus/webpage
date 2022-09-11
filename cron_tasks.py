""" Completes cron tasks from Heroku Scheduler. """
import requests

content = "foo"
r = requests.get('https://turkosaur.us/ping/%s' % content)
print(r)