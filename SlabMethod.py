import bisect

# ==========================================
# 1. THE DATA (Coordinates & Edges)
# ==========================================
# (x, y) tuples
vertex = [
    (0, 4), (2, 8), (2, 2), (5, 6), (5, 3), 
    (8, 9), (8, 5), (8, 1), (11, 4)
]

# (Start_Index, End_Index, "Name of Face Above this edge")
# (Start_Index, End_Index, "Name of Face Above this edge")
edges = [
    # --- Top Boundaries (Above is Unbounded) ---
    (0, 1, "Unbounded"), 
    (1, 5, "Unbounded"), 
    (5, 8, "Unbounded"), 

    # --- Bottom Boundaries ---
    # Above V2-V0 is Face 2 (Bottom-Left)
    (2, 0, "Face 2"), 
    # Above V7-V2 is Face 8 (The long bottom-left triangle)
    (7, 2, "Face 8"), 
    # Above V8-V7 is Face 9 (The bottom-right area)
    (8, 7, "Face 9"),           

    # --- Internal Edges ---
    # Left Side
    (0, 3, "Face 1"),   # Above V0-V3 is Face 1
    (0, 4, "Face 3"),   # Above V0-V4 is Face 3
    (1, 3, "Face 5"),   # Above V1-V3 is Face 5 (Top Triangle)
    (2, 4, "Face 2"),   # Above V2-V4 is Face 2

    # Center/Right Side
    (3, 5, "Face 5"),   # Above V3-V5 is Face 5
    (3, 6, "Face 6"),   # Above V3-V6 is Face 6 (Small Mid-Top)
    (4, 6, "Face 4"),   # Above V4-V6 is Face 4 (Central Wedge Right)
    (4, 7, "Face 9"),   # Above V4-V7 is Face 9 (Bottom-Right Quad)
    (6, 8, "Face 7"),   # Above V6-V8 is Face 7 (Top-Right Peak)
    
    # Note: Vertical edges (like 3-4 and 6-5) are boundaries between slabs 
    # and don't need to be stored for the vertical sort logic.
]

# ==========================================
# 2. HELPER: Calculate Y on a line
# ==========================================
def GetYatXforEdge(p1, p2, x):
    """Returns the y-coordinate of the edge at a specific x."""
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2: return max(y1, y2) # Vertical line
    slope = (y2 - y1) / (x2 - x1)
    return y1 + slope * (x - x1)

# ==========================================
# 3. PRE-PROCESSING (Build the Slabs)
# ==========================================
# Get the Slabs [0, 2, 5, 8, 11]
x_coords = sorted(list(set(v[0] for v in vertex)))

# Create a dictionary to store our slabs: 
# Key = start_x, Value = list of edges inside that slab
slabs = {}

for i in range(len(x_coords) - 1):
    slab_start = x_coords[i]
    slab_end = x_coords[i+1]
    mid_x = (slab_start + slab_end) / 2
    
    active_edges = []
    
    # Find edges that cross this slab
    for u, v, face_name in edges:
        p1, p2 = vertex[u], vertex[v]
        # Ensure p1 is left, p2 is right for math
        if p1[0] > p2[0]: 
            p1, p2 = p2, p1 
        
        # If edge covers the slab width, add it [cite: 91]
        if p1[0] <= slab_start and p2[0] >= slab_end:
            active_edges.append({
                "p1": p1, "p2": p2, "face": face_name,
                "y_at_mid": GetYatXforEdge(p1, p2, mid_x)
            })
            
    # Sort edges by height (y) inside this slab [cite: 93]
    active_edges.sort(key=lambda e: e['y_at_mid'])
    slabs[slab_start] = active_edges

# ==========================================
# 4. QUERY FUNCTION (The Search)
# ==========================================
def locate(qx, qy):
    # Step A: Binary Search for the correct Slab X-index 
    # bisect_right finds where qx would fit in the sorted x_coords
    idx = bisect.bisect_right(x_coords, qx) - 1
    
    if idx < 0 or idx >= len(x_coords) - 1:
        return "Unbounded (Outside X range)"
    
    slab_key = x_coords[idx]
    edges_in_slab = slabs[slab_key]

    # Step B: Search edges within the slab
    # We look for the highest edge that is BELOW our point.
    current_face = "Unbounded (Below everything)"
    
    for edge in edges_in_slab:
        # Calculate edge height at the query's X position
        edge_y = GetYatXforEdge(edge['p1'], edge['p2'], qx)
        
        if qy > edge_y:
            # Point is above this edge, so we are potentially in this edge's face
            current_face = edge['face']
        else:
            # Point is below this edge. Since edges are sorted, we can stop.
            # (We found the ceiling, so the previous edge was the floor)
            break
            
    return current_face

# ==========================================
# 5. TEST RUN
# ==========================================
test_points = [
    # --- Originals ---
    (1, 5), (1, 3), (3, 4.5), (6, 7), (9, 3), (6, 10), (-5, 5),
    
    # --- New Strict Regions ---
    (4, 7.5),  # Face F5 (Top Triangle)
    (6, 6.5),  # Face F6 (Middle-Top Triangle)
    (9, 6),    # Face F7 (Top-Right Peak)
    (4, 2),    # Face F8 (Bottom-Left Long Triangle)
    (7, 3)     # Face F9 (Bottom-Right Quad / Middle area)
]

print(f"{'Point':<15} | {'Region Found'}")
print("-" * 35)
for x, y in test_points:
    print(f"({x}, {y})".ljust(15) + " | " + locate(x, y))

