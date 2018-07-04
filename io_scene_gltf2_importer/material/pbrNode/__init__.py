import bpy
import os
from urllib.parse import urljoin

blenderDir = urljoin(os.path.abspath(__file__), './glTF2_Principled.blend/NodeTree/')

def importGlTFMetallicRoughnessNode():
    if 'glTF Metallic Roughness' not in bpy.data.node_groups:
        bpy.ops.wm.append(directory=blenderDir, filename='glTF Metallic Roughness')

def importGlTFSpecularGlossinessNode():
    if 'glTF Specular Glossiness' not in bpy.data.node_groups:
        bpy.ops.wm.append(directory=blenderDir, filename='glTF Specular Glossiness')