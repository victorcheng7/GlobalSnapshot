# Format of directory:
---

  In here stays the different test suite we have for this project. 
  Each test suite is a directory called test[i] where i is a unique id number (e.g. test1 test2 etc.).
  The format of each test suite is provided below

---
# Format of the files in test suite:
---
  * setup file: Just call it setup
  * input file: [x].in where x is a unqiue postive for the process
  * expected output file: [x].exp where x is a unique positive integer matching with the input file
  	* If there are many possible result, separate them with a "or" preceding and following by a newline character ("\n")
  * output file: [x].out where x is a unique postive integer matching with the input file
    * This is where the program stdout on each process goes into.
  * debug file: [x].debug where x is a unique positive integer matching with the input file
    * This file is the debug log of each process. Used to understand how each process behave
