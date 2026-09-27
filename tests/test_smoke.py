"""冒烟测试：验证 src-layout 与包可导入。"""

import simulation


def test_package_version_exposed():
    assert isinstance(simulation.__version__, str)
    assert simulation.__version__
