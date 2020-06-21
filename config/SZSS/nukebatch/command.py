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
LGT_Read = sys.argv[10]
LGT_image_path = sys.argv[11]
Write_Read = sys.argv[12]
Write_output_path = sys.argv[13]
nuke_save_path = sys.argv[14]

nuke.scriptOpen(nuke_template)

BGCLR_Read = nuke.toNode(BGCLR_Read)
BGCLR_Read['file'].fromUserText(BGCLR_image_path)

SKY_Read = nuke.toNode(SKY_Read)
SKY_Read['file'].fromUserText(SKY_image_path)

IDP_Read = nuke.toNode(IDP_Read)
IDP_Read['file'].fromUserText(IDP_image_path)

CHRCLR_Read = nuke.toNode(CHRCLR_Read)
CHRCLR_Read['file'].fromUserText(CHRCLR_image_path)

LGT_Read = nuke.toNode(LGT_Read)
LGT_Read['file'].fromUserText(CHRCLR_image_path)

Write_Read = nuke.toNode(Write_Read)
Write_Read.knob('file').setValue(Write_output_path)

root = nuke.toNode('root')
root['first_frame'].setValue(BGCLR_Read['first'].getValue())
root['last_frame'].setValue(BGCLR_Read['last'].getValue())

if not os.path.exists(os.path.dirname(nuke_save_path)):
    os.makedirs(os.path.dirname(nuke_save_path))

nuke.scriptSave(nuke_save_path)
