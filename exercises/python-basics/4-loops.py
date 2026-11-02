"""Loops"""

"""While loop"""

# A while-loop is a control flow statement for specifying iteration, which allows code to be executed repeatedly.

# TODO: Write a while loop that prints break_condition and increments it, until it reaches 5

break_condition = 0

while break_condition < 10: 
    print(break_condition)
    break_condition +=1
else:
    print("break_condition is no longer less than 10")    

...

print("out of while loop")

# ----------------------------------------------

"""For loop"""

# For-loop is a control flow statement for specifying iteration, which allows code to be executed repeatedly.

# TODO: Iterate over pets, printing each one

pets = ["dog", "cat", "horse", "rabbit", "snake"]

for i in pets:
    print(i)


mylist = [34, 71]

for i in mylist:
    print(i - 23)

for i in range(4):
    print(i)    

    i didnt undertsand what range means in this context. Can you explain it to me?In Python, the `range()` function is used to generate a sequence of numbers. When you use `range(4)`, it generates a sequence of numbers starting from 0 up to (but not including) 4. So, `range(4)` will produce the numbers 0, 1, 2, and 3.
but what does it have to do with 34 and 71? In the code snippet you provided, the `range(4)` is not directly related to the list `mylist` containing 34 and 71. The `for i in range(4):` loop will simply iterate four times, with `i` taking on the values 0, 1, 2, and 3 during each iteration. 


