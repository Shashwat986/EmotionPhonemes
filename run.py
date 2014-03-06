from nltk.corpus import wordnet as wn
import urllib2
from bs4 import BeautifulSoup
import sys
import codecs
import atexit

try:
	sp = codecs.open('phonoDict.dic','r', encoding = 'utf-8')
	phonoDict = {}
	for line in sp:
		line = line.strip()
		if len(line.split('\t'))<2:
			phonoDict[k] = []
		else:
			k = line.split('\t')[0]
			v = line.split('\t')[1]
		if k not in phonoDict.keys():
			phonoDict[k] = [v]
		else:
			phonoDict[k].append(v)
	sp.close()
except KeyboardInterrupt:
	sys.exit(1)
except:
	phonoDict = {}



def closeFile():
	sp = codecs.open('phonoDict.dic','w', encoding = 'utf-8')
	for elem in phonoDict.keys():
		try:
			v = phonoDict[elem]
			if len(v)==0:
				sp.write(elem+"\t"+" "+"\n")
			else:
				for val in v:
					sp.write(elem+"\t"+val+"\n")
		except:
			print "Unexpected Error while saving!"
			continue
	sp.close()

atexit.register(closeFile)

swn = open('SentiWordNet_3.0.0_20130122.txt','r')

# Freq[0] is a dict storing negative word IPA frequencies
# Freq[1] is a dict storing positive word IPA frequencies
Freq = [{}, {}]
ctr = 0
ctrP = 0
ctrN = 0
ctrIPA = 0

for line in swn:
	line = line.strip()
	if len(line)==0:
		continue
	if line[0]=='#':
		continue
	data = line.split('\t')
	pos = data[0]
	id = data[1]
	posScore = float(data[2])
	negScore = float(data[3])
	objScore = 1 - (posScore + negScore)
	words = data[4].split(' ')
	for elem in words:
		ctr += 1
		
		word = elem.split('#')[0]
		term = int(elem.split('#')[1])
		
		keyphrase = "%s.%s.%02d"%(word,pos,term)
		
		if (posScore >= negScore and posScore >= objScore)	\
				or (negScore >= posScore and negScore >= objScore):
			
			stance = 1 if (posScore >= negScore and posScore >= objScore) else 0
			
			if stance == 1:
				ctrP += 1
			else:
				ctrN += 1
			
			if keyphrase in phonoDict.keys():
				IPAs = phonoDict[keyphrase]
			else:
				try:
					r = urllib2.urlopen('http://en.wiktionary.org/wiki/'+word)
					msg = r.read()
					soup = BeautifulSoup(msg)
				except urllib2.HTTPError, e:
					print keyphrase, ':', e
					if e.code == 404:
						phonoDict[keyphrase] = []
					continue
				except KeyboardInterrupt:
					sys.exit(1)
				except:
					print "Unexpected error!"
					continue
				print keyphrase,
				res = soup.find_all("span", class_ = 'IPA')
				if len(res)==0:
					print ": IPA Unavailable"
					phonoDict[keyphrase] = []
					continue
				print
				
				IPAs = [r.string for r in res if r.string is not None]
				phonoDict[keyphrase] = IPAs
				
			
			ctrIPA += 1
			for IPA in IPAs:
				try:
					for lett in IPA:
						Freq[stance][lett] = Freq[stance].get(lett,0) + 1
				except:
					continue
			
		else:
			print keyphrase,
			print ": Objective"

print "IPA:",ctrIPA
print "(+):",ctrP
print "(-):",ctrN
print "Tot:",ctr

print "Neg:"
fp = open('pos.dat','wb')
for elem in Freq[0].keys():
	fp.write(elem+"\t"+str(Freq[0][elem]))
	print elem.encode('raw_unicode_escape'),':',Freq[0][elem]
fp.close()

print "Pos:"
fp = open('neg.dat','wb')
for elem in Freq[1].keys():
	fp.write(elem+"\t"+str(Freq[1][elem]))
	print elem.encode('raw_unicode_escape'),':',Freq[1][elem]

fp = open('pos.dat','wb')

import json
with open('pos.json', 'wb') as fp:
	json.dump(Freq[0],fp)

with open('neg.json', 'wb') as fp:
	json.dump(Freq[1],fp)
