# cringe_test_system
This is dataset of programming tasks with testing system.

SetUp:
download.py - downloads all tasks to your derictory
links.txt - urls to zip tasks
scrypt_processing.py - processes all task from given derictory and saves information (paths to important files) about them into json
statics.py - calculate some statistics about tasks like how many of them have statements.tex, solution.tex, distribution plot of amount of tests
bench_scrypt.py - converts all problems into json (saves statement_text, solution_text, code_solution)
test_system.py - checks code_solution on particular problem and returns how many points did it earn.
