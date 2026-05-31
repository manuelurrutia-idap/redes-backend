import heapq
import math
from collections import defaultdict, deque

def sanitize_inf(data):
    if isinstance(data, dict):
        return {k: sanitize_inf(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_inf(v) for v in data]
    elif isinstance(data, float) and math.isinf(data):
        return None
    return data

# --- Graph Data Structures Wrapper ---

def build_adj_list(nodes, edges, weight_key='weight', directed=True):
    adj = {node.id: [] for node in nodes}
    for edge in edges:
        w = getattr(edge, weight_key)
        adj[edge.from_activity_id].append({'to': edge.to_activity_id, 'weight': w, 'edge_id': edge.id})
        if not directed:
            adj[edge.to_activity_id].append({'to': edge.from_activity_id, 'weight': w, 'edge_id': edge.id})
    return adj

def build_capacity_graph(nodes, edges):
    adj = {node.id: {} for node in nodes}
    for edge in edges:
        if edge.to_activity_id not in adj[edge.from_activity_id]:
            adj[edge.from_activity_id][edge.to_activity_id] = 0
        adj[edge.from_activity_id][edge.to_activity_id] += edge.capacity
        if edge.from_activity_id not in adj[edge.to_activity_id]:
            adj[edge.to_activity_id][edge.from_activity_id] = 0 # reverse edge for residual
    return adj

def has_cycle(nodes, edges, new_from, new_to):
    # Simulate adding the edge
    adj = {node.id: [] for node in nodes}
    for edge in edges:
        adj[edge.from_activity_id].append(edge.to_activity_id)
    adj[new_from].append(new_to)
    
    visited = {n.id: 0 for n in nodes} # 0: unvisited, 1: visiting, 2: visited
    
    def dfs(u):
        if visited[u] == 1: return True # cycle found
        if visited[u] == 2: return False
        visited[u] = 1
        for v in adj[u]:
            if dfs(v): return True
        visited[u] = 2
        return False
        
    for n in nodes:
        if visited[n.id] == 0:
            if dfs(n.id): return True
    return False

# --- MST ---

def prim(nodes, edges):
    if not nodes: return []
    adj = build_adj_list(nodes, edges, directed=False)
    
    start_node = nodes[0].id
    visited = set([start_node])
    mst_edges = []
    
    # Priority Queue: (weight, from, to, edge_id)
    pq = []
    for neighbor in adj[start_node]:
        heapq.heappush(pq, (neighbor['weight'], start_node, neighbor['to'], neighbor['edge_id']))
        
    while pq and len(visited) < len(nodes):
        weight, u, v, edge_id = heapq.heappop(pq)
        if v not in visited:
            visited.add(v)
            mst_edges.append(edge_id)
            for neighbor in adj[v]:
                if neighbor['to'] not in visited:
                    heapq.heappush(pq, (neighbor['weight'], v, neighbor['to'], neighbor['edge_id']))
                    
    return {"edges": mst_edges}

class UnionFind:
    def __init__(self, n):
        self.parent = {i: i for i in n}
        self.rank = {i: 0 for i in n}
        
    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1

def kruskal(nodes, edges):
    node_ids = [n.id for n in nodes]
    uf = UnionFind(node_ids)
    
    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda e: e.weight)
    mst_edges = []
    
    for edge in sorted_edges:
        if uf.find(edge.from_activity_id) != uf.find(edge.to_activity_id):
            uf.union(edge.from_activity_id, edge.to_activity_id)
            mst_edges.append(edge.id)
            
    return {"edges": mst_edges}

# --- Shortest Path ---

