# Based on Python
FROM python:3.6

LABEL Name=runeclan_discord_bot Version=0.0.1

# Our bot is in app, so copy that whole folder over to /app on the container filesystem
WORKDIR /app
COPY app .

# Using pip:
RUN python3 -m pip install -r requirements.txt
# Start bot
CMD ["python3", "-u", "./runeclanbot.py"]