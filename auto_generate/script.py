import os
import re
import json
import shutil
import argparse
import subprocess

from llm import generate_script, check_package_command, generate_markdown
MAX_TIMES = 3
TEST_CASE_DIR = "generate_test_cases"
TMP_DIR = "tmp"
NOTE_DIR = "note.md"
COMMON_DIR = "common"
SUITE_DIR = "suite2cases"
TESTCASE_DIR = "testcases"
LOGS_DIR = "logs"

# 当前文件目录
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
# 当前执行目录
current_directory = os.getcwd()


def parse_markdown_table(markdown_text):
    # 正则表达式匹配Markdown表格的每一行
    table_rows = re.findall(r'^\|(.*)\|$', markdown_text, re.MULTILINE)

    # 提取表头
    headers = re.split(r'\s*\|\s*', table_rows[0].strip())

    # 解析表格数据
    table_data = []
    for row in table_rows[2:]:  # 跳过头部和分割线
        if row:  # 确保不是空行
            cells = row.split(' | ')
            if len(cells) == len(headers):
                row_data = {headers[i]: cells[i] for i in range(len(headers))}
                table_data.append(row_data)

    return table_data


def get_test_case(md_file):
    with open(md_file, 'r') as f:
        test_case_file = f.read()
    dicts = parse_markdown_table(test_case_file)
    return dicts


def get_command_info(package_name, command):
    if command == package_name:
        command = ""
    command_info = ""
    # 获取命令--help信息
    result = subprocess.run([package_name, command, 'help'], capture_output=True, text=True)
    if result.returncode != 0:
        result = subprocess.run([package_name, command, '--help'], capture_output=True, text=True)
    if result.stdout:
        command_info = result.stdout
    else:
        command_info = result.stderr
    return command, command_info


def get_note(note_dir):
    note = ""
    if not note_dir or not os.path.exists(note_dir):
        return note
    with open(note_dir, 'r') as f:
        note = f.read()
    return note


def execute_script(package_name, rpm_package_name, command, script):
    # 在./suite2cases目录下创建一个{package_name}_{command}.json的文件,作为套件
    with open(os.path.join(current_directory, SUITE_DIR, f'{package_name}_{rpm_package_name}_{command}.json'), 'w') as f:
        suite_json_template = {"path": f"$OET_PATH/{TESTCASE_DIR}/{package_name}", "cases": [{"name": f"{rpm_package_name}_{command}"}]}
        f.write(json.dumps(suite_json_template, indent=4))
    # 在./testcases/package_name目录下创建一个command.sh的文件,作为测试用例
    with open(os.path.join(current_directory, TESTCASE_DIR, package_name, f'{rpm_package_name}_{command}.sh'), 'w') as f:
        f.write(script)
    # 执行脚本
    result = subprocess.run(
        ['bash', 'mugen.sh', '-f', f'{package_name}_{rpm_package_name}_{command}', '-x'],
        capture_output=True, text=True)
    script_exec_result = True if result.returncode == 0 else False
    script_exec_log = ""
    # 获取logs/package_name/command下最新的日志
    log_dir = os.path.join(current_directory, LOGS_DIR, f'{package_name}_{rpm_package_name}_{command}', f"{rpm_package_name}_{command}")
    if os.path.exists(log_dir):
        logs = os.listdir(log_dir)
        if logs:
            latest_log = max(logs, key=lambda x: os.path.getctime(os.path.join(log_dir, x)))
            # 读取日志文件内容
            with open(os.path.join(log_dir, latest_log), 'r') as f:
                script_exec_log = f.read()
    return script_exec_result, script_exec_log


