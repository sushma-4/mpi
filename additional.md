############ THIS DOCUMENT WILL MAINTAIN SHORT CODE SNIPPETS THAT COULD BE USEFUL IN THE FUTURE  ##############


## REVERSE ENGINEERING APPPROACH

```
elif nodes[dest][j].call == 'MPI_Wait':
            if nodes[dest][j].args[1] == 0:
                for tempj in range(ptr[frm][dest], j):
                    temp_thisnode = nodes[dest][tempj]
                    if temp_thisnode.call == 'MPI_Irecv':
                        if temp_thisnode.args[2] == nodes[dest][j].args[0] and temp_thisnode.args[3] == 0 and temp_thisnode.args[0] == frm and temp_thisnode.args[1] == stag:
                            t = (nodes[dest][j].rank, nodes[dest][j].index) 
                            e = (h,t)
                            edges.append(e)
                            temp_thisnode.args[3] == 1 
                            nodes[dest][j].args[1] == 1
                            return True

elif nodes[dest][j].call == 'MPI_Waitall':
  for tempj in range(ptr[frm][dest], j):
      temp_thisnode = nodes[dest][tempj]
      if temp_thisnode.call == 'MPI_Irecv':
          if (temp_thisnode.args[2] in nodes[dest][j].args) and temp_thisnode.args[3] == 0 and temp_thisnode.args[0] == frm and temp_thisnode.args[1] == stag:
              t = (nodes[dest][j].rank, nodes[dest][j].index) 
              e = (h,t)
              edges.append(e)
              temp_thisnode.args[3] == 1 
              l = nodes[dest][j].args
              l.remove(temp_thisnode.args[2])
              return True
```

```
Instead of finding a matching Irecv, this will find a Wait that will have a corresponding Irecv call 
```
