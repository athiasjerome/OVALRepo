#!/usr/bin/env/ python3
"""Splits the OVAL document into its component parts and stores them in the appropriate places in the repository.

Right now, only handles the very simple case of processing a valid oval_definitions file with at least one
definition and puts all of the component pieces in the proper location in the repository


Authors: Gunnar Engelbach <Gunnar.Engelbach@ThreatGuard.com>


TODO:
 - Create missing directories for filepaths when writing them there files
 - Tools for resolving/accepting changes when the OVAL ID for a component refers to an existing item
 - Use the min schema method to determine the minimum schema needed for this definition and add that information to the definition metadata
 - Update the local copy of the whoosh database
 - Other types of validation
     - Are all referenced items either in the document or does it already exist in the repository?
     - Is the definition/metadata/oval_repository/status set to the proper value?
     - Is the definition/metadata/oval_repository/timestamp set to the proper value?
"""


import argparse, os, xml, xml.etree
from lib_oval import OvalDocument
from xml.etree.ElementTree import ElementTree


def main():
    """
    Breaks the OVAL file into its constituent elements and writes each of those into the repository
    """
    
    parser = argparse.ArgumentParser(description='Separates an OVAL file into its component parts and saves them to the repository.')
    options = parser.add_argument_group('options')
    options.add_argument('-f', '--file', required=True, help='The name of the source file')
    options.add_argument('-v', '--verbose', required=False, action="store_true", help='Enable more verbose messages')
    args = vars(parser.parse_args())

    oval = OvalDocument(None)
    filename = args['file']
    if args['verbose']:
        verbose = True
    
    if not oval.parseFromFile(filename):
        print("Unable to parse source file '", filename, "':  no actions taken")
        exit

    deflist = oval.getDefinitions()
    if not deflist or deflist is None or len(deflist) < 1:
        print("Error:  this document does not contain any OVAL definitions.  No further action will be taken")
        exit
        
    if verbose:
        print(" Number of definitions to process: ", len(deflist))
    
    
    writeFiles(deflist, verbose)
    writeFiles(oval.getTests(), verbose)
    writeFiles(oval.getObjects(), verbose)
    writeFiles(oval.getStates(), verbose)
    writeFiles(oval.getVariables(), verbose)


        
#     for test in deflist:
#         filepath = test.constructFilePath()
#         if not filepath or filepath is None:
#             # Some sort of error.  Add this element to our problem list
#             print("## Error with element ", test.getId())
#         elif os.path.exists(filepath):
#             # Add it to the list of possible conflicts
#             print("## File exists: ", filepath)
#         else:
#             print("  ## New file: ", filepath)
#     
    

        
    
    #For each file path, see if a file already exists in the repository
    #  Should it be a collision if the file contents match?
    #  How about if the file contents don't match, but the XML attributes do?
    #File name collisions?  Show the user
    #  For each file, show the current and new element
    #  Prompt for possible actions:  skip, update, retain, cancel
    #  If updating, make sure the version is set properly


def writeFiles(element_list, verbose=False):
    if not element_list or element_list is None:
        return
    
    for element in element_list:
        filepath = element.constructFilePath()
        if filepath and filepath is not None:
            writeFile(filepath, element, verbose)
        
        
def writeFile(path, element, verbose=False):
    
    if verbose:
        if os.path.exists(path):
            print("## Overwrite existing file: ", path)
        else:
            print("@@ Creating new file: ", path)
    
    # Get the namespace of this element
    namespace = element.getNamespace()
    # Register this namespace with the parser as the default namespace
    xml.etree.ElementTree.register_namespace('', namespace)
    e = element.getElement()
    # Fix up the element so it will print nicely
    OvalDocument.indent(e)
    # Create a new ElementTree with this element as the root
    tree = ElementTree(e)
    # And finally, write the full tree to a file including the xml declaration
    tree.write(path, "UTF-8", True)
#     xml.etree.ElementTree.dump(tree)
    
        

if __name__ == '__main__':
    main()