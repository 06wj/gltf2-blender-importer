"""
 * ***** BEGIN GPL LICENSE BLOCK *****
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * Contributor(s): Julien Duroure.
 *
 * ***** END GPL LICENSE BLOCK *****
 * This development is done in strong collaboration with Airbus Defence & Space
 """

from ..texture import *
from ..pbrNode import *
import bpy

class KHR_materials_pbrSpecularGlossiness():

    SIMPLE  = 1
    TEXTURE = 2
    TEXTURE_FACTOR = 3

    def __init__(self, json, gltf):
        self.json = json # material json
        self.pbrJson = json['extensions']['KHR_materials_pbrSpecularGlossiness'] # KHR_materials_pbrSpecularGlossiness json
        self.gltf = gltf # Reference to global glTF instance

        self.diffuse_type   = self.SIMPLE
        self.specgloss_type = self.SIMPLE
        self.vertex_color   = False

        # pbrSpecularGlossiness values
        self.diffuseTexture = None
        self.diffuseFactor    = [1.0,1.0,1.0,1.0]
        self.specularGlossinessTexture = None
        self.glossinessFactor = 1.0
        self.specularFactor   = [1.0,1.0,1.0,1.0]

        # pbr common values
        self.emissiveFactor = [0,0,0,1]
        self.emissiveTexture = None
        self.occlusionTexture = None
        self.normalTexture = None
        self.doubleSided = False
        self.alphaMode = 'OPAQUE'
        self.alphaCutoff = 0.5

        self.nodeX = 200

    def read(self):
        json = self.json
        pbrJson = self.pbrJson

        if self.json is None:
            return # will use default values

        # read pbrSpecularGlossiness values
        pbrKeys = pbrJson.keys()
        if 'diffuseTexture' in pbrKeys:
            self.diffuse_type = self.TEXTURE
            self.diffuseTexture = self.readTexture('diffuseTexture', True)

        if 'diffuseFactor' in pbrKeys:
            self.diffuseFactor = pbrJson['diffuseFactor']

        if 'specularGlossinessTexture' in pbrKeys:
            self.specgloss_type = self.TEXTURE
            self.specularGlossinessTexture = self.readTexture('specularGlossinessTexture', True)

        if 'glossinessFactor' in pbrKeys:
            self.glossinessFactor = pbrJson['glossinessFactor']

        if 'specularFactor' in pbrKeys:
            self.specularFactor = pbrJson['specularFactor']
            if len(self.specularFactor) == 3:
                self.specularFactor.append(1)

        # read common values
        keys = json.keys()
        if 'emissiveTexture' in keys:
            self.emissiveTexture = self.readTexture('emissiveTexture')

        if 'normalTexture' in keys:
            self.normalTexture = self.readTexture('normalTexture')

        if 'occlusionTexture' in keys:
            self.occlusionTexture = self.readTexture('occlusionTexture')

        if 'emissiveFactor' in keys:
            self.emissiveFactor = json['emissiveFactor']
            if len(self.emissiveFactor) == 3:
                self.emissiveFactor.append(1)

        if 'doubleSided' in keys:
            self.doubleSided = json['doubleSided']

        if 'alphaMode' in keys:
            self.alphaMode = json['alphaMode']

        if 'alphaCutoff' in keys:
            self.alphaCutoff = json['alphaCutoff']

    def readTexture(self, textureName, isPbrJson = False):
        textureInfo = self.pbrJson[textureName] if isPbrJson else self.json[textureName]
        texture = Texture(textureInfo['index'], self.gltf.json['textures'][textureInfo['index']], self.gltf)
        texture.read()
        texture.debug_missing()

        if 'texCoord' in textureInfo:
            texture.texcoord = int(textureInfo['texCoord'])
        else:
            texture.texcoord = 0
        return texture

    def use_vertex_color(self):
        self.vertex_color = True

    def create_blender(self, mat_name):
        engine = bpy.context.scene.render.engine
        if engine == 'CYCLES':
            self.create_blender_cycles(mat_name)
        else:
            pass #TODO for internal / Eevee in future 2.8

    def createTextureNode(self, texture, nodeTree):
        texture.blender_create()
        textureNode = nodeTree.nodes.new('ShaderNodeTexImage')
        textureNode.image = bpy.data.images[texture.image.blender_image_name]
        mappingNode = nodeTree.nodes.new('ShaderNodeMapping')
        uvmapNode = nodeTree.nodes.new('ShaderNodeUVMap')
        uvmapNode["gltf2_texcoord"] = texture.texcoord # Set custom flag to retrieve TexCoord
        nodeTree.links.new(mappingNode.inputs[0], uvmapNode.outputs[0])
        nodeTree.links.new(textureNode.inputs[0], mappingNode.outputs[0])

        x = self.nodeX
        y = 0
        textureNode.location = x, y
        y -= 280

        mappingNode.location = x, y
        y -= 290
        
        uvmapNode.location = x, y

        self.nodeX += 400
        return textureNode

    def create_blender_cycles(self, mat_name):
        material = bpy.data.materials[mat_name]
        material.use_nodes = True
        node_tree = material.node_tree

        # delete all nodes except output
        for node in list(node_tree.nodes):
            if not node.type == 'OUTPUT_MATERIAL':
                node_tree.nodes.remove(node)

        output_node = node_tree.nodes[0]
        output_node.location = 1400, 600

        # create PBR node  
        pbrNode = createGlTFSpecularGlossinessNode(node_tree)
        pbrNode.location = 1000, 600
        pbrInputDict = getNodeInputDict(pbrNode)
        
        # pbrSpecularGlossiness values
        pbrInputDict['DiffuseFactor'].default_value = self.diffuseFactor
        pbrInputDict['SpecularFactor'].default_value = self.specularFactor
        pbrInputDict['GlossinessFactor'].default_value = self.glossinessFactor

        if self.specularGlossinessTexture:
            specularGlossinessTextureNode = self.createTextureNode(self.specularGlossinessTexture, node_tree)
            node_tree.links.new(pbrInputDict['Specular'], specularGlossinessTextureNode.outputs[0]) # specular
            node_tree.links.new(pbrInputDict['Glossiness'], specularGlossinessTextureNode.outputs[1]) # glossiness

        if self.diffuseTexture:
            diffuseTextureNode = self.createTextureNode(self.diffuseTexture, node_tree)
            node_tree.links.new(pbrInputDict['Diffuse'], diffuseTextureNode.outputs[0])
            if self.alphaMode != 'OPAQUE':
                node_tree.links.new(pbrInputDict['Alpha'], diffuseTextureNode.outputs[1])
        
        # common values
        pbrInputDict['EmissiveFactor'].default_value = self.emissiveFactor
        pbrInputDict['AlphaCutoff'].default_value = self.alphaCutoff
        pbrInputDict['DoubleSided'].default_value = 1 if self.doubleSided else 0
        pbrInputDict['AlphaMode'].default_value = 1 if self.alphaMode == 'MASK' else 0

        if self.emissiveTexture:
            emissiveNode = self.createTextureNode(self.emissiveTexture, node_tree)
            node_tree.links.new(pbrInputDict['Emissive'], emissiveNode.outputs[0])

        if self.normalTexture:
            normalTextureNode = self.createTextureNode(self.normalTexture, node_tree)
            normalTextureNode.color_space = 'NONE'
            node_tree.links.new(pbrInputDict['Normal'], normalTextureNode.outputs[0])

        if self.occlusionTexture:
            occlusionTextureNode = self.createTextureNode(self.occlusionTexture, node_tree)
            occlusionTextureNode.color_space = 'NONE'
            node_tree.links.new(pbrInputDict['Occlusion'], occlusionTextureNode.outputs[0])
       
        if self.vertex_color:
            vertexColorNode = node_tree.nodes.new('ShaderNodeAttribute')
            vertexColorNode.attribute_name = 'COLOR_0'
            node_tree.links.new(pbrInputDict['COLOR_0'], vertexColorNode.outputs[1])
            pbrInputDict['Use COLOR_0'].default_value = 1.0

        # link node to output
        node_tree.links.new(output_node.inputs[0], pbrNode.outputs[0])


    def debug_missing(self):
        if self.json is None:
            return
        keys = [

                ]

        for key in self.json.keys():
            if key not in keys:
                self.gltf.log.debug("KHR_materials_pbrSpecularGlossiness MISSING " + key)
