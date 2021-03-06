# Split Expenses With Ford-Fulkerson

## Background
You are Dan. You live in an appartment with 3 roommates. Alice is paying the electricity bill, Bob is paying the water bill, 
Carol is paying for the new lights in your balcony and you just went and got groceries for dinner.</br>
The end of the month is here and you want everyone to pay equally so everything will be fair. Unfortunately not everybody paid the same 
amount and it could be pretty annoying to calculate how much someone needs to pay to somebody else. Worry not! This is why this app is for! We will
split the expenses equally, and in a pretty cool way. Check out how it is done.

## How Do You Split the Expenses?
Great question. In the big picture we build a graph where each node is a person and each edge is the amount he needs to pay/get. Then apply the 
Ford-Fulkerson algorithm to find the max flow and the way that money flows through the graph. And that's it.</br>
Are you ready to dive to the small picture? Here we go.</br>
So how to build the graph exactly? Let's explain that with an example. So let's assume Alice paid 50$, Bob paid 30$, Carol 15$ and Dan paid 5$.
So in order to build the graph we need to:</br>
1. Calculate the total amount paid.</br>
Amount = 50 + 30 + 15 + 5 = 100

2. Calculate how much money each person should have paid.</br>
DuePerPerson = Amount / #people = 100 / 4 = 25

3. Calculate the difference between the amount paid by each person and the DuePerPerson.</br>
diff(Alice) = 50 - 25 = 25</br>
diff(Bob) = 30 - 25 = 5</br>
diff(Carol) = 15 - 25 = -10</br>
diff(Dan) = 5 - 25 = -20</br>

4. Create a node in the graph for each person.

5. Create an edge with infinte capacity that connects each person to the other people in the graph.

6. for each diff calculated (at stage 3), if the value is negative, it means the person still needs to reimburse someone: we add an inward
edge to the person with the capacity equall to diff (absolute value of diff). This represents an inward flow of money into the network. Else,
we create an outward edge with capacity equal to diff. This will represent the outward flow of money from the graph. That way we make sure
each person pays the right amount.

7. Applying the Ford-Fulkerson algorithm will result in multiple paths that represent the flow of money from one person to another, 
which is equivalent to dividing the expenses equally between everybody.</br>
But (!), the Ford-Fulkerson algorithm works with one source node and one sink node, and here we may have more than one person who owes money
(multiple sources), and more than one person who needs to get money back (multiple sinks). In order to solve that we create one big source that connects
to all the small original sources (people who owe money), and similarly we create one big sink that connects to all other small sinks 
(people who need to get money back).

And the results are pretty cool:

<img src="/graph_example.png" width="100%" alt="graph flow example">

Alice gets 15$ from Dan and 10$ from Carol, Bob gets 5$ from Dan.</br>
Nice!


 
