#!/usr/bin/env/ python3
"""Library to simplify working with the OVAL XML structure


Authors: Gunnar Engelbach <Gunnar.Engelbach@ThreatGuard.com>



Available classes:
    - OvalDocument:    operations at the OVAL document level, such as reading in an existing OVAL document from
file, creating a new one, finding or adding OVAL elements
    - OvalElement:    the base class for OVAL elements.  Implements a few common methods inherited by the
subclasses for definition, test, state, object, and variable
    - OvalDefinition:    a type of OVAL element with certain attributes available.  Additional classes used by the OvalDefinition class:
        - OvalMetadata:    the metadata associated with a definition, which includes the definition title and description.  Metadata also contains:
            - OvalAffected:    The family and platforms affected by this definition
            - OvalRepositoryInformation:    Additional information added by the OVAL repository
    - OvalTest:    for working with OVAL test elements
    - OvalObject:    for working with OVAL object elements
    - OvalState:    for working with OVAL state elements
    - OvalVariable:    for working with OVAL variable elements



Available exceptions:
    - None at this time
    
    
:Usage:

1. Create an OvalDocument:

    >>> tree = ElementTree()
    >>> tree.parse("OvalTest.xml")
    >>> document = OvalDocument(tree)

2. Find an oval element within the loaded document:

    >>> element = document.getElementByID("oval:org.mitre.oval:def:22382")
    >>> if element is not None:
    >>>    ....

3. Read an XML file with a single OVAL Definition (error checking omitted for brevity):

    >>> tree = ElementTree()    
    >>> tree.parse('test-definition.xml')
    >>> root = tree.getroot()    
    >>> definition = lib_oval.OvalDefinition(root)
    
4. Change information in the definition from #3 and write the changes

    >>> meta = definition.getMetadata()
    >>> repo = meta.getOvalRepositoryInformation()
    >>> repo.setMinimumSchemaVersion("5.9")
    >>> tree.write("outfilename.xml", UTF-8", True)




  

TODO:
    - Add exceptions that give more detail about why a value of None is sometimes returned
    - Expand use of find() to allow for the possibility that the XML document is not using namespaces
    - Lots of pydoc to be added
    - Redo getter/setter for OvalRepository status.

"""

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import lib_repo

import datetime



# __docformat__ = "Epytext en"



class OvalDocument(object):
    """
    For working with OVAL documents.  That interaction will entail the use of the other classes.
    Can be used to find certain elements within the document, update the document, and save the changes to a file
    """
        
    
    # A time format to match what OVAL expects
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
    
    NS_DEFAULT  = {"def": "http://oval.mitre.org/XMLSchema/oval-definitions-5"}
    NS_OVAL     = {"oval": "http://oval.mitre.org/XMLSchema/oval-common-5"}
    NS_XSI      = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    
