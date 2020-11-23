from utility.FringeAnalysisFunctions import *

ks = 5.7325  # factor from phase to depth

# Read in reference and object images
refImg = cv2.imread('../TestPics/S0004000078.jpg', 0)
objImg = cv2.imread('../TestPics/S0004000209.jpg', 0)

plt.imshow(refImg, cmap='gray')
plt.show()
plt.imshow(objImg, cmap='gray')
plt.show()

# Calculate pitch of fringe
pitch = getPitch(refImg)
print(pitch)

# Calculate phase map for reference and object images
phaseRef = fiveStepShift(refImg, pitch, maskHoles=True)
phaseObj = fiveStepShift(objImg, pitch)
# Calculate phase difference
diffPhase = phaseObj - phaseRef
# Unwrap phase difference
unwrappedPhaseMap = unwrapPhase(diffPhase)
# Convert unwrapped phase map to depth
depthMap = unwrappedPhaseMap * ks

plt.imshow(diffPhase)
plt.title('Wrapped Phase Map')
plt.colorbar()
plt.show()
plt.imshow(unwrappedPhaseMap)
plt.title('Unwrapped Phase Map')
plt.colorbar()
plt.show()
