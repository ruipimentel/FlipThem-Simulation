# import numpy as np
# import matplotlib.pyplot as plt
#
# fig, axs = plt.subplots(1, 1)
#
# x = np.linspace(0, 1, 100)
# X, Y = np.meshgrid(x, x)
# # Z = np.sin(X)*np.sin(Y)
#
#
# zdata = np.sin(3*X)*np.sin(5*Y)
#
#
# levels = np.linspace(np.amin(zdata), np.amax(zdata), 4)
#
# cs = axs.contourf(X, Y, zdata, cmap=plt.cm.bone, levels=levels)
# fig.colorbar(cs, ax=axs, format="%.2f")
# #
# # cs = axs[1].contourf(X, Y, zdata, levels=[-1,0,1])
# # fig.colorbar(cs, ax=axs[1])
#
# plt.show()




import matplotlib.pyplot as plt
import numpy as np

# make some data
a = np.random.randn(10,10)

print(a)

# mask some 'bad' data, in your case you would have: data == 0
# a = np.ma.masked_where(a <= 0.0, a)

print(a)

cmap = plt.cm.Blues
# cmap.set_bad(color='white')
#
# plt.imshow(a, interpolation='none', cmap=cmap)
#

#
#
cmap.set_under(color='white')
plt.imshow(a, interpolation='none', cmap=cmap, vmin=0.0000001)
#

plt.show()