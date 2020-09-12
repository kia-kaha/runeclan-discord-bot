import re
import requests
from bs4 import BeautifulSoup


def soup_session(url):
    """BeautifulSoup session."""
    session = requests.Session()
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def get_active_competition_rows(clan_name):

    soup = soup_session("http://www.runeclan.com/clan/" +
                        clan_name + "/competitions")

    row_count = 0
    table_cell = 0
    for table in soup.find_all('table')[4:]:
        for row_tag in soup.find_all('tr'):
            row = table.find_all('td')
            try:
                if row[table_cell + 2].find('span').text == "active":
                    row_count += 1
                table_cell += 5
            except (AttributeError, IndexError):
                break

    return row_count


def get_skills_in_clan_competition(clan_name):

    soup = soup_session("http://www.runeclan.com/clan/" +
                        clan_name + "/competitions")

    for table in soup.find_all('table')[4:]:
        for row in soup.find_all('tr'):
            return table.find_all('td')

    return []


def get_requested_comp_id(message)
    split_message = re.split(" ", message, flags=re.IGNORECASE)
    if len(split_message) < 3
        return -1, "No competition id specified."

    try:
        return int(split_message[2]), ""
    except ValueError:
        return -1, "Invalid competition id specified"

