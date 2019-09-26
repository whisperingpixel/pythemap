import gmpy2 as gm
import numpy as np
import rapidjson
import logging
import pathlib
import operator

from . import constant

class Prime():
    """Everything related to the prime number operations in this package"""

    def __init__(self):
        self.last_prime = constant.FIRST_PRIME_NUMBER


    def next(self):
        """Returns a prime number, which has not been used yet.

        Returns:
            int: Prime number, which has not been used yet in this session.
        """

        self.last_prime = gm.next_prime(self.last_prime)
        return self.last_prime


    def setStart(self, prime):
        """sets or reset the start value for getting the next prime number.

        Based on a start number, the next prime number will be returned. It starts with 2 by
        default, so the first prime number for a new legend will be 3. However, if a legend is
        imported and then some classes being added later, it is necessary to (re)set the starting
        point, e.g., to the highest prime number in the current legend.

        Args:
            prime (int): Any integer can go here.
        """
        self.last_prime = int(prime)


class Legend():
    """Handling hierarchies"""

    def __init__(self):
        self.legend = {}
        self.type = None
        self.p = Prime()
        self.schema = self._importSchema()


    def _importSchema(self, file = None):
        """Imports the schema from a file in the file system.

        Internal function to import the schema. Optionally, it is possible to pass
        the file location as argument, but it will look in the default path.

        Args:
            file (pathlib.Path or str): (Optional) the path to the file.
        
        Returns:
            str: the schema.
        
        Raises:
            Exception if path is not valid
            Exception if schema is not a valid json
        """        
        if file is None:
            file = pathlib.Path(__file__).parent.parent.joinpath("schemas","legend.json")
        else:
            if type(file) not in [pathlib.WindowsPath,pathlib.Path, pathlib.PosixPath]:
                file = pathlib.Path(file)

        if pathlib.Path.exists(file):
            f = open(file, "r")
            schema = f.read()
            f.close()
            return rapidjson.dumps(schema)
        else:
            error = "File for legend schema {} does not exist".format(file)
            logging.critical(error)
            raise Exception(error)


    def put(self, legend):
        """Takes a valid legend and set it up for use in the encoding / decoding process, the prime numbers
        will be generated automatically.

        A valid legend might look like this:
            root =  {
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

        Args:
            legend (dict): a valid dictionary

        Returns:
            -

        Raises:
            Exception: if legend is not valid.
        """

        self.legend = self._validate(legend)
        self.type = self.legend["metadata"]["type"]
        
        def encodeChildren(pos):
            if type(pos) == dict:
                labels = pos.keys()
                for label in labels:
                    children_tree = pos[label]
                    pos[label] = {"child": children_tree, "prime": self.p.next()}
                    encodeChildren(pos[label]["child"])

        encodeChildren(self.legend["items"])


    def addItem(self, item, parent = None):
        """ 
        Adds an item to the (existing legend)

        Args:
            item (string | json): a valid legend item
            parent (string): (optional) the parent legend item

        Raises:
            Exception: If item is None or an empty string
            Exception: If parent is found, but does not exits
            Exception: If item is not string and legend type is not 'option'
            Exception: If new item is ambigous, i.e., more than one is given
        """

        if item is None or item == "":
            raise Exception("New legend item must not be exmpty.")

        #
        # Reset the start point. Just to be sure
        #
        self.p.setStart(self._findHighestPrime())

        #
        # The child dytpe might be dict or list (empty or filled)
        #
        child_dtype = {}

        #
        # We need some special consideratoons for the legend type "options"
        #
        if self.type == constant.OPTIONS:

        #
        # In case the legend type is options, we need to make sure that there is
        # no parent object. It alters some parts in the definitions later, e.g.,
        # options legends have lists instead of dicts
        #
            parent = None

        #
        # Here, the type might be dict or string. If string, we can simply use it
        #

            if type(item) == dict:
                keys = item.keys()
                if len(keys) != 1:
                    raise Exception("Only one item is allowed")
                options_list = item[list(keys)[0]] # we only care about the first one
                child_dtype = list(set(options_list)) # set the options as dtype
                item = list(keys)[0] # set the string as item for later
            else:
                if type(item) != str:
                    raise Exception ("Item must be string or list when legend type is 'options'")
                child_dtype = []

        #
        # If legend type is not options, only strings are allowed. Hierarchies need to
        # be represented by multiple addings
        #
        else:
            if type(item) != str:
                raise Exception ("Item must be string when legend type is not 'options'")

        
        def _update(labels, target):
            parent_found = False
            for label in labels.keys():
                if label == target:
                    labels[label]["child"][item] = {"child": child_dtype, "prime": self.p.next()}
                    return True
                parent_found = _update(labels[label]["child"], target) or parent_found
            return parent_found

        if parent is None:
            self.legend["items"][item] = {"child": child_dtype, "prime": self.p.next()}
        else:
            if _update(self.legend["items"], parent) == False:
                raise Exception("Parent '{}' not found!".format(parent))


    def exportLegend(self):
        """Exports the legend

        Returns:
            dict: Legend.
        """
        return self.legend
    

    def importLegend(self, legend):
        """Imports a legend.

        Args:
            legend (dict): Legend.
        """
        self.legend = legend
        self.p.setStart(self._findHighestPrime())


    def _validate(self, candidate):
        """Checks whether a legend is valid or not.

        Args:
            candidate (dict): Candidate legend.
        
        Raises:
            Exception if legend does not fit the schmea
        """

        validate = rapidjson.Validator(self.schema)
        validate(rapidjson.dumps(candidate))
        return candidate


    def getLabelByPrime(self, encoded):
        pass
        #TODO: Implement


    def getPrimeByLabel(self, label):
        """Returns the prime number for an encoded category, based on the label in the legend,
        which is stored.

        Args:
            label (?): The label of the category for which the prime number should be returned.
        
        Returns:
            int: The prime number for the corresponding category label.
        """
        
        if type(label) == bytes:
            label = label.decode()

        if label == "null_category":
            return constant.NULL_CATEGORY

        def search(candidate, legend):
            #
            # For legend types "hierarcy" and "layers", this
            # will always be a dictioanry
            #
            if type(legend) == dict:
                for label in legend.keys():

                    if candidate == label:
                        return legend[label]["prime"]
                
                    found = search(candidate, legend[label]["child"])

                    if found == constant.FOUND_IN_CHILDREN:
                        return legend[label]["prime"]

                    if found != constant.NULL_CATEGORY:
                        return found
            
            #
            # For legend type "options", this might be a simple list
            #
            if type(legend) == list:
                for label in legend:
                    if candidate == label:
                        return constant.FOUND_IN_CHILDREN

            return constant.NULL_CATEGORY
                
        return search(label, self.legend["items"])


    def toLayers(self):
        """Transforms the individual legends (e.g. a hierarchical one) into layers.

        This is an internal function, which is helpful to convert the differnet legend types
        into layers, which is a necessary step to decode the data.

        Returns:
            dict: A dictionary with category labels and prime number for each layer.
        """
        def addHierarchyToLayers(legend, layers, index):
            for label in legend.keys():
                if not str(index) in layers.keys():
                    layers[str(index)] = []
                layers[str(index)].append({"label":label, "prime": legend[label]["prime"]})
                if len(legend[label]["child"]) > 0:
                    addHierarchyToLayers(legend[label]["child"], layers, index+1)

        def addLayerToLayers(legend, layers):
            for index, key in enumerate(legend.keys()):
                layers[str(index)] = []
                for label in legend[key]["child"]:
                    layers[str(index)].append({"label":label, "prime": legend[key]["child"][label]["prime"]})

        layers = {}
        if self.type == constant.HIERARCHY:
            addHierarchyToLayers(self.legend["items"], layers, 0)

        if self.type == constant.LAYERS:
            addLayerToLayers(self.legend["items"], layers)

        if self.type == constant.OPTIONS:
            index = '0'
            layers = {index: []}
            for label in self.legend["items"].keys():
                layers[index].append({"label": label, "prime": self.legend["items"][label]["prime"]})
            
            logging.warn("Decoding with multiple options is ambiguous")

        return layers


    def length(self):
        """Returns the length of a legend.

        The length of a legend is the depth of a hierarchy or the number of layers

        Returns:
            int: The length of the legend.
        """
        return len(self.legend["items"])

    
    def _findHighestPrime(self, legend = None):
        """Returns the currently highest prime number in a legend.

        This function may be interally used to extract the highest prime number of a legend.
        The highest prime number is important, e.g., to (re)set the starting point in the Prime class.

        Returns:
            int: The highest prime number.
        """

        if legend is None and self.legend is None:
            error = "Cannot find highest prime number: Legend not found!"
            logging.critical(error)
            raise Exception(error)

        if legend is None:
            legend = self.legend

        def search(highest, legend):
            
            if type(legend) != list: # in use-case 3 "options", it might be a list

                for entry in legend.keys():

                    if legend[entry]["prime"] > highest:
                        highest = legend[entry]["prime"]

                    highest = search(highest, legend[entry]["child"])

            return highest
                
        return search(1, legend["items"])


