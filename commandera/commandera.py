from __future__ import print_function, unicode_literals
from bs4 import BeautifulSoup as bs
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
from colorama import Fore, Back, Style

import requests as req

DOMAIN = "https://www.resetera.com/"
BOARD_GAMES = "forums/video-games.7/"
BOARD_GAMES_HANGOUTS = "forums/gaming-hangouts.8/"
BOARD_OFFTOPIC = "forums/etcetera.9/"
BOARD_OFFTOPIC_HANGOUTS = "forums/etcetera-hangouts.10/"

def print_system(text):
    print(Fore.YELLOW + text + Style.RESET_ALL)
def print_command(text):
    print(Fore.BLUE + text + Style.RESET_ALL)
def print_spoiler(text):
    print(Fore.RED + Back.RED + text + Style.RESET_ALL) 
def print_error(text):
    print(Fore.RED + text + Style.RESET_ALL) 

class Board():
    def __init__(self,board=BOARD_GAMES):
        self.board = board

    def getThreads(self,page=1):
        raw = self._reqBoard(page)
        self.threads = self._parseBoard(raw)
        return self.threads

    def _reqBoard(self,page):
        url = DOMAIN + self.board + "page-" + str(page)
        res = req.get(url)
        if res.status_code == 200:
            return res.text
        else:
            return None

    def _parseBoard(self,raw):
        threads = []
        rows = bs(raw,'html.parser').find_all('div',{'class':'structItem--thread'})
        
        for row in rows:
            thread_params = self._parseThreadRow(row)
    
            threads.append(
                Thread(
                    thread_params['url'],
                    thread_params['title'],
                    thread_params['size']
                )
            )

        return threads

    def _parseThreadRow(self,row):

        title,href = self._parseThreadRow_link(row)
        size = self._parseThreadRow_pages(row)
        return {
            'title':title,
            'url': href,
            'size': size
        }
    
    def _parseThreadRow_link(self,row):
        link_raw = row.find_all('div',{'class':'structItem-title'})[0]

        title = link_raw.a.string
        href = link_raw.a['href']

        return title,href
    def _parseThreadRow_pages(self,row):
        pagelisting_html =  row.find_all('span',{'class':'structItem-pageJump'})
        thread_size = 1

        if len(pagelisting_html) > 0:
            thread_size =  pagelisting_html[0].find_all('a')[-1].text
        return thread_size

class Thread():
    def __init__(self,url,title,size):
        self.url = url
        self.title = title
        self.size = int(size)

    def read(self,page=1):
        thread_raw = self._reqThread(page)
        messages = self._parseThread(thread_raw)
        return messages        

    def _reqThread(self,page):
        url = DOMAIN + self.url + "page-" + str(page)
        res = req.get(url)
        if res.status_code == 200:
            return res.text
        else:
            return None

    def _parseThread(self,raw):
        messages_raw = bs(raw,'html.parser').find_all('div',{'class':'message-inner'})

        messages = []

        for message_raw in messages_raw:
            messages.append(Message(message_raw))

        return messages
    
