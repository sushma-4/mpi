# verifyio

## TODO

Functions need to be matched:

| Functions             | Status | Remark |
|-----------------------|--------|--------|
| MPI_File_open         |    Ready for review    |    Matched 3 args: comm, filename, amode    |
| MPI_File_close        |    Included            |    Matched the unique FH |      
| MPI_Comm_dup          |    Ready for review    |    Matched *new comm    |
| MPI_Cart_create       |    Ready for review    |    Matched *new cart    |
| MPI_Cart_sub          |    Ready for review    |    Matched *new comm   |
| MPI_Comm_split        |    Ready for review    |    Matched *new comm    |
| MPI_Comm_split_type   |    Ready for review    |    Matched *new comm    |
| MPI_File_write_at_all |    Included            |    Matched MPI_File, MPI_Offset |
| MPI_File_read_at_all  |    Included            |    Matched MPI_File, MPI_Offset  |
| POSIX                 |                        |    Ignore for now  |
| MPI_File_set_size     |    Included            |    Matched fh      |
| MPI_File_set_view     |    Included            |    Matched fh, etype and *datarep      |
| MPI_File_sync         |    Included            |    Matched fh      | 
| MPI_File_read_all     |    Included            |    Matched fh      |
| MPI_File_read_ordered |    Included            |    Matched fh      | 
| MPI_File_write_all    |    Included            |    Matched fh      |
| MPI_File_write_ordered|    Included            |    Matched fh      |


### Translate ranks from:
1. MPI_Comm_create - Included
2. MPI_Cart_sub - Included

Optimizations:
1. set the call name to None does not really delete it
2. When checking MPI_Wait for a specific MPI_I*, do not start from the begining, look after that MPI_I* call
3. Search for better graph layout strategy for visualization. 
4. Merge collective calls node in visualization 
