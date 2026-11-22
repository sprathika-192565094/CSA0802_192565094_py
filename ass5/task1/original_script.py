# ORIGINAL (poor) script from the assignment - only the path changed to a local file
# so that it can be executed for evidence.
f = open("mess_oct.txt")
data = f.read()
total = 0
report = ""
for line in data.split("\n"):
    try:
        parts = line.split(",")
        total = total + int(parts[2])
        report = report + parts[1] + " " + parts[2] + "\n"
    except:
        pass
print(report)
print("Total", total)
