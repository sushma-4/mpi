import sys
from creader_wrapper import RecorderReader

reader = RecorderReader(sys.argv[1])
func_list = reader.funcs

nodes = []
edges = []


############################
#         MAIN             #
############################
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

        if call == 'MPI_Send' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))
                    
        if call == 'MPI_Recv' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1        
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Ssend' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))

        if call == 'MPI_Sendrecv' and record[i].args[10] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), int(record[i].args[8]), int(record[i].args[9]), record[i].args[10]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Isend' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [int(record[i].args[3]), int(record[i].args[4]), record[i].args[5]]
            temp.append(node(rank,index,call,args))
  
        if call == 'MPI_Irecv' and record[i].args[5] == 'MPI_COMM_WORLD':
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

        if call == 'MPI_Bcast' and record[i].args[4] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [int(record[i].args[3]), record[i].args[4]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Reduce' and record[i].args[6] == 'MPI_COMM_WORLD':
            index = index + 1
            args =  [int(record[i].args[5]), record[i].args[6]]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Gather' and record[i].args[7] == 'MPI_COMM_WORLD':
            index = index + 1
            args =  [int(record[i].args[6]), record[i].args[7]]
            temp.append(node(rank,index,call,args)) 

        if call == 'MPI_Gatherv' and record[i].args[8] == 'MPI_COMM_WORLD':
            index = index + 1
            args =  [int(record[i].args[7]), record[i].args[8]]
            temp.append(node(rank,index,call,args))         
        
        if call == 'MPI_Barrier' and  record[i].args[0] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [record[i].args[0]]
            temp.append(node(rank,index,call,args))

        if call == 'MPI_Allreduce' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [record[i].args[5]]
            temp.append(node(rank,index,call,args)) 
                    
        if call == 'MPI_Allgatherv' and record[i].args[7] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [record[i].args[7]]
            temp.append(node(rank,index,call,args))         
        
    nodes.append(temp)


def getinfo():
    for i in range(len(nodes)):
        for n in nodes[i]:
            print n.rank, n.index
            print n.call
            print n.args
            print ('\n')


#####################  DEFINING FUNCTIONS TO MATCH CALLS #########################


ptr = []
for x in range(reader.GM.total_ranks):
    ptemp = []
    for y in range(reader.GM.total_ranks):
        ptemp.append(0)
    ptr.append(ptemp)


def match_collectives(thisnode):
    x = (thisnode.rank, thisnode.index)
    h = t = []
    h.append(x)

    global ptr
    name = thisnode.call
    r = range(reader.GM.total_ranks)
    r.remove(0)
    for dest in r:
        for j in range(ptr[0][dest],len(nodes[dest])):
            if nodes[dest][j].call == name:
                x = (nodes[dest][j].rank, nodes[dest][j].index)
                h.append(x)
                ptr[0][dest] = j + 1
                break

    e = (h,t)
    edges.append(e)
    
    if len(t) == len(r)+1:
        return True    


def match_redgat(thisnode):
    global ptr
    t = (thisnode.rank, thisnode.index)
    h = []
    name = thisnode.call
    root = thisnode.rank
    r = range(reader.GM.total_ranks)
    r.remove(root)
    for dest in r:
        for j in range(ptr[root][dest],len(nodes[dest])):
            if nodes[dest][j].call == name and nodes[dest][j].args[0] == root:
                x = (nodes[dest][j].rank, nodes[dest][j].index)
                h.append(x)
                ptr[root][dest] = j + 1
                break

    e = (h,t)
    edges.append(e)
    
    if len(h) == len(r):
        return True
    

def match_bcast(thisnode):
    global ptr
    h = (thisnode.rank, thisnode.index)
    t = []
    root = thisnode.rank
    r = range(reader.GM.total_ranks)
    r.remove(root)
    for dest in r:
        for j in range(ptr[root][dest],len(nodes[dest])):
            if nodes[dest][j].call == 'MPI_Bcast' and nodes[dest][j].args[0] == root:
                x = (nodes[dest][j].rank, nodes[dest][j].index)
                t.append(x)
                ptr[root][dest] = j + 1
                break

    e = (h,t)
    edges.append(e)
    
    if len(t) == len(r):
        return True


def find_recv(thisnode):
    global ptr
    h = (thisnode.rank, thisnode.index)
    frm = thisnode.rank
    if thisnode.call == 'MPI_Sendrecv':
        dest = thisnode.args[0]
        stag = thisnode.args[1]
    else:
        dest = thisnode.args[0]
        stag = thisnode.args[1]

    for j in range(ptr[frm][dest],len(nodes[dest])):
        if nodes[dest][j].call == 'MPI_Recv' and nodes[dest][j].args[0] == frm:
            ptr[frm][dest] = j 
            if nodes[dest][j].args[1] == stag:
                t = (nodes[dest][j].rank, nodes[dest][j].index)        
                e = (h,t)
                edges.append(e)
                nodes[dest][j].call = None
                return True
        
        elif nodes[dest][j].call == 'MPI_Sendrecv' and nodes[dest][j].args[2] == frm:
            ptr[frm][dest] = j 
            if nodes[dest][j].args[3] == stag:
                t = (nodes[dest][j].rank, nodes[dest][j].index)        
                e = (h,t)
                edges.append(e)
                nodes[dest][j].args[2] = None
                return True

        elif nodes[dest][j].call == 'MPI_Irecv' and nodes[dest][j].args[0] == frm:
            ptr[frm][dest] = j
            if nodes[dest][j].args[1] == stag:
                nodes[dest][j].call = None
                req = nodes[dest][j].args[2]
                for w in range(j,len(nodes[dest])):
                    if nodes[dest][w].call == 'MPI_Wait' and nodes[dest][w].args == req:
                        t = (nodes[dest][w].rank, nodes[dest][w].index) 
                        e = (h,t)
                        edges.append(e)
                        nodes[dest][w].args.remove(req)
                        return True
                    elif nodes[dest][w].call == 'MPI_Waitall' and (req in nodes[dest][w].args):
                        t = (nodes[dest][w].rank, nodes[dest][w].index) 
                        e = (h,t)
                        edges.append(e)
                        nodes[dest][w].args.remove(req)
                        return True   


#############################  INTERATE EVERY NODE IN THE LIST AND FIND A MATCH ################################

for n in range(reader.GM.total_ranks):
    a = 0
    z = 0
    for thisnode in nodes[n]:
        
        if thisnode.call in ['MPI_Send','MPI_Ssend','MPI_Isend','MPI_Sendrecv']:
            a = a + 1
            if(find_recv(thisnode)):
                z = z + 1
             
        if thisnode.call == 'MPI_Bcast': 
            root = thisnode.args[0]
            if root == n:
                a = a + 1
                if(match_bcast(thisnode)):
                    z = z + 1
        
        if thisnode.call in ['MPI_Reduce','MPI_Gather','MPI_Gatherv']: 
            root = thisnode.args[0]
            if root == n:
                a = a + 1
                if(match_redgat(thisnode)):
                    z = z + 1

        if thisnode.call in ['MPI_Barrier', 'MPI_Allreduce', 'MPI_Allgatherv']:
            if n == 0:
                a = a + 1
                if(match_collectives(thisnode)):
                    z = z + 1
        

    print a, z
    if z == a:
        print 'Calls from Rank', n, 'Successful'

    else:
        print 'Something went wrong'
