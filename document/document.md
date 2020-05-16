# 配置文件详解

## 配置文件所在位置

工具所在路径的/config

## 配置文件目录结构

配置文件按项目分别组织, 

```
项目 | mayabatch | __project_common.yml (maya分层公共配置)
                | layer_setting_0_BGCLR_CHCLR_SKY.yml (bgclr_chclr_sky层配置)
                | layer_setting_1_LGT.yml (LGT层配置)
                | layer_setting_2_IDP.yml (IDP层配置)
     | nukebatch | config.yml (nuke模板组装配置)
                | command.py (nuke模板组装代码)
     | dir_template.yml (项目目录模板配置)
     | seq2mov.yml (序列转视频的配置)

```

## dir_template.yml详解

用于管理项目中的各种用途的路径, 配置形式如下
```
key:
    dir: 目录模板
    file: 文件名模板
```

- key: 表明这组目录和文件的用途,
  - lr: maya分层文件存放路径
  - compositing: 合成渲染序列存放路径
  - images: maya分层渲染序列存放路径
  - mov: 合成视频的存放路径
  - nuke: 合成nuke工程文件存放路径
  - anim: 动画文件存放路径

路径模板中的变量, 用来匹配真实的路径情况。可用的变量包括:
- {episode}: 集数
- {sequence}: 场次
- {shot}: 镜头
- {layer}: 渲染层


## mayabatch详解

包括通用的渲染设置的配置文件和单独分层的渲染设置(会覆盖通用设置)配置文件。

- ___project_common.yml: 公用配置
    - render_type: 渲染器类型
    - render_plugin_name: 渲染器插件的名字
    - common_setting: 通用属性
      - project_dir: 项目根目录
      - output_dir: 输出根目录
      - maya_version: maya版本
      - deadline_command_bin_path: deadlinecommand.exe路径
      - maya_bin_path: maya.exe路径
      - maya_batch_bin_path: mayabatch.exe路径
      - episode_scene_shot_regex: 镜头号的组成模板
      - object_selector: 各种物体分类的命名规则
      - import_file: 各个层需要导入的文件
    - layer_setting: 各分层的属性设置
      - layer_name： 层名
      - selector_list: 层里需要添加的物体
      - character_override_selector_list: 需要覆盖渲染状态的物体列表
      - character_override_attr_list: 需要覆盖的渲染状态的属性列表
      - render_setting: 渲染设置

- layer_setting_0_BGCLR_CHCLR_SKY.yml: 背景层、角色层、天空层的单独配置
  - basic_config: 继承公共配置
  - output_file_name: 输出的文件名
  - layer_setting: 各分层的属性设置, 会覆盖basic_config中layer_setting中的配置

- layer_setting_1_LGT.yml: 灯光层的单独配置
  - basic_config: 继承公共配置
  - output_file_name: 输出的文件名
  - layer_setting: 各分层的属性设置, 会覆盖basic_config中layer_setting中的配置

- layer_setting_2_IDP.yml: IDP层的单独配置
  - basic_config: 继承公共配置
  - output_file_name: 输出的文件名
  - layer_setting: 各分层的属性设置, 会覆盖basic_config中layer_setting中的配置
    

## nukebatch详解

由配置文件、脚本文件组成。

- config.yml: nukebatch配置文件
    - nuke_exe: nuke.exe的路径
    - nuke_template: nuke模板文件路径
    - py_cmd: 脚本文件路径
    - data: 需要根据模板和图层名设计的参数
      - XXX_Read: 节点名
      - XXX_layer: 图层名
    - nuke_cmd: 组装成的nuke命令

- command.py: nuke后台调用的代码文件, 会将参数传入, 在模板文件中进行修改。
  

## seq2movbatch详解

序列转视频所需要调用的ffmpeg命令的配置.
根据输入文件路径模板将选中的文件路径进行解析, 然后根据输出文件路径模板组装出输出路径.

- seq2mov.yml: 序列转视频的配置文件
  - input_file_template: 输入文件的路径, 填入dir_template.yml中的某个key代表路径
  - output_file_template: 输出文件的路径, 填入dir_template.yml中的某个key代表路径
  - ffmpeg_cmd: ffmpeg命令