#     xmlns:oval="http://oval.mitre.org/XMLSchema/oval-common-5" 
#     xmlns:oval-def="http://oval.mitre.org/XMLSchema/oval-definitions-5" 
#     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
#     xsi:schemaLocation="http://oval.mitre.org/XMLSchema/oval-definitions-5 oval-definitions-schema.xsd
#     http://oval.mitre.org/XMLSchema/oval-definitions-5#independent independent-definitions-schema.xsd 
#     http://oval.mitre.org/XMLSchema/oval-definitions-5#solaris solaris-definitions-schema.xsd 
#     http://oval.mitre.org/XMLSchema/oval-common-5 oval-common-schema.xsd 
#     http://oval.mitre.org/XMLSchema/oval-definitions-5#unix unix-definitions-schema.xsd">^M
    
    
    @staticmethod
    def indent(elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                OvalDocument.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i    
    
    
    @staticmethod            
    def getOvalTimestamp(timestamp=None):
        """Renders a datetime to a string formatted according to the OVAL specification.
        if the timestamp argument is None (which it is by default) or is not of type datetime,
        this function will return a string using the current datetime.
        
        @type timestamp: datetime
        @param timestamp: A datetime to be formatted as an OVAL timestamp, or None to use the current time.
        
        @rtype: string
        @return: a string formatted as per OVAL
        """
        if timestamp is None or not isinstance(timestamp, datetime):
            now = datetime.date.today() 
            return now.strftime(OvalDocument.TIME_FORMAT)
        else:
            return timestamp.strftime(OvalDocument.TIME_FORMAT)
 
    
    
    def __init__(self, tree):
#         if not tree or not isinstance(tree, ElementTree):
        if not tree:
            self.tree = None
            return        
        
        self.tree = tree
        
        
    def parseFromFile(self, filename):
        """
        Load an OVAL document from a filename and parse that into an ElementTree
        Returns False if the filename is empty or there is an error parsing the XML document
        @type filename: string
        @param filename: The path to the OVAL XML document to parse
        
        @rtype:    boolean
        @return:    True on success, otherwise False
        """
        try: 
            if not filename:
                self.tree = None
                return False
            else:
                self.tree = ElementTree.parse(filename)
                return True
        except Exception:
            return False
        
        
    def parseFromText(self, xmltext):
        """
        Initializes the ElementTree by parsing the xmltext as XML
        Returns False if the string could not be parsed as XML
        
        @rtype:    boolean
        @return:    True on success, otherwise False
        """
        try:
            if not xmltext:
                return False
            else:
                root = ElementTree.fromstring(xmltext)
                self.tree = ElementTree(root)
                return True
        except Exception:
            return False
            
            
    def writeToFile(self, filename):
        """
        Writes the internal representation of the XmlTree to the given file name
        Returns False on error
        
        @rtype:    boolean
        @return:    True on success, otherwise False
        """
        try:
            if not filename:
                return False
            if not self.tree:
                return False
            
            ### TODO:  Add all necessary namespaces
            self.tree.write(filename, "UTF-8", True, OvalDocument.NS_DEFAULT, "xml")
                
        except Exception:
            return False
    
        
    def getDocumentRoot(self):
        """
        Returns the root element of the XML tree if one has been loaded.
        Otherwise, returns None
        
        @rtype:    Element
        @return:    The root Element of the OVAL document, or None
        """
        if not self.tree:
            return None
        
        return self.tree.getroot()
    
    
    def getGenerator(self, create=False):
        """
        Gets the generator for this OVAL document as an OvalGenerator object.
        If the generator element does not exist, the default behavior is to
        return none.  However, setting the optional parameter to True will cause
        a default generate element to be created, added to the document, and that will be returned.
        A value of None may also be returned if this OvalDocument is empty
        
        @rtype:    OvalGenerator
        @return:    An OvalGenerator object, or None if it does not exist and create was not set to True
        """
        if not self.tree:
            return None
        
        root = self.getDocumentRoot()
        if not root:
            return None
        
        gen_element = root.find("def:generator", OvalDocument.NS_DEFAULT)
        
        if gen_element is not None:
            return OvalGenerator(gen_element)
        
        if not create:
            return None
        else:
            element = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}generator")
            gen = OvalGenerator(element)
            gen.setProduct("The CIS OVAL Repository")
            gen.setTimestamp(None)
            gen.setVersion("5.10.1")
            return gen
            
    
    
                
    def getDefinitions(self):
        """
        Returns a list of all definitions found in this OvalDocment where each item in the list is of type OvalDefinition
        Returns None if no definitions could be found
        
        @rtype:    List
        @return:    All definitions in the OVAL document or None if none were found
        """
        root = self.getDocumentRoot()
        if not root:
            return None
        
        defroot = root.find("def:definitions", OvalDocument.NS_DEFAULT)
        
        if defroot is None:
            return None
        
        element_list = list(defroot)
        if not element_list:
            return None
        
        return [OvalDefinition(element) for element in element_list]
        
        

        
    def getTests(self):
        """
        Returns a list of all tests in this OvalDocument where each list item is of type OvalTest
        Returns None if no tests could be found
        
        @rtype:    List
        @return:    All tests in the OVAL document or None if none were found
        """
        root = self.getDocumentRoot()
        if not root:
            return None
        
        testroot = root.find("def:tests", OvalDocument.NS_DEFAULT)

        if testroot is None:
            return None
        
        element_list = list(testroot)
        if not element_list:
            return None
        
        return [OvalTest(element) for element in element_list]
        
        
        
    def getObjects(self):
        """
        Returns a list of all objects in this OvalDocument where each list item is of type OvalObject
        Returns None if no objects could be found
        
        @rtype:    List
        @return:    All objects in the OVAL document or None if none were found
        """
        root = self.getDocumentRoot()
        if not root:
            return None
        
        objectroot = root.find("def:objects", OvalDocument.NS_DEFAULT)
        
        if objectroot is None:
            return None
        
        element_list = list(objectroot)
        if not element_list:
            return None
        
        return [OvalObject(element) for element in element_list]
    
        
        
    def getStates(self):
        """
        Returns a list of all states in this OvalDocument where each list item is of type OvalState
        Returns None if no states could be found
        
        @rtype:    List
        @return:    All states in the OVAL document or None if none were found
        """
        root = self.getDocumentRoot()
        if not root:
            return None
        
        stateroot = root.find("def:states", OvalDocument.NS_DEFAULT)
        
        if stateroot is None:
            return None
        
        element_list = list(stateroot)
        if not element_list:
            return None
        
        return [OvalState(element) for element in element_list]
        
        
        
        
    def getVariables(self):
        """
        Returns a list of all variables in this OvalDocument where each list item is of type OvalVariable
        Returns None if no variables could be found
        
        @rtype:    List
        @return:    All variables in the OVAL document or None if none were found
        """
        root = self.getDocumentRoot()
        if not root:
            return None
        
        varroot = root.find("def:variables", OvalDocument.NS_DEFAULT)
        
        if varroot is None:
            return None
        
        element_list = list(varroot)
        if not element_list:
            return None
        
        return [OvalVariable(element) for element in element_list]
        
        
        
        
    def getElementByID(self, ovalid):
        """
        Uses the ovalid argument to determine what type of element is being referenced and locate that element
        in the OVAL ElementTree.
        Returns an OvalElement of the appropriate class (OvalDefinition, OvalTest, ...) 
        or None if there is no ElementTree or if a matching item could not be found
        
        @rtype:    OvalElement
        @return:    The located element as the appropriate OvalElement subclass, or None if no matching element was found.
        """
        if not ovalid:
            return None
        
        root = self.getDocumentRoot()
        if not root:
            return None
        
        try:
            oval_type = lib_repo.get_element_type_from_oval_id(ovalid)
        except Exception:
            return None
        
        if oval_type == OvalDefinition.DEFINITION:
            elist = self.getDefinitions()
        elif oval_type == OvalDefinition.TEST:
            elist = self.getTests()
        elif oval_type == OvalDefinition.OBJECT:
            elist = self.getObjects()
        elif oval_type == OvalDefinition.STATE:
            elist = self.getStates()
        elif oval_type == OvalDefinition.VARIABLE:
            elist = self.getVariables()
        else:
            return None
            
        if not elist:
            return None
        
        for element in elist:
            defid = element.getId()
            if defid and defid == ovalid:
                return element
            
                    
        
    
    def addElement(self, element, replace=True):
        """
        Adds the element to the ElementTree for this OVAL document
        The element argument must be of type OvalElement
        This method uses the OVALID of the element to determine what type of element it is
        and if an existing element with that OVALID already exists.
        This method will also create the necessary structure (id est, adding <definitions>, <tests>, etc)
        if the ElementTree does not already contain it.
        By default this method will replace an existing item with the same OVALID, but this behavior can
        be overridden by changing the option second argument to a value of "False"
        Returns True on success, otherwise False
        
        @rtype:    boolean
        @return:    True if the element was added to the document, otherwise False
        """
        if not element or element is None:
            return False
        if not self.tree or self.tree is None:
            return False
        
        ovalid = element.getId()
        if not ovalid:
            return False
        
        root = self.tree.getroot()
        if not root:
            root = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}oval_definitions")
            self.tree._setroot(root)
            
        # If replace has been set to False, then we want to exit with no changes
        #  when an element with this OVALID already appears in the document            
        if not replace:
            existing = self.getElementByID(ovalid)
            if existing:
                return False;
            
        
        try:
            oval_type = lib_repo.get_element_type_from_oval_id(ovalid)
        except Exception:
            return False
                
        # Depending on the ID type, find the parent for it or create that parent if it doesn't exist
        # Then append the current element
        if oval_type == OvalDefinition.DEFINITION:
            parent = root.find("def:definitions", OvalDocument.NS_DEFAULT)
            if parent is None:
                parent = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}definitions")
                root.append(parent)
                
            parent.append(element)
            return True
        
        elif oval_type == OvalDefinition.TEST:
            parent = root.find("def:tests", OvalDocument.NS_DEFAULT)
            if parent is None:
                parent = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}tests")
                root.append(parent)
                
            parent.append(element)
            return True
        
        elif oval_type == OvalDefinition.OBJECT:
            parent = root.find("def:objects", OvalDocument.NS_DEFAULT)
            if parent is None:
                parent = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}objects")
                root.append(parent)
                
            parent.append(element)
            return True
        
        elif oval_type == OvalDefinition.STATE:
            parent = root.find("def:states", OvalDocument.NS_DEFAULT)
            if parent is None:
                parent = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}states")
                root.append(parent)
                
            parent.append(element)
            return True
        
        elif oval_type == OvalDefinition.VARIABLE:
            parent = root.find("def:variables", OvalDocument.NS_DEFAULT)
            if parent is None:
                parent = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}variables")
                root.append(parent)
                
            parent.append(element)
            return True
        
        else:
            return False

