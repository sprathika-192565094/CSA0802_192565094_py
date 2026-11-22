"""Q2 - Tuples, mutability and copying: city bus-stop map."""
import copy
import json
import sys
import time
import timeit

res = {}


def section(t):
    print("\n=== " + t + " ===")


# ---------------------------------------------------------------- the program given in the question
section("Program from the question (TODO 1 completed)")
rows, cols = 3, 4
bad = [[0] * cols] * rows                    # every row is the SAME list object
bad[0][1] = 7
# TODO 1 (completed): rows x cols grid of zeros using a list comprehension, every row a separate list
good = [[0 for _ in range(cols)] for _ in range(rows)]
good[0][1] = 7
print("bad :", bad)
print("good:", good)
print(bad[0] is bad[1], good[0] is good[1])
# Tuples are immutable, so they can be used as dictionary keys
stops = {(13.0827, 80.2707): "Chennai Central", (13.0418, 80.2341): "T. Nagar"}
print(stops[(13.0418, 80.2341)])

# ---------------------------------------------------------------- is and id()
section("The bug and its correction with is and id()")
print("bad : ids of the 3 rows :", [id(r) for r in bad], "-> distinct objects:", len({id(r) for r in bad}))
print("good: ids of the 3 rows :", [id(r) for r in good], "-> distinct objects:", len({id(r) for r in good}))
print("bad[0] is bad[2] ->", bad[0] is bad[2], "| good[0] is good[2] ->", good[0] is good[2])

# ---------------------------------------------------------------- tuples as dictionary keys / unpacking
section("Tuples: unpacking in a for loop and use as keys")
for (lat, lon), name in stops.items():
    print(f"  {name:16} lat={lat}  lon={lon}")
for name, (lat, lon) in sorted((n, c) for c, n in stops.items()):
    print(f"  sorted by name: {name:16} -> {lat:.4f}, {lon:.4f}")
section("A list as a dictionary key")
try:
    stops[[13.0418, 80.2341]] = "T. Nagar again"
except TypeError as e:
    print("TypeError:", e)
try:
    stops[(13.0418, [80.2341])] = "tuple that contains a list"
except TypeError as e:
    print("TypeError (tuple holding a list):", e)
print("hash((13.0418, 80.2341)) =", hash((13.0418, 80.2341)), "(a tuple of immutable items has a hash)")

# ---------------------------------------------------------------- aliasing, shallow and deep copy
section("Aliasing, shallow copy and deep copy")
route = [["Central", "T. Nagar"], ["Adyar"]]          # list that CONTAINS lists
alias = route
shallow1 = copy.copy(route)
shallow2 = route[:]
deep = copy.deepcopy(route)
route[0].append("Guindy")        # change an inner list
route.append(["Tambaram"])       # change the outer list
print("route          :", route)
print("alias   (=)    :", alias, "| same object:", alias is route)
print("shallow copy.copy:", shallow1, "| outer list new:", shallow1 is not route, "| inner list shared:", shallow1[0] is route[0])
print("shallow route[:] :", shallow2, "| inner list shared:", shallow2[0] is route[0])
print("deepcopy         :", deep, "| inner list shared:", deep[0] is route[0])
flat = [1, 2, 3]
flat_copy = flat[:]
flat.append(4)
print("flat list, slice copy is enough:", flat, flat_copy)

# ---------------------------------------------------------------- function changing its argument
section("A function that changes a list argument changes the caller's list")


def add_stop(stops_list):
    stops_list.append("Velachery")          # mutates the SAME object the caller passed


def add_stop_new(stops_list):
    stops_list = stops_list + ["Velachery"]  # builds a new list; only the local name is rebound
    return stops_list


mine = ["Central"]
add_stop(mine)
print("after add_stop(mine)     :", mine)
other = ["Central"]
add_stop_new(other)
print("after add_stop_new(other):", other, "(unchanged); returned value must be used")

# ---------------------------------------------------------------- tuple containing a list
section("Changing a list that is stored inside a tuple")
t = ("route 5", [1, 2])
t[1].append(3)
print("t[1].append(3) works:", t)
try:
    t[1] = [9]
except TypeError as e:
    print("t[1] = [9]  ->  TypeError:", e)
try:
    t[1] += [4]
except TypeError as e:
    print("t[1] += [4] ->  TypeError:", e)
print("...but the list WAS extended before the error:", t)
inner_id = id(t[1])
t[1].append(5)
print("The tuple still holds the SAME list object after the change (ids equal):", id(t[1]) == inner_id, "- tuple immutability is shallow")

