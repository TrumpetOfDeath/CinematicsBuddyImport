# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from .ops.cinematics_buddy_import import CinematicsBuddyImport

bl_info = {
    "name": "Import: Cinematics Buddy Data (.txt)",
    "description": "Import data from Cinematics Buddy BETA (Bakkesmod plugin)",
    "author": "TrumpetOfDeath (Discord: TrumpetOfDeath#3020)",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > Cinematics Buddy Data (.txt)",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}


def menu_func_import(self, context):
    self.layout.operator(CinematicsBuddyImport.bl_idname, text="Cinematics Buddy Animation (.txt)")


def register():
    bpy.utils.register_class(CinematicsBuddyImport)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(CinematicsBuddyImport)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
