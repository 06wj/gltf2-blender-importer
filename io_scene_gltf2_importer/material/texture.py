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
from .image import *

class Texture():
    # glTF samplers constants
    REPEAT = 10497
    CLAMP_TO_EDGE = 33071
    MIRRORED_REPEAT = 33648
    NEAREST = 9728
    LINEAR = 9729
    NEAREST_MIPMAP_NEAREST = 9984
    LINEAR_MIPMAP_NEAREST = 9985
    NEAREST_MIPMAP_LINEAR = 9986
    LINEAR_MIPMAP_LINEAR = 9987

    def __init__(self, index, json, gltf):
        self.index = index
        self.json = json # texture json
        self.gltf = gltf # Reference to global glTF instance
        self.wrapS = Texture.REPEAT
        self.wrapT = Texture.REPEAT
        self.minFilter = Texture.LINEAR
        self.magFilter = Texture.LINEAR

    def read(self):
        if 'source' in self.json.keys():

            if self.json['source'] not in self.gltf.images.keys():
                image = Image(self.json['source'], self.gltf.json['images'][self.json['source']], self.gltf)
                self.gltf.images[self.json['source']] = image

            self.image = self.gltf.images[self.json['source']]
            self.image.read()
            self.image.debug_missing()
        if 'sampler' in self.json.keys():
            samplerId = self.json['sampler']
            if 'samplers' in  self.gltf.json.keys():
                samplers = self.gltf.json['samplers']
                if samplerId < len(samplers):
                    sampler = samplers[samplerId]
                    if 'wrapS' in sampler:
                        self.wrapS = sampler['wrapS']
                    if 'wrapT' in sampler:
                        self.wrapT = sampler['wrapT']

                    if 'minFilter' in sampler:
                        self.minFilter = sampler['minFilter']
                    if 'magFilter' in sampler:
                        self.magFilter = sampler['magFilter']

    def blender_create(self):
        self.image.blender_create()

    def debug_missing(self):

        keys = [
                'source',
                'sampler'
                ]

        for key in self.json.keys():
            if key not in keys:
                self.gltf.log.debug("PBR MISSING " + key)
