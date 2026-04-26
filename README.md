# Algorithms for Computational Logic First Project

This repository holds my solution for the first project of the Algorithms for Computational Logic course at Instituto Superior Técnico. Its main goal was to build a tool that could sole the Nurse Scheduling Problem, whose main problem was to build a schedule for the nurses operating in a hospital/clinic that covered all work shifts that span 24 hours per day.

The problem also had the following restriction to make it more challenging:

- Every day had the same number of shifts, and all the shifts took the same amount of time (e.g. if every day had four shift, each shift took six hours). Every shift had a minimum amount of necessary nurses assigned to be operational;
- Some nurses have managerial qualifications. Each shift must have at least one of those nurses assigned;
- The workload of each nurse of each day of the schedule must be continuous, that is, it should not have any breaks between its assigned shifts;
- During each day, each nurse has a minimum and maximum amount of shifts it can be assigned to;
- Each nurse also has a maximum amount of shifts it can be assigned to throughout all days of the schedule;
- Each nurse has unavailability periods. No nurse can be assigned to a shift in its unavailability period;
- Each nurse wrote down a preference value to each of the shifts. Each of the values expresses the cost of assigning that nurse to a shift. The goal, is to minimize the cost in order to maximize the nurses' preferences.

To solve this problem I built a Python tool that uses a MaxSAT solver by encoding the problem's restrictions and feeding them to the solver. Further details about the solution can be checked in the [report](./report.pdf).

## Running the tool

pip install -r requirements.txt

./proj1 < input > output
