import unittest
import numpy
from gmpy2 import mpz

from . import geo

class TestPrime(unittest.TestCase):
    
    def setUp(self):
        self.p = geo.Prime()

    def test_next(self):
        self.assertEqual(self.p.next(), 3)

class TestLegend(unittest.TestCase):

    def setUp(self):

        self.root_hierarchy =  {
            "metadata":{
                "type":"hierarchy"
            },
            "items": {
                "vegetation":{
                    "agriculture":{
                        "crop field":{}
                    },"forest":{
                        "managed":{},
                        "natural":{}
                    }
                    
                },
                "built-up":{
                    "residential":{},
                    "industrial":{},
                    "commercial":{}
                }
            }
        }

        self.root_layers = {
            "metadata":{
                "type":"layers"
            },
            "items": {
                "1":{
                    "agriculture":{},
                    "forest":{}
                },
                "2":{
                    "granite":{},
                    "basalt":{},
                }
            }
        }

        self.root_options = {
            "metadata":{
                "type":"options"
            },
            "items": {
                "crop field": ["option1",  "option2"],
                "built-up": ["urban", "city", "synonym3"]
                }
            }


    def test_put(self):
        
        self.maxDiff = None

        output_legend_hierarchy = {
            "built-up": {
                "child": {
                "commercial": {
                    "child": {},
                    "prime": mpz(31)
                },
                "industrial": {
                    "child": {},
                    "prime":  mpz(29)
                },
                "residential": {
                    "child": {},
                    "prime":  mpz(23)
                }
                },
                "prime":  mpz(19)
            },
            "vegetation": {
                "child": {
                "agriculture": {
                    "child": {
                    "crop field": {
                        "child": {},
                        "prime":  mpz(7)
                    }
                    },
                    "prime": mpz(5)
                },
                "forest": {
                    "child": {
                    "managed": {
                        "child": {},
                        "prime":  mpz(13)
                    },
                    "natural": {
                        "child": {},
                        "prime":  mpz(17)
                    }
                    },
                    "prime":  mpz(11)
                }
                },
                "prime":  mpz(3)
            }
        }

        output_legend_layers = {
                '1': 
                    {'child': {
                        'agriculture': {'child': {}, 'prime':  mpz(5)},
                        'forest': {'child': {}, 'prime':  mpz(7)}},
                    'prime':  mpz(3)}, 
                '2': {'child': {
                    'granite': {'child': {}, 'prime':  mpz(13)},
                    'basalt': {'child': {}, 'prime':  mpz(17)}},
                    'prime':  mpz(11)
                    }
            }
        

        output_legend_options = {
                'crop field': {'child': ['option1', 'option2'], 'prime':  mpz(3)},
                'built-up': {'child': ['urban', 'city', 'synonym3'], 'prime':  mpz(5)}
            }
        
        self.legend = geo.Legend()
        self.legend.put(self.root_hierarchy)
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_hierarchy)

        self.legend = geo.Legend()
        self.legend.put(self.root_layers)
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_layers)

        self.legend = geo.Legend()
        self.legend.put(self.root_options)
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_options)


    def test_additem_1_1(self):

        #
        # Case 1.1: Hiearchy, without parent
        #
        output_legend_hierarchy = {
            "built-up": {
                "child": {
                    "commercial": {
                        "child": {},
                        "prime": mpz(31)
                    },
                    "industrial": {
                        "child": {},
                        "prime":  mpz(29)
                    },
                    "residential": {
                        "child": {},
                        "prime":  mpz(23)
                    }
                },
                "prime":  mpz(19)
            },
            "vegetation": {
                "child": {
                    "agriculture": {
                        "child": {
                        "crop field": {
                            "child": {},
                            "prime":  mpz(7)
                        }
                        },
                        "prime": mpz(5)
                    },
                    "forest": {
                        "child": {
                            "managed": {
                                "child": {},
                                "prime":  mpz(13)
                            },
                            "natural": {
                                "child": {},
                                "prime":  mpz(17)
                            }
                            },
                            "prime":  mpz(11)
                        }
                },
                "prime":  mpz(3)
            },
            "other": {
                "child": {},
                "prime": mpz(37)
            }
        }

        self.legend = geo.Legend()
        self.legend.put(self.root_hierarchy)
        self.legend.addItem(item = "other")
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_hierarchy)


    def test_additem_1_2(self):

        #
        # Case 1.2: Hiearchy, with parent 1st level
        #
        output_legend_hierarchy = {
            "built-up": {
                "child": {
                    "commercial": {
                        "child": {},
                        "prime": mpz(31)
                    },
                    "industrial": {
                        "child": {},
                        "prime":  mpz(29)
                    },
                    "residential": {
                        "child": {},
                        "prime":  mpz(23)
                    },
                    "other": {
                        "child": {},
                        "prime": mpz(37)
                    }
                },
                "prime":  mpz(19)
            },
            "vegetation": {
                "child": {
                "agriculture": {
                    "child": {
                    "crop field": {
                        "child": {},
                        "prime":  mpz(7)
                    }
                    },
                    "prime": mpz(5)
                },
                "forest": {
                    "child": {
                    "managed": {
                        "child": {},
                        "prime":  mpz(13)
                    },
                    "natural": {
                        "child": {},
                        "prime":  mpz(17)
                    }
                    },
                    "prime":  mpz(11)
                }
                },
                "prime":  mpz(3)
            }
        }

        self.legend = None
        self.legend = geo.Legend()
        self.legend.put(self.root_hierarchy)
        self.legend.addItem(item = "other", parent="built-up")
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_hierarchy)


    def test_additem_1_3(self):

        #
        # Case 1.3: Hiearchy, with parent nth level
        #
        output_legend_hierarchy = {
            "built-up": {
                "child": {
                    "commercial": {
                        "child": {},
                        "prime": mpz(31)
                    },
                    "industrial": {
                        "child": {},
                        "prime":  mpz(29)
                    },
                    "residential": {
                        "child": {
                            "other": {
                                "child": {},
                                "prime": mpz(37)
                            }
                        },
                        "prime":  mpz(23)
                    }
                },
                "prime":  mpz(19)
            },
            "vegetation": {
                "child": {
                "agriculture": {
                    "child": {
                    "crop field": {
                        "child": {},
                        "prime":  mpz(7)
                    }
                    },
                    "prime": mpz(5)
                },
                "forest": {
                    "child": {
                    "managed": {
                        "child": {},
                        "prime":  mpz(13)
                    },
                    "natural": {
                        "child": {},
                        "prime":  mpz(17)
                    }
                    },
                    "prime":  mpz(11)
                }
                },
                "prime":  mpz(3)
            }
        }

        self.legend = geo.Legend()
        self.legend.put(self.root_hierarchy)
        self.legend.addItem(item = "other", parent="residential")
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_hierarchy)


    def test_additem_2_1(self):

        #
        # Case 2.1: Layers, without parent
        #
        output_legend_layers = {
                '1': 
                    {'child': {
                        'agriculture': {'child': {}, 'prime':  mpz(5)},
                        'forest': {'child': {}, 'prime':  mpz(7)}},
                    'prime':  mpz(3)}, 
                '2': {'child': {
                    'granite': {'child': {}, 'prime':  mpz(13)},
                    'basalt': {'child': {}, 'prime':  mpz(17)}
                    },
                    'prime':  mpz(11)
                    },
                '3':  {'child': {}, 'prime':  mpz(19)}
            }
        self.legend = geo.Legend()
        self.legend.put(self.root_layers)
        self.legend.addItem(item = "3")
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_layers)


    def test_additem_2_2(self):

        #
        # Case 2.2: Layers, with parent
        #
        output_legend_layers = {
                '1': 
                    {'child': {
                        'agriculture': {'child': {}, 'prime':  mpz(5)},
                        'forest': {'child': {}, 'prime':  mpz(7)}},
                    'prime':  mpz(3)}, 
                '2': {'child': {
                    'granite': {'child': {}, 'prime':  mpz(13)},
                    'basalt': {'child': {}, 'prime':  mpz(17)},
                    'other':  {'child': {}, 'prime':  mpz(19)}
                    },
                    'prime':  mpz(11)
                    }
            }
        self.legend = geo.Legend()
        self.legend.put(self.root_layers)
        self.legend.addItem(item = "other", parent="2")
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_layers)


    def test_additem_3_1(self):

        #
        # Case 3.1: Options, as string
        #
        output_legend_options = {
                'crop field': {'child': ['option1', 'option2'], 'prime':  mpz(3)},
                'built-up': {'child': ['urban', 'city', 'synonym3'], 'prime':  mpz(5)},
                'other': {'child': [], 'prime':  mpz(7)}
            }

        self.legend = geo.Legend()
        self.legend.put(self.root_options)
        self.legend.addItem(item = "other")
        self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_options)


    def test_additem_3_2(self):

        #
        # Case 3.2: Options, as string
        #
        output_legend_options = {
                'crop field': {'child': ['option1', 'option2'], 'prime':  mpz(3)},
                'built-up': {'child': ['urban', 'city', 'synonym3'], 'prime':  mpz(5)},
                'other': {'child': ['option1', 'synonym2'], 'prime':  mpz(7)}
            }

        self.legend = geo.Legend()
        self.legend.put(self.root_options)
        #self.legend.addItem(item = {"other":['option1', 'synonym2']})
        #self.assertDictEqual(self.legend.exportLegend()["items"], output_legend_options)


    def test_additem_fails_1(self):

        self.legend = geo.Legend()
        self.legend.put(self.root_hierarchy)

        with self.assertRaises(Exception):
            self.legend.addItem(item = None)

        with self.assertRaises(Exception):
            self.legend.addItem(item = "")

        with self.assertRaises(Exception):
            self.legend.addItem(item = [])

        with self.assertRaises(Exception):
            self.legend.addItem(item = {"test": "test"})

        with self.assertRaises(Exception):
            self.legend.addItem(item = "new", parent = "Does not exist")


    def test_additem_fails_2(self):

        self.legend = geo.Legend()
        self.legend.put(self.root_layers)

        with self.assertRaises(Exception):
            self.legend.addItem(item = None)

        with self.assertRaises(Exception):
            self.legend.addItem(item = "")

        with self.assertRaises(Exception):
            self.legend.addItem(item = [])

        with self.assertRaises(Exception):
            self.legend.addItem(item = {"test": "test"})  

        with self.assertRaises(Exception):
            self.legend.addItem(item = "new", parent = "Does not exist")


    def test_additem_fails_3(self):

        self.legend = geo.Legend()
        self.legend.put(self.root_options)

        with self.assertRaises(Exception):
            self.legend.addItem(item = None)

        with self.assertRaises(Exception):
            self.legend.addItem(item = "")

        with self.assertRaises(Exception):
            self.legend.addItem(item = [])


