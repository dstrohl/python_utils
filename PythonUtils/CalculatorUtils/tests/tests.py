# from django.apps import apps
# from django.db import models
# from django.test import TestCase
# import django

import unittest

from common.utils import generatePercentages


# django.setup(
#             )

class UtilityTests( unittest.TestCase ):
    def test_generatePercentages( self ):

        data_array = [{'key':'A10',
                       'values': [{'quarter':1, 'measure':1},
                                  {'quarter':2, 'measure':4},
                                  {'quarter':3, 'measure':500},
                                  {'quarter':4, 'measure':5.2234},
                                  {'quarter':5, 'measure':400},
                                  {'quarter':6, 'measure':0}, ]},
                      {'key':'Radware',
                       'values': [{'quarter':1, 'measure':4},
                                  {'quarter':2, 'measure':4},
                                  {'quarter':3, 'measure':5000},
                                  {'quarter':4, 'measure':5.0345},
                                  {'quarter':5, 'measure':401},
                                  {'quarter':6, 'measure':0}, ]},
                      {'key':'Citrix',
                       'values': [{'quarter':1, 'measure':45},
                                  {'quarter':2, 'measure':4},
                                  {'quarter':3, 'measure':50000},
                                  {'quarter':4, 'measure':0},
                                  {'quarter':5, 'measure':402},
                                  {'quarter':6, 'measure':0}, ]},
                      {'key':'Brocade',
                       'values': [{'quarter':1, 'measure':50},
                                  {'quarter':2, 'measure':4},
                                  {'quarter':3, 'measure':50000.0001},
                                  {'quarter':4, 'measure':10},
                                  {'quarter':5, 'measure':403},
                                  {'quarter':6, 'measure':0}, ]},

                      ]

        data_array_2 = [{'key':'A10',
                       'values': [[1, 1],
                                  [2, 4],
                                  [3, 500],
                                  [4, 5.2234],
                                  [5, 400],
                                  [6, 0], ]},
                      {'key':'Radware',
                       'values': [[1, 4],
                                  [2, 4],
                                  [3, 5000],
                                  [4, 5.0345],
                                  [5, 401],
                                  [6, 0], ]},
                      {'key':'Citrix',
                       'values': [[1, 45],
                                  [2, 4],
                                  [3, 50000],
                                  [4, 0],
                                  [5, 402],
                                  [6, 0], ]},
                      {'key':'Brocade',
                       'values': [[1, 50],
                                  [2, 4],
                                  [3, 50000.0001],
                                  [4, 10],
                                  [5, 403],
                                  [6, 0], ]},

                      ]


        # generatePercentages( data_array, 'values', 'measure' , 'newfield' )
        generatePercentages( data_array_2, 'values', 1 )




        # self.assertEqual( str( tmpQuery ), str( expected ) )
