######### Matching across multicommunicators (without Pointer Approach) ##########

import time
#start_time = time.time()

import sys
from creader_wrapper import RecorderReader

reader = RecorderReader(sys.argv[1])
func_list = reader.funcs

nodes = []
edges = []


splits = []    #Contain MPI_Comm_Split nodes from traces
uids = []      #List of all unique ids

############################
#         MAIN             #
############################

class com_node:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class node:
    def __init__(self, rank, index, call, args):
        self.rank = rank
        self.index = index
        self.call = call
        self.args = args

for rank in range(reader.GM.total_ranks):
    index = -1
    temp = []
    record = reader.records[rank]
    
    for i in range(reader.LMs[rank].total_records):
        call = func_list[record[i].func_id]
        
        ## Point-to-Point calls

        if call == 'MPI_Send':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))
                    
        if call == 'MPI_Recv':
            index = index + 1        
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Ssend':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))

        if call == 'MPI_Sendrecv':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), int(record[i].args[8]), int(record[i].args[9]), record[i].args[10]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Isend':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))
  
        if call == 'MPI_Irecv':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[6], record[i].args[5]]
            temp.append(node(rank,index,call,args))

        if call == 'MPI_Wait':
            index = index + 1
            args = record[i].args[0]
            temp.append(node(rank,index,call,args))
            
        if call == 'MPI_Waitall':
            index = index + 1
            args = record[i].args[1]
            args = args[1:-1]
            args = args.split(',')
            temp.append(node(rank,index,call,args))        

        ## Collective calls
        
        if call == 'MPI_Bcast':
            index = index + 1
            args = [int(record[i].args[3]), record[i].args[4]]
            temp.append(node(rank,index,call,args))

        if call == 'MPI_Ibcast':
            index = index + 1
            args = [int(record[i].args[3]), record[i].args[5], record[i].args[4]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Reduce':
            index = index + 1
            args =  [int(record[i].args[5]), record[i].args[6]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Gather':
            index = index + 1
            args =  [int(record[i].args[6]), record[i].args[7]]
            temp.append(node(rank,index,call,args)) 

        if call == 'MPI_Gatherv':
            index = index + 1
            args =  [int(record[i].args[7]), record[i].args[8]]
            temp.append(node(rank,index,call,args))         
        
        if call == 'MPI_Barrier':
            index = index + 1
            args = [record[i].args[0]]
            temp.append(node(rank,index,call,args))

        if call == 'MPI_Allreduce':
            index = index + 1
            args = [record[i].args[5]]
            temp.append(node(rank,index,call,args)) 
                    
        if call == 'MPI_Allgatherv':
            index = index + 1
            args = [record[i].args[7]]
            temp.append(node(rank,index,call,args))  

        if call == 'MPI_Comm_split':
            uid = record[i].args[3]
            args = [rank,int(record[i].args[2])]
            splits.append(com_node(uid,args))
            if uid not in uids:
                uids.append(uid)   
        
        if call == 'MPI_Comm_dup':
            uid = record[i].args[1]
            args = [rank,rank]
            splits.append(com_node(uid,args))
            if uid not in uids:
                uids.append(uid)
                    
    nodes.append(temp)


def getinfo():
    for i in range(len(nodes)):
        for n in nodes[i]:
            print n.rank, n.index
            print n.call
            print n.args
            print ('\n')


#####################  DEFINING FUNCTIONS TO MATCH CALLS #########################
 
def match_collectives(thisnode, eachcom):
    x = (thisnode.rank, thisnode.index)
    h = t = []
    h.append(x)
    name = thisnode.call
    r = range(len(eachcom))
    r.remove(0)
    for dest in r:
        for n in eachcom[dest]:
            if n.call == name:
                x = (n.rank, n.index)
                h.append(x)
                n.call = None
                break

    e = (h,t)
    edges.append(e)
    
    if len(t) == len(r)+1:
        #print e
        return True    

def match_redgat(thisnode, eachcom):
    t = (thisnode.rank, thisnode.index)
    h = []
    name = thisnode.call
    root = thisnode.args[0]
    r = range(len(eachcom))
    r.remove(root)
    for dest in r:
        for n in eachcom[dest]:
            if n.call == name and n.args[0] == root:
                x = (n.rank, n.index)
                h.append(x)
                n.call = None
                break

    e = (h,t)
    edges.append(e)
    
    if len(h) == len(r):
        #print e
        return True

def match_bcast(thisnode, eachcom):
    h = (thisnode.rank, thisnode.index)
    t = []
    root = thisnode.args[0]
    r = range(len(eachcom))
    r.remove(root)
    for dest in r:
        for n in eachcom[dest]:
            if n.call == 'MPI_Bcast' and n.args[0] == root:
                x = (n.rank, n.index)
                t.append(x)
                n.call = None
                break
            elif n.call == 'MPI_Ibcast' and n.args[0] == root:
                n.call = None
                req = n.args[1]
                destg = translate[thisnode.args[-1]][dest]
                for w in nodes[destg]:
                    if w.call == 'MPI_Wait' and w.args == req:
                        x = (w.rank, w.index) 
                        t.append(x)
                        w.call = None
                        #print e
                        break
                    elif w.call == 'MPI_Waitall' and (req in w.args):
                        x = (w.rank,w.index)
                        t.append(x) 
                        w.args.remove(req)
                        #print e
                        break
                

    e = (h,t)
    edges.append(e)
    
    if len(t) == len(r):
        #print e
        return True

def find_recv(thisnode, eachcom):
    h = (thisnode.rank, thisnode.index)
    frm = translate[thisnode.args[-1]].index(thisnode.rank)
    dest = thisnode.args[0]
    destg = translate[thisnode.args[-1]][dest]
    stag = thisnode.args[1]

    for n in eachcom[dest]:
        if n.call == 'MPI_Recv' and (n.args[0] == frm or n.args[0] == -2) and (n.args[1] == stag or n.args[1] == -1):
            t = (n.rank, n.index)        
            e = (h,t)
            edges.append(e)
            n.call = None
            #print e
            return True
        
        elif n.call == 'MPI_Sendrecv' and (n.args[2] == frm or n.args[2] == -2) and (n.args[3] == stag or n.args[3] == -1):
            t = (n.rank, n.index)        
            e = (h,t)
            edges.append(e)
            n.args[2] = None
            #print e
            return True

        elif n.call == 'MPI_Irecv' and (n.args[0] == frm or n.args[0] == -2) and (n.args[1] == stag or n.args[1] == -1):
            n.call = None
            req = n.args[2]
            for w in nodes[destg]:
                if w.call == 'MPI_Wait' and w.args == req:
                    t = (w.rank, w.index) 
                    e = (h,t)
                    edges.append(e)
                    w.call = None
                    #print e
                    return True
                elif w.call == 'MPI_Waitall' and (req in w.args):
                    t = (w.rank,w.index) 
                    e = (h,t)
                    edges.append(e)
                    w.args.remove(req)
                    #print e
                    return True   

############## TRANSLATING RANKS ####################
agr =  {}
translate = {}

for u in uids:
    temp = []
    for node in splits:
        if node.name == u:
            temp.append(node.args)
    agr[u] = temp

for key, value in agr.items(): 
    a = []
    value.sort(key = lambda x: x[1]) 
    for v in value:
        a.append(v[0])        
    translate[key] = a

translate['MPI_COMM_WORLD'] = range(reader.GM.total_ranks)

'''
for key, value in translate.items():
    print key
    print value
    print '\n'
'''
################### SPLITTING THE DATABASE INTO EACH COMMUNICATOR ###################

coms3d = []

uids.insert(0, 'MPI_COMM_WORLD')
#print len(uids)

for u in uids:
    #print u
    thiscom = []
    ranks_in_this_com = translate[u]

    #print ranks_in_this_com
    for r in ranks_in_this_com:
        temp = []
        for thisnode in nodes[r]:
            if thisnode.args[-1] == u:
                temp.append(thisnode)
        thiscom.append(temp)
    #print len(thiscom)
    coms3d.append(thiscom)
    
    #print "\n"

    '''
    for n in range(reader.GM.total_ranks):
        temp = []
        for thisnode in nodes[n]:
            if thisnode.args[-1] == u:
                temp.append(thisnode)
        thiscom.insert(n, temp)
    coms3d.append(thiscom)
    
    e =  0
    print u
    for f in thiscom:
        e = e + len(f)
    print e
    '''
    
'''
l = 0
for n in nodes:
    l = l + len(n)
print l
'''

#############################  INTERATE EVERY NODE IN THE LIST AND FIND A MATCH ################################
c = -1

for eachcom in coms3d:
    
    c = c + 1
    print 'Processing communicator', uids[c]
    #print 'Translation table: ', translate[uids[c]]
    #print len(eachcom)

    #print '\n'

    ptr = []
    for x in range(len(eachcom)):
        ptemp = []
        for y in range(len(eachcom)):
            ptemp.append(0)
        ptr.append(ptemp)
    
    a = 0 
    z = 0
    for n in range(len(eachcom)):
               
        for thisnode in eachcom[n]:
            if thisnode.call in ['MPI_Bcast', 'MPI_Ibcast']: 
                root = thisnode.args[0]
                if root == n:
                    a = a + 1
                    if(match_bcast(thisnode,eachcom)):
                       z = z + 1
            
            if thisnode.call in ['MPI_Reduce','MPI_Gather','MPI_Gatherv']: 
                root = thisnode.args[0]
                if root == n:
                    #print thisnode.call
                    a = a + 1
                    if(match_redgat(thisnode,eachcom)):
                        z = z + 1
    
            if thisnode.call in ['MPI_Barrier', 'MPI_Allreduce', 'MPI_Allgatherv']:
                if n == 0:
                    a = a + 1
                    if(match_collectives(thisnode,eachcom)):
                        z = z + 1  
            
            if thisnode.call in ['MPI_Send','MPI_Ssend','MPI_Isend','MPI_Sendrecv']:
                a = a + 1
                if (find_recv(thisnode, eachcom)):
                    z = z + 1
                    
        #if a == z:
            #print a ,'\t', z, '\t Calls from', n, 'successful'
    print a, z
    print '\n'

    
#print("--- %s seconds ---" % (time.time() - start_time))
