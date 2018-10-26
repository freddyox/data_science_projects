#! /usr/bin/python3

############################################################
#         Obrecht - 10/24/18
# Let's examine Old Faithful data in an attempt to
# guestimate/predict how much time will elapse
# until the next eruption
#
# The data can be grouped into two clusters, which is done
# using K-Means clustering, and effectively classifies
# the next eruption time into long or short. Therefore,
# if we observe a current eruption that lasts ~4.5 minutes,
# then we expect the next eruption to occur in
# 90 +/- 10 minutes, or so.

# Note that the data I am using is roughly 30 years old, and
# consequently the predictions most likely can be made better.

# Summary
# It really comes down to the eruption time; if it is <3 minutes
# or so, then we should expect a "short" wait time. On the other
# hand, if it is >3 minutes, we should expect a "long" wait time.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from sklearn.cluster import KMeans
import statistics

# I had multiple white-spaces in the data text file => simply do not
# specify the delimiter and python handles it correctly. 
id, erupt, wait = np.loadtxt('data.txt', dtype=None,
                             comments='#', unpack=True)

X = zip(erupt,wait)

# Let's try Kmeans
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

############################################################
# Plotting
fig = plt.figure(figsize=(14,8), dpi=80)
ax = fig.add_subplot(111)    # The big subplot
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

# Turn off axis lines and ticks of the big subplot
ax.spines['top'].set_color('none')
ax.spines['bottom'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['right'].set_color('none')
ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

ax1.set_xlabel("Eruption time (min)", fontsize=15)
ax1.set_ylabel("Waiting time for next eruption (min)", fontsize=15)
ax2.set_xlabel("Eruption time (min)", fontsize=15)
ax2.set_ylabel("Waiting time for next eruption (min)", fontsize=15)
ax1.set_xlim(1.0,6.0)
ax1.set_ylim(40.0,100.0)
ax2.set_xlim(1.0,6.0)
ax2.set_ylim(40.0,100.0)

# Make labels bigger
for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_xticklabels() + ax2.get_yticklabels():
    label.set_fontsize(14)

# Get the cluster assignment
classes=list(kmeans.labels_)
print(kmeans.cluster_centers_)
print(kmeans.n_iter_)
# Let's get x,y coordinates for each of the two clusters,
# create dict with ID as key
A = { i:(erupt[i],wait[i]) for i in range(len(erupt)) if classes[i]==0 }
B = { i:(erupt[i],wait[i]) for i in range(len(erupt)) if classes[i]==1 }

# Let's unpack it so I can plot them individually
# classA = list(A.values())  # get the x,y coordinate, which is a tuple
#Bx = [i[0] for i in classA] # get tuple first element, make a list
#By = [i[1] for i in classA] # get tuple 2nd element, make a list

# The above can be condensed using zip, so zip makes 2 lists, one
# for each element of the tuple, access it using unpacking method
Ax, Ay = zip(*list(A.values()))
Bx, By = zip(*list(B.values()))

# Calculate the averages of the data, comes out to be the same
# as the location of the cluster means, obviously.
Mu = ((sum(Ax)/len(Ax), sum(Ay)/len(Ay)),
      (sum(Bx)/len(Bx), sum(By)/len(By)))

print("<A>   = (%1.3f, %1.3f)" % (Mu[0][0], Mu[0][1]))
print("<B>   = (%1.3f, %1.3f)" % (Mu[1][0], Mu[1][1]))
print("A_sig = (%1.3f, %1.3f)" % (statistics.stdev(Ax),statistics.stdev(Ay)))
print("B_sig = (%1.3f, %1.3f)" % (statistics.stdev(Bx),statistics.stdev(By)))

# Plot everything in a canvas
ax1.scatter(erupt, wait, marker='s', color='black', s=20)
ax2.scatter(Ax, Ay, marker='o', color='red', s=20, label='Long')
ax2.scatter(Bx, By, marker='v', color='green', s=25, label='Short')
mux, muy = zip(*Mu)
ax2.scatter(mux,muy, marker='*', color='black', s=150, label='Means')

ax2.legend(loc='upper left', frameon=False, prop={'size':20})

plt.show()
