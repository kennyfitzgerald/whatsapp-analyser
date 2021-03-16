# Define filename:
filename = '_chat.txt'

# Initiate whatsapp object
chat = whatsapp.WhatsApp(filename, manual_recode={'+447714576053':'Steves'})

# Get main chat
x = w.main_chat

wp.plot_cumilative_mentions_multi_term(w.main_chat, ['piles'], w.chat_name, cumsum=True)


w.main_chat[w.main_chat.message.str.contains('omitted')]




len(x)/(max(x.index) - min(x.index)).days

# Generate message counts per day:
days = 60
msg_counts = pd.DataFrame({'mpd' : (x.index).floor('d').value_counts().sort_index()})
msg_counts = msg_counts.reindex(pd.date_range(min(msg_counts.index), max(msg_counts.index)), fill_value=0)
msg_counts['SMA'] = msg_counts.iloc[:, 0].rolling(window=days).mean()

msg_counts['year'] = msg_counts.index.year
msg_counts['date'] = msg_counts.index.strftime('%m-%d')
unstacked = msg_counts.set_index(['year', 'date']).SMA.unstack(-2)

years = unstacked.columns.tolist()
fig, ax = plt.subplots(figsize=(15, 7))

for year in years:
    ax.plot(unstacked[year])

ax.grid()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_major_formatter(ticker.NullFormatter())
ax.margins(x=0)
ax.legend(years, loc='center left', bbox_to_anchor=(1, .5))

ax.set_xlabel('Month')
ax.set_ylabel('Messages')
ax.set_title(w.chat_name + ' message counts: ' + str(days) + ' day simple moving average', loc='left')

plt.figure(figsize=[15,10])
plt.grid(True)
msg_counts['SMA'].plot()
plt.plot(msg_counts['SMA'],label='SMA 7 Days')
plt.legend(loc=2)

# Generate density by weekdaysz
# day_counts = x.groupby('weekday').agg(count())


# Generate message counts per day: PER PERSON
days = 100

msg_counts = x.groupby([x.index.floor('d'), 'sender']).size().reset_index()
msg_counts.columns = ['date', 'sender', 'message_count']

unstacked = msg_counts.set_index(['sender', 'date']).message_count.unstack(-2)
unstacked = unstacked.reindex(pd.date_range(min(unstacked.index), max(unstacked.index)), fill_value=0)
unstacked = unstacked.fillna(0)
unstacked[w.members] = unstacked[w.members].rolling(window=days).mean()

fig, ax = plt.subplots(figsize=(15, 7))

for member in w.members:
    ax.plot(unstacked[w.members])

ax.grid()
ax.xaxis.set_major_locator(mdates.MonthLocator((1, 7)))
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
ax.xaxis.set_minor_formatter(ticker.NullFormatter())
ax.margins(x=0)
ax.legend(w.members, loc='center left', bbox_to_anchor=(1, .5))
ax.set_xlabel('Month')
ax.set_ylabel('Messages')
ax.set_title(w.chat_name + ' message counts: ' + str(days) + ' day simple moving average', loc='left')

chat = w.main_chat
terms = ['well cold', 'well hot']
member = 'Albert'


ind_msg = x.loc[x.sender.str.match(member) & x.message.str.contains(term), :]

ind_msg = pd.DataFrame({'mpd' : (ind_msg.index).floor('d').value_counts().sort_index()})
ind_msg = ind_msg.reindex(pd.date_range(min(ind_msg.index), max(ind_msg.index)), fill_value=0)

ind_msg['cumilative'] = ind_msg.mpd.cumsum()

ind_msg['year'] = ind_msg.index.year
ind_msg['date'] = ind_msg.index.strftime('%m-%d')

fig, ax = plt.subplots(figsize=(15, 7))
ax.plot(ind_msg['cumilative'])

ax.grid()
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
ax.xaxis.set_minor_formatter(ticker.NullFormatter())
ax.margins(x=0)

ax.set_xlabel('Month')
ax.set_ylabel('Mentions')
ax.set_title(w.chat_name + ': Cumilative mentions of ' + "'" + term.replace('\\', '') + "' by " + member, loc='left')



# Cumilative stuff by all
days = 365
split = False
term = 'well cold'
members = w.members
cum_all = x.loc[x.message.str.contains(term), :]

cum_all = cum_all.groupby([cum_all.index.floor('d'), 'sender']).size().reset_index()
cum_all.columns = ['date', 'sender', 'message_count']


cum_all = cum_all.set_index(['sender', 'date']).message_count.unstack(-2)
cum_all = cum_all.reindex(pd.date_range(min(cum_all.index), max(cum_all.index)), fill_value=0)
cum_all = cum_all.fillna(0)
cum_all = cum_all.cumsum()



fig, ax = plt.subplots(figsize=(15, 7))
ax.plot(cum_all)

ax.grid()
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
ax.xaxis.set_minor_formatter(ticker.NullFormatter())
ax.margins(x=0)

ax.legend(cum_all.columns, loc='center left', bbox_to_anchor=(1, .5))
ax.set_xlabel('Month')
ax.set_ylabel('Mentions')
ax.set_title(w.chat_name + ': Cumilative mentions of ' + "'" + term.replace('\\', '') + "'", loc='left')
