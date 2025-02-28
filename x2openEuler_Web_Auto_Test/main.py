import os
import pytest
import config.config as cg


if __name__ == '__main__':
    report_name = "x2openEuler_report"
    report_path = os.path.join(cg.ROOT_DIR, 'report')
    if not os.path.exists(report_path):
        os.mkdir(report_path)
    report_file = os.path.join(report_path, report_name)
    pytest.main(["-s", "-v", "-n=3", "test_case/task_upgrade/test_task_upgrade.py", f"--html={report_file}.html"])
