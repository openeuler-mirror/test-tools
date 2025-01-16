import os
import subprocess
from Aops_Web_Auto_Test.config.conf import cm

testcase_dir = 'test_case'
if not os.path.exists(cm.REPORT_PATH):
    os.makedirs(cm.REPORT_PATH)

report_filename = os.path.join(cm.REPORT_PATH, 'test_report.html')

if __name__ == '__main__':
    pytest_cmd = ['pytest', f'--html={report_filename}', testcase_dir]
    subprocess.run(pytest_cmd, check=True)