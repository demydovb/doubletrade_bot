# Telegram bot for Doubletrade affiliate program.

## Background

*I have travel project and its web-site and Facebook/Telegram pages which connected with travel affiliate program (Doubletrade, which have offer to work with Skyscanner). When I post best travel deals ( direct links to book cheap flight),  I have to log in my personal cabinet and generate via those site special affiliate links. But as I need to generate different links for website/facebook/telegram and there may be not only one travel link + every platform required special markdown for links, it was quite boring to do it manually and I've decided to write Telegram bot, which will accept raw Skyscanner links and return me generated and stylized links for every platform.*

![First demo](https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif)

## What this bot can:
1. Work only with authorized user ( by default - project's admins accounts in Telegram).
2. Parse link and define departure and arrivals airports.
3. Store in DB mapping IATA code - city name ( it's needed for detecting departure and arrival cities from raw url - user should add airport in DB (if it doesn't exists already in DB, otherwise user will get message about existing) before generating links with that airport.
4. Work asynchronously.
5. Add different markdown for different platform.

**Demo:**
![Second demo](https://giphy.com/gifs/1fly80FHe75kB9Ae5M)

If you need to play around/test this bot - just write me and I'll give you bot's username and grant privileges to work with. 