class TestRaster(unittest.TestCase):
    
    def setUp(self):
        self.a = numpy.array(
            [
                ["vegetation", "agriculture", "crop field"],
                ["vegetation", "forest", "managed"]
            ])
        self.r = geo.Raster()
        self.legend = geo.Legend()
        root =  {
            "metadata":{
                "type":"hierarchy"
            },
            "items":{
                "vegetation":{
                    "agriculture":{
                        "crop field":{}
                    },"forest":{
                        "managed":{},
                        "natural":{}
                    }
                    
                },
                "built-up":{
                    "residential":{},
                    "industrial":{},
                    "commercial":{}
                }
            }
        }
        self.legend.put(root)

        self.a_part = numpy.array(
            [
                [
                    ["vegetation", "agriculture"],
                    ["vegetation", "forest"]
                ],
                [
                    ["vegetation", "agriculture"],
                    ["vegetation", "forest"]
                ],
            ])
        

        self.new_layer = numpy.array(
            [
                [
                    "crop field",
                    "managed"
                ],
                [
                    "crop field",
                    "managed"
                ],
            ])

        self.mask = numpy.array([
            [
                [1, 1],
                [0, 0]
            ]
        ])

    def test_encode(self):
        expected = [105, 429]
        encoded = self.r.encode(self.a, self.legend, keep=True)
        self.assertTrue((encoded == expected).all())


    def test_decode_stored(self):
        #
        # For testing whether storage in object works.
        #
        r_new = geo.Raster() #this makes sure that this is a completely new object
        r_new.encode(self.a, self.legend, keep=True)
        self.assertTrue(numpy.alltrue(r_new.decode() == self.a))


    def test_decode_extern(self):
        #
        # For testing whether decoding works with data + legend passed to the
        # function.
        #
        encoded = self.r.encode(self.a, self.legend, keep=False)

        r_ext = geo.Raster() #this makes sure that this is a completely new object
        self.assertTrue(numpy.alltrue(r_ext.decode(encoded, self.legend) == self.a))


    def test_mask(self):
        #
        # For testing whether masking works with data + legend stored in object
        #

        #
        # Single categories
        #
        r_new = geo.Raster() #this makes sure that this is a completely new object
        expected_mask = numpy.array([0, 1]) #for "forest"
        r_new.encode(self.a, self.legend, keep=True)
        self.assertTrue(numpy.alltrue(r_new.mask("forest") == expected_mask))

        #
        # Multiple categories
        #
        expected_mask = numpy.array([0, 2]) #for ["forest", "managed"]
        self.assertTrue(numpy.alltrue(r_new.mask(["forest", "managed"]) == expected_mask))

        expected_mask = numpy.array([1, 1]) #for ["forest", "agriculture"]
        self.assertTrue(numpy.alltrue(r_new.mask(["forest", "agriculture"]) == expected_mask))


    def test_mask_extern(self):
        #
        # For testing whether masking works with data + legend passed to the
        # function.
        #
        encoded = self.r.encode(self.a, self.legend, keep=False)

        expected_mask = numpy.array([0, 1]) #for "forest"
        r_ext = geo.Raster() #this makes sure that this is a completely new object
        self.assertTrue(numpy.alltrue(r_ext.mask("forest", encoded, self.legend) == expected_mask))


    def test_exportencoded(self):
        #
        # For testing export of encoded data
        #
        encoded = self.r.encode(self.a, self.legend, keep=False) #option not to keep must raise an error
        with self.assertRaises(Exception):
            self.r.exportEncoded()

        encoded = self.r.encode(self.a, self.legend, keep=True) #option to store works
        self.assertTrue(numpy.alltrue(encoded == self.r.exportEncoded()))
    

    def test_importencoded(self):
        #
        # For testing import
        #
        encoded = self.r.encode(self.a, self.legend, keep=False)
        
        r1 = geo.Raster()
        r1.importEncoded(encoded)

        self.assertTrue(numpy.alltrue(encoded == r1.exportEncoded()))
        
        r2 = geo.Raster()
        r2.importEncoded(encoded, self.legend)

        self.assertTrue(numpy.alltrue(encoded == r2.exportEncoded()))
    

    def test_add(self):
        encoded = self.r.encode(self.a, self.legend, keep=False)

        combined = self.r.add(
            layer = self.new_layer,
            data = self.r.encode(self.a_part,self.legend),
            legend = self.legend,
            keep = False)

        self.assertTrue(numpy.alltrue(encoded == combined))

        #
        # With mask
        #
        encoded = self.r.encode(self.a, self.legend, keep=False)
        combined = self.r.add(
            layer = self.new_layer,
            data = self.r.encode(self.a_part,self.legend),
            legend = self.legend,
            mask = self.mask,
            keep = False)
        expected = numpy.array([
                [105, 429],
                [15, 33]
            ])
        self.assertTrue(numpy.alltrue(expected == combined))


    def test_remove(self):
        removed = self.r.remove(
            layer = self.new_layer,
            data = self.r.encode(self.a, self.legend, keep=False),
            legend = self.legend,
            keep = False)

        part = self.r.encode(self.a_part, self.legend, keep=False)
        self.assertTrue(numpy.alltrue(part == removed))

        #
        # With mask
        #
        removed = self.r.remove(
            layer = self.new_layer,
            data = self.r.encode(self.a, self.legend, keep=False),
            legend = self.legend,
            mask = self.mask,
            keep = False)
        expected = numpy.array([
                [15, 33],
                [105, 429]
            ])
        self.assertTrue(numpy.alltrue(expected == removed))

    def test_destroy(self):
        obj = geo.Raster()
        obj.encode(self.a, self.legend, keep=True)
        obj.mask("forest")
        obj.destroy()
        with self.assertRaises(Exception):
            self.r.mask("forest")

if __name__ == '__main__':
    unittest.main()