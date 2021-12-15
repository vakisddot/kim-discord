# K.I.M. - Discord Censor Bot
#### Video Demo:  <https://youtu.be/qYyUt6RFYEE>
#### Description:
  K.I.M. is a Discord anti-profanity bot that will do its best to clean up text messages from users.
  
   ![screen2](Screenshot2.png)
  
  The way that it works is that it reads messages and compares certain parts of the message to words, tagged as profanity in its database. The database is different for each server and moderators or admins can add and remove words at their will. (The bot assumes that users with the "Manage Messages" permissions are mods or admins). K.I.M. uses SQL to read and write to its database.
  
   ![screen1](Screenshot1.png)
  
  The bot has a bunch of commands that can be manipulated for each server, such as:
  - adding or removing "replacement phrases" (a replacement phrase is a phrase that the bot will randomly choose and replace a censored word with)
  - adding or removing descriptions (a description is a piece of text that the bot will spew out whenever a user uses a filtered word, it can be used in a way to poke fun at the users who swear)
  - setting a server swear threshold and punishing users who go over said threshold!
  
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
### KimDB.db (not present in repo)
  This is the database file. The schema is available to see in **KimDB-schema**.
  
-------------------------------------------------------------------------------------------------------------------------------------------------------------
### KimHelpMessages
  This is a folder of text files that store the information that is displayed whenever a **/kim help** command is executed.
  

