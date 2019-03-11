# Telegram bot for Doubletrade affiliate program.

## Background

*I have travel web site and Facebook/Telegram pages where I provide details to the most incredible flight deals. I cooperate with couple of affiliate programs, among them - Doubletrade, which have offer to work with Skyscanner. 

When I share best travel deals ( direct links to booking cheap flight),  I have to log in my personal cabinet in Doubletrade and generate via their special tool affiliate links. But as I need to generate different links for web site/Facebook/Telegram and there may be not only one travel link + every platform required special markdown for links, it was quite boring and took a time to do it manually and I've decided to write Telegram bot, which accepts raw Skyscanner links and return me generated and stylized links for every platform.*

![First demo](https://media.giphy.com/media/1lBIEni8wON0Lk8B9g/giphy.gif)

## What this bot can:
1. Work only with authorized user ( by default - project's admins accounts in Telegram).
2. Parse link and define departure and arrivals airports.
3. Store in DB mapping IATA code - city name ( it's needed for detecting departure and arrival cities from raw url - user should add airport in DB (if it doesn't exists already in DB, otherwise user will get message about existing) before generating links with that airport.
4. Work asynchronously.
5. Add different markdown for different platform.

**Demo:**

![Second demo](https://media.giphy.com/media/1fly80FHe75kB9Ae5M/giphy.gif)

## Technologies:

1. Python 3.5.2
2. PostgreSQL + SQLAlchemy.
3. Asyncio.
4. Telegram-python-bot library.

If you need to play around/test this bot - just write me and I'll give you bot's username and grant privileges to work with. 
