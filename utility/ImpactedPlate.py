import time as t
from utility.FringeAnalysisFunctions import *


fileName = fileNameGen('S000400000', 27, 'jpg', 'S0004')
refImg = cv2.imread(fileName, 0)
plt.imshow(refImg, cmap='gray')
plt.show()

pitch = getPitch(refImg)
print('Pitch: '+str(pitch))

phaseRef = fiveStepShift(refImg, pitch, maskHoles=False)

pointA = []
pointB = []
pointC = []
pointD = []
pointE = []
time = []

tic = t.perf_counter()

ks = 5.7325
prefix = 'S000400000'
for i in range(27, 1937):
    fileName = fileNameGen(prefix, i, 'jpg', 'S0004')
    objImg = cv2.imread(fileName, 0)

    # phaseRef = fiveStepShift(refImg, pitch, maskHoles=False)
    phaseObj = fiveStepShift(objImg, pitch, maskHoles=False)

    diffPhase = phaseObj - phaseRef
    # diffPhaseAfter = phaseObjAfter - phaseRef
    
    # unwrappedPhaseMapBefore = unwrap_phase(diffPhaseBefore, True, 100) * ks *1e-3
    unwrappedPhaseMap = unwrap_phase(diffPhase, True, 100) * ks

    frameTime = (i-27)/250.
    time.append(frameTime)
 
    pointA.append(np.average(unwrappedPhaseMap[95:105, 95:105]))
    pointB.append(np.average(unwrappedPhaseMap[395:405, 95:105]))
    pointC.append(np.average(unwrappedPhaseMap[95:105, 395:405]))
    pointD.append(np.average(unwrappedPhaseMap[395:405, 395:405]))
    pointE.append(np.average(unwrappedPhaseMap[260:270, 260:270]))
    print('Processed frame: '+str(i))

toc = t.perf_counter()
print(f"Takes {toc - tic:0.4f} seconds")

print(pointA)

plt.plot(time, pointA)
plt.plot(time, pointB)
plt.plot(time, pointC)
plt.plot(time, pointD)
plt.plot(time, pointE)
plt.show()
# np.savetxt('pointA', pointA)
# np.savetxt('pointB', pointB)
# np.savetxt('pointC', pointC)
# np.savetxt('pointD', pointD)
# np.savetxt('pointE', pointE)


