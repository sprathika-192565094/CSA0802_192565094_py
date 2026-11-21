"""Q5 - Functions, parameters and scope: college canteen order system."""
import json


# ------------------------------------------------------------------ the bug and the fix
def add_item_buggy(item, order=[]):
    order.append(item)
    return order


def add_item(item, order=None):
    # TODO 1 (completed): create a new empty list when order is None, append the item and return the list
    if order is None:
        order = []
    order.append(item)
    return order


# ------------------------------------------------------------------ parameter styles
PRICES = {"Tea": 12, "Vada": 10, "Dosa": 40, "Coffee": 15}


def price_with_gst(item, quantity=1, gst_rate=0.05):
    """item: positional, quantity & gst_rate: default/keyword parameters. Returns TWO values."""
    total = PRICES[item] * quantity
    gst = round(total * gst_rate, 2)
    return total, gst                       # a tuple (total, gst)


# ------------------------------------------------------------------ alternative designs
def new_order():
    """Closure: the order list lives inside the enclosing function, one per customer."""
    order = []

    def add(item):
        order.append(item)
        return order
    return add


def add_item_explicit(item, order):
    """Caller must always pass the list."""
    order.append(item)
    return order


# ------------------------------------------------------------------ scope demonstrations
bill_count = 0


def next_bill_wrong():
    try:
        bill_count += 1                     # UnboundLocalError: assignment makes bill_count local
    except UnboundLocalError as e:
        return f"UnboundLocalError: {e}"


def next_bill_global():
    global bill_count
    bill_count += 1
    return bill_count


def counter():
    count = 0

    def inc():
        nonlocal count                      # rebinds the variable of the enclosing function
        count += 1
        return count
    return inc


def local_demo():
    x = "local"
    return x


if __name__ == "__main__":
    print("=== The bug (output required by the question) ===")
    print(add_item_buggy("Tea"), add_item_buggy("Vada"))
    print(add_item("Tea"), add_item("Vada"))
    print("add_item_buggy.__defaults__ =", add_item_buggy.__defaults__)
    print("add_item.__defaults__       =", add_item.__defaults__)
    print("default list is ONE object created at definition time; it is the list returned by both calls:",
          add_item_buggy.__defaults__[0] is add_item_buggy("x") and add_item_buggy.__defaults__[0].pop() == "x")

    print("\n=== Test with three customers in sequence (fixed design, order passed on for the same customer) ===")
    customers = {}
    for name, wanted in [("Arun", ["Tea", "Vada"]), ("Bala", ["Dosa"]), ("Chitra", ["Coffee", "Vada", "Tea"])]:
        order = None
        for item in wanted:
            order = add_item(item, order)
        customers[name] = order
        print(f"{name:7}: {order}")
    independent = all(len(v) == n for v, n in zip(customers.values(), (2, 1, 3)))
    print("Orders independent of each other:", independent)

    print("\nSame three customers with the BUGGY function:")
    for name, wanted in [("Arun", ["Tea", "Vada"]), ("Bala", ["Dosa"]), ("Chitra", ["Coffee", "Vada", "Tea"])]:
        order = None
        for item in wanted:
            order = add_item_buggy(item) if order is None else add_item_buggy(item, order)
        print(f"{name:7}: {order}")
    print("add_item_buggy.__defaults__ now =", add_item_buggy.__defaults__)

    print("\n=== Alternative designs ===")
    arun, bala = new_order(), new_order()
    arun("Tea"); arun("Vada"); bala("Dosa")
    print("closure -> Arun:", arun("Coffee"), "| Bala:", bala("Tea"))
    a, b = [], []
    add_item_explicit("Tea", a); add_item_explicit("Dosa", b)
    print("explicit list -> a:", a, "| b:", b)

    print("\n=== Parameter styles and multiple return values ===")
    print("positional      :", price_with_gst("Tea", 3))
    print("keyword         :", price_with_gst(item="Dosa", quantity=2))
    print("default only    :", price_with_gst("Vada"))
    print("override default:", price_with_gst("Coffee", quantity=2, gst_rate=0.12))
    total, gst = price_with_gst("Dosa", 2)
    print(f"unpacked        : total={total}, gst={gst}")

    print("\n=== Scope rules ===")
    print("local   :", local_demo(), "| 'x' visible outside?", "x" in globals())
    print("without global:", next_bill_wrong())
    print("with global   :", next_bill_global(), next_bill_global(), "(bill_count =", bill_count, ")")
    c1, c2 = counter(), counter()
    print("nonlocal      :", c1(), c1(), c1(), "| independent counter:", c2())
    json.dump(dict(independent=independent), open("results.json", "w"))
