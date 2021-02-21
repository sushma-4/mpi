#include <omp.h> 
#include <stdio.h> 
#include <stdlib.h> 

int main(int argc, char* argv[]) 
{ 
	int k = 0;
	float x = 999999.0;
	int i, j, n = 5;
	
	int C[5] = {1,2,3,4,5};
	int D[5] = {1,2,3,4,5};

	int threadnum, numthreads, myfirst, mylast;

	#pragma omp parallel private(i,j,k,threadnum,myfirst,mylast), reduction(min:x)
	{
		int threadnum = omp_get_thread_num(), numthreads = omp_get_num_threads();
	
  		int myfirst = n*threadnum/numthreads, mylast = n*(threadnum+1)/numthreads;
		//printf("This thread: %d, %d \t", myfirst, mylast);
		
		for (i = myfirst; i < mylast; i++) {
			k = (i+1)*4;
			for (j = k; j < n; j++) {
					C[i] += D[j] * 3;
				}
			if (C[i] < x) {
				x = C[i];
				// printf("%f\n", x);
			}
			//printf("This threadinfo i = %d, k = %d, x = %f \n", i,k,x);
			//if (i == n-1) {xx = x;}
		}
		
	}	

	printf("i = %d, j = %d, k = %d, x = %f\n", i, j, k, x);	
	//printf("%d %d \n", C[0], C[1]);
} 

/*
Begin of parallel region 
	#pragma omp parallel private(nthreads, tid) 
	{ 
		// Getting thread number 
		tid = omp_get_thread_num(); 
		printf("Welcome to GFG from thread = %d\n", 
			tid); 

		if (tid == 0) { 

			// Only master thread does this 
			nthreads = omp_get_num_threads(); 
			printf("Number of threads = %d\n", 
				nthreads); 
		} 
	} 
*/