from matplotlib import cm
from utility.FringeAnalysisFunctions import *

ks = 1  # factor from phase to depth

# Read in reference and object images
refImg = cv2.imread('../TestPics/cone2-r.jpg', 0)
objImg = cv2.imread('../TestPics/cone2.jpg', 0)

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

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# X = np.array([[x for x in range(0, 1000)] for i in range(0, 1000)])
# Y = np.array([[x for i in range(0, 1000)] for x in range(0, 1000)])
# surf = ax.plot_surface(X, Y, depthMap, rstride=50, cstride=50, cmap=cm.coolwarm, linewidth=0, antialiased=False)
# ax.set_zlim(0, 80)
# fig.colorbar(surf, shrink=0.5, aspect=5)
#
# plt.show()

max_depth = -1000
min_depth = 1000

for row in depthMap:
    for elem in row:
        if elem >= max_depth:
            max_depth = elem
        if elem <= min_depth:
            min_depth = elem

step = 256 / (max_depth - min_depth)

gray = np.array([[int((elem - min_depth) * step) for elem in row] for row in depthMap])
# gray = np.array([[80 if elem > 6 else 3 for elem in row] for row in gray])
gray = gray.astype(np.uint8)
gray = cv2.medianBlur(gray, 5)

gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 2)

print(gray)

plt.imshow(gray)
plt.show()

circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1,
                           gray.shape[0],
                           param1=50, param2=5,
                           minRadius=1, maxRadius=int(gray.shape[0] / 2))

if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        center = (i[0], i[1])
        # circle center
        cv2.circle(objImg, center, 1, (0, 100, 100), 3)
        # circle outline
        radius = i[2]
        cv2.circle(objImg, center, radius, (255, 0, 255), 3)

cv2.imshow("detected circles", objImg)
cv2.waitKey(0)