class Message():
    def __init__(self,raw):
        self.raw = raw
        self.scrapped = False

    def getText(self):
        if self.scrapped is False:
            self.text = self._scrapMessage(self.raw)

        return self.text

    def getRaw(self):
        return self.raw

    def _scrapMessage(self,raw):
        self.raw = raw

        self.date = self.raw.find('time',{'class':'u-dt'}).text
        self.user = self.raw.find('a',{'class':'username'}).text
        
        self.raw = self._formatImage(self.raw)
        self.raw = self._formatTweet(self.raw)
        self.raw = self._formatSpoilers(self.raw)
        self.raw = self._formatQuote(self.raw)

        
        self.text = self.raw.find('article',{'class':'message-body'}).text
        
        
        self.text = bs(Back.YELLOW+Fore.BLACK + self.date + " || " + self.user + " said: " + Style.RESET_ALL,'html.parser').text + self.text + bs(Fore.YELLOW + "_______________________________________________________________" + Style.RESET_ALL,'html.parser').text

        self.scrapped = True
        
        return self.text

    def _formatImage(self,raw=None):
        if raw is None:
            raw = self.raw
            
        images_raw = raw.find_all('img',{'class':'bbImage'})

        for image_raw in images_raw:
            image_src = bs(Fore.MAGENTA +image_raw['src']+ " " + Style.RESET_ALL,'html.parser')
            image_raw.insert_after(image_src)
            image_raw.decompose()

        return raw

    def _formatSpoilers(self,raw=None):
        if raw is None:
            raw = self.raw

        spoilers_raw = raw.find_all('div',{'class':'bbCodeSpoiler'})
        for spoiler_raw in spoilers_raw:

            spoiler_content = bs(Fore.RED + Back.RED +spoiler_raw.find('div',{'class':'bbCodeBlock-content'}).text+ " " + Style.RESET_ALL,'html.parser')
            spoiler_raw.insert_after(spoiler_content)
            spoiler_raw.decompose()
        
        return raw

    def _formatQuote(self,raw=None):
        if raw is None:
            raw = self.raw

        quotes_raw = raw.find_all('div',{'class':'bbCodeBlock--quote'})

        for quote_raw in quotes_raw:

            quote_user_raw = quote_raw.find('div',{'class':'bbCodeBlock-title'})
            if(quote_user_raw is not None):
                quote_user_raw = quote_user_raw.text
            else:
                quote_user_raw = ''

            quote_user = bs(Back.WHITE + Fore.BLACK + quote_user_raw + " " + Style.RESET_ALL,'html.parser')
            quote_content = bs(Back.WHITE + Fore.BLACK + quote_raw.find('div',{'class':'bbCodeBlock-expandContent'}).text + " " + Style.RESET_ALL,'html.parser')
            quote_raw.clear()
            quote_raw.insert(0,quote_user)
            quote_raw.insert(1,quote_content)

        return raw

    def _formatTweet(self,raw=None):
        if raw is None:
            raw = self.raw
        
        tweets_raw = raw.find_all('iframe',{'data-s9e-mediaembed':'twitter'})

        for tweet_raw in tweets_raw:
            tweet_id = tweet_raw['data-s9e-lazyload-src'].split("#",1)[1] 
            res = req.get("http://twitter.com/anyuser/status/"+str(tweet_id))

            if res.status_code == 200:
                tweet_outside_raw = bs(res.text, 'html.parser').find('div',{'class':['tweet','permalink-tweet']})

                tweet_user = bs(Back.CYAN + tweet_outside_raw['data-name'] + " " + Style.RESET_ALL,'html.parser')
                tweet_content = bs(Back.CYAN + tweet_outside_raw.find('div',{'class':'js-tweet-text-container'}).text + " " +Style.RESET_ALL,'html.parser')
                
                tweet_raw.clear()
                tweet_raw.insert(0,tweet_user)
                tweet_raw.insert(1,tweet_content)
                
        return raw

