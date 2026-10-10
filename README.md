# Why is the milk always at the back of the supermarket?

*[Versión en español](README.es.md)*

A graph-theory study of a real supermarket: a survey of 100 people, a floor plan measured with a laser meter, and exact shortest shopping routes computed in Python.

![Supermarket floor plan](figures/floor_plan.png)

## Where this comes from

When I was a kid I noticed that the sweets were always at exactly my eye level. Years later I found out that wasn't a coincidence: supermarkets place products with a very clear idea of how we move around the store. One of the most repeated claims is that the essentials, like milk, eggs or fruit, are put at the back and far apart from each other, so you have to walk through the whole store and end up buying more on the way.

When I had to pick a topic for my Extended Essay in Mathematics (IB Diploma, Analysis and Approaches), I thought I could actually test this. I surveyed 100 people on how often they buy 29 different products. Then I asked the manager of a Carrefour near my home for permission to measure the store with a laser distance meter, aisle by aisle. With all that I built two graphs, one with the 7 most-bought products and one with the 7 least-bought, and found by hand the shortest route to pick them all up. The route for the most-bought products came out a lot longer.

## Why I came back to it

I really liked this project, but it had ended up as a PDF with graphs drawn by hand and calculations done table by table. I wanted to see how far I could take it if I did it properly. I was also curious to find out how AI could help me with something like this.

I rebuilt it in Python with the help of Claude, an AI assistant. The survey, the measurements, the question and the way the study is set up are mine and come from the essay. The AI helped me with the parts I found hardest or hadn't been able to do: rebuilding the floor plan to scale from my notes, writing and testing the code, finding mistakes in my calculations, and adding a test that wasn't in the original essay, the comparison with chance explained below.

Moving everything into code brought up a few mistakes in the essay. I list them further down. None of them changes the conclusion.

## What I did

First I turned every survey answer into purchases per month ("once a week" counts as 4, "twice a month" as 2, and so on down to "never", which is 0). Fruit comes out on top with 3.71 purchases a month and salt at the bottom with 0.47. I took the top 7 and the bottom 7. I left sugar out because it sits on the same shelf as the salt.

Then I turned the floor plan into a graph: every aisle crossing and every product is a node, and every stretch of aisle is an edge with its length in meters. Dijkstra's algorithm gives the walking distance between any two products.

The route that leaves the entrance, visits the 7 products and comes back to the checkout is a shortest Hamiltonian cycle, which is the well-known traveling salesman problem. In the essay I solved it with the nearest-neighbor algorithm, which gives a good answer but doesn't guarantee the best one. Now I solve it exactly with the Held-Karp algorithm, and a test checks that it gives the same result as trying all 5,040 possible orders.

The last part is my favorite. In the essay I only compared one group with the other, and that doesn't prove much. Now I compute the shortest route for all 3,432 groups of 7 products that can be formed from the 14 I measured. That way I can see whether the most-bought products are more spread out than you would get by pure chance.

## What I found

![Shortest routes](figures/routes.png)

The route through the 7 most-bought products is 181.0 m long, and the one through the 7 least-bought is 113.0 m. That's 60% longer.

![All possible groups](figures/all_groups.png)

Out of the 3,432 possible groups, only 69 others (2%) make you walk as far as the most-bought products or further. And only 7 others have a route as short as the least-bought products, or shorter.

There's one thing I hadn't noticed in the essay. Almost any group of 7 products gives a long route, because it nearly always includes something from the back of the store: the median is 167 m. So the most striking result isn't so much that the most-bought products are far away, but that the least-bought ones are all grouped together near the entrance.

![Shortest-distance graphs](figures/graphs.png)

These are the two graphs from the essay, with the distances recomputed on the floor plan. I was glad to see that my nearest-neighbor solution had actually found the optimal route in both cases, even though my explanation of why it worked wasn't right.

## Mistakes I found in the essay

- I wrote that the route was 163% longer. It's 63%: I mixed up "1.63 times as long" with "163% longer".
- I worked out the distance from the entrance to the milk and to the butcher counter through the left aisle, but the center aisle is shorter (58.9 and 67.3 m instead of 62.1 and 70.5). That's why the most-bought route drops from 184.2 to 181.0 m. The least-bought route stays at 113 m, the same as in the essay.
- I copied the ice cream to organic food distance wrong: I wrote 21.8 m, which is actually ice cream to salt. The right one is 27.2 m.
- From yogurt to milk I wrote 20.4 m, but going past the eggs it's 18.0 m.
- I said that nearest neighbor always gives the shortest cycle because it picks the closest product at every step. That isn't true in general, which is why I now compute the exact optimum.
- In the survey spreadsheet I typed 0.0162 where it should have been 0.162 (for cereal). It doesn't change anything in the result.

The other 22 distances I calculated by hand match the floor plan to the decimeter, and there's a test that checks it.

## What this study doesn't prove

It's a single supermarket, so I can't say they all do the same. The survey was answered by people around me, not by a representative sample. I didn't measure the distance from the entrance to the center aisle; I inferred it from my own calculations. If you can only enter through the left aisle, the routes are 187.4 and 116.2 m and the conclusion doesn't change. And while the most-bought products being far away fits the idea of a sales strategy, there could be other reasons too, like where the cold rooms or the loading area are.

## Running it

```bash
pip install -r requirements.txt
python main.py          # prints the results and regenerates the figures
python -m pytest        # checks that the code reproduces the essay
```

The data is in `data/`, the code in `src/`, the tests in `tests/` and the figures in `figures/`.
