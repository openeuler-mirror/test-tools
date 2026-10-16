#!/bin/bash
#==============================================================================
# 软件包对比脚本 - 优化版
# 功能：对比发布公告与repo中的源码包，生成xlsx结果文件（含everything、epol两个sheet）
# 用法：bash 软件包对比.sh
#==============================================================================
set -euo pipefail

# 工作目录
WORK_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$WORK_DIR"

#============================ 配置区域（按需修改）=============================
REPO_BASE="http://121.36.84.172/dailybuild/EBS-openEuler-24.03-LTS-SP4/rc10_openeuler-2026-06-29-02-08-05"
GPGKEY="http://121.36.84.172/dailybuild/EBS-openEuler-24.03-LTS-SP4/rc10_openeuler-2026-06-29-02-08-05/source/RPM-GPG-KEY-openEuler"
RELEASE_BRANCH="openEuler-24.03-LTS-SP4"
OUTPUT_FILE="${WORK_DIR}/软件包对比结果.xlsx"
#==============================================================================

echo "================================================"
echo "  软件包对比脚本 - 优化版"
echo "  工作目录: ${WORK_DIR}"
echo "  输出文件: ${OUTPUT_FILE}"
echo "================================================"

#============================ 1. 配置yum源 =============================
echo "[1/6] 配置 source / EPOL_source 源..."
cat > /etc/yum.repos.d/compare.repo <<EOF
[source]
name=source
baseurl=${REPO_BASE}/source/
enabled=1
gpgcheck=1
gpgkey=${GPGKEY}

[EPOL_source]
name=EPOL_source
baseurl=${REPO_BASE}/EPOL/main/source/
enabled=1
gpgcheck=1
gpgkey=${GPGKEY}
EOF
echo "  -> 源配置完成"

#============================ 2. 导出源码包列表 =============================
echo "[2/6] 导出repo源码包列表..."
dnf list --repo="source" | grep ".src" | awk '{print $1}' | awk -F. 'OFS="."{$NF="";print}' | awk '{print substr($0,1,length($0)-1)}' | sort > everything_source_list
dnf list --repo="EPOL_source" | grep ".src" | awk '{print $1}' | awk -F. 'OFS="."{$NF="";print}' | awk '{print substr($0,1,length($0)-1)}' | sort > epol_source_list
echo "  -> everything_source_list: $(wc -l < everything_source_list) 个包"
echo "  -> epol_source_list:       $(wc -l < epol_source_list) 个包"

#============================ 3. 获取发布软件包列表 =============================
echo "[3/6] 从release-management获取发布软件包列表..."
dnf install -y git >/dev/null 2>&1
git clone https://atomgit.com/openeuler/release-management.git
cp -r release-management/${RELEASE_BRANCH}/baseos ./
cp -r release-management/${RELEASE_BRANCH}/everything-exclude-baseos ./
cp -r release-management/${RELEASE_BRANCH}/epol ./
rm -rf release-management

cat baseos/pckg-mgmt.yaml | grep "name:" | awk '{print $NF}' > baseos/baseos_source
cat everything-exclude-baseos/pckg-mgmt.yaml | grep "name:" | awk '{print $NF}' > everything-exclude-baseos/everything_source
cat epol/pckg-mgmt.yaml | grep "name:" | awk '{print $NF}' | sort > epol_source

dnf install -y dos2unix >/dev/null 2>&1
dos2unix baseos/baseos_source everything-exclude-baseos/everything_source epol_source

echo "  -> baseos_source:    $(wc -l < baseos/baseos_source) 个包"
echo "  -> everything_source:$(wc -l < everything-exclude-baseos/everything_source) 个包"
echo "  -> epol_source:      $(wc -l < epol_source) 个包"

#============================ 4. 数据检查 =============================
echo "[4/6] 数据检查..."
# 检查baseos_source、everything_source是否有重复
DUP=$(cat baseos/baseos_source everything-exclude-baseos/everything_source | sort | uniq -d)
if [ -n "$DUP" ]; then
    echo "  [警告] baseos_source 与 everything_source 存在重复软件包:"
    echo "$DUP"
else
    echo "  -> 无重复软件包"
fi
# 汇总
cat baseos/baseos_source everything-exclude-baseos/everything_source | sort > huizong_everthing_source
echo "  -> 汇总everything: $(wc -l < huizong_everthing_source) 个包"

#============================ 5. 对比分析 =============================
echo "[5/6] 进行对比分析..."
# --- everything ---
cat everything_source_list huizong_everthing_source | sort | uniq -d > everything_d
cat everything_source_list huizong_everthing_source | sort | uniq -u > everything_u
cat huizong_everthing_source everything_u | sort | uniq -d > huizong_everthing_source_u
cat everything_source_list everything_u | sort | uniq -d > everything_source_list_u

# --- epol ---
cat epol_source_list epol_source | sort | uniq -d > epol_d
cat epol_source_list epol_source | sort | uniq -u > epol_u
cat epol_source epol_u | sort | uniq -d > epol_source_u
cat epol_source_list epol_u | sort | uniq -d > epol_source_list_u

