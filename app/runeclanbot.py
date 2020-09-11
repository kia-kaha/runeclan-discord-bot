import discord
from itertools import chain
from os import environ

from helper_methods import *

client = discord.Client()
arrow = u"\u2192"

class RuneClanBot:

    channel = None
    clan_name = environ["CLAN_NAME"]
    sent_message = ""

    def __init__(self, channel, clan_name, sent_message):
        self.channel = channel
        self.clan_name = clan_name
        self.sent_message = sent_message


@client.event
async def get_help():
    await RuneClanBot.channel.send("""RuneClan Discord bot commands:
"!help": Displays this message
"!info": Lists the clan's information
"!keys": List's the clan's key members
"!events": Lists the clan's recent activity
"!achievements": Lists the clan's recent achievements
"!today": List the top clan members with the most exp gained today
"!comp": List current competitions
"!comp top <competition>": List competition leaders (e.g. !comp top firemaking)

Bot originally made by slick rick, modified by The Matt
""")


@client.event
async def get_clan_info():

    soup = soup_session("http://www.runeclan.com/clan/" +
                        RuneClanBot.clan_name)

    list_to_print = RuneClanBot.clan_name.replace("_", " ") + " - Clan Info:\n"

    for clan_info in soup.find_all('span', attrs={'class': 'clan_subtext'}):
        list_to_print += clan_info.text + " " + clan_info.next_sibling + \
            "\n"  # next sibling prints out untagged text

    await RuneClanBot.channel.send(list_to_print)


@client.event
async def get_key_ranks():

    soup = soup_session("http://www.runeclan.com/clan/" +
                        RuneClanBot.clan_name)

    list_to_print = ""

    for names in soup.find_all(attrs={'class': 'clan_ownerbox'}):
        list_to_print += (names.text[2:] + " " +
                          arrow + " " + names('img')[0]['alt'] + "\n")

    await RuneClanBot.channel.send(list_to_print)


@client.event
async def get_clan_event_log():

    soup = soup_session("http://www.runeclan.com/clan/" +
                        RuneClanBot.clan_name)

    events = ""
    events_counter = 0
    event_list_end = False

    list_count_requested = get_requested_list_count(
        RuneClanBot.sent_message, 40, 10)

    if list_count_requested[1]:
        await RuneClanBot.channel.send(list_count_requested[1])
        return

    events_to_print = list_count_requested[0]

    for events_table in soup.find_all(attrs={'class': 'clan_event_box'})[0:events_to_print]:
        if " XP" in events_table.text or re.match("([0-9]{2,3} [A-Z][a-z]+)", events_table.text):
            event_list_end = True
            break

        events += events_table.text + "\n"
        events_counter += 1

    events = events.replace(".", " " + arrow + " ")
    events = events.replace("!", " " + arrow + " ")

    if event_list_end:
        events = "Only " + str(events_counter) + " events are currently recorded on " + \
            RuneClanBot.clan_name.replace(
                "_", " ") + "'s RuneClan page:\n\n" + events

    await RuneClanBot.channel.send(events)


@client.event
async def get_clan_achievements():

    soup = soup_session("http://www.runeclan.com/clan/" +
                        RuneClanBot.clan_name)

    achievements = ""
    clan_name_to_print = RuneClanBot.clan_name.replace("_", " ")
    index = 0
    total_achievements_displayed = 0
    list_count_requested = get_requested_list_count(
        RuneClanBot.sent_message, 40, 10)

    if list_count_requested[1]:
        await RuneClanBot.channel.send(list_count_requested[1])
        return

    achievements_to_print = list_count_requested[0]

    for clan_achievements_table in soup.find_all(attrs={'class': 'clan_event_box'}):
        if " XP" not in clan_achievements_table.text and not re.match("([0-9]{2,3} [A-Z][a-z]+)", clan_achievements_table.text):
            index += 1
        else:
            break

    for clan_achievements_table in soup.find_all(attrs={'class': 'clan_event_box'})[index:index + achievements_to_print]:
        achievements += clan_achievements_table.text + "\n"
        total_achievements_displayed += 1

    achievements = achievements.replace("XP", "XP " + arrow + " ")

    achievements = re.sub("([0-9]{2,3} [A-Z][a-z]+)",
                          r"\1" + " " + arrow + " ", achievements)

    if total_achievements_displayed != achievements_to_print:
        achievements = "Only " + str(total_achievements_displayed) + " clan achievements are currently recorded on " + \
            clan_name_to_print + "'s RuneClan page:\n\n" + achievements

    await RuneClanBot.channel.send(achievements)


