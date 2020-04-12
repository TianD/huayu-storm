# coding: utf-8

import os
import nuke
import sys

nuke_template = sys.argv[1]
BGCLR_Read = sys.argv[2]
BGCLR_image_path = sys.argv[3]
SKY_Read = sys.argv[4]
SKY_image_path = sys.argv[5]
IDP_Read = sys.argv[6]
IDP_image_path = sys.argv[7]
CHRCLR_Read = sys.argv[8]
CHRCLR_image_path = sys.argv[9]
Write_Read = sys.argv[10]
Write_output_path = sys.argv[11]
nuke_save_path = sys.argv[12]

nuke.scriptOpen(nuke_template)

BGCLR_Read = nuke.toNode(BGCLR_Read)
BGCLR_Read['file'].fromUserText(BGCLR_image_path)

SKY_Read = nuke.toNode(SKY_Read)
SKY_Read['file'].fromUserText(SKY_image_path)

IDP_Read = nuke.toNode(IDP_Read)
IDP_Read['file'].fromUserText(IDP_image_path)

CHRCLR_Read = nuke.toNode(CHRCLR_Read)
CHRCLR_Read['file'].fromUserText(CHRCLR_image_path)

Write_Read = nuke.toNode(Write_Read)
Write_Read.knob('file').setValue(Write_output_path)

root = nuke.toNode('Root')
root['first_frame'].setValue(read_source['first'].getValue())
root['last_frame'].setValue(read_source['last'].getValue())

nuke.scriptSave(nuke_save_path)