echo "  --- everything ---"
echo "  共有:     $(wc -l < everything_d) 个"
echo "  公告独有: $(wc -l < huizong_everthing_source_u) 个"
echo "  repo独有: $(wc -l < everything_source_list_u) 个"
echo "  --- epol ---"
echo "  共有:     $(wc -l < epol_d) 个"
echo "  公告独有: $(wc -l < epol_source_u) 个"
echo "  repo独有: $(wc -l < epol_source_list_u) 个"

#============================ 6. 生成xlsx结果文件 =============================
echo "[6/6] 生成xlsx结果文件..."
# 安装openpyxl
if ! python3 -c "import openpyxl" 2>/dev/null; then
    dnf install -y python3-openpyxl >/dev/null 2>&1 || pip3 install openpyxl >/dev/null 2>&1 || true
fi

python3 - <<'PYEOF'
import os, sys
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
except ImportError:
    print("[警告] openpyxl未安装，跳过xlsx生成")
    sys.exit(0)

wb = openpyxl.Workbook()

# 样式定义
header_font = Font(bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
common_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")   # 绿色-共有
announce_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # 黄色-公告独有
repo_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")     # 红色-repo独有
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)
center_align = Alignment(horizontal='center', vertical='center')
left_align = Alignment(horizontal='left', vertical='center')

HEADERS = ["序号", "软件包名", "类型", "说明"]

def count_lines(path):
    if not os.path.exists(path):
        return 0
    with open(path) as f:
        return sum(1 for line in f if line.strip())

def fill_sheet(ws, common_file, announce_file, repo_file, sheet_label):
    """填充一个sheet的数据"""
    # 写表头
    ws.append(HEADERS)
    for col in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    row_num = 1
    sections = [
        (common_file,  "共有",     "公告和repo都有", common_fill),
        (announce_file, "公告独有", "仅公告中有",     announce_fill),
        (repo_file,     "repo独有", "仅repo中有",     repo_fill),
    ]
    for filepath, type_label, desc, fill in sections:
        if not os.path.exists(filepath):
            continue
        with open(filepath) as f:
            for line in f:
                pkg = line.strip()
                if not pkg:
                    continue
                row_num += 1
                ws.cell(row=row_num, column=1, value=row_num - 1)
                ws.cell(row=row_num, column=2, value=pkg)
                ws.cell(row=row_num, column=3, value=type_label)
                ws.cell(row=row_num, column=4, value=desc)
                for col in range(1, 5):
                    cell = ws.cell(row=row_num, column=col)
                    cell.border = thin_border
                    cell.fill = fill
                    cell.alignment = center_align if col != 2 else left_align

    # 调整列宽
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 45
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 20
    # 冻结表头
    ws.freeze_panes = 'A2'
    # 自动筛选
    ws.auto_filter.ref = f"A1:D{row_num}"

# ====== Sheet 1: everything ======
ws1 = wb.active
ws1.title = "everything"
fill_sheet(ws1, "everything_d", "huizong_everthing_source_u", "everything_source_list_u", "everything")

# ====== Sheet 2: epol ======
ws2 = wb.create_sheet("epol")
fill_sheet(ws2, "epol_d", "epol_source_u", "epol_source_list_u", "epol")

# ====== Sheet 3: 汇总 ======
ws3 = wb.create_sheet("汇总", 0)  # 放在最前面
ws3.append(["分类", "共有", "公告独有", "repo独有", "合计"])
for col in range(1, 6):
    cell = ws3.cell(row=1, column=col)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border

ev_c = count_lines("everything_d")
ev_a = count_lines("huizong_everthing_source_u")
ev_r = count_lines("everything_source_list_u")
ep_c = count_lines("epol_d")
ep_a = count_lines("epol_source_u")
ep_r = count_lines("epol_source_list_u")

data = [
    ["everything", ev_c, ev_a, ev_r, ev_c + ev_a + ev_r],
    ["epol",       ep_c, ep_a, ep_r, ep_c + ep_a + ep_r],
    ["合计",       ev_c+ep_c, ev_a+ep_a, ev_r+ep_r, ev_c+ev_a+ev_r+ep_c+ep_a+ep_r],
]
for i, row in enumerate(data, start=2):
    for j, val in enumerate(row, start=1):
        cell = ws3.cell(row=i, column=j, value=val)
        cell.border = thin_border
        cell.alignment = center_align
        if i == 4:  # 合计行加粗
            cell.font = Font(bold=True)
ws3.column_dimensions['A'].width = 15
for col in ['B', 'C', 'D', 'E']:
    ws3.column_dimensions[col].width = 12

output = os.path.join(os.path.dirname(os.path.abspath(".")), "软件包对比结果.xlsx")
output = os.path.join(os.getcwd(), "软件包对比结果.xlsx")
wb.save(output)
print(f"  -> 已生成: {output}")
PYEOF

echo ""
echo "================================================"
echo "  对比完成！"
echo "  结果文件: ${OUTPUT_FILE}"
echo "  Sheet说明:"
echo "    汇总       - 各类别数量统计"
echo "    everything - everything源码包对比明细"
echo "    epol       - epol源码包对比明细"
echo "  颜色说明:"
echo "    绿色 - 共有（公告和repo都有）"
echo "    黄色 - 公告独有（仅公告中有）"
echo "    红色 - repo独有（仅repo中有）"
echo "================================================"