@client.event
async def get_todays_hiscores():

    soup = soup_session("http://www.runeclan.com/clan/" +
                        RuneClanBot.clan_name + "/xp-tracker")

    todays_hiscores = ""
    list_count_requested = get_requested_list_count(
        RuneClanBot.sent_message, 40, 10)

    if list_count_requested[1]:
        await RuneClanBot.channel.send(list_count_requested[1])
        return

    rows_to_print = list_count_requested[0]

    table = soup.find_all('table')[3]

    for row_cell in table.find_all('tr')[1:]:
        row = row_cell.find_all('td')

        if "Clan Total" == row[1].text:
            todays_hiscores += RuneClanBot.clan_name.replace(
                "_", " ") + "'s Total Xp for Today: " + row[2].text + " xp\n\n"
            continue

        # Prevents row duplication.
        if f"Rank {row[0].text}:" in todays_hiscores:
            continue

        todays_hiscores += f"Rank {row[0].text}: {row[1].text} {arrow} {row[2].text} xp\n"

        if int(row[0].text) == rows_to_print:
            break

    await RuneClanBot.channel.send(todays_hiscores)


@client.event
async def get_competitions():

    soup = soup_session("http://www.runeclan.com/clan/" +
                        RuneClanBot.clan_name + "/competitions")

    competition_rows = get_active_competition_rows(RuneClanBot.clan_name)
    row_index = 0
    time_left = ""

    if competition_rows == 0:
        await RuneClanBot.channel.send(RuneClanBot.clan_name.replace("_", " ") + " has no active competitions at this time.")
    else:
        for table in soup.find_all('table')[4:]:
            row = table.find_all('td')

        while competition_rows > 0:
            time_left += "There are " + competition_rows + " competitions active:\n"
            if row[row_index + 2].find('span').text == "active":
                time_left += "The " + \
                    row[row_index + 1].text + " XP competition has " + \
                    row[row_index + 4].text[:-6] + " remaining!\n"
            competition_rows -= 1
            row_index += 5

        await RuneClanBot.channel.send(time_left)


@client.event
async def get_competition_leaders():

    soup = soup_session("http://www.runeclan.com/clan/" +
                        RuneClanBot.clan_name + "/competitions")

    table = soup.find_all('td', {'class': 'competition_td competition_name'})
    skills_of_the_month = get_skills_in_clan_competition(RuneClanBot.clan_name)
    row_count = get_active_competition_rows(RuneClanBot.clan_name)
    clan_name_to_print = RuneClanBot.clan_name.replace("_", " ")

    list_count_requested = get_requested_list_count(
        RuneClanBot.sent_message, 10, 5)

    if list_count_requested[1]:
        await RuneClanBot.channel.send(list_count_requested[1])
        return

    rows_to_print = list_count_requested[0]

    list_of_ranks = []
    list_of_skills = []

    player_rank_count = 0
    skill_header_count = 0
    skill_count = 0
    if get_active_competition_rows(RuneClanBot.clan_name) == 0:
        await RuneClanBot.channel.send(clan_name_to_print + " has no active competitions at this time.")
    else:
        for row in table:
            for link in row.find_all('a', href=True):

                soup = soup_session(
                    "http://www.runeclan.com/clan/Envision/" + link['href'])

                row_index = 0
                for table in soup.find_all('table')[3:]:
                    while skill_header_count < row_count:
                        list_of_skills.append(f"{clan_name_to_print}'s competition hiscores:\n {skills_of_the_month[1+skill_count].text}")
                        skill_header_count += 1
                        skill_count += 5
                    try:
                        rows = table.find_all('td')
                        list_of_ranks.append(f"Rank {rows[row_index].text}: {rows[row_index+1].text} {arrow} Xp Gained: {rows[row_index+2].text} xp")
                        if rows[row_index].text == rows_to_print:
                            player_rank_count += 1
                            break
                        else:
                            row_index += 3
                        player_rank_count += 1
                    except IndexError:
                        break

        list_to_print = ""
        skills = 0

        while skills < row_count:
            list_to_print += list_of_skills[skills]
            for row in list_of_ranks[skills * rows_to_print:(skills * rows_to_print) + rows_to_print]:
                list_to_print += str(row) + "\n\n"

            skills += 1

        try:
            await RuneClanBot.channel.send(list_to_print)
        except:
            await RuneClanBot.channel.send("Character limit exceeded. Please reduce the amount of ranks you wish to search for.")


@client.event
async def on_message(message):

    RuneClanBot.channel = message.channel
    RuneClanBot.sent_message = message.content.replace("'", "")

    try:
        command = list_of_commands[RuneClanBot.sent_message.lower().rsplit(" top", 1)[
            0].strip()]
        await command()
    except KeyError:
        pass

    return

if __name__ == '__main__':

    list_of_commands = {
        "!help": get_help,
        "!info": get_clan_info,
        "!keys": get_key_ranks,
        "!events": get_clan_event_log,
        "!achievements": get_clan_achievements,
        "!today": get_todays_hiscores,
        "!comp": get_competitions,
        "!comp top": get_competition_top,
    }

    client.run(environ["RUNECLANBOT_TOKEN"])