#--------------------- END OF OvalDocument class ----------------------------



class OvalGenerator(object):
    """
    Contains information about this OvalDocument, such as the schema version, the product that produced it, and when it was produced
    """
    
    def __init__(self, element):
        self.element = element
        
        
    def getProduct(self):
        """
        Gets the value of the product element
        """
        if not self.element:
            return None
        
                    
#         child = self.element.find("{http://oval.mitre.org/XMLSchema/oval-common-5}product_name")
        child = self.element.find("oval:product_name", OvalDocument.NS_OVAL)
        if child is None:
            return None
        else:            
            return child.text
            
        
        
    def setProduct(self, product):
        """
        Sets a value for the product element.  If a product element does not already exist, one will be created
        """
        if not self.element:
            return False
        
        if not product:
            return False

        child = self.element.find("oval:product_name", OvalDocument.NS_OVAL)
        if child is not None:
            child.text = product
        else:
            child = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}product_name")
            child.text = product
            self.element.append(child)
            
        
        
    def getSchemaVersion(self):
        """
        Gets the value of the schema_version element
        """
        if not self.element:
            return None
        
        child = self.element.find("oval:schema_version", OvalDocument.NS_OVAL)
        if child is not None:
            return child.text
        else:
            return None
        
        
    def setSchemaVersion(self, version):
        """
        Sets a value for the schema_version element.  If that element does not exist, one will be created.
        """
        if not self.element:
            return False
        
        if not version:
            return False
        
        child = self.element.find("oval:schema_version", OvalDocument.NS_OVAL)
        if child is not None:
            child.text = version
        else:
            child = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}schema_version")
            child.text = version
            self.element.append(child)

        
    def getTimestamp(self):
        """
        Gets the value of the timestamp element
        """
        if not self.element:
            return None
        
        child = self.element.find("oval:timestamp", OvalDocument.NS_OVAL)
        if child is not None:
            return child.text
        else:
            return None


    def setTimestamp(self, timestamp):
        """
        Sets a value for the timestamp element.  If that elememtn does not exist, one will be created.
        If the timestamp argument is set to None, the timestamp will be set to the current time.
        """
        if not self.element:
            return False
        
        if not timestamp:
            now = datetime.date.today()
            timestamp = now.strftime(OvalDocument.TIME_FORMAT)
                    
        child = self.element.find("oval:timestamp", OvalDocument.NS_OVAL)
        if child is not None:
            child.text = timestamp
        else:
            child = Element("{" + OvalDocument.NS_OVAL.get("oval") + "}timestamp")
            child.text = timestamp
            self.element.append(child)
        
        
    def getExtra(self, name, namespace=None):
        """
        Gets the value of the first child element of the generator where the tag name matches 'name'
        If the namespace argument is not provided, it will be assumed that the child element does not have a namespace.
        """
        if not self.element:
            return None
        
        if not name:
            return None
        
        if namespace is not None:
            child = self.element.find(name, namespace)
        else:
            child = self.element.find(name)
            
        if child is not None:
            return child.text
        else:
            return None


    def setExtra(self, name, value, namespace=None):
        """
        Sets the value if the first child element with a tag name of 'name' to 'value'.  If the namespace argument is None,
        it will be assumed that the child element does not have a namespace
        """
        if not self.element or not name or not value:
            return None
        
        if namespace is not None:
            child = self.element.find(name, namespace)
        else:
            child = self.element.find(name)
            
        if child is not None:
            child.text = value
        else:
            if namespace is not None:
                child = Element(name)
            else:
                child = Element(name, namespace)
            child.text = value
            self.element.append(child)
        
        