# ---------------------------------------------------------------- memory: list vs tuple
section("Memory of a list and a tuple of 1,000,000 values (sys.getsizeof)")
N = 1_000_000
L = list(range(N))
Tp = tuple(range(N))
Lapp = []
for i in range(N):
    Lapp.append(i)
print(f"list(range(N))        : {sys.getsizeof(L):>10,} bytes")
print(f"list built by append  : {sys.getsizeof(Lapp):>10,} bytes (over-allocated to make append fast)")
print(f"tuple(range(N))       : {sys.getsizeof(Tp):>10,} bytes")
print(f"per element: list {sys.getsizeof(L) / N:.2f} bytes, tuple {sys.getsizeof(Tp) / N:.2f} bytes (both store 8-byte references; the int objects are extra and the same for both)")
res["mem"] = dict(list=sys.getsizeof(L), list_append=sys.getsizeof(Lapp), tuple=sys.getsizeof(Tp))

section("Time to create and index a tuple and a list of the same 1,000,000 values (best of 5)")
t_cl = min(timeit.repeat(lambda: list(range(N)), number=1, repeat=5))
t_ct = min(timeit.repeat(lambda: tuple(range(N)), number=1, repeat=5))
t_il = min(timeit.repeat(lambda: [L[i] for i in range(0, N, 1)], number=1, repeat=5))
t_it = min(timeit.repeat(lambda: [Tp[i] for i in range(0, N, 1)], number=1, repeat=5))
small_l = min(timeit.repeat("[1, 2, 3, 4, 5]", number=1_000_000, repeat=5))
small_t = min(timeit.repeat("(1, 2, 3, 4, 5)", number=1_000_000, repeat=5))
print(f"create 1,000,000 values : list {t_cl:.4f} s | tuple {t_ct:.4f} s")
print(f"index all 1,000,000     : list {t_il:.4f} s | tuple {t_it:.4f} s")
print(f"create a 5-element literal 1,000,000 times: list {small_l:.4f} s | tuple {small_t:.4f} s (tuple literal of constants is built once at compile time)")
res["time"] = dict(create_list=t_cl, create_tuple=t_ct, index_list=t_il, index_tuple=t_it, lit_list=small_l, lit_tuple=small_t)

# ---------------------------------------------------------------- alternative concept: dictionary grid
section("Alternative concept: zones kept in a dictionary keyed by (row, col)")
R, C = 1000, 1000
dense = [[0 for _ in range(C)] for _ in range(R)]
sparse = {}
import random
rnd = random.Random(3)
cells = [(rnd.randrange(R), rnd.randrange(C)) for _ in range(1000)]          # only 1,000 zones ever get passengers
for r, c in cells:
    dense[r][c] += 1
    sparse[(r, c)] = sparse.get((r, c), 0) + 1
same = all(dense[r][c] == v for (r, c), v in sparse.items()) and sum(map(sum, dense)) == sum(sparse.values())
mem_dense = sys.getsizeof(dense) + sum(sys.getsizeof(row) for row in dense)
mem_sparse = sys.getsizeof(sparse)
mem_sparse_total = mem_sparse + sum(sys.getsizeof(k) for k in sparse)       # table + the key tuples (ints are small shared objects)
print("both structures give identical counts:", same)
print(f"list of lists  1000 x 1000 : {mem_dense / 1e6:8.2f} MB of list storage (O(rows x cols))")
print(f"dict, {len(sparse)} non-empty zones: {mem_sparse / 1e3:8.2f} KB dict table + {(mem_sparse_total - mem_sparse) / 1e3:.2f} KB key tuples = {mem_sparse_total / 1e3:.2f} KB (O(non-empty zones))")
d_t = min(timeit.repeat(lambda: [dense[r][c] for r, c in cells], number=20, repeat=3)) / 20
s_t = min(timeit.repeat(lambda: [sparse.get((r, c), 0) for r, c in cells], number=20, repeat=3)) / 20
print(f"read 1,000 zones: list of lists {d_t * 1e6:.1f} us | dictionary {s_t * 1e6:.1f} us (both O(1) per access)")
res["grid"] = dict(same=same, mem_dense=mem_dense, mem_sparse=mem_sparse_total, t_dense=d_t, t_sparse=s_t, nonempty=len(sparse))
json.dump(res, open("results.json", "w"), indent=1)
