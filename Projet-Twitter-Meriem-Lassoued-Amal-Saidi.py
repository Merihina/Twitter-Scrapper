from tkinter import *
from PIL import ImageTk,Image
import tweepy
from tweepy import OAuthHandler
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from textblob import TextBlob

#============================================================================================================
#Vider la Page (Interface Graphique)
def delete_frame(x):
    for widget in fenetre.winfo_children():
        if x == 1 :
            widget.pack_forget()
        else :
            widget.destroy()

#============================================================================================================
#Nettoyer la zone texte pour l'analyse sentimentale (Twitter)
def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\ / \ / \S+)", " ", tweet).split())

#============================================================================================================
#Analyse sentimentale (Twitter)
def get_tweet_sentiment(tweet):

        analysis = TextBlob(clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

#============================================================================================================
#Moteur de recherche Twitter
def request_tweets(status):

    consumer_key = "WcusTBCUDdtZ5abenLVel02Aw"
    consumer_secret = "fTbZ5hoym4lfSfW4ydGgltSpke1yEP0QccmBxafaNnMQNcCcEg"
    access_token = "927353832618807297-JDDfW1sahuaHB63jVZBjQbXzeQcQZCw"
    access_token_secret = "BdUBSDrBfltMvyMzJhMWwewWhDz2HGMQND2tCqT2jj4yh"
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    global Key
    global N

    maxTweets = N  # Nombre de tweet max a recuperer
    tw_block_size = N  # Nombre de Tweet par requete
    tweetCount = 0

    if Key[0] == '#' :
        search_query = Key
    else :
        search_query = "#"+Key

    Key = search_query

    if status == "0":
        Until = None
    else:
        Until = status

    while tweetCount < maxTweets:
        try:
            newtweets = api.search(q=search_query, count=tw_block_size, since_id= None, until=Until)
            if not newtweets:
                break
            tweetCount += len(newtweets)
        except tweepy.TweepError as e:
            print("Une erreur est survenue.")
            break
    return newtweets

#============================================================================================================
#Convertir modele de recherche Tweepy vers Pandas Dataframe :
def toDataFrame(tweets):

    DataSet = pd.DataFrame()
    DataSet['Name'] = [tweet.user.screen_name for tweet in tweets]
    DataSet['tweetText'] = [tweet.text for tweet in tweets]
    DataSet["Sensitive"] = [get_tweet_sentiment(tweet.text) for tweet in tweets]
    DataSet['Retweeted'] = [tweet.retweet_count for tweet in tweets]
    DataSet['tweetFavoriteCt'] = [tweet.favorite_count for tweet in tweets]
    DataSet['Publication'] = [str(clean_tweet(tweet.source)) for tweet in tweets]
    DataSet['tweetCreated'] = [tweet.created_at for tweet in tweets]
    DataSet['userID'] = [tweet.user.id for tweet in tweets]
    DataSet['userScreen'] = [tweet.user.screen_name for tweet in tweets]
    DataSet['userName'] = [tweet.user.name for tweet in tweets]
    DataSet['userCreateDt'] = [tweet.user.created_at for tweet in tweets]
    DataSet['userDesc'] = [tweet.user.description for tweet in tweets]
    DataSet['userFollowerCt'] = [tweet.user.followers_count for tweet in tweets]
    DataSet['userFriendsCt'] = [tweet.user.friends_count for tweet in tweets]
    DataSet['userLocation'] = [tweet.user.location for tweet in tweets]
    DataSet['userTimezone'] = [tweet.user.time_zone for tweet in tweets]
    DataSet['Langue'] = [tweet.lang for tweet in tweets]

    return DataSet

#============================================================================================================
#Moteur Principale de notre application (Interface Graphique)
def search(status):

    #Fonction de recherche de tweet
    new_tweets = request_tweets(status)

    #Convertir le format Tweepy en Dataframe
    Tweets = toDataFrame(new_tweets)

    #Affiche les parametre de recherche
    Keyword = "Votre mot clef : "+ Key
    number = "Recherche sur "+str(N)+" Tweets"
    if status == "0" :
        since = "Affichage des plus récents"
    else :
        since = "Affichage depuis le "+Until

    champ_label = Label(fenetre, text=Keyword , font=("Arial Bold", 25), foreground="red")
    champ_label.grid(row=0, column=0)

    champ_label = Label(fenetre, text=number, font=("Arial", 15), foreground="black")
    champ_label.grid(row=1, column=0)

    champ_label = Label(fenetre, text=since, font=("Arial", 15), foreground="black")
    champ_label.grid(row=2, column=0)

    #Affichage Taux d'apparation
    champ_label = Label(fenetre, text="Taux Apparition", font=("Arial Bold", 25), foreground="black")
    champ_label.grid(row=0, column=1)

    Average_tweet = Tweets['tweetCreated']
    Average_tweet = Average_tweet.value_counts().mean()
    Average_tweet = str(Average_tweet) + " Post/Seconde"
    champ_label = Label(fenetre, text=Average_tweet, font=("Arial", 15), foreground="black")
    champ_label.grid(row=2, column=1)

    #Affichage Sentiment
    champ_label = Label(fenetre, text="Sentiment", font=("Arial Bold", 25), foreground="black")
    champ_label.grid(row=0, column=2)

    All = Tweets['Sensitive']
    All = All.value_counts()

    for i in range(0,len(All)):
        if All.index[i] == "neutral" :
            neutral = str(round((int(All["neutral"]) * 100) / N)) + "% Neutre"
            champ_label = Label(fenetre, text=neutral, font=("Arial", 15), foreground="grey")
            champ_label.grid(row=1, column=2)
        if All.index[i] == "positive" :
            positive = str(round((int(All["positive"]) * 100) / N)) + "% Positif"
            champ_label = Label(fenetre, text=positive, font=("Arial", 15), foreground="green")
            champ_label.grid(row=2, column=2)
        if All.index[i] == "negative":
            negative = str(round((int(All["negative"]) * 100) / N)) + "% Négatif"
            champ_label = Label(fenetre, text=negative, font=("Arial", 15), foreground="red")
            champ_label.grid(row=3, column=2)

    #Affichage Courbe Language
    figure = Figure(figsize=(5, 5), dpi=100)
    ax = figure.subplots()
    ax.title.set_text('Language des publications')
    chart = sns.swarmplot(x="Langue", data=Tweets, ax=ax)
    canvas = FigureCanvasTkAgg(figure, fenetre)
    canvas.draw()
    canvas.get_tk_widget().grid(row=5, column=0)

    #Affichage Courbe Retwwet
    figure2 = Figure(figsize=(5, 5), dpi=100)
    ax2 = figure2.subplots()
    sns.violinplot(x = "Retweeted", data=Tweets, ax=ax2)
    ax2.title.set_text('Quantité de Retweet des post')
    canvas = FigureCanvasTkAgg(figure2, fenetre)
    canvas.draw()
    canvas.get_tk_widget().grid(row=5, column=1)

    #Affichage Courbe Source
    figure3 = Figure(figsize=(5, 5), dpi=100)
    ax3 = figure3.subplots()
    sns.stripplot(y="Publication", data=Tweets, ax=ax3)
    ax3.title.set_text('Source des publications')
    canvas = FigureCanvasTkAgg(figure3, fenetre)
    canvas.draw()
    canvas.get_tk_widget().grid(row=5, column=2)

    #Bouton pour lancer une nouvelle recherche
    btn = Button(fenetre, text="Nouvelle Recherche", command=renew)
    btn.grid(row=6, column=1)




#============================================================================================================
#Convertisseur de Date (Interface Graphique)
def dateconvert():
    year = str(annee.get())
    month = str(mois.get())
    day = str(jour.get())
    global Until
    Until = year+"-"+month+"-"+day
    delete_frame(1)
    search(Until)


#============================================================================================================
#Recherche a partir d'une Date (interface graphique)
def date_specs():
    champ_label0 = Label(fenetre, text="Veuillez saisir la date", font=("Arial Bold", 25))
    champ_label0.pack()
    champ_label1 = Label(fenetre, text="")
    champ_label1.pack()
    champ_label2 = Label(fenetre, text="Anneé (YYYY)")
    champ_label2.pack()
    var_an = StringVar()
    global annee
    annee = Entry(fenetre, textvariable=var_an, width=30)
    annee.pack()
    champ_label2 = Label(fenetre, text="Mois (MM)")
    champ_label2.pack()
    var_mois = StringVar()
    global mois
    mois = Entry(fenetre, textvariable=var_mois, width=30)
    mois.pack()
    champ_label2 = Label(fenetre, text="Jour (DD)")
    champ_label2.pack()
    var_jour = StringVar()
    global jour
    jour = Entry(fenetre, textvariable=var_jour, width=30)
    jour.pack()
    btn = Button(fenetre, text="Définir", command=dateconvert)
    btn.pack()
    champ_label1 = Label(fenetre, text="")
    champ_label1.pack()
    champ_label2 = Label(fenetre, text="Pour des raisons de performance, nous vous conseillons de ne pas dépasser les 4 jours en arriéres. ")
    champ_label2.pack()

#============================================================================================================
#Initialisateur du tableau de bord (interface graphique)

def clicked():
    global Key
    Key = str(keynote.get())
    global N
    N = int(capacite.get())
    global Choix
    Choix = int(choice.get())
    global  Until
    Until = "0"
    delete_frame(1)
    if Choix == 1 :
        search(Until)
    else :
        date_specs()

#============================================================================================================
#Nouvelle recherche (Interface Graphique)
#============================================================================================================
#Lancer une nouvelle recherche
def renew():
    delete_frame(0)
    canvas = Canvas(fenetre, width = 250, height = 250)
    canvas.pack()
    img = ImageTk.PhotoImage(Image.open("twitter.png"))
    canvas.create_image(20, 20, anchor=NW, image=img)
    champ_label0 = Label(fenetre, text="Nouvelle recherche", font=("Arial Bold", 25))
    champ_label0.pack()
    champ_label1 = Label(fenetre, text="")
    champ_label1.pack()
    champ_label2 = Label(fenetre, text="Veuillez saisir votre mot-clef")
    champ_label2.pack()
    var_key = StringVar()
    global keynote
    keynote = Entry(fenetre, textvariable=var_key, width=30)
    keynote.pack()
    champ_label3 = Label(fenetre, text="Veillez entrer le nombre de tweets voulu")
    champ_label3.pack()
    var_capacite = StringVar()
    global capacite
    capacite = Entry(fenetre, textvariable=var_capacite, width=30)
    capacite.pack()
    champ_label4 = Label(fenetre, text="Veillez choisir les parametres recherches :")
    champ_label4.pack()
    global choice
    choice = StringVar(fenetre, "0")
    Radiobutton(fenetre,text="Les plus récents",padx = 20,value=1,variable = choice).pack()
    Radiobutton(fenetre,text="Spécifier une date",padx = 20,value=0,variable = choice).pack()
    champ_label1 = Label(fenetre, text="")
    champ_label1.pack()
    btn = Button(fenetre, text="Execution", command=clicked)
    btn.pack()
    champ_label = Label(fenetre, text="©2020 - Meriem Lassoued & Amal Saidi")
    champ_label.pack( side = BOTTOM )

#============================================================================================================
#Interface Graphique
fenetre = Tk()
fenetre.title("Twitter Big-Data")
fenetre.geometry('1500x750')
canvas = Canvas(fenetre, width = 250, height = 250)
canvas.pack()
img = ImageTk.PhotoImage(Image.open("twitter.png"))
canvas.create_image(20, 20, anchor=NW, image=img)
champ_label0 = Label(fenetre, text="Bienvenue sur l'interface de recherche Twitter", font=("Arial Bold", 25))
champ_label0.pack()
champ_label1 = Label(fenetre, text="")
champ_label1.pack()
champ_label2 = Label(fenetre, text="Veuillez saisir votre mot-clef")
champ_label2.pack()
var_key = StringVar()
keynote = Entry(fenetre, textvariable=var_key, width=30)
keynote.pack()
champ_label3 = Label(fenetre, text="Veillez entrer le nombre de tweets voulu")
champ_label3.pack()
var_capacite = StringVar()
capacite = Entry(fenetre, textvariable=var_capacite, width=30)
capacite.pack()
champ_label4 = Label(fenetre, text="Veillez choisir les parametres recherches :")
champ_label4.pack()
choice = StringVar(fenetre, "0")
Radiobutton(fenetre,text="Les plus récents",padx = 20,value=1,variable = choice).pack()
Radiobutton(fenetre,text="Spécifier une date",padx = 20,value=0,variable = choice).pack()
champ_label1 = Label(fenetre, text="")
champ_label1.pack()
btn = Button(fenetre, text="Execution", command=clicked)
btn.pack()
champ_label = Label(fenetre, text="©2020 - Meriem Lassoued & Amal Saidi")
champ_label.pack( side = BOTTOM )
fenetre.mainloop()
