import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def create_block(x_min,y_min,z_min,x_max,y_max,z_max,color,alpha):
    vertices = np.array([
        [x_min, y_min, z_min],
        [x_max, y_min, z_min],
        [x_max, y_max, z_min],
        [x_min, y_max, z_min],
        [x_min, y_min, z_max],
        [x_max, y_min, z_max],
        [x_max, y_max, z_max],
        [x_min, y_max, z_max]
    ])
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[4], vertices[7], vertices[3], vertices[0]]
    ]

    return Poly3DCollection(faces, facecolors = color,edgecolors ='black',linewidth = 1.2, alpha = alpha)

substrate_length = 10
substrate_width = 6
substrate_thickness = 1

fig = plt.figure()
ax = fig.add_subplot(111,projection= '3d')

substrate = create_block(
    0,0,0,substrate_length,substrate_width,substrate_thickness,
    color=(0.45,0.45,0.5),  # P-type color
    alpha=1
)

ax.add_collection3d(substrate)

ax.set_xlim(0, substrate_length)
ax.set_ylim(0, substrate_width)
ax.set_zlim(0, 8)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

plt.show()