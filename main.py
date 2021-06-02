from ics import Calendar, Event
import arrow
import re

# regex to parse command input
R = re.compile(r"(.+)\s(\d\d|\d)[\.\/](\d\d|\d)[\.\/](\d\d\d\d)\s(\d\d|\d):(\d\d)\s(\d\d|\d):(\d\d)\s[Gg][Mm][Tt]([\+-]\d\d?)?(\s.+)?")

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = ""

START_MSG = "Hi\! To generate calendar invite files for your events, make sure you follow the proper format as in the following examples:\n\n/invite Our Amazing Event 03\.05\.2021 09:20 15:00 gmt\+3\n/invite Our Amazing Event 3/5/2021 9:20 15:20 GMT our favorite cafe\n/invite Our Online Protest 3\.5\.2021 12:20 13:30 GMT\-5 zoom\-location\n\nYour location can be anything \(ex\. a zoom link\) and is optional, but you should follow the right order: *title date start time end time timezone location*\.\nFeel free to add me to groups for maximum utility\."
ABOUT_MSG = "I was created by @boghison. The code is available at https://github.com/boghison/icsbot"
FORMAT_MSG = "It seems like you provided info in the wrong format. Please check your message and retry."
ERR_MSG = "Sorry, something went wrong."
HERE_MSG = "See you there! ✌️"

def normalize(t):
    if len(t) == 1:
        return "0" + t
    return t

def norm_tz(tz):
    if tz is None:
        return "+0000"
    elif len(tz) == 3:
        return tz + '00'
    else:
        return tz[0] + '0' +  tz[1] + '00'


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_markdown_v2(START_MSG)


def about(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(ABOUT_MSG)

def generate(update: Update, _: CallbackContext) -> None:
    msg = update.message.text
    m = R.match(msg)

    if m == None:
        update.message.reply_text(FORMAT_MSG)
    else:
        try: 
            title, date, month, year, start_hour, start_minute, end_hour, end_minute, timezone, location = m.groups()
            start = arrow.get('{y}-{m}-{d}T{h}:{min}:00.000{tz}'.format(y=year, m=normalize(month), d=normalize(date), h=normalize(start_hour), min=start_minute, tz=norm_tz(timezone)))
            end = arrow.get('{y}-{m}-{d}T{h}:{min}:00.000{tz}'.format(y=year, m=normalize(month), d=normalize(date), h=normalize(end_hour), min=end_minute, tz=norm_tz(timezone)))

            c = Calendar()
            e = Event(name=title[5:].strip(), begin=start, end=end)
            if location:
                e.location = location.strip()
            c.events.add(e)
            update.message.reply_document(bytes(str(c), 'utf-8'), filename="invite.ics", caption=HERE_MSG)
            del c
        except:
            update.message.reply_text(ERR_MSG)




def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("about", about))
    dispatcher.add_handler(CommandHandler("invite", generate))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()