class OvalElement(object):
    """
    The base class for the primary OVAL XML Elements.  Contains a few basic operations common to all
    OVAL Elements.
    TODO:
    """
    
    DEFINITION = "definition"
    TEST = "test"
    OBJECT = "object"
    STATE = "state"
    VARIABLE = "variable"


    def __init__(self, element):
        self.element = element
        
                
        
    def getId(self):
        """
        Returns the OVAL ID for this element, or None if
         1. This object was instantiated without an Element
         2. The underlying element does not have an "id" attribute
        """
        if not self.element:
            return None
        
        return self.element.get("id")
        
        
    def setId(self, ovalid):
        """
        Sets the OVAL ID for this element
        Returns False if there is no underlying Xml ELement for this object
        """
        
        if not self.element:
            return False
        
        if ovalid is not None:
            self.element.set("id", ovalid)


    def getVersion(self):
        if not self.element:
            return None
        
        return self.element.get("version")
    
    
    def setVersion(self, version):
        if not self.element:
            return False
        if not version:
            return False
        if not isinstance(version, int):
            return False
        
        self.element.set("version", version)
        return True
    
    
    def incrementVersion(self):
        version = self.getVersion()
        if not version:
            version = 1
        else:
            if not isinstance(version, int):
                version = 1
            else:
                version = version + 1
        
        self.setVersion(version)
        
        
        
    def getIndexSequence(self):
        ovalid = self.getId()
        if not ovalid or ovalid is None:
            return 1000
        
        # Get the numeric index from the end of the OVAL ID
        position = ovalid.rfind(':')
        if position < 0:
            return 1000
        
        try:
            position = position + 1
            index = ovalid[position:]
        
            # Apply the modulus function to determine which bucket it belongs to
            return int(int(index)/1000 + 1) * 1000
            # Or another way to do it:
