import sys
import codecs
import json
from time import strftime

# Freq[0] is a dict storing negative word IPA frequencies
# Freq[1] is a dict storing positive word IPA frequencies
Freq = [{}, {}]
FreqList = {}
ctr = 0
ctrP = 0
ctrN = 0
ctrIPA = 0

sp = codecs.open('phonoDict_all_2014.02.25(4.03).dic','r',encoding = 'utf-8')

for line in sp:
	ctr += 1
	
	try:
		word, stance, IPA = line.split('\t')
		stance = int(stance)
		IPA = IPA.strip()
	except:
		print line
		continue
	
	
	if stance == 1:
		ctrP += 1
	elif stance == -1:
		ctrN += 1
	else:
		# Objective word
		continue
	
	# Reset stance so that Freq[] can use it.
	stance = 1 if stance==1 else 0
	
	ctrIPA += 1
	for lett in IPA:
		Freq[stance][lett] = Freq[stance].get(lett,0) + 1
		FreqList[lett] = FreqList.get(lett,[])+[word]

print "IPA:",ctrIPA
print "(+):",ctrP
print "(-):",ctrN
print "Tot:",ctr


#print "Neg:"
fp = codecs.open('negFreq_{}.dat'.format(strftime('%Y.%m.%d(%H.%M)')),'w', encoding = 'utf-8')
for elem in sorted(Freq[0], key = Freq[0].get, reverse = True):
	fp.write(elem+"\t"+str(Freq[0][elem])+"\n")
	#print elem.encode('raw_unicode_escape'),':',Freq[0][elem]
fp.close()

with open('neg_{}.json'.format(strftime('%Y.%m.%d(%H.%M)')), 'wb') as fp:
	json.dump(Freq[0],fp)

	
#print "Pos:"
fp = codecs.open('posFreq_{}.dat'.format(strftime('%Y.%m.%d(%H.%M)')),'w', encoding = 'utf-8')
for elem in sorted(Freq[1], key = Freq[1].get, reverse = True):
	fp.write(elem+"\t"+str(Freq[1][elem])+"\n")
	#print elem.encode('raw_unicode_escape'),':',Freq[1][elem]
fp.close()

with open('pos_{}.json'.format(strftime('%Y.%m.%d(%H.%M)')), 'wb') as fp:
	json.dump(Freq[1],fp)


# Rank the matrices by 
rankDiffs = {}
defRank = max(len(Freq[0].keys()),len(Freq[1].keys()))
f0 = sorted(Freq[0], key = Freq[0].get, reverse = True)
f1 = sorted(Freq[1], key = Freq[1].get, reverse = True)
for elem0 in f0:
	for elem1 in f1:
		if elem0 == elem1:
			rankDiffs[elem0] = abs(f0.index(elem0)-f1.index(elem1))
			break

defRank = max(len(Freq[0].keys()),len(Freq[1].keys()))

for elem0 in f0:
	if elem0 not in f1:
		rankDiffs[elem0] = defRank - f0.index(elem0)
for elem1 in f1:
	if elem1 not in f0:
		rankDiffs[elem1] = defRank - f1.index(elem1)


fp = codecs.open('diff_{}.dat'.format(strftime('%Y.%m.%d(%H.%M)')),'w',encoding='utf-8')
for elem in sorted(rankDiffs, key = rankDiffs.get, reverse = True):
	if (elem in f0 and elem not in f1):
		fp.write(elem + "\t" + str(rankDiffs[elem]) + "\t" + '-' + "\t" + "100" + " (" + str(Freq[0][elem]) + ")\n")# + str(FreqList[elem]) + "\n")
		continue
	if (elem in f1 and elem not in f0):
		fp.write(elem + "\t" + str(rankDiffs[elem]) + "\t" + '+' + "\t" + "100" + " (" + str(Freq[1][elem]) + ")\n")#" + str(FreqList[elem]) + "\n")
		continue
	if f1.index(elem) < f0.index(elem):
		fp.write(elem + "\t" + str(rankDiffs[elem]) + "\t" + '+' + "\t" + str((100.0*Freq[1][elem])/(Freq[1][elem]+Freq[0][elem])) + " (" + str(Freq[1][elem]) + ")\n")#" + str(FreqList[elem]) + "\n")
		continue
	if f0.index(elem) < f1.index(elem):
		fp.write(elem + "\t" + str(rankDiffs[elem]) + "\t" + '-' + "\t" + str((100.0*Freq[0][elem])/(Freq[1][elem]+Freq[0][elem])) + " (" + str(Freq[0][elem]) + ")\n")#" + str(FreqList[elem]) + "\n")
		continue
fp.close()



