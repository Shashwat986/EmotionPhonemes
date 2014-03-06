import urllib2
from bs4 import BeautifulSoup
import sys
import codecs
import atexit
from time import strftime


numContinue=0
if len(sys.argv)>=2:
	numContinue = int(sys.argv[1])

def closeFile():
	sp.write("Processed till line: "+str(ctrL))
	sp.close()

sp = codecs.open('phonoDict_{}_{}.dic'.format(numContinue, strftime('%Y.%m.%d(%H.%M)')),'w', encoding = 'utf-8')
atexit.register(closeFile)
swn = open('SentiWordNet_3.0.0_20130122.txt','r')

ctr = 0
ctrP = 0
ctrN = 0
ctrIPA = 0
ctrL = 0
for line in swn:
	ctrL += 1
	if ctrL<numContinue:
		continue

	print ctrL
	
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
			
			stance = 1 if (posScore >= negScore and posScore >= objScore) else -1
			
			if stance == 1:
				ctrP += 1
			else:
				ctrN += 1
			
			try:
				r = urllib2.urlopen('http://en.wiktionary.org/wiki/'+word)
				msg = r.read()
				soup = BeautifulSoup(msg)
			except urllib2.HTTPError, e:
				if e.code == 404:
					sp.write(keyphrase+"\t"+str(stance)+"\t"+" "+"\n")
				else:
					print keyphrase, ':', e
				continue
			except KeyboardInterrupt:
				sys.exit(1)
			except:
				print "Unexpected error!"
				raise
				continue
			res0 = soup.find_all("span", class_ = 'IPA')
			res = []
			for r in res0:
				if "English" in r.parent.__repr__():
					res.append(r)

			if len(res)==0:
				sp.write(keyphrase+"\t"+str(stance)+"\t"+" "+"\n")
				continue
			
			IPAs = [r.string for r in res if r.string is not None]
			
			ctrIPA += 1
			for IPA in IPAs:
				try:
					sp.write(keyphrase+"\t"+str(stance)+"\t"+IPA+"\n")
				except:
					continue
			
		else:
			sp.write(keyphrase+"\t"+str(0)+"\t"+" "+"\n")

print "IPA:",ctrIPA
print "(+):",ctrP
print "(-):",ctrN
print "Tot:",ctr

sp.close()
swn.close()