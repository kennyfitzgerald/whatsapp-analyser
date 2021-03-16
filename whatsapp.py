# Third party library imports
import pandas as pd
import PySimpleGUI as sg

# Local library imports
import chat_parser

# This class takes a whatsapp chat in the form of a .txt file and returns a pandas dataframe containing all content
# with an index of dates.

class WhatsApp:

    def __init__(self, filename, manual_recode=None):

        # Load chat parser object
        cp = chat_parser.ChatParser(filename)

        # Define elements
        self.full_df = cp.full_chat
        self.main_chat = self.full_df.drop('content', axis=1)
        self.creation_date = self._get_creation_date()
        self.chat_creator = self._get_chat_creator()

        # Remove encryption rows
        self.main_chat = self.main_chat[~self.main_chat.message.str.contains('Messages and calls are end-to-end encrypted.', na=False)]

        # Define more elements
        self.chat_names = self._chat_name_changes()
        self.chat_name = self.chat_names['chat_name'][-1]
        self.icon_changes = self._icon_changes()
        self.desc_changes = self._desc_changes()
        self.media = self._get_media()
        self.entries_exits = self._chat_entries_exits()

        # Remap members:
        self.remap_members = {**self._remap_members(), **manual_recode}
        self.main_chat.sender = self.main_chat.sender.replace(self.remap_members)
        self.chat_names.sender = self.chat_names.sender.replace(self.remap_members)
        self.icon_changes.sender = self.icon_changes.sender.replace(self.remap_members)
        self.desc_changes.sender = self.desc_changes.sender.replace(self.remap_members)
        self.media = self.media.replace(self.remap_members)

        # Remove changed phone number entries from main chat:
        self.main_chat = self.main_chat[~self.main_chat.sender.str.contains('changed their phone number to a new number')]

        # Get list of members
        self.members = self._get_members()
        self.members = list(pd.Series(self.members).replace(self.remap_members))

        # Recode 'You'
        self.you = self._rename_yourself()
        self.chat_names.sender = self.chat_names.sender.str.replace('You', self.you)
        self.desc_changes.sender = self.desc_changes.sender.str.replace('You', self.you)
        self.icon_changes.sender = self.icon_changes.sender.str.replace('You', self.you)
        self.desc_changes.sender = self.desc_changes.sender.str.replace('You', self.you)
        self.entries_exits.sender = self.entries_exits.sender.str.replace('You', self.you)

        # Convert messages to lowercast
        self.main_chat['message'] = self.main_chat.message.str.lower()

    def _get_creation_date(self):
        """ Gets chat creation date and removes first row from main chat.
        """
        creation_date = self.main_chat.index[0]
        self.main_chat = self.main_chat.iloc[1:]

        return(creation_date)

    def _get_chat_creator(self):
        """ Gets chat name and removes next two rows from main chat.
        """
        creator = self.main_chat.sender[0].replace(' added you', '').replace(' created this group', '')
        self.main_chat = self.main_chat.iloc[2:]

        return(creator)

    def _remove_rows(self, df1, df2):
        """ Removes all rows found in df2 from df1
        """
        df1 = df1.reset_index()
        df2 = df2.reset_index()
        df_all = df1.merge(df2.drop_duplicates(), how='left', indicator=True)
        df_all = df_all[df_all['_merge'] == 'left_only']
        df_all = df_all.drop('_merge', axis=1)
        df_all = df_all.set_index('index')

        return(df_all)

    def _chat_name_changes(self):
        """ Extracts all name changes from self.main_chat and returns a dataframe of name changes containing two columns:
            sender and chat_name.
        """

        # Find name changes
        chat_names = self.main_chat[self.main_chat['sender'].str.contains(" changed the subject to ")]

        # Drops name change rows from main chat
        self.main_chat = self._remove_rows(self.main_chat, chat_names)

        # Format columns:
        chat_names = pd.DataFrame(chat_names['sender'])
        chat_names[['sender', 'chat_name']] = chat_names['sender'].str.split(' changed the subject to ', 1, expand=True)
        chat_names['chat_name'] = chat_names['chat_name'].str.lstrip('\“').str.rstrip('\”').str.strip()
        chat_names = chat_names[['sender', 'chat_name']]

        return(chat_names)

    def _icon_changes(self):
        """ Extracts all icon changes from self.main_chat and returns a dataframe of icon changes.
        """

        # Find icon changes
        icon = self.main_chat[self.main_chat['sender'].str.contains(" changed this group\'s icon")]

        # Drops name change rows from main chat
        self.main_chat = self._remove_rows(self.main_chat, icon)

        # Format columns:
        icon = pd.DataFrame(icon['sender'])
        icon['sender'] = icon['sender'].str.replace(' changed this group\'s icon', '')

        return(icon)

    def _desc_changes(self):
        """ Extracts all description changes from self.main_chat and returns a dataframe of desc changes.
        """

        # Find icon changes
        desc = self.main_chat[self.main_chat['sender'].str.contains(" changed the group description")]

        # Drops name change rows from main chat
        self.main_chat = self._remove_rows(self.main_chat, desc)

        # Format columns:
        desc = pd.DataFrame(desc['sender'])
        desc['sender'] = desc['sender'].str.replace(' changed the group description', '')

        return desc

    def _get_media(self):
        """ Returns a dataframe of media objects by detecting strings  'image omitted'
        """

        # Find icon changes
        media = self.main_chat[self.main_chat['message'].str.contains("image omitted", na=False)]

        # Drops name change rows from main chat
        self.main_chat = self._remove_rows(self.main_chat, media)

        # Format columns:
        media = pd.DataFrame(media['sender'])

        return media


    def _chat_entries_exits(self):
        """ Returns a dataframe of chat users being added or leaving the chat, and also removes these rows from the
            self.main_chat dataframe.
        """

        exits = self.main_chat[self.main_chat.sender.str.endswith(' left')]
        exits = pd.concat([exits, self.main_chat[self.main_chat.sender.str.startswith(self.chat_creator + ' removed ')]])
        self.main_chat = self._remove_rows(self.main_chat, exits)
        exits = pd.DataFrame(exits['sender'].str.replace(' left', '').str.replace(self.chat_creator + ' removed ', '').str.replace('you', 'You'))
        exits['action'] = 'left'

        entries = self.main_chat[self.main_chat.sender.str.startswith(self.chat_creator + ' added ')]
        self.main_chat = self._remove_rows(self.main_chat, entries)
        entries = pd.DataFrame(entries['sender'].str.replace(self.chat_creator + ' added ', '').str.replace('you', 'You'))
        entries['action'] = 'joined'

        entries_exits = pd.concat([entries, exits]).sort_index()

        return entries_exits

    def _remap_members(self):

        remap = dict()
        senders = self.main_chat['sender'][~self.main_chat['sender'].str.contains('changed their phone number to a new number')]
        number_changes = self.main_chat['sender'][self.main_chat['sender'].str.contains('changed their phone number to a new number')]

        if number_changes.empty:
            return (remap)

        for timestamp, change in number_changes.iteritems():

            change = change.replace(' changed their phone number to a new number. Tap to message or add the new number.', '')

            entry_exit_before = self.entries_exits[self.entries_exits.index < timestamp]
            extry_exit_after = self.entries_exits[self.entries_exits.index > timestamp]
            extry_exit_after = extry_exit_after.reindex(index=extry_exit_after.index[::-1])

            remove_before, remove_after = [], []

            for sender, action in entry_exit_before.itertuples(index=False):
                if action == 'left':
                    remove_before.append(sender)
                elif action == 'joined' and sender in remove_before:
                    remove_before.remove(sender)

            for sender, action in extry_exit_after.itertuples(index=False):
                if action == 'joined':
                    remove_after.append(sender)
                elif action == 'left' and sender in remove_after:
                    remove_after.remove(sender)

            before = senders[senders.index < timestamp]
            before = list(sorted(set(list(before)), key=list(before).index))
            before = [x for x in before if x not in remove_before]

            after = senders[senders.index > timestamp]
            after = list(sorted(set(list(after)), key=list(after).index))
            after = [x for x in after if x not in remove_after]

            remap[change] = [s for s in after if s not in before][0]

        return remap


    def _get_members(self):
        """ Returns a list of chat members.
        """
        # Chat members
        members = list(set(list(self.main_chat.sender)))

        return members

    def _rename_yourself(self):
        """ Replaces 'You' with your actual name, as chosen from a list. This can then be used to update the other
            dataframe we have so far.
        """

        # Potential replacements for 'you' where applicable:
        to_replace = list(set(self.members).difference(set(list(self.chat_names.sender))))

        if len(to_replace) == 1:
            values = dict()
            values['LB'] = to_replace[0]
            return values['LB']
        else:
            event, values = sg.Window('Select your name, or the name of the person that provided the chat file: ', [
                [sg.Text('Select one->'), sg.Listbox(to_replace, size=(20, 3), key='You')],
                [sg.Button('Ok'), sg.Button('Cancel')]]).read(close=True)

            if event == 'Ok':
                sg.popup(f'You chose {values["You"][0]}')
            else:
                sg.popup_cancel('User aborted')
                values["LB"] = 'You'

        return values['You'][0]