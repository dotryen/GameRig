import bpy
import math

from itertools import count

from .skin_rigs import BaseSkinChainRigWithRotationOption
from rigify.rigs.skin.basic_chain import Rig as basic_chain
from rigify.base_rig import stage
from rigify.utils.misc import map_list

class Rig(BaseSkinChainRigWithRotationOption, basic_chain):
    
    def initialize(self):
        super().initialize()

        self.enable_scale = self.params.enable_scale

    ####################################################
    # B-Bone handle MCH

    @stage.generate_bones
    def make_mch_handle_bones(self):
        mch = self.bones.mch
        chain = self.get_node_chain_with_mirror()

        # If the last handle mch will be shared, drop it from chain
        if self.next_chain_rig:
            chain = chain[0:-1]

        mch.handles = map_list(self.make_mch_handle_bone, count(0),
                               chain, chain[1:], chain[2:])

        if self.use_pre_handles:
            mch.handles_pre = map_list(self.make_mch_pre_handle_bone, count(0), mch.handles)
        else:
            mch.handles_pre = mch.handles

    @stage.parent_bones
    def parent_mch_handle_bones(self):
        mch = self.bones.mch

        if self.use_pre_handles:
            for pre in mch.handles_pre:
                self.set_bone_parent(pre, self.rig_parent_bone, inherit_scale='AVERAGE')

        for handle in mch.handles:
            self.set_bone_parent(handle, self.rig_parent_bone, inherit_scale='AVERAGE')

    @stage.parent_bones
    def parent_deform_chain(self):
        deform = self.bones.deform

        self.set_bone_parent(self.bones.deform[0], self.rig_parent_bone)
        self.parent_bone_chain(self.bones.deform, use_connect=False)

        # This puts the deformation bones into the def hierarchy of its parent rig
        self.clean_def_hierarchy(self.bones.deform[0])

    @stage.rig_bones
    def rig_mch_handle_bones(self):
        mch = self.bones.mch
        chain = self.get_node_chain_with_mirror()

        # Rig Auto-handle emulation (on pre handles)
        for args in zip(count(0), mch.handles_pre, chain, chain[1:], chain[2:]):
            self.rig_mch_handle_auto(*args)

        # Apply user transformation to the final handles
        for args in zip(count(0), mch.handles, chain, chain[1:], chain[2:], mch.handles_pre):
            self.rig_mch_handle_user(*args)

    ##############################
    # Deform chain

    @stage.rig_bones
    def rig_deform_chain(self):
        handles = self.get_all_mch_handles()
        for args in zip(count(0), self.bones.deform, self.bones.org, handles[1:]):
            self.rig_deform_bone(*args)

    def rig_deform_bone(self, i, deform, org, handle):
        if self.enable_scale:
            self.make_constraint(deform, 'COPY_TRANSFORMS', org)
        else:
            self.make_constraint(deform, 'COPY_LOCATION', org)
            self.make_constraint(deform, 'COPY_ROTATION', org)
        self.make_constraint(deform, 'COPY_ROTATION', handle, space="LOCAL", use_xyz=[False, True, False], mix_mode="AFTER")

    @classmethod
    def add_parameters(self, params):
        super().add_parameters(params)
        params.enable_scale = bpy.props.BoolProperty(
            name="Scale",
            default=False,
            description="Deformation bones will inherit the scale of their ORG bones. Enable this only if you know what you are doing because scale can break your rig in the game engine"
        )

    @classmethod
    def parameters_ui(self, layout, params):
        super().parameters_ui(layout, params)

        row = layout.row()
        row.prop(params, "enable_scale")


def create_sample(obj):
    from ..basic.copy_chain import create_sample as inner
    obj.pose.bones[inner(obj)["bone.01"]].rigify_type = 'game.skin.basic_chain'
