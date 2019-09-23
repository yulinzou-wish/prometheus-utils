from prometheus_utils import Mon

class BaseMon(Mon):
    metric_name_ext = 'base'
    label_dict_ext = {'app': 'test'}

class ABCMon(BaseMon):
    metric_name_ext = 'abc'
    label_dict_ext = {'module': 'abc'}

class XYZMon(BaseMon):
    metric_name_ext = 'xyz'
    label_dict_ext = {'module': 'xyz'}

class ApiMon(ABCMon):
    metric_name_ext = 'abcapi'
    label_dict_ext = {'api': '123'}