class Era:
    def __init__(self):
        self.cur_Board=None
        self.cur_Board_page=None
        self.cur_Thread=None
        self.cur_Thread_page=None
        self.cur_Messages=None
        self.cur_i_Messages=None
        self.start()

    def start(self):
        self.askBoardFromList()

    def askBoardFromList(self):
        board_url = Choices("What board do you want to explore?",{
            "Games":BOARD_GAMES,
            "Games hangouts":BOARD_GAMES_HANGOUTS,
            "Etcetera":BOARD_OFFTOPIC,
            "Etcetera hangouts":BOARD_OFFTOPIC_HANGOUTS,
            "EXIT":0
        }).ask()

        self.cur_Board = Board(board=board_url)

        self.askThreadFromList(page=1)

    def askThreadFromList(self,page):
        self.cur_Board_page = page

        threads = self.cur_Board.getThreads(page)

        thread_choices = []
        for thread in threads:
            thread_choices.append({
                "name":thread.title + "[P:"+str(thread.size)+"]",
                "value":thread
            })

        thread_choices.append({
            "name":"[__NEXT ->__]",
            "value":"next"
        })

        if page>1:
            thread_choices.append({
                "name":"[__PREV <-__]",
                "value":"prev"
            })

        thread_choices.append({
            "name":"[__BACK TO BOARD LIST__]",
            "value":"up"
        })

        res = ChoicesList("Choose a thread to read",thread_choices).ask()

        if res == "next":
            self.askThreadFromList(page+1)
        elif res == "prev":
            self.askThreadFromList(page-1)
        elif res == "up":
            self.askBoardFromList()
        else:
            self.cur_Thread = res
            self.askThreadReadingFrom()

    def askThreadReadingFrom(self):
        self.cur_Thread.title

        choices = []
        choices.append({
            "name":"[__FIRST PAGE__]",
            "value":"first"
        })

        if self.cur_Thread.size > 1:
            choices.append({
                "name":"[__LAST PAGE__]",
                "value":"last"
            })
            choices.append({
                "name":"[__OTHER PAGE__]",
                "value":"other"
            })

        choices.append({
            "name":"[__BACK TO THREADS LIST__]",
            "value":"back"
        })

        res = ChoicesList("Where do you want to start reading from?",choices).ask()  

        if res == "first":
            self.loadMessagesFromThread(page=1)
            self.readThread()
        elif res == "last":
            self.loadMessagesFromThread(page=self.cur_Thread.size)
            self.readThread()
        elif res == "other":
            self.askThreadPage()
        elif res == "back":
            self.askThreadFromList(page=self.cur_Board_page)

    def loadMessagesFromThread(self,page):
        self.cur_Thread_page = page
        self.cur_Messages = self.cur_Thread.read(self.cur_Thread_page)

    def askThreadPage(self):
        res = int(InputString("Which page do you want to read?").ask())

        if res > 0 and res <= self.cur_Thread.size:
            self.loadMessagesFromThread(page=res)
            self.readThread()
        else:
            self.askThreadReadingFrom()

    def readThread(self,message_index=0):
        if len(self.cur_Messages) > message_index and message_index >= 0:
            self.cur_i_Messages = message_index
            message = self.cur_Messages[self.cur_i_Messages]
            print_system(self.cur_Thread.title)
            print_system("[CMNT: #"+str(self.cur_i_Messages+1)+"/"+str(len(self.cur_Messages))+" || PAGE: #"+str(self.cur_Thread_page)+"/"+str(self.cur_Thread.size)+"]")


            print(message.getText())

            res = Choices("What do you want to do?",{
                "[__NEXT ->__]":"next",
                "[__PREV <-__]":"prev",
                "[__CHANGE PAGE__]":"back",
                "[__BACK TO THREAD LIST__]":"up"
            }).ask()

            if res == "next":
                self.readThread(self.cur_i_Messages+1)
            elif res =="prev":
                self.readThread(self.cur_i_Messages-1)
            elif res == "back":
                self.askThreadReadingFrom()
            elif res == "up":
                self.askThreadFromList(page=self.cur_Board_page)
        else:
            if message_index < 0:
                #prev page
                if self.cur_Thread_page > 1:
                    print_command("loading next page...")
                    self.loadMessagesFromThread(self.cur_Thread_page-1)
                    self.readThread()
                else:
                    print_error("First page! Returning to thread page control...")
                    self.askThreadReadingFrom()
            else:
                #next page
                    if self.cur_Thread.size >= self.cur_Thread_page+1:
                        print_command("loading prev page...")
                        self.loadMessagesFromThread(self.cur_Thread_page+1)
                        self.readThread()
                    else:
                        print_error("Last page! Returning to thread page control...")
                        self.askThreadReadingFrom()

class Question:
    def __init__(self):
        self.questionPackage=None
    def ask(self):
        return prompt(self.questionPackage)['res']

class InputString(Question):
    def __init__(self,question,label=''):
        self.label = label
        self.question = question
        self.questionPackage = {
            'type': 'input',
            'name': 'res',
            'message': self.question
        }

class Choices(Question):
    def __init__(self,question,choices,label=''):
        self.label = label
        self.choices = self.formatChoices(choices)
        self.question = question
        self.questionPackage = {
            'type': 'list',
            'name': 'res',
            'message': self.question,
            'choices': self.choices
        }

    def formatChoices(self,choices):
        choices_formated = []

        for choice in choices:
            choices_formated.append({
                "name":choice,
                "value":choices[choice]
            })

        return choices_formated

class ChoicesList(Question):
    def __init__(self,question,choices,label=''):
        self.label = label
        self.choices = choices
        self.question = question
        self.questionPackage = {
            'type': 'list',
            'name': 'res',
            'message': self.question,
            'choices': self.choices
        }  