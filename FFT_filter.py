# manualTemplate.py
# A script to perform a template attack
# Will attack one subkey of AES-128

import numpy as np
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt

# Useful utilities
sbox=(
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16) 
hw = [bin(x).count("1") for x in range(256)]

def cov(x, y):
    # Find the covariance between two 1D lists (x and y).
    # Note that var(x) = cov(x, x)
    return np.cov(x, y)[0][1]


# Uncomment to check
#print sbox
#print [hw[s] for s in sbox]


# Start calculating template
# 1: load data
tempTraces = np.load(r'/Users/DanielYou/chipwhisperer/projects/tut_randkey_randplain_data/traces/2016.08.15-14.47.21_traces.npy')
tempPText  = np.load(r'/Users/DanielYou/chipwhisperer/projects/tut_randkey_randplain_data/traces/2016.08.15-14.47.21_textin.npy')
tempKey    = np.load(r'/Users/DanielYou/chipwhisperer/projects/tut_randkey_randplain_data/traces/2016.08.15-14.47.21_keylist.npy')

#print tempPText
#print len(tempPText)
#print tempKey
#print len(tempKey)
#plt.plot(tempTraces[0])
#plt.show()

#d_fft = np.fft.fft(tempTraces[0])
#plt.plot(d_fft)
#plt.show()


# Template is ready!
# 1: Load attack traces
atkTraces = np.load(r'/Users/DanielYou/chipwhisperer/projects/tut_fixedkey_randplain_data/traces/2016.08.15-14.49.51_traces.npy')
atkPText  = np.load(r'/Users/DanielYou/chipwhisperer/projects/tut_fixedkey_randplain_data/traces/2016.08.15-14.49.51_textin.npy')
atkKey    = np.load(r'/Users/DanielYou/chipwhisperer/projects/tut_fixedkey_randplain_data/traces/2016.08.15-14.49.51_knownkey.npy')

#turn attack trace to frequency domain
atk_fft = []

for i in range(len(atkTraces)):
    full_atk = np.fft.fft(atkTraces[i])
    atk_fft.append(full_atk[:len(full_atk)/2])

print "full atk len", len(full_atk)
print "temp atk fft", len(atk_fft[0])

#turn template trace to frequency domain
template_fft = []

for i in range(len(tempTraces)):
    full = np.fft.fft(tempTraces[i])
    template_fft.append(full[:len(full)/2])

print "full len", len(full)
print "temp fft", len(template_fft[0])

#turn template trace to frequency domain
#print "atk fft length: ", len(atk_fft[0])

##
fullkey = []
key_right = []


#attack each subkey in every loop
for key_num in range(16):
    
    #turn template to frequency domain
    ##trace_fft = np.fft.fft(tempTraces[key_num])

    print "***Attacking key #", key_num
    # 2: Find HW(sbox) to go with each input
    # Note - we're only working with the first byte here
    tempSbox = [sbox[tempPText[i][key_num] ^ tempKey[i][key_num]] for i in range(len(tempPText))] 
    tempHW   = [hw[s] for s in tempSbox]
    
    #print tempSbox
    #print tempHW
    #transform = np.fft.fft(tempTraces[key_num])
    #plt.grid(transform)
    #plt.show()
    
    # 2.5: Sort traces by HW
    # Make 9 blank lists - one for each Hamming weight
    tempTracesHW = [[] for _ in range(9)]
    #print "template length :", len(template_fft[0])
    # Fill them up
    for i in range(len(tempTraces)):
        HW = tempHW[i]
        #tempTracesHW[HW].append(tempTraces[i])
        tempTracesHW[HW].append(template_fft[i])
    
    # Switch to numpy arrays
    tempTracesHW = [np.array(tempTracesHW[HW]) for HW in range(9)]

    # 3: Find averages
    #tempMeans = np.zeros((9, len(tempTraces[0])))
    tempMeans = np.zeros((9, len(template_fft[0])))

    for i in range(9):
        tempMeans[i] = np.average(tempTracesHW[i], 0)
        
    #plt.plot(tempMeans[2])
    #plt.grid()
    #plt.show()
    
    
    # 4: Find sum of differences
    #tempSumDiff = np.zeros(len(tempTraces[0]))
    tempSumDiff = np.zeros(len(template_fft[0]))
    for i in range(9):
        for j in range(i):
            tempSumDiff += np.abs(tempMeans[i] - tempMeans[j])
    
    #trans_SumDiff = np.fft.fft(tempSumDiff)
    #print trans_SumDiff
    #print "FFT length", len(trans_SumDiff)
    #print "sum of diff length: ", len(tempSumDiff)
    #plt.plot(tempSumDiff)
    #plt.grid()
    #plt.show()
    
    #plt.plot(tempSumDiff)
    #plt.grid()
    #plt.show()
    
    
    # 5: Find POIs
    tmpPOIs = []
    #POIs = []
    numPOIs = 10
    POIspacing = 3
    
    for i in range(numPOIs+2):
        # Find the max
        nextPOI = tempSumDiff.argmax()
        if(nextPOI != 795 and nextPOI != 705):
            tmpPOIs.append(nextPOI)
    
        
        # Make sure we don't pick a nearby value
        poiMin = max(0, nextPOI - POIspacing)
        poiMax = min(nextPOI + POIspacing, len(tempSumDiff))
        for j in range(poiMin, poiMax):
            tempSumDiff[j] = 0
    
    
    #throw first 2 POIs
    if (len(tmpPOIs) == 11):
        POIs = tmpPOIs[1:]
    else:
        POIs = tmpPOIs

    print "POIs :", tmpPOIs
    print "trim :", POIs
    
    # 6: Fill up mean and covariance matrix for each HW
    meanMatrix = np.zeros((9, numPOIs))
    covMatrix  = np.zeros((9, numPOIs, numPOIs))
    for HW in range(9):
        for i in range(numPOIs):
            # Fill in mean
            meanMatrix[HW][i] = tempMeans[HW][POIs[i]]
            for j in range(numPOIs):
                x = tempTracesHW[HW][:,POIs[i]]
                y = tempTracesHW[HW][:,POIs[j]]
                covMatrix[HW,i,j] = cov(x, y)
            
    #print meanMatrix
    #print covMatrix[0]
    #print atkPText
    #print [hex(x)[2:5] for x in atkKey]
    
    
    # 2: Attack
    # Running total of log P_k
    P_k = np.zeros(256)
    #atk_fft = np.fft.fft(atkTraces)
    #for j in range(len(atkTraces)):
    for j in range(len(atk_fft)):
        # Grab key points and put them in a small matrix
        #a = [atkTraces[j][POIs[i]] for i in range(len(POIs))]
        a = [atk_fft[j][POIs[i]] for i in range(len(POIs))]
        
        # Test each key
        for k in range(256):
            # Find HW coming out of sbox
            HW = hw[sbox[atkPText[j][key_num] ^ k]]
        
            # Find p_{k,j}
            rv = multivariate_normal(meanMatrix[HW], covMatrix[HW], allow_singular=True)
            p_kj = rv.pdf(a)

            # Add it to running total
            P_k[k] += np.log(p_kj)
            #print P_k  
        # Print our top 5 results so far
        # Best match on the right
        print P_k.argsort()[-10:]
    
    #Answer
    fullkey.append(P_k.argsort()[-1]) 

    #check if the key is right
    if(fullkey[key_num] == atkKey[key_num]):
        key_right.append(1)
    else:
        key_right.append(0)    

#print result
print [hex(x)[2:4] for x in fullkey]
print key_right