def get_test_script_by_rpm_package_name(package_name, rpm_package_name):
    package_info = ""
    # 获取软件包help信息
    print(f"获取二进制软件包{rpm_package_name}的help信息：")
    result = subprocess.run([rpm_package_name, 'help'], capture_output=True, text=True)
    if result.returncode != 0:
        result = subprocess.run([rpm_package_name, '--help'], capture_output=True, text=True)
    if result.stdout:
        package_info = result.stdout
    else:
        package_info = result.stderr
    if 'usage' in package_info or 'Usage' in package_info:
        print(package_info)  # 打印软件包的帮助信息
    else:
        print(f"获取二进制软件包{rpm_package_name}的help信息失败")
        return []

    commands = check_package_command(rpm_package_name, package_info)
    if not commands:
        print(f"获取软件包{package_name}的子命令为空")
        commands = ['']
    if rpm_package_name in commands:
        commands.remove(rpm_package_name)
    print(f"获取软件包{rpm_package_name}的子命令：{commands}")
    software_dir = os.path.join(current_dir_path, TEST_CASE_DIR, package_name)
    # 如果不存在在test_cases目录下package_name文件夹的话，则创建
    os.makedirs(software_dir, exist_ok=True)
    # 根据note_dir，获取note_dir文件的内容
    note_file = get_note(os.path.join(current_dir_path, TMP_DIR, NOTE_DIR))
    # 根据common_dir，获取common_dir文件的内容
    common_file = os.path.join(current_dir_path, TMP_DIR, COMMON_DIR)
    # 创建/testcases/package_name/common文件夹
    os.makedirs(os.path.join(current_directory, TESTCASE_DIR, package_name, 'common'), exist_ok=True)
    # 把common_file文件夹内的所有文件拷贝到/testcases/package_name/common目录下
    shutil.copytree(common_file, os.path.join(current_directory,
                    TESTCASE_DIR, package_name, 'common'), dirs_exist_ok=True)
    result_commands = []
    # 遍历commands，生成测试脚本
    for index, command in enumerate(commands):
        # 获取命令信息
        command_name, command_info = get_command_info(rpm_package_name, command)
        if not command:
            command = f"{rpm_package_name}_{index+1}"
        # 脚本执行结果
        history_script = ""
        history_script_exec_result = False
        history_script_exec_log = ""
        times = 0
        # 生成测试脚本并执行
        while not history_script_exec_result and times < MAX_TIMES:
            times += 1
            # 生成测试脚本
            script = generate_script(package_name, rpm_package_name, package_info, command_name, command_info,
                                     note_file, history_script, history_script_exec_log)
            if not script:
                script = history_script
            else:
                history_script = script
            # 执行生成的脚本
            history_script_exec_result, history_script_exec_log = execute_script(package_name, rpm_package_name, command, script)
            print(f"第{times}次校验测试脚本{rpm_package_name}/{rpm_package_name}_{command}.sh,结果：{history_script_exec_result}")

        # 在software_dir下保存{command}.sh
        with open(os.path.join(software_dir, f'{command}.sh'), "w") as f:
            f.write(script)
        result_commands.append(command)
        print(f"生成测试脚本{software_dir}/{command}.sh")

    return result_commands



