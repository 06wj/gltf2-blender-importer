import bpy
import os
from urllib.parse import urljoin

blenderDir = urljoin(os.path.abspath(__file__), './glTF2_Principled.blend/NodeTree/')

def _importGroupNode(groupName):
    if groupName not in bpy.data.node_groups:
        bpy.ops.wm.append(directory=blenderDir, filename=groupName)

def _createGroupNode(node_tree, groupName):
    _importGroupNode(groupName)

    pbrNode = node_tree.nodes.new("ShaderNodeGroup")
    pbrNode.node_tree = bpy.data.node_groups[groupName]
    
    return pbrNode

def getNodeInputDict(node):
    inputDict = {}
    for nodeSocket in node.inputs:
        inputDict[nodeSocket.name] = nodeSocket
    return inputDict

def createGlTFMetallicRoughnessNode(node_tree):
    return _createGroupNode(node_tree, 'glTF Metallic Roughness')

def createGlTFSpecularGlossinessNode(node_tree):
    return _createGroupNode(node_tree, 'glTF Specular Glossiness')