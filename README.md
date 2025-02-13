#cringe_test_system

This is a dataset of programming tasks with a testing system.

Setup:

download.py – downloads all tasks to your directory.

links.txt – contains URLs to ZIP archives with tasks.

script_processing.py – processes all tasks from a given directory and saves information (paths to important files) about them into a JSON file.

statistics.py – calculates some statistics about tasks, such as how many of them have statements.tex, solution.tex, and generates a distribution plot of the number of tests.

bench_script.py – converts all problems into JSON format (saves statement_text, solution_text, code_solution).

test_system.py – checks code_solution for a particular problem and returns the number of points it earned.