def get_test_script(package_name):
    # 安装软件包
    print("正在安装软件包...")
    result = subprocess.run(['dnf', 'install', '-y', package_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"安装软件包失败：{result.stderr}")
        return
    # 通过软件包获取二进制包名
    # 安装rpm
    print("正在安装rpm包...")
    result = subprocess.run(['dnf', 'install', '-y', 'rpm'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"安装rpm失败：{result.stderr}")
        return
    # 安装rpmdevtools
    print("正在安装rpmdevtools...")
    result = subprocess.run(['dnf', 'install', '-y', 'rpmdevtools'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"安装rpmdevtools失败：{result.stderr}")
        return
    # 获取软件源码包
    print("正在获取软件源码包...")
    result = subprocess.run(['yumdownloader', '--source', package_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"获取软件源码包失败：{result.stderr}")
        return
    lines = result.stdout.splitlines()
    src_rpm_package_name = ""
    for line in lines:
        # 检查行中是否包含krb5的源代码包
        if package_name in line and '.src.rpm' in line:
            # 获取line中krb5到.src.rpm的字符串内容
            src_rpm_package_name = re.search(rf'{package_name}.*\.src\.rpm', line).group(0)

    if not src_rpm_package_name:
        print("未找到软件源码包")
        return
    print(f"找到软件源码包：{src_rpm_package_name}")
    # 安装软件源码包
    print("正在安装软件源码包...")
    result = subprocess.run(['rpm', '-ivh', src_rpm_package_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"安装软件源码包失败：{result.stderr}")
        return
    # 构建软件源码包
    print("正在构建软件源码包...")
    result = subprocess.run(
        ['rpmbuild', '-ba', f"/root/rpmbuild/SPECS/{package_name}.spec"],
        capture_output=True, text=True)
    # 检查命令是否成功执行
    if result.returncode != 0:
        # 从错误输出中提取依赖列表
        dependencies = re.findall(r'(\w+) is needed', result.stderr)
        if dependencies:
            print("需要安装的依赖软件包列表:")
            for dep in dependencies:
                # 尝试安装依赖
                dep_result = subprocess.run(['yum', 'install', '-y', dep], capture_output=True, text=True)
                if dep_result.returncode == 0:
                    print(f"安装依赖{dep}")
                else:
                    print(f"安装依赖{dep}失败：{dep_result.stderr}")
                    return
        # 重新构建软件源码包
        print("重新构建软件源码包...")
        result = subprocess.run(
            ['rpmbuild', '-ba', f"/root/rpmbuild/SPECS/{package_name}.spec"],
            capture_output=True, text=True)
        if result.returncode != 0:
            print(f"重新构建软件源码包失败：{result.stderr}")
            return

    print(f"软件源码包{package_name}构建成功")
    # 遍历~/rpmbuild/RPMS下的架构文件夹,在遍历架构文件夹内除了debuginfo、debugsource、help之外的rpm包
    extracted_names = []
    for arch in os.listdir("/root/rpmbuild/RPMS"):
        for rpm in os.listdir(f"/root/rpmbuild/RPMS/{arch}"):
            if package_name in rpm and 'debuginfo' not in rpm and 'debugsource' not in rpm and 'help' not in rpm:
                print(f"找到软件包{package_name}的rpm包：{rpm}")
                # 正则表达式，用于匹配文件名直到-数字之前
                pattern = re.compile(r'(.+?)-\d+')
                match = pattern.search(rpm)
                if match:
                    extracted_names.append(match.group(1))
    # 遍历提取到的二进制包名,获取二进制命令名
    rpm_package_names = []
    # 正则表达式，用于匹配 /usr/bin/ 后面的文件名
    pattern = re.compile(r'/usr/bin/(\S+)')
    for extracted_name in extracted_names:
        # 执行 rpm 命令和 grep 命令，捕获输出
        rpm_result = subprocess.run(['rpm', '-ql', extracted_name], stdout=subprocess.PIPE, text=True)
        # 检查 rpm 命令是否成功执行
        if rpm_result.returncode == 0:
            # 将输出按行分割
            rpm_lines = rpm_result.stdout.splitlines()
            # 遍历每一行，使用正则表达式提取文件名
            for line in rpm_lines:
                match = pattern.search(line)
                if match:
                    # 将提取的文件名添加到列表中
                    rpm_package_names.append(match.group(1))
    # 生成所有二进制包的测试脚本
    total_commands = []
    for rpm_package_name in rpm_package_names:
        commands = get_test_script_by_rpm_package_name(package_name, rpm_package_name)
        if commands:
            total_commands.extend(commands)
    # 在software_dir下保存{package_name}.json套件
    print("开始生成套件...")
    software_dir = os.path.join(current_dir_path, TEST_CASE_DIR, package_name)
    with open(os.path.join(software_dir, f'{package_name}.json'), "w") as f:
        suite_json_template = {"path": f"$OET_PATH/{TESTCASE_DIR}/{package_name}", "cases": []}
        for index, command in enumerate(total_commands):
            if not command:
                command = f"{package_name}_{index+1}"
            suite_json_template["cases"].append({"name": f"{command}"})
        json.dump(suite_json_template, f, indent=4)
        print(f"生成{package_name}.json套件")

def get_test_script_md(package_name):
    # 读取software_dir下的.sh文件
    software_dir = os.path.join(current_dir_path, TEST_CASE_DIR, package_name)
    # 每个文件生成对应的md文件
    for file in os.listdir(software_dir):
        if file.endswith(".sh"):
            # 读取文件内容
            with open(os.path.join(software_dir, file), "r") as f:
                script = f.read()
            # 生成md文件
            md_file = generate_markdown(package_name, file, script)
            # 在software_dir下保存{file}.md
            with open(os.path.join(software_dir, f"{file}.md"), "w") as f:
                f.write(md_file)
            print(f"生成测试文档{software_dir}/{file}.md")


def main():
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description='根据软件包的help和测试文档生成测试脚本')

    # 添加参数
    # 模式
    parser.add_argument('-m', '--mode', help='模式，默认为shell，shell和md', default='shell')
    # 软件包名
    parser.add_argument('-n', '--package-name', help='软件包名称')

    # 解析命令行参数
    args = parser.parse_args()

    # 根据参数执行操作
    if args.mode == 'shell':
        get_test_script(args.package_name)
    elif args.mode == 'md':
        get_test_script_md(args.package_name)


if __name__ == "__main__":
    main()
