# K.I.M. - Discord Censor Bot
#### Video Demo:  <URL HERE>
#### Description:
  K.I.M. is a Discord anti-profanity bot that will do its best to clean up text messages from users.
  
   ![screen2](Screenshot2.png)
  
  The way that it works is that it reads messages and compares certain parts of the message to words, tagged as profanity in its database. The database is different for each server and moderators or admins can add and remove words at their will. (The bot assumes that users with the "Manage Messages" permissions are mods or admins). K.I.M. uses SQL to read and write to its database.
  
   ![screen1](Screenshot1.png)
  
  The bot has a bunch of commands that can be manipulated for each server, such as:
  - adding or removing "replacement phrases" (a replacement phrase is a phrase that the bot will randomly choose and replace a censored word with)
  - adding or removing descriptions (a description is a piece of text that the bot will spew out whenever a user uses a filtered word, it can be used in a way to poke fun at the users who swear)
  - setting a server swear threshold and punishing users who go over said threshold!
  
  Add KIM to your server: https://discord.com/oauth2/authorize?client_id=854075604035305542&permissions=10246&scope=bot
