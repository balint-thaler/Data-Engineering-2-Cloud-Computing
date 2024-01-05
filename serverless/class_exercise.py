#%%
import boto3
import pprint
import os

translate = boto3.client("translate")
text_hun = "Ahogy minden évben, úgy idén is kiválasztotta Európa legmeghatározóbb embereit a Politico." 
"A lap három kategóriába sorolja a jelölteket: cselekvők, álmodozók és felforgatók – utóbbi kategóriába került idén is Orbán Viktor." 
"Egy helyet viszont rontott, már nem a második, csak a harmadik legnagyobb zavarkeltőnek számít Európában." 
"A Politico indoklása szerint Orbán Viktor 2011 óta „leépítette jogállamiságot és a médiaszabadságot, összeütközésbe került az uniós intézményekkel, túszként tartotta fogva Brüsszelt azzal, hogy a pénzszerzés érdekében vétózott, és baráti viszonyt alakított ki Vlagyimir Putyin orosz elnökkel”." 
"„Magyarország erős embere jó úton halad, hogy továbbra is az EU ünneprontójaként lépjen fel.” A Politico arra is figyelmeztet, hogy a 2024-es EU-elnökség alatt Orbán „túlzásba eshet”, és „a hat hónapos mandátumot arra használhatja fel, hogy az európai értékekkel ellentétes politikát támogasson”.Érdekesség, hogy tavaly csak Giorgia Meloni olasz miniszterelnök előzte meg a listán a magyar kormányfőt, aki idén pályát váltott, a „cselekvők” kategóriában került az első helyre." 
"Orbán Viktornál Elvira Nabiullina, az Orosz Központi Bank elnöke és Carles Puigdemont, az Európai Parlament spanyol képviselője bizonyult nagyobb felforgatónak idén. A legnagyobb álmodozó Volodimir Zelenszkij ukrán elnök, az év legbefolyásosabb embere pedig Donald Tusk, az Európai Tanács korábbi elnöke, Lengyelország volt miniszterelnöke lett, aki az októberi választás után a lengyel koalíciós kormány vezető ereje lehet." 
"Ebben a cikkben írtunk bővebben arról, hogy a magyar kormány számára ez nem jó hír, fontos szövetségesét veszítheti el ugyanis Orbán uniós ügyekben. A teljes ranglistát itt lehet böngészni."
# %%
text_en = translate.translate_text(
    Text=text_hun, SourceLanguageCode="hu", TargetLanguageCode="en")
print(text_en["TranslatedText"])
# %%
print(text_en["TranslatedText"])
# %%
comprehend = boto3.client(service_name="comprehend", region_name="eu-west-1")
sentiment1 = comprehend.detect_sentiment(Text=text_en["TranslatedText"], LanguageCode="en")
print(sentiment1)
# %%
google_translate =  "As every year, Politico has selected Europe's most influential people this year as well. The paper classifies the candidates into three categories: doers, dreamers and subversives – Viktor Orbán was placed in the latter category again this year. However, he lost one place, he is no longer considered the second, but the third biggest trouble maker in Europe."
"According to Politico's rationale, since 2011 Viktor Orbán has undermined the rule of law and media freedom, clashed with EU institutions, held Brussels hostage by vetoing in order to obtain money, and developed a friendly relationship with Russian President Vladimir Putin.Hungary's strongman is well on his way to continuing to act as the EU's party-spoiler."
"Politico also warns that during the 2024 EU presidency, Orbán could go overboard and use the six-month mandate to support policies that are contrary to European values."
"It is interesting that last year only the Italian Prime Minister Giorgia Meloni preceded the Hungarian Prime Minister on the list, who changed careers this year and came first in the doers category."
"For Viktor Orbán, Elvira Nabiullina, president of the Russian Central Bank, and Carles Puigdemont, Spanish representative of the European Parliament, proved to be more subversive this year. The biggest dreamer was Ukrainian President Volodymyr Zelenskyi, and the most influential person of the year was Donald Tusk, former president of the European Council and former prime minister of Poland, who may be the leading force of the Polish coalition government after the October election. In this article, we wrote more about how this is not good news for the Hungarian government, because Orbán may lose an important ally in EU affairs."
"The full ranking list can be browsed here."
sentiment2 = comprehend.detect_sentiment(Text=google_translate, LanguageCode="en")
print(sentiment2)
#%%
bing_translate = "As every year, Politico has selected Europe's most influential people. The paper divides the nominees into three categories: doers, dreamers and subversives – the latter category includes Viktor Orbán again this year. However, it has dropped one place, it is no longer the second, only the third biggest disruptor in Europe."
"Since 2011, Viktor Orban has dismantled the rule of law and media freedom, clashed with EU institutions, held Brussels hostage by vetoing money and established friendly relations with Russian President Vladimir Putin."
"Hungary's strongman is well on his way to continuing to act as a spoiler of the EU's celebration."
"Politico also warns that during his 2024 EU presidency, Orban could go overboard and use the six-month mandate to support policies contrary to European values."
"Interestingly, last year only Italian Prime Minister Giorgia Meloni was ahead of the Hungarian Prime Minister."

