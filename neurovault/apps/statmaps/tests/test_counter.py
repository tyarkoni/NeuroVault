import json
import os.path
import time
from .utils import clearDB
from operator import itemgetter
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from neurovault.apps.statmaps.utils import count_images_processing
from neurovault.apps.statmaps.forms import NIDMResultsForm
from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from neurovault.apps.statmaps.models import Atlas, Collection, Image,StatisticMap

class Test_Counter(TestCase):
    def setUp(self):
        print "\n\n### TESTING COUNTER ###"
        self.test_path = os.path.abspath(os.path.dirname(__file__))
        self.user = User.objects.create(username='neurovault')
        self.client = Client()
        self.client.login(username=self.user)
        self.Collection1 = Collection(name='Collection1',owner=self.user)
        self.Collection1.save()


    def tearDown(self):
        clearDB()

    # An empty database should have zero images still processing
    def test_empty_database(self):
        images_processing = count_images_processing()
        print "%s images processing [should be 0]" %(images_processing)
        assert_equal(images_processing,0)

    def test_statmaps_processing(self):

        # The counter is the count of the number of images with the field "transform" set to None
        # The field is populated with the file when image comparisons are done, meaning that if there is only one
        # image in the database (case below) we cannot calculate comparisons, and the "transform" field remains none
        # This is currently the only way that we can test the counter, which will be "1" in this case
        print "\nTesting Counter - added statistic maps ###" 
        Image1 = StatisticMap(name='Image1', collection=self.Collection1, file='motor_lips.nii.gz', map_type="Z")
        Image1.file = SimpleUploadedFile('motor_lips.nii.gz', file(os.path.join(self.test_path,'test_data/statmaps/motor_lips.nii.gz')).read())
        Image1.save()
        images_processing = count_images_processing()
        print "%s images processing [should be 1]" %(images_processing)
        assert_equal(images_processing,1)

        # When we add an image, the comparison will be calculated with image1, and both images transform fields will be populated
        # the counter will be set to 0.  Celery runs in synchronous mode when testing (meaning that jobs are run locally, one
        # after the other, instead of being sent to worker nodes) so there is no way to test submitting a batch of async
        # jobs and watching the "images still processing" counter go from N to 0. There is also no way of arbitrarily
        # setting an image transform field to "None" because on save, all image comparisons are automatically re-calcualted        
        Image2 = StatisticMap(name='Image2', collection=self.Collection1, file='beta_0001.nii.gz', map_type="Other")
        Image2.file = SimpleUploadedFile('beta_0001.nii.gz', file(os.path.join(self.test_path,'test_data/statmaps/beta_0001.nii.gz')).read())
        Image2.save()
        images_processing = count_images_processing()
        print "%s images processing [should be 0]" %(images_processing)
        assert_equal(images_processing,0)

