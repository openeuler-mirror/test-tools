import re
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import ChatMessage
from config import config
from prompt import GENERATE_SCRIPT_SYS_PROMPT, GENERATE_SCRIPT_USER_PROMPT, CHECK_PACKAGE_SYS_PROMPT, CHECK_PACKAGE_USER_PROMPT, GENERATE_MARKDOWN_SYS_PROMPT, GENERATE_MARKDOWN_USER_PROMPT
MAX_TIMEOUT = 30
MAX_TOKENS = 8192


def get_llm():
    llm = ChatOpenAI(
        openai_api_key=config["LLM_KEY"],
        openai_api_base=config["LLM_URL"],
        model_name=config["LLM_MODEL_NAME"],
        tiktoken_model_name="cl100k_base",
        max_tokens=MAX_TOKENS,
        streaming=True,
        temperature=0.1,
        request_timeout=MAX_TIMEOUT,
    )
    return llm


def get_chat_message(role, content):
    return ChatMessage(role=role, content=content)


def generate_script(package_name, rpm_package_name, package_info, command_name,command_info, note, history_script, history_script_result):
    llm = get_llm()
    messages = [
        get_chat_message("system", GENERATE_SCRIPT_SYS_PROMPT),
        get_chat_message(
            "user", GENERATE_SCRIPT_USER_PROMPT.format(
                package_name=package_name, package_info=package_info, command_name=command_name,command_info=command_info, note=note, history_script=history_script,history_script_result=history_script_result)),]
    try:
        result = llm.invoke(messages).content
        matches = re.findall(r"```shell(.*?)```", result, re.DOTALL)
        return matches[0]
    except Exception as e:
        print(f"调用大模型生成脚本失败:{str(e)}")
        return ""


def check_package_command(package_name, package_info):
    llm = get_llm()
    messages = [get_chat_message("system", CHECK_PACKAGE_SYS_PROMPT), get_chat_message(
        "user", CHECK_PACKAGE_USER_PROMPT.format(package_name=package_name, package_info=package_info)), ]
    result = llm.invoke(messages).content
    matches = re.findall(r"```json(.*?)```", result, re.DOTALL)
    if matches:
        result_json = json.loads(matches[0])
        return result_json['command']
    else:
        return None


def generate_markdown(package_name, test_script_name, test_script):
    llm = get_llm()
    messages = [get_chat_message("system", GENERATE_MARKDOWN_SYS_PROMPT), get_chat_message(
        "user", GENERATE_MARKDOWN_USER_PROMPT.format(package_name=package_name, test_script_name=test_script_name, test_script=test_script)), ]
    result = llm.invoke(messages).content
    matches = re.findall(r"```markdown(.*?)```", result, re.DOTALL)
    return matches[0]
