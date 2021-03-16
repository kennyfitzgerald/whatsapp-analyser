# Third party library imports
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


# This function takes as input a chat object, a list of terms, an optional chat name and chat member constraint as
# inputs and returns a plot of cumulative mentions of any of the listed terms in the chat over time. There is also
# a built in functionality to visualise as a simple moving average, or to remove the cumulative measure.

def plot_cumulative_mentions_multi_term(chat, terms, chat_name='WhatsApp Chat', member='(.*?)', cum_sum=True, avg=False):

    # Filter messages by member (if applicable)
    messages = chat.loc[chat.sender.str.match(member), :]

    # Dictionary to store series
    multi = dict()

    # Loop through terms and add counts series to list
    for term in terms:
        mentions = messages.loc[chat.message.str.contains(term), 'message']
        mentions = mentions.groupby(mentions.index.floor('d')).size()
        mentions = mentions.reindex(pd.date_range(min(mentions.index), max(mentions.index)), fill_value=0).fillna(0)
        mentions = mentions.rename(term)
        multi[term] = mentions

    # Convert to dataframe and apply cum_sum or average
    multi = pd.DataFrame(multi).fillna(0)

    if cum_sum:
        multi = multi.cumsum()
    if avg:
        multi = multi.rolling(window=avg).mean()

    # Produce plots
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.plot(multi)
    ax.grid()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax.margins(x=0)
    ax.legend(multi.columns, loc='center left', bbox_to_anchor=(1, .5))
    ax.set_xlabel('Month')
    ax.set_ylabel('Mentions')
    ax.set_title(chat_name + ': Cumulative mentions', loc='left')