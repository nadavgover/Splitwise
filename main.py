import pandas as pd  # for graph visualization
import networkx as nx  # for graph visualization
import matplotlib.pyplot as plt  # for graph visualization


from data_structures import Queue

class Node(object):
    def __init__(self, name, debt, flow=None, children=None, residual_capacity=None):
        self.name = name
        self.children = children
        self.capacity = debt  # The capacity will be the absolute value of the debt
        self.flow = flow
        self.parent = None  # for BFS
        self.visited = False  # for BFS
        self.residual_capacity = residual_capacity  # for BFS
        self.flow_log = {}  # format: {to: amount}, this will tell us how much each person owes who

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class SplitIt(object):
    """An application to split expenses equally between friends.
    Uses Ford-Fulkerson algorithm (to be exact it's Edmonds-Karp)"""
    def __init__(self):
        self.nodes = self._get_nodes()
        self.source = None
        self.sink = None
        self._make_graph()

    def _make_graph(self):
        """Makes a graph out of the node
        Returns the source and the sink of the graph"""

        sources = self._find_source_nodes()
        sinks = self._find_sink_nodes()

        # Make the source
        if not sources:
            raise ValueError("Nobody owes money, everything is settled up.\n"
                  "Or there was a mistake in inputting the amount of money each one owes")

        source = self._make_big_source(sources=sources)

        # Make the sink
        if not sinks:
            raise ValueError("Nobody deserves to get anymore money, everything is settled up.\n"
                  "Or there was a mistake in inputting the amount of money each one owes")
        sink = self._make_big_sink(sinks=sinks)

        # Connect all the nodes to each other with infinite capacity and zero flow
        self._initialize_graph()

        # Add the source and the sink to the graph
        self.nodes.extend([source, sink])
        self.source = source
        self.sink = sink

    def _initialize_graph(self):
        """Connects all the nodes to each other with infinite capacity and zero flow"""
        for node in self.nodes:
            for other_node in self.nodes:
                if node != other_node:
                    if node.children is None:
                        node.children = []
                    if node.flow is None:
                        node.flow = 0
                    if node.residual_capacity is None:
                        node.residual_capacity = float("inf")
                    node.children.append(other_node)

    def _find_source_nodes(self):
        """Finds the source nodes of the graph (there might be more than one).
        Input: Node list
        Output: Node list which are sources of the graph (which owe money)
        If the debt is negative it means the person owes money and is inward flow to the network"""
        return [node for node in self.nodes if node.capacity < 0]

    def _make_big_source(self, sources):
        """Joins all the sources to one big source.
        Since the max-flow algorithm works on one source, we need to join all the small sources into one.
        The big source will be considered as the source of the graph."""

        # source is the only node allowed to have more than one capacity and flow
        big_source = Node(name="source", children=sources,
                          debt=[abs(source.capacity) for source in sources],
                          flow=[0 for _ in sources],
                          residual_capacity=[abs(source.capacity) for source in sources])


        # Adding the big source as a parent of all the other small sources
        for source in sources:
            source.capacity = float("inf")  # initializing all the sources to now be with infinite capacity
            source.residual_capacity = float("inf")
        return big_source

    def _find_sink_nodes(self):
        """Finds the sink nodes of the graph (there might be more than one).
        Input: Node list
        Output: Node list which are sinks of the graph (which need to get back money)
        If the debt is positive it means the person needs to get back money and is outward flow of the network"""
        return [node for node in self.nodes if node.capacity > 0]

    def _make_big_sink(self, sinks):
        """Joins all the sinks to one big sink.
        Since the max-flow algorithm works on one sink, we need to join all the small sinks into one.
        The big sink will be considered as the sink of the graph."""

        big_sink = Node(name="sink", children=None,
                        debt=float("inf"), flow=0, residual_capacity=float("inf"))

        for sink in sinks:
            sink.children = [big_sink]
            # sink.capacity = float("inf")
            sink.residual_capacity = sink.capacity
            sink.flow = 0
        return big_sink

    def _BFS(self, source=None, sink=None, nodes=None):
        """Breadth first search (BFS).
        Finds a path between source and sink and returns it. If no path is found returns false"""

        if source is None:
            source = self.source
        if sink is None:
            sink = self.sink
        if nodes is None:
            nodes = self.nodes

        for node in nodes:
            node.visited = False

        q = Queue()
        q.enqueue(source)
        source.visited = True
        while not q.is_empty():
            current_node = q.dequeue()
            children = current_node.children
            for i in range(len(children)):
                child = children[i]
                if current_node.name.lower() == "source":
                    residual_capacity = current_node.residual_capacity[i]
                else:
                    residual_capacity = child.residual_capacity
                if child.name == sink.name:
                    return self._extract_path_from_bfs(current_node, source, sink)
                if not child.visited and residual_capacity > 0:
                    child.visited = True
                    child.parent = current_node
                    q.enqueue(child)

        return False  # no path found

    def _extract_path_from_bfs(self, node, source, sink):
        """Returns the trace from source to sink
        Goes up the graph until it finds the source"""

        path = [sink]
        while node.parent is not None:  # node.parent is None iff Node is the source of the graph
            path.append(node)
            node = node.parent
        path.append(source)
        path.reverse()
        return path

    def _edmonds_karp(self):
        """Finds the max-flow of the graph"""
        max_flow = 0
        path = self._BFS(source=self.source, sink=self.sink)
        while path:  # while there is a path in the residual graph between the source and the sink
            min_residual_capacity = self._find_min_residual_capacity_in_path(path)
            max_flow += min_residual_capacity
            self._send_flow_along_path(path, min_residual_capacity)
            path = self._BFS(source=self.source, sink=self.sink)
        return max_flow  # Currently this value is unused but it is nice to have since this is the core of the algorithm

    def _find_min_residual_capacity_in_path(self, path):
        """Finds the minimum residual capacity of a path"""
        residual_capacities = []
        for node in path:
            if node.name.lower() == "source":
                small_source = path[1]  # the small source is the source that the big source was comprised of that is part of the path
                index = node.children.index(small_source)
                residual_capacities.append(node.residual_capacity[index])
            else:
                residual_capacities.append(node.residual_capacity)

        return min(residual_capacities)

    def _send_flow_along_path(self, path, flow_amount):
        """Sends certain amount of flow along a certain path"""
        for i in range(len(path)):
            node = path[i]
            if node.name.lower() == "source":
                # The source might have more than one child with a capacity, so we need to check who it is that is in the path
                # in order to add flow to it
                small_source = path[i+1]  # the small source is the source that the big source was comprised of that is part of the path
                index = node.children.index(small_source)
                node.flow[index] += flow_amount
                node.residual_capacity[index] = node.capacity[index] - node.flow[index]


            else:
                if node.name.lower() == "sink":  # the sink has no outward flow
                    continue
                node.flow += flow_amount
                node.residual_capacity = node.capacity - node.flow
                # if node.name.lower() != "sink" and path[i+1].name.lower() != "sink":

            if node.name.lower() != "sink":
                existing_flow = node.flow_log.get(path[i+1], 0)
                node.flow_log[path[i+1]] = existing_flow + flow_amount  # {to: amount}
                    # node.flow_log += "{} gives {:.2f} to {}\n".format(node.name, flow_amount, path[i+1].name)

    def split_it(self):
        """Splits the bill equally between everybody"""
        return self._edmonds_karp()

    def _get_user_input(self):
        user_amount = input("How many people are splitting the bill: ")
        users = []
        for i in range(int(user_amount)):
            user_name = input("What is the name of person #{}: ".format(i+1))
            users.append(user_name.capitalize())

        paid_amounts = []
        for user in users:
            paid = input("How much did {} pay: ".format(user))
            paid_amounts.append(int(paid))

        return users, paid_amounts

    def _get_nodes_from_user_input(self, users, paid_amounts):
        """Make nodes (of the graph) out of user input"""
        total_amount_paid = sum(paid_amounts)
        due_per_person = total_amount_paid / len(users)
        difference_of_payments = [paid - due_per_person for paid in paid_amounts]

        nodes = []
        for user, diff in zip(users, difference_of_payments):
            node = Node(name=user, debt=diff)
            nodes.append(node)

        return nodes

    def _get_nodes(self):
        """Gets user input and returns the nodes to self"""
        users, paid_amounts = self._get_user_input()
        nodes = self._get_nodes_from_user_input(users=users, paid_amounts=paid_amounts)
        return nodes

    def __repr__(self):
        ret_val = "\n'Split It' is always here to help!\n" \
                  "The Following are the transactions needed to be done in order to settle up:\n"
        for node in self.nodes:
            for to_node in node.flow_log:
                # format of flow_log: {to: amount}
                from_name = node.name
                amount = node.flow_log[to_node]
                to_name = to_node.name
                if to_name.lower() == "sink" or from_name.lower() == "source":  # don't print the sink since this is artificial in the graph
                    continue
                current = "{} gives {:.2f} to {}\n".format(from_name.capitalize(), amount, to_name.capitalize())
                ret_val += current

        return ret_val

    def __str__(self):
        return self.__repr__()

    def get_transactions(self):
        return self.__str__()

    def visualize_graph(self, only_edges_with_flow=True):
        """Plot the graph to see how the algorithm worked out who paid who"""
        from_list, to_list = self._get_edges_for_visualization(only_edges_with_flow=only_edges_with_flow)
        edge_labels = self._get_edge_labels(from_list=from_list, to_list=to_list)

        # Build a data frame with the edges
        df = pd.DataFrame({'from': [node.name for node in from_list], 'to': [node.name for node in to_list]})

        # Build the graph. Note that we use the DiGraph function to create the directed graph
        graph = nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.DiGraph())

        # Make the graph
        pos = nx.spring_layout(graph)
        nx.draw(graph, with_labels=True, node_size=2000, node_color="skyblue", arrows=True, pos=pos)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='#7d868f')

        plt.axis('off')
        plt.show()

    def _get_edges_for_visualization(self, nodes=None, only_edges_with_flow=True):
        """Get the edges for visualization
        Input:
            nodes: list of Node of the graph
            only_edges_with_flow: set to True if you wish take only edges which have flow in them.
                                  set to False if you wish to take all edges (also edges with 0 flow)
        output format:
            from_list - list of Node, start point of edge
            to_list - list of Node, end point of edge
            when those two lists are zipped together (zip)
            so it means there is an edge between the two corresponding zipped from and to elements"""

        if nodes is None:
            nodes = self.nodes

        from_list = []
        to_list = []
        if only_edges_with_flow:
            for node in nodes:
                if node.name.lower() == "sink":  # there is nothing after the sink
                    continue
                for to_node in node.flow_log:
                    from_list.append(node)
                    to_list.append(to_node)

        else:  # if all edges
            for node in nodes:
                if node.name.lower() == "sink":  # there is nothing after the sink
                    continue
                for child in node.children:
                    from_list.append(node)
                    to_list.append(child)

        return from_list, to_list

    def _get_edge_labels(self, from_list, to_list, nodes=None):
        """Returns a dictionary of labels for the edges
        The labels are flow/capacity"""
        if nodes is None:
            nodes = self.nodes

        # Initialize the labels to be with no flow and infinite capacity
        # edge_labels = {(from_node.name, to_node.name): "0.00/{}".format(float("inf")) for from_node, to_node in zip(from_list, to_list)}

        edge_labels = {}
        for node in nodes:
            for to_node in node.flow_log:
                # format of flow_log: {to: amount}
                from_name = node.name
                if from_name.lower == "sink":  # there is no edge coming out of the sink
                    continue
                amount = node.flow_log[to_node]
                to_name = to_node.name
                if node.name.lower() == "source":
                    index = node.children.index(to_node)
                    capacity = node.capacity[index]
                else:
                    capacity = node.capacity

                edge_labels[(from_name, to_name)] = "{:.2f}/{:.2f}".format(amount, capacity)

        return edge_labels


def main():
    splitit = SplitIt()
    splitit.split_it()
    transactions = splitit.get_transactions()
    print(transactions)
    splitit.visualize_graph(only_edges_with_flow=True)


if __name__ == '__main__':
    main()