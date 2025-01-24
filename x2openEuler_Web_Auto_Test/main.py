import os
import pytest
import config.config as cg


if __name__ == '__main__':
    report_path = os.path.join(cg.ROOT_DIR, 'report')
    if not os.path.exists(report_path):
        os.mkdir(report_path)
    pytest.main(["-s", "-v", "test_case/task_upgrade/test_task_upgrade.py", "--html=./report/x2openEuler_report.html"])
