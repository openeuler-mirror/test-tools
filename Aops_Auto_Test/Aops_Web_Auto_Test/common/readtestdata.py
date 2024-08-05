import yaml
import os
from Aops_Web_Auto_Test.config.conf import cm


def readyml(dict, name):
    data_path = os.path.join(cm.TESTDATA_PATH, '%s'%dict, '%s.yaml' % name)
    if not os.path.exists(data_path):
        raise FileNotFoundError("%s 文件不存在！" % data_path)
    with open(data_path, encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data
