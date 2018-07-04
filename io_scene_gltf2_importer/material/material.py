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

import bpy
from .pbr import *
from .map import *
from .extensions import *

class Material():
    def __init__(self, index, json, gltf):
        self.index = index
        self.json = json # Material json
        self.gltf = gltf # Reference to global glTF instance
        self.name = None

        self.blender_material = None

        self.emissivemap  = None
        self.normalmap    = None
        self.occlusionmap = None

    def read(self):

        # If no index, this is the default material
        if self.index is None:
            self.pbr = Pbr(None, self.gltf)
            self.pbr.read()
            self.pbr.debug_missing()
            self.name = "Default Material"
            return

        if 'extensions' in self.json.keys():
            if 'KHR_materials_pbrSpecularGlossiness' in self.json['extensions'].keys():
                self.KHR_materials_pbrSpecularGlossiness = KHR_materials_pbrSpecularGlossiness(self.json, self.gltf)
                self.KHR_materials_pbrSpecularGlossiness.read()
                self.KHR_materials_pbrSpecularGlossiness.debug_missing()

        # Not default material
        if 'name' in self.json.keys():
            self.name = self.json['name']

        if 'pbrMetallicRoughness' in self.json:
            self.pbr = Pbr(self.json, self.gltf)
            self.pbr.read()
            self.pbr.debug_missing()

    def use_vertex_color(self):
        if hasattr(self, 'KHR_materials_pbrSpecularGlossiness'):
            self.KHR_materials_pbrSpecularGlossiness.use_vertex_color()
        else:
            self.pbr.use_vertex_color()

    def create_blender(self):
        if self.name is not None:
            name = self.name
        else:
            name = "Material_" + str(self.index)

        mat = bpy.data.materials.new(name)
        self.blender_material = mat.name

        if hasattr(self, 'KHR_materials_pbrSpecularGlossiness'):
            self.KHR_materials_pbrSpecularGlossiness.create_blender(mat.name)
        elif hasattr(self, 'pbr'):
            # create pbr material
            self.pbr.create_blender(mat.name)

    def set_uvmap(self, prim, obj):
        node_tree = bpy.data.materials[self.blender_material].node_tree
        uvmap_nodes =  [node for node in node_tree.nodes if node.type == 'UVMAP']
        for uvmap_node in uvmap_nodes:
            if uvmap_node["gltf2_texcoord"] in prim.blender_texcoord.keys():
                uvmap_node.uv_map = prim.blender_texcoord[uvmap_node["gltf2_texcoord"]]

    def debug_missing(self):
        if self.index is None:
            return
        keys = [
                'name',
                'pbrMetallicRoughness',
                'emissiveFactor',
                'normalTexture',
                'emissiveTexture',
                'occlusionTexture'
                ]

        for key in self.json.keys():
            if key not in keys:
                self.gltf.log.debug("MATERIAL MISSING " + key)
