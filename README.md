# K.I.M. - Discord Censor Bot

  K.I.M. is a Discord anti-profanity bot that will do its best to clean up text messages from bad-mannered users!
  
   ![screen2](Screenshot2.png)
  
  The bot reads through each message sent and checks if the message contains words, tagged as profanity in its database. The database is specific for each server and admins/mods can add and remove "profanity" words at their will. (The bot assumes that an admin/mod is a user with the "Manage Messages" permission).
  
   ![screen1](Screenshot1.png)
  
  The bot has a bunch of commands that can be used for each server, such as:
  - adding or removing "replacement phrases" (a replacement phrase is a phrase that the bot will randomly choose and replace a profanity word with)
  - adding or removing descriptions (a description is a piece of text that the bot will spew out whenever a user uses a profanity word, it can be used in a way to poke fun at users who like to swear!)
  - setting a server profanity threshold and punishing users who go over said threshold
  
  [Add KIM to your server](https://discord.com/oauth2/authorize?client_id=854075604035305542&permissions=10246&scope=bot)

-------------------------------------------------------------------------------------------------------------------------------------------------------------
## Code Explained:

  K.I.M. uses Discord's API, combined with SQLite for Python.
 
### KimBot.py
  
  So the main file that we'll be looking at is **KimBot.py**. It basically features a bunch of functions that get executed on certain events. The most important function is **on_message()**, which reads data about every single text message that gets sent and stores it temporarily in variables in **config.py**. It then proceeds to generate a "character map", which basically is a python list that takes every single character from a string and determines if the string contains a "censor" word through an algorithm. If there's at least one *"True"* character in the map, then the bot has detected a bad word! 
  
  When a bad word has been detected, the bot will automatically delete the message and replace it with its own, that will contain a description and a reformatted message that will either not feature the censor word(s) or will tag the censor word(s) as a spoiler. Also, if the server keeps track of how many censor words have been used by the users, it will automatically update the database and will give out warnings and punishments if needed.
  
  The rest of the functions in **KimBot.py** either output data to the user or input data through SQL queries. (or they just help with that)
  
-------------------------------------------------------------------------------------------------------------------------------------------------------------
### KimExtras.py
  
  This is the most complicated part of the code and the one that I hated debugging the most. This features the **sensitive()** function that tries to detect "l33t" speech, unicode, cyrillic letters, punctuations, spacing and character repititon, so that the bot will read "hello" and "heee33lllo_o000" as the same word. 
  
  **createBotMessage()** is the function that generates the bot's message that is sent whenever a user uses a swear word.  
  
  **createCharacterMap()** is the most cryptic function in my opinion. As mentioned earlier, it will return a list that shows what type of character each character is. (it can either be a good, bad or "skip" character). This helps with **createBotMessage()**, as the bot will know which characters from the message should actually be censored. 
  
-------------------------------------------------------------------------------------------------------------------------------------------------------------
### config.py
  This stores global variables and is used for communication between the previous two files. It features the **addNewServer()** function that automatically updates the database whenever the bot joins a new server.
  
-------------------------------------------------------------------------------------------------------------------------------------------------------------
### KimDB.db
  This is the database file. It features 5 tables - servers, users, words, phrases, descriptions.
  - servers - stores server settings
  - users - keeps track of how many times a user has sworn for each server
  - words - stores profanity words for each server
  - phrases - stores replacement phrases for each server
  - descriptions - stores descriptions for each server
  
-------------------------------------------------------------------------------------------------------------------------------------------------------------
### KimHelpMessages
  This is a folder of text files that store the information that is displayed whenever a **/kim help** command is executed.
  

