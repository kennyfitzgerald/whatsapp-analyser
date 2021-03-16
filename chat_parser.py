# Standard library imports
import re

# Third party library imports
import pandas as pd


# This class takes a whatsapp chat in the form of a .txt file and returns a pandas dataframe containing all content
# and an index of dates.


class ChatParser:

    def __init__(self, filename):

        self.chars_to_strip = ['\u200e', '\u202c', '\xa0', '\u202a']
        self.to_replace_with_space = ['\n']
        self.txt = self._open_txt(filename)
        self.full_chat = self._txt_to_df()

    def _strip_chars(self, string):
        """ Strips a list of character strings from a string
        """
        for term in self.chars_to_strip:
            string = string.replace(term, '')

        return string

    def _replace_with_space(self, string):
        """ Replace a list of character strings with spaces
        """
        for term in self.to_replace_with_space:
            string = string.replace(term, ' ')

        return string

    def _open_txt(self, filename):
        """ Opens a text file and returns a string, strips string using _strip_chars
        """
        with open('test_data/' + filename, 'r', encoding='utf8') as file:
            txt = file.read()
            txt = self._strip_chars(txt)
            # txt = self._replace_with_space(txt)
            return txt

    def _parse_dates(self):
        """ Takes a text string of a WhatsApp chat and returns a list of dates. First date is removed because the first
            message is always removed too. This is because it is never a message.
        """

        dates = re.findall(r'\[\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}:\d{2}]', self.txt)
        dates = pd.to_datetime(dates, format='[%d/%m/%Y, %H:%M:%S]')

        return dates

    def _parse_content(self):
        """ Takes a string of text and returns a list of people and messages.
        """

        content = re.split(r'\n\[\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}:\d{2}]\s', self.txt)
        content[0] = content[0][23::]

        return content

    def _txt_to_df(self):
        """ Compiles dates and content attributes into a pandas dataframe, then splits by column to add messages and
            senders. Also adds additional columns for weekday, month, year, and hour.
        """

        # Create df
        df = pd.DataFrame(index=self._parse_dates(), data={'content': self._parse_content()})

        # Split into two columns
        df[['sender', 'message']] = df['content'].str.split(':', 1, expand=True)

        # adds additional columns for weekday, month, year, and hour
        df['year'] = df.index.year
        df['month'] = df.index.month
        df['weekday'] = df.index.day_name()
        df['hour'] = df.index.hour

        return df
