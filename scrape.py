
import bs4
import re
import requests

BASE_URL = 'http://www.toti.eu.com/beatles/'
TAGS_TO_FILTER = ('style','script','[document]','head','title')
SONG_MATCHER = 'showsong\.asp\?id\=[0-9]+'
MATCHERS = (
        'Visit also:', 
        'www', 
        '#BeginLibraryItem', 
        '#EndLibraryItem',
        'The Beatles Lyrics Repository',
        'Main page')

def include(element):
	if element.parent.name in TAGS_TO_FILTER:
		return False
	element = element.lstrip()
	if not element:
		return False
	for matcher in MATCHERS:
		if element.startswith(matcher):
			return False
	return True

def process(element):
	element = element.strip()
	element.replace('’', '\'')
    element.replace('`', '\'')
    element.replace('“','"')
    element.replace('”','"')
    return element

def scrape_song(url):
	resp = requests.get(url)
	soup = bs4.BeautifulSoup(resp.text, features='lxml')
	elements = soup.findAll(text=True)
	elements = [element for element in elements if include(element)]
    elements = [process(element) for element in elements]
    title,writer = elements[:2]
    lines = elements[2:]
    return title, writer, lines

if __name__=="__main__":
	resp = requests.get(BASE_URL+'showall.asp')
	song_urls = re.findall(SONG_MATCHER,resp.text)
	database = []
	for i, song_url in enumerate(song_urls):
		title,writer,lines = scrape_song(BASE_URL+song_url)
		database.append((title, writer, lines))
        if i % 10 == 0:
            print("Scraped %d files; %d remaining." % (i, len(song_urls) - i))

    with open('songs.txt','w') as file_:
    	for title,writer,lines in database:
    		line = "{}\t{}\t{}\n".format(title,writer,"\\".join(lines))
    		file_.write(line)
