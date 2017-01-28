from bs4 import BeautifulSoup
import re
import requests

######################################################
# Helper functions
######################################################


def prettify_text(dct):
    for key, val in dct.iteritems():
        dct[key] = val.strip(' \n\r\t')
    return dct


def get_base_url(url):
    regex = r'(.*)\/(ideas|brief|research|feedback|refinement|final-feedback)'
    return re.findall(regex, url)[0][0]

######################################################
# API
######################################################


class OpenIdeo:
    """
    Class that contains all functions necessary to retrieve data from the openIdeo site
    """
    @staticmethod
    def get_challenge_stats(challenge_url):
        """
        Returns details about a challenge (url)
        Ex. https://challenges.openideo.com/challenge/{challenge_name}/brief
        :param challenge_url: String
        :return: Dictionary
        """
        soup = BeautifulSoup(requests.get(challenge_url).text, 'html.parser')
        return OpenIdeo.scrape_challenge_stats(soup)

    @staticmethod
    def scrape_challenge_stats(soup):
        """
        Scrapes BS object to return details
        :param soup: BeautifulSoup object
        :return: dictionary
        """
        try:
            challenge_statement = soup.find('h1', attrs={'class': 'headline-text'}).getText()
            challenge_summary = soup.find('p', attrs={'class': 'description'}).getText()

            answer_dict = {'challenge_statement': challenge_statement,
                           'challenge_summary': challenge_summary}

            return prettify_text(answer_dict)
        except:
            return {}

    @staticmethod
    def get_one_idea(challenge_url, author=None):
        """
        Retrieves information about one idea, or the particular idea
        Ex. https://challenges.openideo.com/challenge/{challenge_name}/ideas/{first_name}-{last_name}-s-idea
        :param challenge_url: String
        :param author: String
        :return: Dictionary
        """
        base_url = get_base_url(challenge_url)
        if author is None:
            # open the ideas page
            soup = BeautifulSoup(requests.get(base_url + '/ideas').text, 'html.parser')
            # get the first idea listed
            first_idea = soup.find('div', attrs={'class': 'main-item-info'}).a['href']
            # href returns something like '/challenge/healthcare-access/ideas/johannes-mangane-s-idea'
            # parse the first idea page
            soup = BeautifulSoup(requests.get('https://challenges.openideo.com' + first_idea).text, 'html.parser')
        else:
            first, last = author.lower().split()
            soup = BeautifulSoup(requests.get(base_url + '/ideas/' + first + '-' + last + '-s-idea').text, 'html.parser')

        return OpenIdeo.scrape_idea_stats(soup)

    @staticmethod
    def scrape_idea_stats(soup):
        """
        Scrapes BS idea object to return details
        :param soup: BeautifulSoup object
        :return: dictionary
        """
        try:
            idea_title = soup.select('h1.headline-text.user-font')[0].text
            idea_blurb = soup.select('p.sub-headline-text.user-font')[0].text
            author = soup.find('a', {'itemprop': 'name'}).getText()
            num_comments = soup.select('a > span.stat-count')[0].text
            try:
                num_applause = soup.select('span.stat-count.hide-on-zero')[0].text
            except:
                num_applause = 0
            answer_dict = {'idea_title': idea_title,
                           'idea_blurb': idea_blurb,
                           'author': author,
                           'comments': num_comments,
                           'applause': num_applause}

            return prettify_text(answer_dict)
        except:
            return {}


if __name__ == '__main__':
    o = OpenIdeo()
    print(o.get_challenge_stats('https://challenges.openideo.com/challenge/healthcare-access/brief'))
    print(o.get_one_idea('https://challenges.openideo.com/challenge/healthcare-access/brief'))