#             sequence = int(index)
#             mod = sequence % 1000
#             return sequence - mod + 1000
        except Exception:
            return 1000
        
        
        
    def getFileName(self):
        """
        Use my OVAL ID to create a base file name.  That really just means replacing ':' with '_'
        *NOTE* This does not include the path to the file.
        """
        ovalid = self.getId()
        if not ovalid or ovalid is None:
            return None
        
        return ovalid.replace(':', '_') + ".xml"

        
        
    def getPredicate(self):
        """
        The portion of the element name that precedes the "_"
        So, for "password_test", the predicate would be "password"
        """
        localname = self.getLocalName()
        if not localname or localname is None:
            return None
        
        return localname.rsplit('_',1)[0]

            
    def getElement(self):
        """
        Get the raw xml.etree.ElementTree.Element for this node.  Can be used to directly manipulate the
        XML in ways not currently supported by this library
        """
        return self.element
            
    
            
    def getName(self):
        """
        Get the tag name (XMl element name) of the underlying XML Element, which includes the schema URI
        """
        if not self.element or self.element is None:
            return None
        
        return self.element.tag
    
    
    def getLocalName(self):
        """
        Just the element name with the schema URI (if any) removed
        """
        
        if not self.element or self.element is None:
            return None

        #Check if this node name is prefixed by a URI, in which case return every after the URI
        if '}' in self.element.tag:
            return str(self.element.tag).rsplit('}',1)[1]
        
        #If no namespace prefix, just return the node name
        return self.element.tag
    
    
    
    def getNamespace(self):
        """
        Returns the URI of the namespace or None if this node does not have a namepsace
        """
        if not self.element or self.element is None:
            return None

        tag = self.element.tag
        
        if not tag or tag is None:
            return None
        
        # If the oval ID does not contain a namespace, then we can't determine the schema shortname
        if not '}' in tag:
            return None
        
        try:
            position = tag.find('}')
            if position < 0:
                return None
            
            namespace = tag[:position]
            return namespace[1:]
        except Exception:
            return None

    
    def getSchemaShortName(self):
        """
        """
        if not self.element or self.element is None:
            return None

        tag = self.element.tag
        
        if not tag or tag is None:
            return None
        
        # If the oval ID does not contain a namespace, then we can't determine the schema shortname
        if not '}' in tag:
            return None
        
        try:
            schema = tag.rsplit('}', 1)[0]
            if not '#' in schema:
                return None
            return schema.rsplit('#', 1)[1].strip()
        except Exception:
            return None
        
    
    def constructFilePath(self):
        """
        """
        if not self.element or self.element is None:
            return None
        
        # The path is:  repo_base / element type / schema short name / local node name / index bucket / converted file name
        try:
            return lib_repo.get_repository_root_path() + "/" + self.getType() + "s/" + self.getSchemaShortName() \
                + "/" + self.getLocalName() + "/" + str(self.getIndexSequence()) + "/" + self.getFileName()
        except Exception:
            return None

    
    @staticmethod    
    def asOvalElement(element):
        """
        For an XML Element, determines if it fits one of the implemented OvalElement subclasses and,
        if so, returns an instantiation of that class
        """        
        
        if not element or element is None:
            return None
        
        try:        
            ovalid = element.get("id")
            if not ovalid or ovalid is None:
                return None
        
            oval_type = lib_repo.get_element_type_from_oval_id(ovalid)
            return OvalElement.create(oval_type, element)
        except Exception:
            return None
        
            
    @staticmethod            
    def create(oval_type, element):
        """
        Create an OvalElement of the proper OVAL element type
        """
        if not oval_type:
            return None
        
        
        if oval_type == OvalDefinition.DEFINITION:
            return OvalDefinition(element)
        elif oval_type == OvalDefinition.TEST:
            return OvalTest(element)
        elif oval_type == OvalDefinition.OBJECT:
            return OvalObject(element)
        elif oval_type == OvalDefinition.STATE:
            return OvalState(element)
        elif oval_type == OvalDefinition.VARIABLE:
            return OvalVariable(element)
        else:
            return None
    



