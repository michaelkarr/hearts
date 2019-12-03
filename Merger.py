from collections import defaultdict
import pickle

class Merger():
    def mergeQ(filenames):
        q = defaultdict(int)
        count = defaultdict(int)
        qs = {}
        for filename in filenames:
            q_curr = pickle.load(open(filename,'rb'))
            for (s,a) in q_curr.keys():
                if count[(s,a)] > 0:
                    # Moving average over agents
                    update = q[(s,a)]*count[(s,a)] + q_curr[(s,a)] / (count[(s,a)]+1)
                    q[(s,a)] = update
                else:
                    q[(s,a)] = q_curr[(s,a)]
                count[(s,a)] += 1
        for filename in filenames:
            pickle.write(q, open(filename, 'wb'))
