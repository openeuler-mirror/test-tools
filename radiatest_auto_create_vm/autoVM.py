import requests
import urllib3
from typing import Dict
urllib3.disable_warnings( )

AUTH_TOKEN = "JWT eyJhbGciOiJIUzUxMiIsImlhdCI6MTc2Mjc3MjYwMywiZXhwIjoxNzYyOTUyNjAzfQ.I+g4WPGd4SP3GLEZw/lMJwotHJ0Gm5UgjPPval+z2DTaANMDx8g46t1Tsj1DiXo43G9dVHWZvOZwROS0UGxilpMtvpvpAHygs7S+nO9SCno=.txxtCPoSY6Wv9-kPHSg_cSB7_wVCIq17L6KICHAPKvD5WTbSS6djOIX93LkXDAqP48rXNmyBhFx9YdX4hBM8qA"

def vm_req(auth: str,body:Dict):
    hds = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': 'application/json,text/plain,*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': auth,
    'Origin': 'https://172.168.131.14:21500',
    'Connection': 'keep-alive',
    'Referer': 'https://172.168.131.14:21500/home/ws/default/resource-pool/management/vmachine/0A==',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
    }
    resp = requests.post('https://172.168.131.14:21500/api/v1/vmachine', headers=hds, json=body, verify=False)
    print(resp.status_code,resp.content)
    return resp

def get_vm_ip(auth: str, target_description: str):
    hds = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': 'application/json,text/plain,*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': auth,
    'Origin': 'https://172.168.131.14:21500',
    'Connection': 'keep-alive',
    'Referer': 'https://172.168.131.14:21500/home/ws/default/resource-pool/management/vmachine/0A==',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
    }
    resp = requests.get('https://172.168.131.14:21500/api/v1/vmachine?description=Auto-created+VM+test&machine_group_id=8&page_num=1&page_size=50', headers=hds, verify=False)
    data = resp.json()
    print(data)
    for item in data.get('data', {}).get("items", []):
        if item.get('description') == target_description:
            print(item.get('ip'))
            return item.get('ip')


if __name__ == "__main__":
    auth_token = AUTH_TOKEN
    # 构造虚拟机创建请求体
    body = {
        "frame_number": [{"frame": "aarch64", "machine_num": 1}],
        "pm_select_mode": "auto",
        "product": "openEuler",
        "version": "55",
        "milestone_id": "172884",
        "cpu_mode": "host-passthrough",
        "memory": 4096,
        "socket": 1,
        "cores": 1,
        "threads": 1,
        "description": "Auto-created VM test",
        "method": "import",
        "permission_type": "public",
        "create_id": "gitee_11364881",
        "org_id": 2,
        "machine_group_id": "8"
    }

    # vm_req(auth_token, body)
    print(get_vm_ip(auth_token, "Auto-created VM test"))