def dijkstra(nodes, edges, source, target=None):
    adj = build_adj_list(nodes, edges, directed=True)
    dist = {n.id: float('inf') for n in nodes}
    dist[source] = 0
    prev = {n.id: None for n in nodes}
    edge_to = {n.id: None for n in nodes}
    
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        if target and u == target: break
        
        for neighbor in adj[u]:
            v = neighbor['to']
            w = neighbor['weight']
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                edge_to[v] = neighbor['edge_id']
                heapq.heappush(pq, (dist[v], v))
                
    path_nodes = []
    path_edges = []
    if target:
        curr = target
        if prev[curr] is not None or curr == source:
            while curr is not None:
                path_nodes.insert(0, curr)
                if edge_to[curr] is not None:
                    path_edges.insert(0, edge_to[curr])
                curr = prev[curr]
    
    return sanitize_inf({"distance": dist.get(target, dist), "path": path_nodes, "edges": path_edges})

def bellman_ford(nodes, edges, source, target=None):
    dist = {n.id: float('inf') for n in nodes}
    dist[source] = 0
    prev = {n.id: None for n in nodes}
    edge_to = {n.id: None for n in nodes}
    
    for _ in range(len(nodes) - 1):
        for edge in edges:
            u = edge.from_activity_id
            v = edge.to_activity_id
            w = edge.weight
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                edge_to[v] = edge.id
                
    # check negative cycles
    for edge in edges:
         if dist[edge.from_activity_id] != float('inf') and dist[edge.from_activity_id] + edge.weight < dist[edge.to_activity_id]:
             raise ValueError("Graph contains a negative-weight cycle")
             
    path_nodes = []
    path_edges = []
    if target:
        curr = target
        if prev[curr] is not None or curr == source:
            while curr is not None:
                path_nodes.insert(0, curr)
                if edge_to[curr] is not None:
                    path_edges.insert(0, edge_to[curr])
                curr = prev[curr]
                
    return sanitize_inf({"distance": dist.get(target, dist), "path": path_nodes, "edges": path_edges})

def floyd_warshall(nodes, edges):
    dist = {u.id: {v.id: float('inf') for v in nodes} for u in nodes}
    nxt = {u.id: {v.id: None for v in nodes} for u in nodes}
    
    for n in nodes:
        dist[n.id][n.id] = 0
        
    for edge in edges:
        dist[edge.from_activity_id][edge.to_activity_id] = edge.weight
        nxt[edge.from_activity_id][edge.to_activity_id] = edge.to_activity_id
        
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i.id][k.id] != float('inf') and dist[k.id][j.id] != float('inf'):
                    if dist[i.id][j.id] > dist[i.id][k.id] + dist[k.id][j.id]:
                        dist[i.id][j.id] = dist[i.id][k.id] + dist[k.id][j.id]
                        nxt[i.id][j.id] = nxt[i.id][k.id]
                        
    return sanitize_inf({"distances": dist, "next": nxt})

def a_star(nodes, edges, source, target):
    # For A*, we need a heuristic. We'll use 0 as default since nodes have no coordinates.
    # This reduces it to Dijkstra, but code structure is A*
    adj = build_adj_list(nodes, edges, directed=True)
    
    def h(n): return 0
    
    open_set = [(h(source), source)]
    came_from = {}
    edge_to = {}
    
    g_score = {n.id: float('inf') for n in nodes}
    g_score[source] = 0
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == target:
            path_nodes = [current]
            path_edges = []
            while current in came_from:
                path_edges.insert(0, edge_to[current])
                current = came_from[current]
                path_nodes.insert(0, current)
            return sanitize_inf({"distance": g_score[target], "path": path_nodes, "edges": path_edges})
            
        for neighbor in adj[current]:
            v = neighbor['to']
            tentative_g = g_score[current] + neighbor['weight']
            if tentative_g < g_score[v]:
                came_from[v] = current
                edge_to[v] = neighbor['edge_id']
                g_score[v] = tentative_g
                f_score = tentative_g + h(v)
                heapq.heappush(open_set, (f_score, v))
                
    return sanitize_inf({"distance": float('inf'), "path": [], "edges": []})

# --- Max Flow ---