class Raster():
    """For raster data"""

    def __init__(self):
        self.data = None
        self.legend = Legend()


    def encode(self, data, legend = None, keep = False):
        """Takes a multi-band numpy matrix and encodes it into a single-band numpy matrix.

        Takes a multi-band numpy matrix consisting of classes and returns a single-band
        numpy matrix. Optionally, a known legend can be used for reproducible encoding.

        Args:
            data (numpy.ndarray): multi-band numpy array, which should be encoded. 
            legend (Legend, optional): An optional class legend implemented in the
                Legend class.
            keep (Boolean): Optional switch to keep the data. Default is false.

        Returns:
            numpy.ndarray: Encoded numpy array.
        """

        encoded_data = None

        self.legend = legend

        for i in range(data.shape[-1]):
            sliced = data[...,i]
            encoded = np.ones_like(sliced, dtype=int)
            for label in np.unique(sliced)[::-1].tolist():
                encoded[sliced == label] = self.legend.getPrimeByLabel(label)

            if encoded_data is not None:
                encoded_data = np.multiply(encoded_data, encoded)
            else:
                encoded_data = encoded

        if keep:
            self.data = encoded_data

        return encoded_data


    def decode(self, data = None, legend = None):
        """Takes an encoded single-band numpy matrix and returns the decoded multi-band matrix.

        Takes a single-band numpy, which is encoded and returns the multi-band matrix consisting
        of classes. Optionally, a known legend can be used for decoding.

        Args:
            data (numpy.ndarray): single-band numpy array, which should be decoded. 
            legend (Legend, optional): An optional class legend implemented in the
                Legend class.

        Returns:
            numpy.ndarray: Decoded numpy array.
        """

        #
        # Perform some checks whether all necessary data are availble
        #
        if data is None and self.data is None:
            error = "Can't decode: No data set found or provided."
            logging.critical(error)
            raise Exception(error)            
        
        if legend is None and self.legend is None:
            error = "Can't decode: No legend found."
            logging.critical(error)
            raise Exception(error)

        if data is None:
            data = self.data

        if legend is None:
            legend = self.legend

        #
        # Get legend layer-ready
        #
        layers = legend.toLayers()

        #
        # Iterate through all the "layers"
        #
        for depth in range(len(layers)):
            #
            # Get all categories in layer
            #
            categories = layers[str(depth)]

            #
            # Create an empty array. To this, the output will be matched
            #
            new_slice = np.empty_like(data, dtype=np.chararray)

            #
            # For all categories in this layer, convert prime number back
            #
            for cat in categories:
                new_slice[data % cat["prime"] == 0] = np.array(cat["label"])

            #
            # If this was the first iteration, store it as new data set, else
            # append the new layer to the existing data set
            #
            new_slice = np.expand_dims(new_slice, axis=data.ndim)

            if depth == 0:
                 decoded_data = new_slice
            else:
                decoded_data = np.concatenate((decoded_data, new_slice), axis=data.ndim)

        #
        # Return the transposed data set (it has the same shape as the input npw)
        #
        return decoded_data
        

    def mask(self, labels, data = None, legend = None, logic = 'OR'):
        """Create a mask based on provided label(s) and encoded data.

        Takes encoded data and calculates a mask based on provided labels. The
        labels might be provided as single string or a list of strings. In this
        case

        Args:
            labels (list(str) or str): Either a string with the labels or a list of
                strings with the labels. 
            legend (Legend, optional): An optional class legend implemented in the
                Legend class.
            logic (string, optional): An optional logic operator, can be 'AND' or 'OR'.

        Returns:
            numpy.ndarray: mask
        
        Raises:
            Exception: if no data is stored or provided and mask can't be calculated.
            Exception: if no legend is stored or provided and mask can't be calculated.
            Exception: if logic not one of 'AND' or 'OR'
        """

        #
        # Perform some checks whether all necessary data are availble
        #
        if data is None and self.data is None:
            error = "Can't calculate mask: No data set found or provided."
            logging.critical(error)
            raise Exception(error)
        
        if legend is None and self.legend is None:
            error = "Can't calculate mask: No legend found."
            logging.critical(error)
            raise Exception(error)

        if data is None:
            data = self.data

        if legend is None:
            legend = self.legend

        if type(labels) is not list:
            labels = [labels]
        
        logic = logic.upper()

        allowed_logic = {"AND": operator.mul, "OR": operator.add}
        if logic not in allowed_logic.keys():
            raise Exception("Logic must be one of " + ",".join(allowed_logic).keys())

        #mask = np.zeros_like(data, dtype=int)

        for i,label in enumerate(labels):
            label_encoded = legend.getPrimeByLabel(label)
            if i == 0:
                mask = ((data % label_encoded) == 0).astype(int)
            else:
                mask = allowed_logic[logic](mask, ((data % label_encoded) == 0).astype(int))

        return mask


    def exportEncoded(self):
        """Returns the encoded data.

        If data is stored in the object, they can be exported here. If no data is
        present, an exception will be thrown.

        Returns:
            numpy.ndarray: Encoded numpy array.
        

        Raises:
            Exception: if no data is stored and expert can't be performed.
        """

        if self.data is None:
            error = "No data to export"
            logging.critical(error)
            raise Exception(error)
        
        return self.data


    def importEncoded(self, data, legend = None):
        """Imports the encoded data.

        If data is already encoded, they can be imported here. A legend is optional.

        Args:
            data (numpy.ndarray): Encoded numpy array.
            legend (Legend): An object of the legend class.
        
        """
        self.data = data

        if legend is not None:
            self.legend = legend


    def _sanitise(self, layer):
        """Sanitises values, which are allowed in numpy, but not in pythemap.

        This is an internal function, which replaces all values, which are not allowed in
        pythemap (i.e. where the math breaks) with other values, e.g., "null_category" and
        converts all to strings.

        Args:
            layer (numpy.ndarray): the candidate numpy array.

        Returns:
            numpy.ndarray: The sanitised numpy array.
        """        
        layer[layer == None] = "null_category"
        layer = layer.astype(str)
        return layer


    def _createMaskExisting(self, data, layer):
        """Creates a mask with true values for all cells, where the values in <layer> are
        already stored in <mask>.

        This is an internal function, which helps to keep the semiprimes shorter, because if 
        a new layer contains a value, which is already in data, it will not be multiplied again.

        Args:
            data (numpy.ndarray): the (existing) data.
            layer (numpy.ndarray): the layer with new data.

        Returns:
            numpy.ndarray: The mask.
        """        
        #
        # Create a mask where existing values are 0 and not existing are 1. Then,
        # add with the encoded value of the new layer
        #
        layer = ((data % layer) != 0).astype(int) * layer
        
        #
        # everything which remains 0 should be one, the multiplication with these values
        # do not have an effect
        #
        return (layer == 0).astype(int) + layer


    def _createUserDefinedMask(self, layer, mask):
        """Masks out all values from a layer, if the values are in a cell, which does not have a true
        value in the user-defined mask.

        This is an internal function, which allows users to use a mask in the add/remove functions..

        Args:
            layer (numpy.ndarray): the layer with new data.
            mask (numpy.ndarray): the user-defined mask.

        Returns:
            numpy.ndarray: The layer with masked values.
        """        
        #
        # Create a 0/1 mask
        #
        mask = (mask != 0).astype(int)

        #
        # Multiply layer with mask. If mask == 0, the data will be removed
        #
        layer = layer * mask

        #
        # Replace 0 with 1 as it will be multiplied with the data later
        #
        return layer + (layer == 0).astype(int)


    def add(self, layer = None, data = None, legend = None, mask = None, keep = False):
        """Adds another layer to the encoded dataset

        If data is already encoded, they can be imported here. A legend is optional.

        Args:
            layer (numpy.ndarray): (Optional) numpy array with categorical variables, which should be
                added to the dataset.
            data (numpy.ndarray): (Optional) multi-layer numpy array with categorical variables.
            legend (Legend): (Optional) An object of the legend class, which is used to encode
                the categorical variables.
            mask (numpy.ndarray): (Optional) a numpy array with a mask (0/1 or True/False), for which
                the adding should be done
            keep (boolean): (Optional) a switch to choose whether the data should be stored (updated, if 
                it is already stored) or only returned.
        
        Returns:
            numpy.ndarray: The new dataset
        
        Raises:
            Exception: If data or legend is neither stored nor passed as argument
            Exception: If the shape of layer, data, and mask (or any of these) does not fit.
        """
        
        if legend is None and self.legend is None:
            error = "Can't add: No legend found"
            logging.critical(error)
            raise Exception(error)
            

        if legend is not None:
            legend = self.legend

        if data is None and self.legend is None:
            error = "Can't add: No data found"
            logging.critical(error)
            raise Exception(error)

        if data is None:
            data = self.data

        layer = self._sanitise(layer)

        encoded_layer = np.ones_like(layer, dtype=int)

        for label in np.unique(layer)[::-1].tolist():
            encoded_layer[layer == label] = self.legend.getPrimeByLabel(label)

        encoded_layer = self._createMaskExisting(data, encoded_layer)
        if mask is not None:
            encoded_layer = self._createUserDefinedMask(encoded_layer, mask)
            
        #
        # Multiply the existing encoded data with the encoded layer
        #
        data = data * encoded_layer

        if keep:
            self.data = data

        return data


    def remove(self, data = None, layer = None, legend = None, mask = None, keep = False):
        """Removes a layer from the encoded dataset

        If data is already encoded, they can be imported here. A legend is optional.

        Args:
            layer (numpy.ndarray): (Optional) numpy array with categorical variables, which should be
                added to the dataset.
            data (numpy.ndarray): (Optional) multi-layer numpy array with categorical variables.
            legend (Legend): (Optional) An object of the legend class, which is used to encode
                the categorical variables.
            mask (numpy.ndarray): (Optional) a numpy array with a mask (0/1 or True/False), for which
                the adding should be done
            keep (boolean): (Optional) a switch to choose whether the data should be stored (updated, if 
                it is already stored) or only returned.
        
        Returns:
            numpy.ndarray: The new dataset
        
        Raises:
            Exception: If data or legend is neither stored nor passed as argument
            Exception: If the shape of layer, data, and mask (or any of these) does not fit.
        """
        if legend is None and self.legend is None:
            error = "Can't add: No legend found"
            logging.critical(error)
            raise Exception(error)

        if legend is not None:
            legend = self.legend

        if data is None and self.legend is None:
            error = "Can't add: No data found"
            logging.critical(error)
            raise Exception(error)
        
        if data is None:
            data = self.data

        layer = self._sanitise(layer)

        encoded_layer = np.empty_like(layer, dtype=int)
        
        for label in np.unique(layer)[::-1].tolist():
            encoded_layer[layer == label] = self.legend.getPrimeByLabel(label)
    
        if mask is not None:
            encoded_layer = self._createUserDefinedMask(encoded_layer, mask)

        data = data / encoded_layer
        
        #
        # convert to integer ... it will always be int
        #
        data = data.astype(int)

        if keep:
            self.data = data

        return data


    def destroy(self):
        """Destroys the data and frees the memory.

        """

        del self.data
        del self.legend