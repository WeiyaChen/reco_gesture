from recoUtils import Matrix

class ARTGloveFrame:
    """The structure which contains a frame of tracking data"""
    def __init__(self):
        self._fr = 0
        self._timestamp = 0
        self._gl = 0
        self._glove_list = None

    def __str__(self):
        res = "FrameID: "+str(self._fr)+"\nTimestamp: "+str(self._timestamp)+"\nGloveNb: "+str(self._gl)+"\n"
        i = 0
        while i < self._gl:
            res += str(self._glove_list[i])+'\n'
            i += 1
        return res


class Finger:
    """The structure to store the raw data of a finger"""
    def __init__(self, n, pos, ori, radtip, phalen, phaang):
        self._name = n
        # A list (x, y, z)
        self._position = pos
        # A list containing a 3*3 orientation matrix
        self._orientation = ori
        # the radius of the finger tip
        self._radius_tip = radtip
        # A list: length for 3 phalanx
        self._phalanx_length = phalen
        # A list: 2 angles between 3 phalanx
        self._phalanx_angles = phaang

    def __str__(self):
        res = "Name: "+str(self._name)+"\nPosition: "+str(self._position)+"\nOrientation: "+str(self._orientation)
        res += "\nTipRadius: "+str(self._radius_tip)+"\nPhalanxLength: "+str(self._phalanx_length)+"\nPalanxAngle: "+str(self._phalanx_angles)+'\n'
        return res

class Glove:
    """The structure to store the raw data of a hand (coming from the glove of course)"""
    def __init__(self, t, gid, q, lr, fn, fingers, pos, ori):
        self._timestamp = t
        self._id = gid
        self._quality = q
        # 0 -> left, 1 -> right
        self._l_or_r = lr
        self._finger_number = fn
        # A list (x, y, z)
        self._position = pos
        # A list containing a 3*3 orientation matrix
        self._orientation = ori
        # A list of fingers
        self._fingers = fingers

    def __str__(self):
        res = "Timestamp: "+str(self._timestamp)+"\nID: "+str(self._id)+"\nQuality: "+str(self._quality)+"\nLR: "
        if self._l_or_r == 0:
            res += "left"
        else:
            res += "right"
        res += "\nFingerNumber: "+str(self._finger_number)+"\nFingers:\n"
        for finger in self._fingers:
            res += str(finger)

        return res


class RecoTuple:
    """To store the data of a glove after feature extraction"""
    def __init__(self, t, gid, q, lr, fn, slist):
        self._timestamp = t
        self._id = gid
        self._quality = q
        self._l_or_r = lr
        self._finger_number = fn
        self._s_list = slist # A list of average value for each feature


class Feature:
    """A character which can help to determine a gesture, e.g., the distance between the hand center and index tip"""
    def __init__(self, n, w=0):
        self._name = n
        self._weight = w

    def setWeight(self, w):
        self._weight = w
    

class GestureClass:
    """Represents a type of gesture"""
    def __init__(self, n, flist):
        self._name = n
        self._feature_list = flist
        self._sample_list = list()
        
        self._train_sample_nb = 0
        self._base_weight = 0
        self._co_matrix = Matrix(len(self._feature_list))
    
        #self._trained = False

    def __str__(self):
        res = "<class>\n" + self._name + "\n"
        for f in self._feature_list:
            res += f._name + ":" + str(f._weight) + "\n"
        res += str(self._base_weight) + "\n"
        res += str(self._train_sample_nb) + "\n<samples>\n"
        for s in self._sample_list:
            for ele in s:
                res += str(ele) + " "
            res += "\n"
        res += "</samples>\n</class>\n"
        return res
    
    def getFeatureAverage(self, f_id):
        """Calcultate the average value of a given feature"""
        res = 0
        i = 0
        while i < self._train_sample_nb:
            res += self._sample_list[i][f_id]
            i += 1
        res = res / len(self._sample_list)
        return res

    def calculateCovarianceMatrix(self):
        i = 0
        j = 0
        while i < self._co_matrix._size:
            while j < self._co_matrix._size:
                res = 0
                k = 0
                while k < self._train_sample_nb:
                    res += (self._sample_list[k][i] - self.getFeatureAverage(i)) * (self._sample_list[k][j] - self.getFeatureAverage(j))
                    k += 1
                self._co_matrix.set(i,j,res)
                j += 1
            j = 0
            i += 1

        print("Covariance Matrix is done for gesture <",self._name,">")

    def calculateFeatureWeight(self, inv_ccmatrix):
        if inv_ccmatrix is None:
            print("Calculate inverse ccmatrix first")
            return None
        else:
            w = 0
            i = 0
            f_id = 0
            while f_id < len(self._feature_list):
                while i < len(self._feature_list):
                    w += inv_ccmatrix.get(i,f_id) * self.getFeatureAverage(i)
                    i += 1
                i = 0
                self._feature_list[f_id].setWeight(w)
                f_id += 1
            print("Feature weights calculation is done.")
        
    def calculateBaseWeight(self):
        w = 0
        i = 0
        while i < len(self._feature_list):
            w += self._feature_list[i]._weight * self.getFeatureAverage(i)
            i += 1
        w = - (w / 2)
        self._base_weight = w
        print("Base weight calculation is done.")

    def showTrainingResult(self):
        print("Class Name:",self._name,"\nBase weight:",self._base_weight)
        for f in self._feature_list:
            print(f._name,":",f._weight)

    def giveScore(self, s_list):
        """Give a score for the input recoTuple"""
        res = 0
        i = 0
        while i < len(self._feature_list):
            res += self._feature_list[i]._weight * s_list[i]
            i += 1
        return res + self._base_weight

