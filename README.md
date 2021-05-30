# iGO

Be the fastest with iGO!
<br /> 
## What is iGO?
iGO is a telegram bot that allows you to reach a desired destination in the city of Barcelona in the fastest way possible by car. It does so by calculating a time parameter that considers lenght, maximum speed avaliable during the trip and real time traffic congestion for each street in the city. Yes, we know, quite cool 😎

---

## How to use iGO:

First of all make sure you fit the specified requirements mentioned in the requirements.txt file. For additional help with installation there are some references at the end of the README, you might want to check them out.

Once the requirements are fullfilled you can download the archives containing the code:
* *i_go.py* file for the code of the iGO module.
* *bot.py* file for the code of the iGO telegram bot.

`NOTE:` other files contained in the folder are images for the README document or your own files that the program generates to work.

<br /> 
To use the bot, first of all open your telegram account and add the bot to your chats, you can do so by clicking the following link:

[Start chatting with our bot!](https://t.me/igo_Pol_Jan_bot)

Let's activate the bot, you can execute *bot.py* in the terminal using python3:
```bash
python3 bot.py
```
<br /> 

`NOTE:` if a message pops up saying that the bot is already on it's because the bot is running through another computer, do not worry you can use it anyways! Sadly we currently don't have the means to keep the bot running 24/7 but it doesn't need a huge amount of resources so you can do it with no worries.

`NOTE:`if you are the first user executing the code you might need to wait a few seconds or even a minute if your computer is slower to let the bot get and arrange the data.

`NOTE:` every 5 minutes traffic congestion data is updated, if you request a route but global data is old you might need to wait around a minute again 😄.

Now you can start chatting with the bot, type */start* in the chat and the bot will present itself and offer you some help on usage in case you need it. To enable route generation you might want to share your location with the bot so it knows where you are, you can do so with the share location feature that the telegram app has. <br /> 


`CURRENT BASE BOT FEATURES:`
* /start -> initiates the conversation
* /help -> gets help
* /author -> gets the names of the authors of the bot
* /go <destination> -> shows a map image with the fastest route from your location to the indicated destination
* /where -> shows a picture of your current location (the one you shared, this version does not have a 'real time GPS implemented')

<br /> 
Wonderful! 🌠 let's see a real example. 
`USAGE EXAMPLE:`

<img src="https://github.com/puigde/ap2-igo/blob/be052f0b70ede1b0d7a02e727158c3380a5525f0/tutorial1.png" width=40% height=40%>
<img src="https://github.com/puigde/ap2-igo/blob/be052f0b70ede1b0d7a02e727158c3380a5525f0/tutorial2.png" width=40% height=40%>


Easy, isn't it? you are ready to go! 🚙 
<br /> 
  
---
 *LATEST UPDATE❗ NEW TRAFFIC FEATURE!*
* /traffic -> shows a map image with the current traffic situation using color references indicated by a posterior message.
  
---  
<br /> 
  
## Help with installation, some references:

* Previous to Osmnx:
  In Ubuntu, previosly type `sudo apt install libspatialindex-dev`. In Mac, type `brew install spatialindex gdal` and get the
  latest versions of the installators.

1. `pip3 install --upgrade pip setuptools wheel`
2. `pip3 install --upgrade osmnx`
3. `pip3 install --upgrade staticmap`

* [Osmnx installation](https://github.com/gboeing/osmnx)
* [NetworkX installation](https://networkx.org/documentation/stable/install.html)
* [Pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)


---
## Development overview:
The program has been developed using the python language. We have used some libraries in order to accomplish the needed tasks.
<br /> 
First of all we developed the igo.py module which is used by the bot and accomplishes 3 main tasks:
1. Getting the data 
2. Formating and grouping the data 
3. Using the data, module functionalities

Then, we developed the actual bot which let's the user access module functionalities in a very interactive and comfortable way through the telegram chat.

To get a deeper insight of our thought process and how the code works check the documentation of both i_go.py and bot.py 😄
 
Working on iGo was very interesting as it was our first time managing a team project of this magnitude, we tried our best to make a sensible implementation.  

---
  
*developed by Pol Puigdemont and Jan Sallent, Data Science and Engineering students at UPC, 2021*
