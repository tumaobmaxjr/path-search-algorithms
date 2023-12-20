import tkinter as tk
from tkinter import simpledialog
from queue import Queue
import heapq
import math

class Node:
    def __init__(self, label, x, y, color='lightblue'):
        self.label = label
        self.x = x
        self.y = y
        self.color = color

class Connection:
    def __init__(self, node1, node2, edge_label):
        self.node1 = node1
        self.node2 = node2
        self.edge_label = edge_label

class GraphEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Graph Node Customizer")

        self.graph = []
        self.connections = []

        self.canvas = tk.Canvas(self.master, width=400, height=400, bg='white')
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        self.canvas.bind("<Button-1>", self.handle_click)

        self.selected_node = None
        self.start_node = None
        self.goal_node = None

        self.enqueue_label = tk.Label(self.master, text="Enqueues: 0")
        self.enqueue_label.pack(side=tk.TOP)

        self.extensions_label = tk.Label(self.master, text="Extensions/Paths: 0")
        self.extensions_label.pack(side=tk.TOP)

        self.queue_size_label = tk.Label(self.master, text="Queue Size: 0")
        self.queue_size_label.pack(side=tk.TOP)

        self.path_elements_label = tk.Label(self.master, text="Path Elements: None")
        self.path_elements_label.pack(side=tk.TOP)

        self.path_cost_label = tk.Label(self.master, text="Path Cost: 0")
        self.path_cost_label.pack(side=tk.TOP)

        # Add a button for selecting start and goal nodes
        self.selection_button = tk.Button(self.master, text="Select Start and Goal Nodes", command=self.select_nodes)
        self.selection_button.pack(side=tk.TOP, padx=5, pady=5)

        # Add a button for running BFS
        self.bfs_button = tk.Button(self.master, text="Run BFS", command=self.run_bfs)
        self.bfs_button.pack(side=tk.TOP)

        # Add a button for running DFS
        self.dfs_button = tk.Button(self.master, text="Run DFS", command=self.run_dfs)
        self.dfs_button.pack(side=tk.TOP)

        # Add a button for running Hill Climbing
        self.hill_climbing_button = tk.Button(self.master, text="Run Hill Climbing", command=self.run_hill_climbing)
        self.hill_climbing_button.pack(side=tk.TOP)

        # Add a button for running Beam Search
        self.beam_search_button = tk.Button(self.master, text="Run Beam Search", command=self.run_beam_search)
        self.beam_search_button.pack(side=tk.TOP)

        # Add a button for running Branch and Bound
        self.branch_and_bound_button = tk.Button(self.master, text="Run Branch and Bound", command=self.run_branch_and_bound)
        self.branch_and_bound_button.pack(side=tk.TOP)

        # Add a button for running A*
        self.a_star_button = tk.Button(self.master, text="Run A*", command=self.run_a_star)
        self.a_star_button.pack(side=tk.TOP)

        # Add a button for deleting nodes
        self.delete_button = tk.Button(self.master, text="Delete Node", command=self.delete_node)
        self.delete_button.pack(side=tk.TOP)

        # Add a button for deleting edges
        self.delete_edge_button = tk.Button(self.master, text="Delete Edge", command=self.delete_edge)
        self.delete_edge_button.pack(side=tk.TOP)

        # Add a button for clearing the graph
        self.clear_button = tk.Button(self.master, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.TOP)

    def handle_click(self, event):
        clicked_node = self.get_clicked_node(event.x, event.y)

        if not clicked_node:
            label = simpledialog.askstring("Node Label", "Enter node label:")
            if label is not None:
                new_node = Node(label, event.x, event.y)
                self.graph.append(new_node)
                self.reset_colors()  # Reset colors when adding a new node
                self.draw_graph()

        else:
            if not self.selected_node:
                self.selected_node = clicked_node
            else:
                if self.selected_node != clicked_node:
                    edge_label = simpledialog.askstring("Edge Label", "Enter edge label:")
                    if edge_label is not None:
                        new_connection = Connection(self.selected_node, clicked_node, edge_label)
                        self.connections.append(new_connection)
                        self.reset_colors()  # Reset colors when adding a new connection
                        self.draw_connections()

                self.selected_node = None

    def get_clicked_node(self, x, y):
        for node in self.graph:
            if (x - 20) <= node.x <= (x + 20) and (y - 20) <= node.y <= (y + 20):
                return node
        return None

    def draw_graph(self):
        self.canvas.delete("all")

        for node in self.graph:
            x, y = node.x, node.y
            color = 'green' if node == self.start_node else 'red' if node == self.goal_node else node.color
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline='black')
            self.canvas.create_text(x, y, text=node.label, font=("Helvetica", 20, "bold"))

        self.draw_connections()

    def draw_connections(self):
        for connection in self.connections:
            x1, y1 = connection.node1.x, connection.node1.y
            x2, y2 = connection.node2.x, connection.node2.y
            self.canvas.create_line(x1, y1, x2, y2, fill='black', width=1)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y, text=connection.edge_label)

    def select_nodes(self):
        start_label = simpledialog.askstring("Select Start Node", "Enter the label of the start node:")
        goal_label = simpledialog.askstring("Select Goal Node", "Enter the label of the goal node:")

        self.start_node = self.find_node_by_label(start_label)
        self.goal_node = self.find_node_by_label(goal_label)

        if self.start_node and self.goal_node:
            self.reset_colors()  # Reset colors when selecting start and goal nodes
            self.update_node_color(self.start_node, 'green')
            self.update_node_color(self.goal_node, 'red')

        self.print_graph_info()

    def run_bfs(self):
        if not self.start_node or not self.goal_node:
            print("Please select start and goal nodes first.")
            return

        self.reset_colors()  # Reset colors before running BFS

        bfs_queue = Queue()
        visited = set()

        bfs_queue.put(self.start_node)
        visited.add(self.start_node)

        enqueue_count = 0
        extensions_count = 0
        queue_size = 0
        path_elements = []
        path_cost = 0

        while not bfs_queue.empty():
            current_node = bfs_queue.get()
            self.update_node_color(current_node, 'blue')  # Mark as visited

            for connection in self.connections:
                if connection.node1 == current_node and connection.node2 not in visited:
                    bfs_queue.put(connection.node2)
                    visited.add(connection.node2)

                if connection.node2 == current_node and connection.node1 not in visited:
                    bfs_queue.put(connection.node1)
                    visited.add(connection.node1)

            self.draw_graph()
            self.master.update()  # Update the window to show the changes
            self.master.after(1000)  # Pause for visualization (adjust as needed)

            # Update BFS information labels
            enqueue_count += 1
            extensions_count += len(self.connections)  # Assuming each connection represents a potential extension
            queue_size = bfs_queue.qsize()
            path_elements.append(current_node.label)

            # Update labels
            self.enqueue_label.config(text=f"Enqueues: {enqueue_count}")
            self.extensions_label.config(text=f"Extensions/Paths: {extensions_count}")
            self.queue_size_label.config(text=f"Queue Size: {queue_size}")
            self.path_elements_label.config(text=f"Path Elements: {', '.join(path_elements)}")
            self.path_cost_label.config(text=f"Path Cost: {path_cost}")

    def run_dfs(self):
        if not self.start_node or not self.goal_node:
            print("Please select start and goal nodes first.")
            return

        self.reset_colors()  # Reset colors before running DFS

        dfs_stack = [self.start_node]
        visited = set()

        enqueue_count = 0
        extensions_count = 0
        queue_size = 0
        path_elements = []
        path_cost = 0

        while dfs_stack:
            current_node = dfs_stack.pop()
            self.update_node_color(current_node, 'blue')  # Mark as visited

            for connection in self.connections:
                if connection.node1 == current_node and connection.node2 not in visited:
                    dfs_stack.append(connection.node2)
                    visited.add(connection.node2)

                if connection.node2 == current_node and connection.node1 not in visited:
                    dfs_stack.append(connection.node1)
                    visited.add(connection.node1)

            self.draw_graph()
            self.master.update()  # Update the window to show the changes
            self.master.after(1000)  # Pause for visualization (adjust as needed)

            # Update DFS information labels
            enqueue_count += 1
            extensions_count += len(self.connections)  # Assuming each connection represents a potential extension
            queue_size = len(dfs_stack)
            path_elements.append(current_node.label)

            # Update labels
            self.enqueue_label.config(text=f"Enqueues: {enqueue_count}")
            self.extensions_label.config(text=f"Extensions/Paths: {extensions_count}")
            self.queue_size_label.config(text=f"Queue Size: {queue_size}")
            self.path_elements_label.config(text=f"Path Elements: {', '.join(path_elements)}")
            self.path_cost_label.config(text=f"Path Cost: {path_cost}")


    def run_hill_climbing(self):
        if not self.start_node or not self.goal_node:
            print("Please select start and goal nodes first.")
            return

        self.reset_colors()  # Reset colors before running Hill Climbing

        current_node = self.start_node
        visited = set([current_node])

        enqueue_count = 0
        extensions_count = 0
        path_elements = []
        path_cost = 0

        while current_node != self.goal_node:
            neighbors = self.get_neighbors(current_node, visited)
            if not neighbors:
                print("No path found.")
                return

            best_neighbor = self.get_best_neighbor(neighbors)
            self.update_node_color(current_node, 'blue')  # Mark as visited

            # Update Hill Climbing information labels
            enqueue_count += 1
            extensions_count += len(neighbors)
            path_elements.append(current_node.label)

            # Update labels
            self.enqueue_label.config(text=f"Enqueues: {enqueue_count}")
            self.extensions_label.config(text=f"Extensions/Paths: {extensions_count}")
            self.path_elements_label.config(text=f"Path Elements: {', '.join(path_elements)}")
            self.path_cost_label.config(text=f"Path Cost: {path_cost}")

            self.draw_graph()
            self.master.update()  # Update the window to show the changes
            self.master.after(1000)  # Pause for visualization (adjust as needed)

            current_node = best_neighbor
            visited.add(current_node)

        print("Goal reached!")

    def get_neighbors(self, current_node, visited):
        neighbors = []

        for connection in self.connections:
            if connection.node1 == current_node and connection.node2 not in visited:
                neighbors.append(connection.node2)

            if connection.node2 == current_node and connection.node1 not in visited:
                neighbors.append(connection.node1)

        return neighbors

    def get_best_neighbor(self, neighbors):
        # You can customize the heuristic function here
        # For simplicity, let's use the Euclidean distance as the heuristic
        def heuristic(node):
            return math.sqrt((node.x - self.goal_node.x)**2 + (node.y - self.goal_node.y)**2)

        return min(neighbors, key=heuristic)


    def run_beam_search(self, beam_width=2):
        if not self.start_node or not self.goal_node:
            print("Please select start and goal nodes first.")
            return

        self.reset_colors()  # Reset colors before running Beam Search

        beam = [(0, [self.start_node])]  # Priority queue with (cost, path) tuples
        visited = set([self.start_node])

        enqueue_count = 0
        extensions_count = 0
        queue_size = 0
        path_elements = []
        path_cost = 0

        while beam:
            _, current_path = heapq.heappop(beam)
            current_node = current_path[-1]

            if current_node == self.goal_node:
                # Goal reached
                path_cost = len(current_path) - 1  # The cost is the number of edges traversed
                break

            neighbors = self.get_neighbors(current_node, visited)
            for neighbor in neighbors:
                if neighbor not in visited:
                    new_path = current_path + [neighbor]
                    cost = len(new_path) - 1  # The cost is the number of edges traversed
                    heapq.heappush(beam, (cost, new_path))
                    visited.add(neighbor)

            # Update Beam Search information labels
            enqueue_count += 1
            extensions_count += len(neighbors)
            queue_size = len(beam)
            path_elements = [node.label for node in current_path]

            # Update labels
            self.enqueue_label.config(text=f"Enqueues: {enqueue_count}")
            self.extensions_label.config(text=f"Extensions/Paths: {extensions_count}")
            self.queue_size_label.config(text=f"Queue Size: {queue_size}")
            self.path_elements_label.config(text=f"Path Elements: {', '.join(path_elements)}")
            self.path_cost_label.config(text=f"Path Cost: {path_cost}")

            self.update_node_color(current_node, 'blue')  # Mark as visited
            self.draw_graph()
            self.master.update()  # Update the window to show the changes
            self.master.after(1000)  # Pause for visualization (adjust as needed)

        print("Goal reached!")

    def run_branch_and_bound(self):
        if not self.start_node or not self.goal_node:
            print("Please select start and goal nodes first.")
            return

        self.reset_colors()  # Reset colors before running Branch and Bound

        priority_queue = [(0, [self.start_node])]  # Priority queue with (cost, path) tuples
        visited = set([self.start_node])

        enqueue_count = 0
        extensions_count = 0
        queue_size = 0
        path_elements = []
        path_cost = 0

        while priority_queue:
            _, current_path = heapq.heappop(priority_queue)
            current_node = current_path[-1]

            if current_node == self.goal_node:
                # Goal reached
                path_cost = len(current_path) - 1  # The cost is the number of edges traversed
                break

            neighbors = self.get_neighbors(current_node, visited)
            for neighbor in neighbors:
                if neighbor not in visited:
                    new_path = current_path + [neighbor]
                    cost = len(new_path) - 1  # The cost is the number of edges traversed
                    heapq.heappush(priority_queue, (cost, new_path))
                    visited.add(neighbor)

            # Update Branch and Bound information labels
            enqueue_count += 1
            extensions_count += len(neighbors)
            queue_size = len(priority_queue)
            path_elements = [node.label for node in current_path]

            # Update labels
            self.enqueue_label.config(text=f"Enqueues: {enqueue_count}")
            self.extensions_label.config(text=f"Extensions/Paths: {extensions_count}")
            self.queue_size_label.config(text=f"Queue Size: {queue_size}")
            self.path_elements_label.config(text=f"Path Elements: {', '.join(path_elements)}")
            self.path_cost_label.config(text=f"Path Cost: {path_cost}")

            self.update_node_color(current_node, 'blue')  # Mark as visited
            self.draw_graph()
            self.master.update()  # Update the window to show the changes
            self.master.after(1000)  # Pause for visualization (adjust as needed)

        print("Goal reached!")

    def run_a_star(self):
        if not self.start_node or not self.goal_node:
            print("Please select start and goal nodes first.")
            return

        self.reset_colors()  # Reset colors before running A*

        priority_queue = [(0 + self.heuristic(self.start_node), 0, [self.start_node])]  # Priority queue with (f-cost, g-cost, path) tuples
        visited = set([self.start_node])

        enqueue_count = 0
        extensions_count = 0
        queue_size = 0
        path_elements = []
        path_cost = 0

        while priority_queue:
            _, g_cost, current_path = heapq.heappop(priority_queue)
            current_node = current_path[-1]

            if current_node == self.goal_node:
                # Goal reached
                path_cost = len(current_path) - 1  # The cost is the number of edges traversed
                break

            neighbors = self.get_neighbors(current_node, visited)
            for neighbor in neighbors:
                if neighbor not in visited:
                    new_path = current_path + [neighbor]
                    g_cost_new = g_cost + 1  # Assuming each edge has a cost of 1
                    f_cost = g_cost_new + self.heuristic(neighbor)
                    heapq.heappush(priority_queue, (f_cost, g_cost_new, new_path))
                    visited.add(neighbor)

            # Update A* information labels
            enqueue_count += 1
            extensions_count += len(neighbors)
            queue_size = len(priority_queue)
            path_elements = [node.label for node in current_path]

            # Update labels
            self.enqueue_label.config(text=f"Enqueues: {enqueue_count}")
            self.extensions_label.config(text=f"Extensions/Paths: {extensions_count}")
            self.queue_size_label.config(text=f"Queue Size: {queue_size}")
            self.path_elements_label.config(text=f"Path Elements: {', '.join(path_elements)}")
            self.path_cost_label.config(text=f"Path Cost: {path_cost}")

            self.update_node_color(current_node, 'blue')  # Mark as visited
            self.draw_graph()
            self.master.update()  # Update the window to show the changes
            self.master.after(1000)  # Pause for visualization (adjust as needed)

        print("Goal reached!")

    def heuristic(self, node):
        # Euclidean distance as the heuristic
        return math.sqrt((node.x - self.goal_node.x)**2 + (node.y - self.goal_node.y)**2)

    def delete_node(self):
        node_label = simpledialog.askstring("Delete Node", "Enter the label of the node to delete:")
        node_to_delete = self.find_node_by_label(node_label)

        if node_to_delete:
            self.graph.remove(node_to_delete)
            self.connections = [conn for conn in self.connections if conn.node1 != node_to_delete and conn.node2 != node_to_delete]
            self.reset_colors()  # Reset colors after deleting a node
            self.draw_graph()

    def delete_edge(self):
        edge_label = simpledialog.askstring("Delete Edge", "Enter the label of the edge to delete:")
        self.connections = [conn for conn in self.connections if conn.edge_label != edge_label]
        self.reset_colors()  # Reset colors after deleting an edge
        self.draw_graph()

    def clear_graph(self):
        response = tkinter.messagebox.askyesno("Clear Graph", "Are you sure you want to clear the graph?")
        if response:
            self.graph = []
            self.connections = []
            self.start_node = None
            self.goal_node = None
            self.selected_node = None
            self.reset_colors()
            self.draw_graph()
            self.print_graph_info()

    def find_node_by_label(self, label):
        for node in self.graph:
            if node.label == label:
                return node
        return None

    def update_node_color(self, node, color):
        node.color = color
        self.draw_graph()

    def reset_colors(self):
        for node in self.graph:
            node.color = 'lightblue'
        self.draw_graph()

    def print_graph_info(self):
        print("\nGraph Information:")
        print("Nodes:")
        for node in self.graph:
            print(f"  {node.label}")

        print("\nConnections:")
        for connection in self.connections:
            print(f"  {connection.node1.label} --({connection.edge_label})--> {connection.node2.label}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()