class OvalDefinition(OvalElement):
    
    
    def __init__(self, element):
        if element is not None:
            self.element = element
        else:
            self.element = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}definition")
            self.element.set("version", "1")
            meta = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}metadata")
            self.element.append(meta)
    
    
    def getType(self):
        return OvalElement.DEFINITION
    


    def getMetadata(self):
        """
        Returns the metadata for this definition as an object of type OvalMetadata, or None if it that element does not exist
        """
        if not self.element:
            return None
        
        metadata = self.element.find("def:metadata", OvalDocument.NS_DEFAULT)
        if metadata is not None:
            return OvalMetadata(metadata)
        return None
    
    
    
    def getClass(self):
        if not self.element:
            return None
        
        return self.element.get("class")
    
    def setClass(self, ovalclass):
        if not self.element:
            return False
        
        if not ovalclass:
            return False
        
        self.element.set("class", ovalclass)
        return True
    
            
        
    def getReferencingIDs(self):
        if not self.element:
            return None
        
        return self.xpath("//@*[name()='definition_ref' or name()='test_ref'")
    
    
    def constructFilePath(self):
        if not self.element or self.element is None:
            return None
        
        # The path is:  repo_base / class / converted file name
        try:
            return lib_repo.get_repository_root_path() + "/definitions/" + self.getClass() + "/" + self.getFileName()
        except Exception:
            return None
        
    


