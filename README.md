# MPI-x-Multiprocessing
In this project, I set out to compare two parallel computing approaches in Python—`multiprocessing` and `mpi4py`—by implementing a numerical integration of the sine function over the interval \[0, π] using the Riemann sum method with a substantial number of subdivisions (N = 1e9). The primary goal was to assess performance differences and evaluate the ease of implementation between these two methods.

**Implementation Overview**

The code is designed to detect the availability of an MPI environment. If MPI is available, it executes the integration using `mpi4py`; otherwise, it defaults to using Python's `multiprocessing` module.

* **MPI (`mpi4py`) Approach**: Each MPI process computes a portion of the Riemann sum independently. The partial results are then aggregated using `comm.reduce` with the `MPI.SUM` operation. Timing is measured using `MPI.Wtime()`, and the results are recorded in a file named `time_mpi.txt`.

* **Multiprocessing Approach**: The integration interval is divided into chunks, each assigned to a separate process managed by Python's `Pool`. Each process computes its assigned portion of the sum, and the results are combined. Execution time is measured using `time.time()`, with outcomes saved in `time_mp.txt`.

After execution, if both timing files are present, the script generates a plot (`comparison_1e9.png`) comparing the runtime performance of both approaches across varying numbers of processes.

**Performance Comparison**

Empirical results indicate that the `mpi4py` implementation outperforms the `multiprocessing` approach, particularly as the number of processes increases. This performance gain is attributed to MPI's efficient inter-process communication and its ability to operate across multiple nodes in a distributed system. In contrast, `multiprocessing` is confined to a single machine's resources, limiting its scalability.

Furthermore, `mpi4py` leverages direct memory access patterns and optimized communication protocols, leading to reduced overhead and faster execution times compared to the shared-memory model of `multiprocessing`.

**Ease of Use**

From a development standpoint, `multiprocessing` offers a more straightforward and Pythonic interface, making it accessible for those new to parallel programming. It integrates seamlessly with Python's standard library and requires minimal setup.

On the other hand, `mpi4py` introduces additional complexity, such as the need to manage MPI environments and understand concepts like ranks and communicators. However, for applications that demand high performance and scalability across distributed systems, the initial learning curve is justified by the significant performance benefits.

**Conclusion**

In summary, while `multiprocessing` is suitable for simple, shared-memory parallel tasks on a single machine, `mpi4py` is the preferred choice for high-performance computing tasks that require scalability and efficient communication across multiple nodes. The choice between the two should be guided by the specific requirements of the application and the available computing resources.