sentiment3 = comprehend.detect_sentiment(Text=bing_translate, LanguageCode="en")
print(sentiment3)
#%%
import pandas as pd
df_sentiments = pd.DataFrame(index = ["Positive", "Negative", "Neutral", "Mixed"], columns=["AWS", "Google", "Bing"])

# %%
df_sentiments.loc["Positive", "AWS"] = sentiment1["SentimentScore"]["Positive"]
df_sentiments.loc["Negative", "AWS"] = sentiment1["SentimentScore"]["Negative"]
df_sentiments.loc["Neutral", "AWS"] = sentiment1["SentimentScore"]["Neutral"]
df_sentiments.loc["Mixed", "AWS"] = sentiment1["SentimentScore"]["Mixed"]
df_sentiments.loc["Positive", "Google"] = sentiment2["SentimentScore"]["Positive"]
df_sentiments.loc["Negative", "Google"] = sentiment2["SentimentScore"]["Negative"]
df_sentiments.loc["Neutral", "Google"] = sentiment2["SentimentScore"]["Neutral"]
df_sentiments.loc["Mixed", "Google"] = sentiment2["SentimentScore"]["Mixed"]
df_sentiments.loc["Positive", "Bing"] = sentiment3["SentimentScore"]["Positive"]
df_sentiments.loc["Negative", "Bing"] = sentiment3["SentimentScore"]["Negative"]
df_sentiments.loc["Neutral", "Bing"] = sentiment3["SentimentScore"]["Neutral"]
df_sentiments.loc["Mixed", "Bing"] = sentiment3["SentimentScore"]["Mixed"]
df_sentiments = df_sentiments.astype(float)
df_sentiments.round(decimals = 4)

#%%
import requests
from bs4 import BeautifulSoup
# %%
url = "https://orf.at/stories/3339404/"
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to fetch webpage: Status code {response.status_code}")
# %%
webpage = BeautifulSoup(response.content, "html.parser")
# Using CSS selectors to scrape the section
description_html = webpage.select("p")
texts = [text.get_text().strip() for text in description_html]
text = "\n".join(texts)
short_text = text[:3900]
# %%
comprehend = boto3.client(service_name="comprehend", region_name="eu-west-1")
sentiment_ger = comprehend.detect_sentiment(Text=short_text, LanguageCode="de")
print(sentiment_ger)
# %%
response = translate.translate_text(
    Text=short_text, SourceLanguageCode="de", TargetLanguageCode="en"
)
print(response["TranslatedText"])
# %%
aws_ger = comprehend.detect_sentiment(Text=response["TranslatedText"], LanguageCode="en")
print(aws_ger)
# %%
sentiment_aws = comprehend.detect_sentiment(Text = aws_ger, LanguageCode="de")
#%%
print(sentiment_aws)
print(sentiment_ger)
# %%
short_text
# %%
print(sentiment_ger)
print()