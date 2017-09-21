import numpy as np
import matplotlib.pyplot as plt

def defender_benefit(def_rate, att_rate, def_cost):
    if def_rate >= att_rate:
        return 1 - (att_rate / (2 * def_rate)) - def_cost * def_rate
    else:
        return def_rate / (2 * att_rate) - def_cost * def_rate


X = np.linspace(0.1, 0.25, 1000)
Y = []

for x in X:
    print(x)
    Y.append(defender_benefit(x, 0.055, 1.0))

plt.plot(X, Y)
plt.xlabel("Defender's rate")
plt.ylabel("Defender's Benefit")

plt.show()
