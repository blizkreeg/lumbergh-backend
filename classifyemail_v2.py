import docclass
import string
import re
import csv

# Train the dataset

c1 = docclass.naivebayes(docclass.getwords)
c1.setdb('taskdb1.db')
c1.setthreshold('task',2.0)

# Naive Bayes Classifier

fileinp = "/Users/manu/email30/data/taskclassifierinput2.csv"
reader = csv.reader(open(fileinp,"U"))
for row in reader:
	c1.train(row[0],row[1])


fout = open('/Users/manu/email30/data/reports/bayesPerfTest1_taskTh2pt0.csv','wb')
OUT = csv.writer(fout)
OUT.writerow(('body','act','pred','accuracy','precision','recall','fmeasure'))

fileinp = "/Users/manu/email30/data/taskclassifiertest1.csv"
reader = csv.reader(open(fileinp,"U"))

i = 0
predcat = ''
tp=0.001
fn=0.001
fp=0.001
tn=0.001
precision=0
recall =0
accuracy=0
fmeasure=0

for row in reader:
	predcat = c1.classify(row[0],default='nontask')
	if row[1] == 'task':
		if predcat == 'task':
			tp += 1
		else:
			fn += 1
	else:
		if predcat == 'task':
			fp += 1
		else:
			tn += 1
 
	accuracy = (tp+tn)/(tp+tn+fn+fp)
	precision = tp/(tp+fp)
	recall = tp/(tp+fn)
	fmeasure = 2*precision/(precision+recall)
	
	OUT.writerow((row[0],row[1],predcat,accuracy,precision,recall,fmeasure))

fout.close()
print accuracy, precision, recall, fmeasure


# Pattern matching

def patternmatch(msg):
	#regexes = {'let\s+me|us\s+know\s+if|when|what\s'}
	regexes = ["let\s+(me|us)\s+know\s+(if|when|what)(.+)((\?)|(\.))",
				"look\s+into\s+this",
				"(could|can|will)\s+you\s+(please)?.+\?",
				"((is it)|(would it be))\s+possible.+\?",
				"please\s+advi(c|s)e",
				"would(\s+\w*)appreciate\s+(it\s+)?(if|when|what)",
				"(could|can|will)\s+you\s+(please)?(.+)(update)?\?"
				"please\s+take\s+a\s+look",
				"(do|did|have)\s+(we|you).+\?",
				"((i was)|(we were))\s+wondering.+\?",
				"is\s+this\s+something.+\?",
				"(i|we)\s+(will)?\s+need\s+your"]
	
	for patterns in regexes:
		if re.match(patterns,msg,re.I): 
			return 'task'
	return 'nontask'

	
fout = open('/Users/manu/email30/data/reports/patternPerfTest1.csv','wb')
OUT = csv.writer(fout)
OUT.writerow(('body','act','pred','accuracy','precision','recall','fmeasure'))

fileinp = "/Users/manu/email30/data/taskclassifiertest1.csv"
reader = csv.reader(open(fileinp,"U"))

i = 0
predcat = ''
tp=0.001
fn=0.001
fp=0.001
tn=0.001
precision=0
recall =0
accuracy=0
fmeasure=0

for row in reader:
	predcat = patternmatch(row[0])
	if row[1] == 'task':
		if predcat == 'task':
			tp += 1
		else:
			fn += 1
	else:
		if predcat == 'task':
			fp += 1
		else:
			tn += 1
 
	accuracy = (tp+tn)/(tp+tn+fn+fp)
	precision = tp/(tp+fp)
	recall = tp/(tp+fn)
	fmeasure = 2*precision/(precision+recall)
	
	OUT.writerow((row[0],row[1],predcat,accuracy,precision,recall,fmeasure))

fout.close()
print accuracy, precision, recall, fmeasure

# Combined Bayes and Pattern Matching

fout = open('/Users/manu/email30/data/reports/combBayesPatternPerfTest1.csv','wb')
OUT = csv.writer(fout)
OUT.writerow(('body','act','pred','accuracy','precision','recall','fmeasure'))

fileinp = "/Users/manu/email30/data/taskclassifiertest1.csv"
reader = csv.reader(open(fileinp,"U"))


i = 0
predcat = ''
predcat1 = ''
predcat2 = ''
tp=0.001
fn=0.001
fp=0.001
tn=0.001
precision=0
recall =0
accuracy=0
fmeasure=0

for row in reader:
	predcat1 = patternmatch(row[0])
	predcat2 = c1.classify(row[0])
	
	if predcat1 == 'task':
		predcat = 'task'
	else:
		predcat = predcat2
	if row[1] == 'task':
		if predcat == 'task':
			tp += 1
		else:
			fn += 1
	else:
		if predcat == 'task':
			fp += 1
		else:
			tn += 1
 
	accuracy = (tp+tn)/(tp+tn+fn+fp)
	precision = tp/(tp+fp)
	recall = tp/(tp+fn)
	fmeasure = 2*precision/(precision+recall)
	
	OUT.writerow((row[0],row[1],predcat,accuracy,precision,recall,fmeasure))

fout.close()
print accuracy, precision, recall, fmeasure

# Fisher's method

c2 = docclass.fisherclassifier(docclass.getwords)
c2.setdb('taskdb1.db')
c2.setminimum('task',0.6)

fout = open('/Users/manu/email30/data/reports/fisherPerfTest1_taskMin0pt6.csv','wb')
OUT = csv.writer(fout)
OUT.writerow(('body','act','pred','accuracy','precision','recall','fmeasure'))

fileinp = "/Users/manu/email30/data/taskclassifiertest1.csv"
reader = csv.reader(open(fileinp,"U"))

i = 0
predcat = ''
tp=0.001
fn=0.001
fp=0.001
tn=0.001
precision=0
recall =0
accuracy=0
fmeasure=0

for row in reader:
	predcat = c2.classify(row[0],default='nontask')
	if row[1] == 'task':
		if predcat == 'task':
			tp += 1
		else:
			fn += 1
	else:
		if predcat == 'task':
			fp += 1
		else:
			tn += 1
 
	accuracy = (tp+tn)/(tp+tn+fn+fp)
	precision = tp/(tp+fp)
	recall = tp/(tp+fn)
	fmeasure = 2*precision/(precision+recall)
	
	OUT.writerow((row[0],row[1],predcat,accuracy,precision,recall,fmeasure))

fout.close()
print accuracy, precision, recall, fmeasure



	