from matplotlib import cm
from utility.FringeAnalysisFunctions import *

ks = 1  # factor from phase to depth

# Read in reference and object images
refImg = cv2.imread('../TestPics/cone3-r.jpg', 0)
objImg = cv2.imread('../TestPics/cone3.jpg', 0)

# plt.imshow(refImg, cmap='gray')
# plt.show()
# plt.imshow(objImg, cmap='gray')
# plt.show()

# Calculate pitch of fringe
pitch = getPitch(refImg)
print(pitch)

# Calculate phase map for reference and object images
phaseRef = fiveStepShift(refImg, pitch)
phaseObj = fiveStepShift(objImg, pitch)
# Calculate phase difference
diffPhase = phaseObj - phaseRef
# Unwrap phase difference
unwrappedPhaseMap = unwrapPhase(diffPhase)
# Convert unwrapped phase map to depth
depthMap = unwrappedPhaseMap * ks

# plt.imshow(diffPhase)
# plt.title('Wrapped Phase Map')
# plt.colorbar()
# plt.show()
# plt.imshow(unwrappedPhaseMap)
# plt.title('Unwrapped Phase Map')
# plt.colorbar()
# plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
X = np.array([[x for x in range(0, 1000)] for i in range(0, 1000)])
Y = np.array([[x for i in range(0, 1000)] for x in range(0, 1000)])
surf = ax.plot_surface(X, Y, depthMap, rstride=50, cstride=50, cmap=cm.coolwarm, linewidth=0, antialiased=False)
ax.set_zlim(0, 80)
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()
