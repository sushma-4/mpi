# Contains P2P calls with improved efficiency, i.e., the pointer approach

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

        if call == 'MPI_Send' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = int(record[i].args[3])
            temp.append(node(rank,index,call,args))
                    
        if call == 'MPI_Recv' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1        
            args = int(record[i].args[3])
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Ssend' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = int(record[i].args[3])
            temp.append(node(rank,index,call,args))

        if call == 'MPI_Sendrecv' and record[i].args[10] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [int(record[i].args[3]),int(record[i].args[8])]
            temp.append(node(rank,index,call,args))
        
        if call == 'MPI_Isend' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = int(record[i].args[3])
            temp.append(node(rank,index,call,args))
  
        if call == 'MPI_Irecv' and record[i].args[5] == 'MPI_COMM_WORLD':
            index = index + 1
            args = [int(record[i].args[3]),record[i].args[6]]
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

    nodes.append(temp)



ptr = []
for x in range(reader.GM.total_ranks):
    ptemp = []
    for y in range(reader.GM.total_ranks):
        ptemp.append(0)
    ptr.append(ptemp)


def getinfo():
    for i in range(len(nodes)):
        for n in nodes[i]:
            print n.rank, n.index
            print n.call
            print n.args
            print ('\n')


def find_recv(thisnode):
    global ptr
    h = (thisnode.rank, thisnode.index)
    frm = thisnode.rank
    if thisnode.call == 'MPI_Sendrecv':
        dest = thisnode.args[0]
    else:
        dest = thisnode.args
    for j in range(ptr[frm][dest],len(nodes[dest])):
        if nodes[dest][j].call == 'MPI_Recv' and nodes[dest][j].args == frm:
            t = (nodes[dest][j].rank, nodes[dest][j].index)        
            e = (h,t)
            edges.append(e)
            ptr[frm][dest] = j + 1
            return True
        
        if nodes[dest][j].call == 'MPI_Sendrecv' and nodes[dest][j].args[1] == frm:
            t = (nodes[dest][j].rank, nodes[dest][j].index)        
            e = (h,t)
            edges.append(e)
            ptr[frm][dest] = j + 1
            return True
        
        if nodes[dest][j].call == 'MPI_Irecv' and nodes[dest][j].args[0] == frm:
            #print nodes[dest][j].rank, nodes[dest][j].index
            ptr[frm][dest] = j + 1
            req = nodes[dest][j].args[1]
            for w in range(j,len(nodes[dest])):
                if nodes[dest][w].call == 'MPI_Wait' and nodes[dest][w].args == req:
                    t = (nodes[dest][w].rank, nodes[dest][w].index) 
                    e = (h,t)
                    edges.append(e)
                    nodes[dest][w].args.remove(req)
                    return True
                if nodes[dest][w].call == 'MPI_Waitall' and req in nodes[dest][w].args:
                    t = (nodes[dest][w].rank, nodes[dest][w].index) 
                    e = (h,t)
                    edges.append(e)
                    nodes[dest][w].args.remove(req)
                    return True 


for n in range(reader.GM.total_ranks):
    a = 0
    z = 0
    for thisnode in nodes[n]:
        if thisnode.call == 'MPI_Isend' or thisnode.call == 'MPI_Ssend' or thisnode.call == 'MPI_Send' or thisnode.call == 'MPI_Sendrecv':
            a = a + 1
            if(find_recv(thisnode)):
                z = z + 1
            else:
                print thisnode.rank, thisnode.index
                break          
   
    if z == a:
        print 'Sends from Rank', n, 'Successful'

#getinfo()