class OvalMetadata(object):
    
    def __init__(self, element):
        if element is not None:
            self.element = element
        else:
            self.element = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}metadata")
        
        
    def getTitle(self):
        if not self.element:
            return None
        
        title_element = self.element.find("def:title", OvalDocument.NS_DEFAULT)
        if title_element is not None:
            return title_element.text
        return None
    
    
    
    
    def getDescription(self):
        if not self.element:
            return None
        
        desc_element = self.element.find("def:description", OvalDocument.NS_DEFAULT)
        if desc_element is not None:
            return desc_element.text;
        return None
    
    
    def getAffected(self):
        if not self.element:
            return None
        
        aff_element = self.element.find("def:affected", OvalDocument.NS_DEFAULT)
        if aff_element is not None:
            return OvalAffected(aff_element)
        return None
    
    
    def getOvalRepositoryInformation(self):
        if not self.element:
            return None
        
        repo_element = self.element.find("def:oval_repository", OvalDocument.NS_DEFAULT)
        if repo_element is not None:
            return OvalRepositoryInformation(repo_element)
        return None
    
    
    
class OvalAffected(object):
    
    def __init__(self, element):
        self.element = element
        
        
        
class OvalRepositoryInformation(object):
    
    def __init__(self, element):
        self.element = element
        
        
    def getStatus(self):
        if self.element is None:
            return None
        
        status = self.element.find("def:status", OvalDocument.NS_DEFAULT)
        
        if status is None:
            return None
        
        return status.text
            
            
    def setStatus(self, status):
        if self.element is None:
            return
        
        if not status or status is None:
            return
        
        element = self.element.find("def:status", OvalDocument.NS_DEFAULT)
        
        if element is None:
            element = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}status")
            self.element.append(element)
        
        element.text = status
        
        
    def getMinimumSchemaVersion(self):
        if self.element is None:
            return None
        
        version = self.element.find("def:min_schema", OvalDocument.NS_DEFAULT)
        
        if version is None:
            return None
        
        return version.text
        

    def setMinimumSchemaVersion(self, version):
        if self.element is None:
            return
        
        if not version or version is None:
            return
        
        child = self.element.find("def:min_schema", OvalDocument.NS_DEFAULT)
        
        if child is None:
            child = Element("{" + OvalDocument.NS_DEFAULT.get("def") + "}min_schema")
            self.element.append(child)
        
        child.text = version
        
        
        
        
        
class OvalTest(OvalElement):
    
    def __init__(self, element):
        self.element = element
        
        
    def getType(self):
        return OvalElement.TEST
        


class OvalObject(OvalElement):
    
    def __init__(self, element):
        self.element = element


    def getType(self):
        return OvalElement.OBJECT
        
        
class OvalState(OvalElement):
    
    def __init__(self, element):
        self.element = element
        
        
    def getType(self):
        return OvalElement.STATE
        
        
class OvalVariable(OvalElement):
    
    def __init__(self, element):
        self.element = element
        
        
    def getType(self):
        return OvalElement.VARIABLE                        