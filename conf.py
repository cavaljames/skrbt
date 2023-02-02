"""
@File    :   conf.py    
@Contact :   zhangyu@onesight.com

@Modify Time    @Author @Version    @Description
------------    ------- --------    -----------
2023/1/29      zhangyu 1.0         None
"""

import configparser


target_configfile = './skrbt.ini'
conf = configparser.ConfigParser()
conf.read(target_configfile)


# 获取属性
def get_conf(group, name):
    return conf.get(group, name)


# 修改属性
def set_conf(group, name, value):
    conf.set(group, name, value)
    with open(target_configfile, 'w') as f:
        conf.write(f)


# 增加属性
def add_conf(group, name, value):
    conf.set(group, name, value)
    with open(target_configfile, 'w') as f:
        conf.write(f)


# 删除属性
def del_conf(group, name):
    conf.remove_option(group, name)
    with open(target_configfile, 'w') as f:
        conf.write(f)