def bfs_capacity(rGraph, s, t, parent):
    visited = {i: False for i in rGraph}
    queue = deque([s])
    visited[s] = True
    
    while queue:
        u = queue.popleft()
        for ind, val in rGraph[u].items():
            if visited[ind] == False and val > 0:
                queue.append(ind)
                visited[ind] = True
                parent[ind] = u
                if ind == t:
                    return True
    return False

def ford_fulkerson(nodes, edges, source, target):
    rGraph = build_capacity_graph(nodes, edges)
    parent = {n.id: -1 for n in nodes}
    max_flow = 0
    
    while bfs_capacity(rGraph, source, target, parent):
        path_flow = float('inf')
        s = target
        while s != source:
            path_flow = min(path_flow, rGraph[parent[s]][s])
            s = parent[s]
            
        max_flow += path_flow
        v = target
        while v != source:
            u = parent[v]
            rGraph[u][v] -= path_flow
            rGraph[v][u] += path_flow
            v = parent[v]
            
    # Also return edges with flow (comparing original to residual)
    orig_graph = build_capacity_graph(nodes, edges)
    flow_edges = []
    for edge in edges:
        u, v = edge.from_activity_id, edge.to_activity_id
        flow = orig_graph[u].get(v, 0) - rGraph[u].get(v, 0)
        if flow > 0:
            flow_edges.append({"edge_id": edge.id, "flow": flow})
            
    return {"max_flow": max_flow, "flow_edges": flow_edges}

# --- Project Management ---

def cpm(nodes, edges):
    # Calculates Early Start, Early Finish, Late Start, Late Finish, Slack, Critical Path
    adj = build_adj_list(nodes, edges, directed=True, weight_key='time')
    in_degree = {n.id: 0 for n in nodes}
    for e in edges:
        in_degree[e.to_activity_id] += 1
        
    durations = {n.id: n.duration for n in nodes}
    
    # topological sort
    queue = deque([n.id for n in nodes if in_degree[n.id] == 0])
    top_order = []
    while queue:
        u = queue.popleft()
        top_order.append(u)
        for neighbor in adj[u]:
            v = neighbor['to']
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
                
    if len(top_order) != len(nodes):
        raise ValueError("Graph has a cycle, cannot compute CPM")
        
    # Forward Pass
    ES = {n.id: 0 for n in nodes}
    EF = {n.id: durations[n.id] for n in nodes}
    for u in top_order:
        for neighbor in adj[u]:
            v = neighbor['to']
            ES[v] = max(ES[v], EF[u]) # time on edge not strictly used for CPM standard unless it represents lag
            EF[v] = ES[v] + durations[v]
            
    project_duration = max(EF.values()) if EF else 0
    
    # Backward Pass
    LS = {n.id: project_duration - durations[n.id] for n in nodes}
    LF = {n.id: project_duration for n in nodes}
    
    rev_adj = {n.id: [] for n in nodes}
    for e in edges:
        rev_adj[e.to_activity_id].append({'to': e.from_activity_id})
        
    for u in reversed(top_order):
        for neighbor in rev_adj[u]:
            v = neighbor['to']
            LF[v] = min(LF[v], LS[u])
            LS[v] = LF[v] - durations[v]
            
    slack = {n.id: LS[n.id] - ES[n.id] for n in nodes}
    critical_path = [n.id for n in nodes if slack[n.id] == 0]
    critical_edges = [e.id for e in edges if e.from_activity_id in critical_path and e.to_activity_id in critical_path]
    
    return {
        "project_duration": project_duration,
        "critical_path": critical_path,
        "critical_edges": critical_edges,
        "nodes": {
            n.id: {"ES": ES[n.id], "EF": EF[n.id], "LS": LS[n.id], "LF": LF[n.id], "slack": slack[n.id]}
            for n in nodes
        }
    }

def pert(nodes, edges):
    # Simplified PERT using the existing durations as expected times.
    return cpm(nodes, edges)
