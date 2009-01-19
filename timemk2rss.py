#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import urllib2
import cgi
import time
import datetime
import codecs
import re

class Timemk2RSS:
    def __init__(self, naslov,topic,urlkategorija):
        self.naslov = naslov
        self.topic = topic
        self.urlkategorija = urlkategorija
        self.outputdir = '/home/glisha/webapps/nginx_timemk2rss/timemk2rss/public_html/'
        self.elementi = []

    def _zemi_stranata(self):
        req = urllib2.Request(self.urlkategorija,{},{'User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.4) Gecko/2008111318 Ubuntu/8.10 (intrepid) Firefox/3.0.4'})
        try:
            resp = urllib2.urlopen(req)
            self.stranata = resp.read()
            #print self.stranata
            return True
        except urllib2.URLError:
            self.stranata = u''
            return False

    def _najdi_vesti(self):
        soup = BeautifulSoup(self.stranata)
        vesti=soup.findChildren('div',{'class':'span-15 last'})
    
        for vest in vesti:
            alink = vest.findChild('a')
            izvor = vest.findChild('span',{'class':'source'}).findChild('strong')
            koga = vest.findChild('span',{'class':'when'})
            chasa = re.compile(u'([0-9]+) (час|мин).*')
            if koga:
                najdov = chasa.search(koga.string)
            else:
                najdov = False

            if najdov:
                koga = najdov.groups()[0]
                edinica = najdov.groups()[1]
                if edinica==u'час':
                    objaveno=datetime.datetime.now()-datetime.timedelta(hours=int(koga))
                else:
                    objaveno=datetime.datetime.now()-datetime.timedelta(minutes=int(koga))
            else:
                objaveno=datetime.datetime.now()
    
            self.elementi.append({'title':u"%s: %s" % (izvor.string,alink.string),
                                'url':alink['href'],
                                'published':objaveno})

        sodrzini = soup.findChildren('div',{'class':'span-12 last article-snippet'})
        
        i=0
        for sodrzina in sodrzini:
            self.elementi[i]['description']=cgi.escape(sodrzina.prettify())
            self.elementi[i]['description']=self.elementi[i]['description'].replace('href="index.psp?slot=','href="http://www.time.mk/index.psp?slot=')
            self.elementi[i]['description']=self.elementi[i]['description'].decode('utf-8')
            i+=1

   
    def _format_date(self,dt):
        """convert a datetime into an RFC 822 formatted date
    
        Input date must be in GMT.
        """
        # Looks like:
        #   Sat, 07 Sep 2002 00:00:01 GMT
        # Can't use strftime because that's locale dependent
        #
        # Isn't there a standard way to do this for Python?  The
        # rfc822 and email.Utils modules assume a timestamp.  The
        # following is based on the rfc822 module.
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
                ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
                dt.day,
                ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month-1],
                dt.year, dt.hour, dt.minute, dt.second)

    def outputrss(self):
        if self._zemi_stranata():
            #print len(self.stranata)
            self._najdi_vesti()
            
            ime = '%s/%s.xml' % (self.outputdir,self.topic.lower())
            fajl = codecs.open(ime,"w","utf-8")
            fajl.write(u"""<?xml version="1.0" encoding="utf-8"?>
                        <rss version="2.0">
                        <channel>
                        <title>%s</title>
                        <link>%s</link>
                        <description>%s (неофицијален рсс канал)</description>
                        <language>mk</language>
                        <image>
                        <title>%s</title>
                        <url>%s</url>
                        <link>%s</link>
                        </image>\n""" % (self.naslov,cgi.escape(self.urlkategorija),self.naslov,self.naslov,'http://www.time.mk/time.mk.png','http://time.mk'))

            for element in self.elementi:
                fajl.write("""<item>
                            <title>%s</title>
                            <link>%s</link>
                            <description>%s</description>
                            <pubDate>%s</pubDate>
                            <guid>%s</guid>
                            </item>""" % (element['title'],cgi.escape(element['url']),element['description'],self._format_date(element['published']),cgi.escape(element['url'])))
    
            fajl.write("</channel></rss>")
            fajl.close()


if __name__=='__main__':

    sekcii = [
        {'naslov':u'Time.mk топ вести',
        'topic':u'top',
        'url':'http://www.time.mk/index.psp'},
        {'naslov':u'Time.mk Македонија',
        'topic':u'MK',
        'url':'http://www.time.mk/index.psp?slot=1&topic=MK'},
        {'naslov':u'Time.mk Балкан',
        'topic':u'BALKAN',
        'url':'http://www.time.mk/index.psp?slot=1&topic=BALKAN'},
        {'naslov':u'Time.mk Свет',
        'topic':u'WORLD',
        'url':'http://www.time.mk/index.psp?slot=1&topic=WORLD'},
        {'naslov':u'Time.mk Економија',
        'topic':u'ECONOMY',
        'url':'http://www.time.mk/index.psp?slot=1&topic=ECONOMY'},
        {'naslov':u'Time.mk Култура',
        'topic':u'CULTURE',
        'url':'http://www.time.mk/index.psp?slot=1&topic=CULTURE'},
        {'naslov':u'Time.mk Спорт',
        'topic':u'SPORT',
        'url':'http://www.time.mk/index.psp?slot=1&topic=SPORT'},
        {'naslov':u'Time.mk Занимливости',
        'topic':u'FUN',
        'url':'http://www.time.mk/index.psp?slot=1&topic=FUN'},
       {'naslov':u'Time.mk Црна хроника',
        'topic':u'CHRONIC',
        'url':'http://www.time.mk/index.psp?slot=1&topic=CHRONIC'},
       {'naslov':u'Time.mk Технологија',
        'topic':u'TECH',
        'url':'http://www.time.mk/index.psp?slot=1&topic=TECH'},
        ]


    for sekcija in sekcii:
        #print sekcija['topic']
        rss = Timemk2RSS(naslov=sekcija['naslov'],topic=sekcija['topic'],urlkategorija=sekcija['url'])
        rss.outputrss()

