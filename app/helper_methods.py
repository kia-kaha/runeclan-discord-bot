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


def get_requested_list_count(message, max_list, default):

    try:
        if " top" in message.lower():
            if not re.split(" top", message, flags=re.IGNORECASE)[1].strip().isdigit() or not 1 <= int(re.split(" top", message, flags=re.IGNORECASE)[1].strip()) <= max_list:
                return 0, f"This feature is only valid for integer values between 1 and {max_list}."
            else:
                return int(re.split(" top", message, flags=re.IGNORECASE)[1].strip()), ""
    except:
        return 0, f"This feature is only valid for integer values between 1 and {max_list}."

    return default, ""
