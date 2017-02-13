import os
import json
import string
from sklearn import svm
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, mean_absolute_error, average_precision_score, explained_variance_score, r2_score
from natsort import natsorted, ns
import numpy as np
import matplotlib.pyplot as plt

indir = 'descriptors'
annotationsfile = 'annotations.csv'

missing_at_csv = [
'1029.json',
'1059.json',
'1064.json',
'1255.json',
'1297.json',
'1320.json',
'1614.json',
'1654.json',
'1968.json'
]

jsonfiles = os.listdir(indir)
jsonfiles = [f for f in jsonfiles if f.endswith('.json') and f not in missing_at_csv]
jsonfiles = natsorted(jsonfiles, key=lambda y: y.lower())

trainingset = []
testset = []

valencetraining = []
valenceeval = []
arousaltraining = []
arousaleval = []

''' This function iterates over all the json file and gets the numeric values '''
def walkjson(x, xname, d, indents=0):
    ''' beats_position length varies for each audio file,
        spectral_spread sometimes detected as non-numeric value,
        ignoring both... '''
    if xname == 'beats_position' or xname == 'spectral_spread':
        return
    if isinstance(x, dict):
        #print '{}{}'.format('\t'*indents, xname)
        for k,v in x.iteritems():
            walkjson(v, k, d, indents + 1)
    elif isinstance(x, list):
        #print '{}{}'.format('\t'*indents, xname)
        for idx,l in enumerate(x):
            walkjson(l, idx, d, indents + 1)
    elif isinstance(x, tuple):
        #print '{}tuple'.format('\t'*indents)
        for idx,t in enumerate(x):
            walkjson(t, idx, d, indents + 1)
    else:
        if isinstance(x, float) or isinstance(x, int):
            #print '{}{}'.format('\t'*indents, x)
            d.append(x)
        else:
            ''' NON-NUMERIC '''
            #print 'NON-NUMERIC {}'.format(x)

for filename in jsonfiles:
    with open(os.path.join(indir,filename)) as f:
        data = 	json.load(f)
        descriptors = []
        walkjson(data, filename, descriptors)
        if int(filename[:-5]) < 1701:
            trainingset.append(descriptors)
        else:
            testset.append(descriptors)
        #print '{} - {}'.format(filename, len(descriptors), len(nonnumeric), nonnumeric)

trainingset = np.array(trainingset, dtype=np.float64)
testset = np.array(testset, dtype=np.float64)
trainingset = preprocessing.normalize(trainingset)
testset = preprocessing.normalize(testset)

with open(annotationsfile) as csv:
    lines = csv.readlines()
    for line in lines[1:]:
        annot = line.strip().split(',')
        if int(annot[0]) < 1701:
            valencetraining.append(annot[1])
            arousaltraining.append(annot[2])
        else:
            valenceeval.append(annot[1])
            arousaleval.append(annot[2])


valencetraining = np.array(valencetraining, dtype=np.float64)
arousaltraining = np.array(arousaltraining, dtype=np.float64)
valenceeval = np.array(valenceeval, dtype=np.float64)
arousaleval = np.array(arousaleval, dtype=np.float64)

valsvr = svm.SVR()
valsvr.fit(trainingset, valencetraining)

arosvr = svm.SVR()
arosvr.fit(trainingset, arousaltraining)

valpredict = valsvr.predict(testset)
aropredict = arosvr.predict(testset)

mse = mean_squared_error(valenceeval, valpredict)
mae = mean_absolute_error(valenceeval, valpredict)
evs = explained_variance_score(valenceeval, valpredict)
r2 = r2_score(valenceeval, valpredict)
print 'Evaluation'
print "Mean Squared Error: {}\nMean Absolute Error: {}\nExplained Variance Score: {}\nR2 Score: {}".format(mse, mae, evs, r2)

### Plotting first 100 features
plt.subplot(211)
plt.plot(np.arange(0,100), valenceeval[:100], 'r')
plt.subplot(211)
plt.plot(np.arange(0,100), valpredict[:100], 'b')
plt.subplot(212)
plt.plot(np.arange(0,100), arousaleval[:100], 'r')
plt.subplot(212)
plt.plot(np.arange(0,100), aropredict[:100], 'b')
plt.show()
