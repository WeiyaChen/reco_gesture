from dataAcquisition import DataReceiver
from featureExtraction import FeatureExtractor
from classifier import Rubine

class RecoPipeline:
    """The gesture dependents only on the forme of the hand, and is the same for left and right hand
        The gesture is not on two hands level. More complicated gestures sure dependent on the gestures of both hands
    """
    def __init__(self):
        # for training, use right hand
        self._dataReceiver = DataReceiver(1)

        self._featureExtractor = FeatureExtractor()
        self._classifier = Rubine("conf/feature_list.txt")
        
        # for recognition
        self._dataReceiver_l = DataReceiver(0)
        self._dataReceiver_r = DataReceiver(1)

        self._featureExtractor_l = FeatureExtractor()
        self._featureExtractor_r = FeatureExtractor()
        self._classifier = Rubine("conf/feature_list.txt")
        

    def train(self, file_path, gclass_name):
        """Use samples to train the pipeline (learning process)
            file_path --> the file which contains training samples
            gclass_name --> the name of associated gesture class
        """
        self._dataReceiver.readDataFromFile(file_path)
        if not self._classifier.hasGestureClass(gclass_name):
            self._classifier.createGestureClass(gclass_name)
        
        sample = self._dataReceiver.getOneSampleFrame()
        # while there are still data to treat
        while sample != None:
            self._featureExtractor.addSampleFrame(sample)
            if self._featureExtractor._seg_activated == True:
                rtuple = self._featureExtractor.getRecoTuple()
                #print(rtuple._s_list)
            
                self._classifier.addRecoTupleForTraining(rtuple, gclass_name)
            sample = self._dataReceiver.getOneSampleFrame()
    
        # start the training process
        self._classifier.train(gclass_name)
        self._classifier.showTrainingResult()
            
        # save the trained classifier
        self._classifier.saveClassifierToFile()
        # load the trained data for two empty classifiers, one for each hand
        

    def calcultatePrecision(self, gclass_name):
        """Get the precision of recognition for a given gesture class"""
        return self._classifier.calcultatePrecision(gclass_name)

    def recognition(self):
        """The main function to do gesture recognition"""
        print("Begin recognition process...")

        sample_left = self._dataReceiver_l.getOneSampleFrame()
        sample_right = self._dataReceiver_r.getOneSampleFrame()

        self._featureExtractor_l.addSampleFrame(sample_left)
        if self._featureExtractor_l._seg_activated == True:
            rtuple = self._featureExtractor_l.getRecoTuple()
            self._classifier.recognition(rtuple._s_list)
            print(rtuple._l_or_r, rtuple._timestamp)

        self._featureExtractor_r.addSampleFrame(sample_right)
        if self._featureExtractor_r._seg_activated == True:
            rtuple = self._featureExtractor_r.getRecoTuple()
            self._classifier.recognition(rtuple._s_list)
            print(rtuple._l_or_r, rtuple._timestamp)

    def recognitionFromFile(self, file_path):
        """Gesture recognition for the data stored in a file"""
        print("Begin recognition process from file...")
        self._dataReceiver_l.readDataFromFile("data/final_dataset2.txt")
        self._dataReceiver_r.readDataFromFile("data/final_dataset2.txt")

        sample_left = self._dataReceiver_l.getOneSampleFrame()
        sample_right = self._dataReceiver_r.getOneSampleFrame()

        # while there are still data to treat
        while sample_left != None or sample_right != None:
            if sample_left != None:
                self._featureExtractor_l.addSampleFrame(sample_left)
                if self._featureExtractor_l._seg_activated == True:
                    rtuple = self._featureExtractor_l.getRecoTuple()
                    self._classifier.recognition(rtuple._s_list)
                    print(rtuple._l_or_r, rtuple._timestamp)

            if sample_right != None:
                self._featureExtractor_r.addSampleFrame(sample_right)
                if self._featureExtractor_r._seg_activated == True:
                    rtuple = self._featureExtractor_r.getRecoTuple()
                    self._classifier.recognition(rtuple._s_list)
                    print(rtuple._l_or_r, rtuple._timestamp)

            sample_left = self._dataReceiver_l.getOneSampleFrame()
            sample_right = self._dataReceiver_r.getOneSampleFrame()

if __name__ == "__main__":
    rp = RecoPipeline()
    rp.train("data/flat_twohands.txt", "flat")
    rp.calcultatePrecision("flat")
