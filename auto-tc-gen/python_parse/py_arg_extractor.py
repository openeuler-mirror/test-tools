# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
# @Author    	:   hourui
# @Contact   	:   softgreet@qq.com
# @Date      	:   2023-10-12 12:00:00
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   python中参数解析
#####################################

#coding=UTF-8

import ast
import os
import subprocess
import sys
from abc import ABCMeta
from copy import deepcopy
from typing import Union, Iterable
import timeout_decorator
from pebble import ProcessPool
from python_parse.parser import UniArgParser, ArgParser, OptParser
from python_parse.commonlib import FileType, compare_ast
from logger import log

# 检测到这些函数调用时不予执行
no_exe_label = {
    'input',
    'print',
    'os.system',
    'time.sleep',
    'subprocess'
}

pool = ProcessPool()
log_file = ''


def subprocess_task(code='', global_env={}):
    """
    Args:
        code: 放在子进程中尝试执行的代码，防止因执行所需系统环境和参数的缺失导致的崩溃
        global_env: python代码的执行时的环境
    """
    stdin_bac, stdout_bac, stderr_bac = sys.stdin, sys.stdout, sys.stderr
    sys.stdin, sys.stdout, sys.stderr = None, None, None
    # 对于因执行所需系统环境和参数的缺失导致的异常不作处理
    try:
        ret_sink = '__RET_SINK'
        exec(f"{ret_sink}={code}", global_env)
        return global_env[ret_sink]
    except:
        log.warning("因模拟执行python代码时的输入参数未知以及所需系统环境的缺失导致的异常", log_file)
    finally:
        sys.stdin, sys.stdout, sys.stderr = stdin_bac, stdout_bac, stderr_bac


@timeout_decorator.timeout(1)
def timing_wrap_func(func, args, keywords):
    """
    封装需要执行的函数，超时退出
    :param: 执行的回调函数func及其参数args, keywords
    """
    stdin_bac, stdout_bac, stderr_bac = sys.stdin, sys.stdout, sys.stderr
    sys.stdin, sys.stdout, sys.stderr = None, None, None
    try:
        return func(*args, **keywords)
    except:
        log.warning("因模拟执行python代码时的输入参数未知以及所需系统环境的缺失导致的异常", log_file)
    finally:
        sys.stdin, sys.stdout, sys.stderr = stdin_bac, stdout_bac, stderr_bac


class ImportObj:
    """
    引用对象， 封装了引用的路径,如果不封装直接用string表示的话将无法区分是一个引用还是一个值为字符串的变量。
    """

    def __init__(self, val=None) -> None:
        self.val: str = val

    # 引用路径的合并
    def __add__(self, obj):
        if isinstance(obj, str):
            return ImportObj(f"{self.val}.{obj}")
        elif isinstance(obj, ImportObj):
            return ImportObj(f"{self.val}.{obj.val}")
        else:
            raise RuntimeError("Wrong parameter type")

    def __str__(self) -> str:
        return self.val


class Environment(metaclass=ABCMeta):
    """python执行环境的一个不完全简单模拟
    作为抽象基类存储了当前环境下定义和引用的变量,函数以及类;同时定义了对各种ast节点的通用处理方法,即命名为exec_{ast节点类型}的方法
    Attributes:
        driver: ast节点的处理方法的驱动,通过表驱动的方式用来判断该如何处理特定类型的ast节点,具体通过类方法exec_driver来使用和维护
        UNSCAN/SCANNING/SCANNED: 当前环境的扫描状态
    """
    UNSCAN = 0
    SCANNING = 1
    SCANNED = 2

    driver = None

    @classmethod
    def exec_driver(cls, env, node: ast.AST):
        """
        Args:
            env:通过类方法来调用的,所以需要再传入一个Environment对象,调用的时候通常是传递self
            node: 抽象语法树节点
        """
        if not cls.driver:
            # 为不需要进行处理的节点定义的默认不作任何处理的函数
            def default(m, n): return None

            cls.collection = {
                ast.List: list,
                ast.Tuple: tuple,
                ast.Set: set,
            }
            cls.bin_op = {
                ast.Add: lambda x, y: x + y,
                ast.Sub: lambda x, y: x - y,
                ast.Mult: lambda x, y: x * y,
                ast.Div: lambda x, y: x / y,
                ast.FloorDiv: lambda x, y: x // y,
                ast.Mod: lambda x, y: x % y,
                ast.Pow: lambda x, y: x ** y,
                ast.LShift: lambda x, y: x << y,
                ast.RShift: lambda x, y: x >> y,
                ast.BitOr: lambda x, y: x | y,
                ast.BitAnd: lambda x, y: x & y,
                ast.MatMult: lambda x, y: x @ y
            }
            cls.driver = {
                ast.Import: cls.exec_import_statement,
                ast.ImportFrom: cls.exec_import_from,
                ast.ClassDef: cls.exec_cls_or_fun_def,
                ast.FunctionDef: cls.exec_cls_or_fun_def,
                ast.Expr: cls.exec_expr,
                ast.Call: cls.exec_call,
                ast.Return: cls.exec_return,
                ast.If: cls.exec_if_statement,
                ast.With: cls.exec_block,
                ast.Try: cls.exec_block,
                ast.While: cls.exec_block,
                ast.For: cls.exec_block,
                ast.Constant: cls.exec_constant,
                ast.Attribute: cls.exec_attribute,
                ast.Name: cls.exec_name,
                ast.Assign: cls.exec_assign,
                ast.AugAssign: cls.exec_aug_assign,
                ast.List: cls.exec_collection,
                ast.Tuple: cls.exec_collection,
                ast.Set: cls.exec_collection,
                ast.Dict: cls.exec_dict,
                ast.ListComp: cls.exec_collection_comp,
                ast.SetComp: cls.exec_collection_comp,
                ast.GeneratorExp: cls.exec_collection_comp,
                ast.DictComp: cls.exec_collection_comp,
                ast.Delete: default,
                ast.Break: default,
                ast.Continue: default,
                ast.Raise: default,
                ast.arguments: default,
                ast.Compare: default,
                ast.Global: default,
                ast.Lambda: default,
                ast.BinOp: cls.exec_bin_op,
                ast.UnaryOp: cls.exec_unary_op,
                ast.BoolOp: default,
                ast.IfExp: default,
                ast.Pass: default,
                ast.Slice: default,
                ast.Subscript: default,
                ast.Assert: default,
                ast.Yield: default,
                ast.YieldFrom: default,
                ast.Starred: default,
                ast.JoinedStr: default
            }
        return cls.driver[type(node)](env, node)

    def __init__(self, node: Union[ast.Module, ast.FunctionDef, ast.ClassDef], parent_env) -> None:
        """
        Args:
            node:   和当前环境相对应的ast节点,节点类型只能是ast.Module, ast.FunctionDef, ast.ClassDef,
                    分别对应了python执行时的模块级别的全局环境(ModEnv),函数和方法内部的局部环境(FuncEnv)以及类环境(ClsEnv)
            parent_env: 当前环境的父环境。ModEnv没有父环境。而三种环境下面都可能会有子FuncEnv,子ClsEnv。
        Attributes:
            self.unknown_import_star:   未知的from xxx import *
            self.imports: 对python内置变量、方法和对象,第三方包的变量、方法和对象以及无法求出值的包内其它模块的变量的引用
            self.variables:   存储了当前环境下定义的变量对象和方法/类的定义以及从包内其它模块导入的可以求出值的变量和方法/类定义
            self.import_codes: 存储了检测到的import语句,用于在执行一些未知方法时模拟Python的命名空间
            self.scanned:    当前Environment是否被扫描过,扫描过的将不再重复检测方法/类定义
        """
        self.node = node
        self.parent_env: Environment = parent_env
        self.unknown_import_star = set()
        self.imports = {}
        self.variables = {}
        self.import_codes = []
        self.scanned = Environment.UNSCAN

    def exec(self, args: list = None, keywords: dict = None):
        if self.scanned == Environment.UNSCAN:
            self.scanned = Environment.SCANNING
        ret = self.exec_codeblock(list(ast.iter_child_nodes(self.node)))
        self.scanned = Environment.SCANNED
        return ret

    def exec_codeblock(self, nodes: list[ast.AST]):
        ret = None
        for node in nodes:
            val = self.exec_driver(self, node)
            # 检测的目的是检测到所有语句，所以遇到return语句并不真的返回，并且选择最后一个作为返回值
            if val and isinstance(node, ast.Return):
                ret = val
        return ret

    def exec_import_statement(self, node: ast.Import) -> None:
        """处理import语句
        能成功求解出值的放入Variable中,否则放入Import中
        """
        if self.scanned != Environment.SCANNING:
            return
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            target = self.locate(alias.name)
            if target:
                self.variables[name] = target
            else:
                self.imports[name] = ImportObj(alias.name)
                self.import_codes.append(ast.unparse(node))

    def exec_import_from(self, node: ast.ImportFrom) -> None:
        if self.scanned != Environment.SCANNING:
            return None
        if node.level != 0:
            # 处理从相对路径.和..导入的情况
            path = self.get_root_env().belongs.get_path()
            if path.endswith('__init__'):
                path = path[:-9]
                node.level -= 1
            while node.level != 0:
                path = path[:path.rfind('.')]
                node.level -= 1
            node.module = f"{path}.{node.module}" if node.module else path
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            if name != '*':
                # 处理from xxx import *
                module_path = f"{node.module}.{alias.name}"
                val = self.locate(module_path)
                if val:
                    self.variables[name] = val
                else:
                    self.imports[name] = ImportObj(module_path)
                    self.import_codes.append(ast.unparse(node))
            else:
                module = self.locate(node.module)
                if module:
                    # 定位到了Package/Module这样的Python包内文件组织结构上的抽象类时需要转化为对应的初始模块(__init__.py)/ModEnv
                    if isinstance(module, Package):
                        module = module.init
                    if isinstance(module, Module):
                        source_env = module.env
                    else:
                        source_env = module
                    if not source_env.scanned:
                        source_env.exec()
                    self.imports.update(source_env.imports)
                    self.variables.update(source_env.variables)
                else:
                    self.unknown_import_star.add(ImportObj(node.module))
                    self.import_codes.append(ast.unparse(node))

    def exec_cls_or_fun_def(self, node: Union[ast.ClassDef, ast.FunctionDef]) -> None:
        """
        存储函数和类定义到Variable中
        """
        if self.scanned != Environment.SCANNING:
            return
        if isinstance(node, ast.ClassDef):
            self.variables[node.name] = ClsEnv(node, self)
        elif isinstance(node, ast.FunctionDef):
            self.variables[node.name] = FuncEnv(node, self)
        else:
            raise RuntimeError("Wrong args in exec_ClsOrFunDef!")

    def dfs_assign(self, targets: Union[list, tuple], vals: Iterable):
        n = len(targets)
        if len(vals) != n:
            vals = [None for i in range(n)]
        for i in range(n):
            target = str(targets[i])
            if (vals[i] is not None) or (target not in self.variables):
                self.variables[target] = vals[i]

    def exec_assign(self, node: ast.Assign) -> None:
        """
        处理赋值语句, 因为Python支持a,(b,[c,d],e),f这样的递归赋值,需要递归的进行处理(调用dfs_Assign方法)
        """
        val = self.exec_driver(self, node.value)
        targets = [self.exec_driver(self, target) for target in node.targets]
        if isinstance(targets[0], (tuple, list)):
            if not isinstance(val, Iterable):
                val = [val]
            self.dfs_assign(targets[0], val)
        else:
            for target in targets:
                if not target:
                    continue
                if isinstance(target, ImportObj):
                    target = target.val
                    if target.startswith('self.'):
                        cls_env = self.get_cls_env()
                        cls_env.variables[target[5:]] = val
                    else:
                        self.variables[target] = val
                else:
                    raise RuntimeError("unknown ret type")

    def exec_aug_assign(self, node: ast.AugAssign) -> None:
        trans_bin_op_node = ast.BinOp()
        trans_bin_op_node.left = deepcopy(node.target)
        trans_bin_op_node.left.ctx = ast.Load()
        trans_bin_op_node.op = node.op
        trans_bin_op_node.right = node.value
        trans_assign_node = ast.Assign()
        trans_assign_node.targets = [node.target]
        trans_assign_node.value = trans_bin_op_node
        # 防止在ast.unparse查看对应代码时出错,所以给了个虚假的临时行号1，但它不影响unparse的结果
        trans_assign_node.lineno = 1
        self.exec_driver(self, trans_assign_node)

    def exec_if_statement(self, node: ast.If):
        # 当测试条件是__name__ == '__main__'时只有启动模块才往下执行内部的代码块
        target = ast.parse(
            "if __name__ == '__main__':\n\tpass", mode='exec').body[0].test
        if (not compare_ast(node.test, target)) or self.booted():
            return self.exec_codeblock(node.body)

    def exec_block(self, node: Union[ast.With, ast.Try, ast.While, ast.For]):
        return self.exec_codeblock(node.body)

    def exec_expr(self, node: ast.Expr) -> None:
        self.exec_driver(self, node.value)

    def exec_call(self, node: ast.Call):
        func = self.exec_driver(self, node.func)
        node_args, node_keywords = node.args, node.keywords
        args, keywords = [], {}
        if node_args:
            if isinstance(node_args[-1], ast.Starred):
                star_val = self.exec_driver(self, node_args[-1].value)
                if isinstance(star_val, Iterable):
                    args.extend(star_val)
                node_args = node_args[:-1]
            for arg in node_args:
                val = self.exec_driver(self, arg)
                args.append(val.val if isinstance(val, ImportObj) else val)
        if node_keywords:
            if not node_keywords[-1].arg:
                star_val = self.exec_driver(self, node_keywords[-1].value)
                if isinstance(star_val, dict):
                    keywords.update(star_val)
                node_keywords = node_keywords[:-1]
            for keyword in node_keywords:
                val = self.exec_driver(self, keyword.value)
                if isinstance(val, Environment):
                    val = str(val)
                keywords[keyword.arg] = val.val if isinstance(
                    val, ImportObj) else val
        if func:
            # 对类名的调用视为对类的__init__方法的调用，在该类之前未被扫描过的时候先执行一遍
            if isinstance(func, ClsEnv):
                if func.scanned == Environment.UNSCAN:
                    func.exec()
                if '__init__' in func.variables:
                    func.variables['__init__'].exec(args, keywords)
                return func
            # 对自身的递归调用不予执行
            if isinstance(func, FuncEnv):
                if func != self:
                    return func.exec(args, keywords)
                return None
            elif isinstance(func, ImportObj):
                func = func.val
                # 程序国际化时对字符串的封装,_("xxx")可以将"xxx"转化为对应国家地区的文字
                if func == '_':
                    return args[0] if args else None
                # 通过load_entry_point根据group和entry_name动态加载软件包真正的执行入口函数时的处理
                if func == 'load_entry_point':
                    _, group, entry_name = args
                    name = self.get_entry(group, entry_name)
                    target = self.locate(name)
                    if isinstance(target, FuncEnv):
                        return target.exec(args, keywords)
                    return None
                # 对super调用的处理,仅处理了和参数相关的部分，其它调用不予处理
                if func == "super":
                    if not args or args[0] == self.get_cls_env():
                        for base in self.get_cls_env().bases:
                            if isinstance(base, ArgParser) or isinstance(base, OptParser):
                                return base
                    return None
                # 处理self调用
                if func.startswith('self.'):
                    cls_env = self.get_cls_env()
                    ok, ret = cls_env.find(func[5:])
                    if ok:
                        return ret
                if func in UniArgParser.PARSERS:
                    # 创建参数处理库optparse/argparse的参数parser对象时转为对Parser.py中自定义参数parser的对象的创建
                    return UniArgParser.build(func, args, keywords)
                else:
                    # 未知的引用方法的执行
                    try:
                        keywords = ','.join(
                            f"{key}={val}" for key, val in keywords.items())
                        args = ','.join(f"'{arg}'" if isinstance(
                            arg, str) else str(arg) for arg in args)
                        if keywords and args:
                            code = "{}({},{})".format(func, args, keywords)
                        elif keywords:
                            code = "{}({})".format(func, keywords)
                        elif args:
                            code = "{}({})".format(func, args)
                        else:
                            code = "{}()".format(func)
                        if func not in no_exe_label:
                            return self.exec_code(code)
                    except:
                        # 屏蔽处理未知引用方法导致的异常
                        log.warning("因模拟执行python代码时的输入参数未知以及所需系统环境的缺失导致的异常", log_file)
            elif callable(func):
                # 可调用对象的处理，包括内置方法（str.split,list.append等）的执行和自定义参数parser对象的方法的执行
                return timing_wrap_func(func, args=args, keywords=keywords)
        return None

    def exec_return(self, node: ast.Return):
        if node.value:
            return self.exec_driver(self, node.value)
        return None

    def exec_constant(self, node: ast.Constant):
        return node.value

    def exec_attribute(self, node: ast.Attribute):
        """ 处理属性Attribute
        属性在ast节点中被表示为:{node.value}.{node.attr},且使用属性的方式有ast.Load,ast.Store,ast.Del
        ast.Load需要去加载属性的值
        ast.Store只需要返回对应的ImportObj对象,方便后续赋值
        ast.Del不予处理,目标是检测代码而不是真的执行,不过仍然和ast.Store一样返回了对应的ImportObj对象
        """
        val = self.exec_driver(self, node.value)
        if val:
            # node.value是Package对象时递归的去寻找node.attr,对应于从包名开始书写的Python表达式,eg: os.path.xxx
            if isinstance(val, Package):
                return val.dfs_locate([node.attr])
            # node.value是Module对象时需要转化为Module对应的ModEnv，然后在后续在ModEnv中进行寻找
            if isinstance(val, Module):
                val = val.env
            if isinstance(node.ctx, ast.Load):
                if isinstance(val, (ModEnv, ClsEnv)):
                    return val.find(node.attr)[1]
                elif isinstance(val, ImportObj):
                    if val.val == 'self':
                        ok, ret = self.get_cls_env().find(node.attr)
                        if ok:
                            return ret
                    val = val + node.attr
                    if val.val in no_exe_label:
                        return None
                    ok, ret = self.find(val.val)
                    if ok:
                        return ret
                    if val.val not in UniArgParser.PARSERS:
                        return val
                    else:
                        return UniArgParser.build(val.val)
                # 可能在之前已经得到了一个对象，即node.value是一个对象，此时通过内置函数直接返回对应的属性对象
                elif hasattr(val, node.attr):
                    return getattr(val, node.attr)
                else:
                    return None
            else:
                if isinstance(val, (ModEnv, ClsEnv)):
                    val = ImportObj(val.get_path())
                if isinstance(val, ImportObj):
                    return val + node.attr
        return None

    def exec_name(self, node: ast.Name):
        # python 中__file__表示当前文件名,这里没有选择去获取当前环境的根环境的所属模块的名字，直接取了命令名字。在检测参数的目标导向下其它文件的文件名并不重要
        if node.id == '__file__':
            return self.get_cur_command()
        if isinstance(node.ctx, ast.Load):
            # self直接返回了一个属性对象，放到了上一级去处理，也可以返回当前所属的ClsEnv
            if node.id == 'self':
                return ImportObj('self')
            ok, ret = self.find(node.id)
            if ok:
                if isinstance(ret, ImportObj):
                    val = ret.val
                    if val in no_exe_label:
                        return None
                    for i in range(len(val) + 1):
                        if (i == len(val) or val[i] == '.') and val[:i] in UniArgParser.PARSERS:
                            ret = UniArgParser.build(val[:i])
                            if val[i + 1:]:
                                attrs = val[i + 1:].split('.')
                                for attr in attrs:
                                    if hasattr(ret, attr):
                                        ret = getattr(ret, attr)
                            break
                return ret
        return ImportObj(node.id)

    def exec_collection(self, node: Union[ast.List, ast.Tuple, ast.Set]):
        # 处理集合对象list,tuple,set。该return语句等价于list/tuple/set(...), ...指代集合对象内部的值
        return self.__class__.collection[type(node)](self.exec_driver(self, elt) for elt in node.elts)

    def exec_collection_comp(self, node: Union[ast.ListComp, ast.SetComp, ast.GeneratorExp]):
        # 处理Python中的推导式,类似于[i for i in ...]
        val = self.exec_code(ast.unparse(node))
        if val and isinstance(node, ast.GeneratorExp):
            try:
                return list(val)
            except:
                # 并非所有情况都能转化成功
                log.warning("因模拟执行python代码时的输入参数未知以及所需系统环境的缺失导致的异常", log_file)
        return val

    def exec_code(self, code: str):
        """在Python中通过exec的方式真正的执行一段代码code
        在执行之前先获取到当前环境以及父环境的所有可能的import语句并执行,得到一个global_env
        同时将当前环境以及父环境的variables中的内容更新到global_env中
        最后将code,globalEnv封装成一个子进程任务放到子进程中去执行
        """
        try:
            global_env = {}
            for importCode in self.get_import_codes():
                try:
                    exec(importCode, global_env)
                except ImportError:
                    continue
            global_env.update(self.variables)
            node = self.parent_env
            while node:
                for key, val in node.variables.items():
                    if key not in global_env:
                        global_env[key] = val
                node = node.parent_env
            future = pool.schedule(subprocess_task, args=[
                code, global_env], timeout=1)
            result = future.result(1)
            return result
        except:
            return None

    def exec_dict(self, node: ast.Dict):
        """
        和list/set/tuple类似,不过是键值对的形式
        """
        keys, vals = node.keys, node.values
        ret = {}
        if keys:
            if keys[-1] is None:
                dblstar_val = self.exec_driver(self, vals[-1])
                if isinstance(dblstar_val, dict):
                    ret.update(dblstar_val)
                keys = keys[:-1]
                vals = vals[:-1]
            for i in range(len(keys)):
                key = self.exec_driver(self, keys[i])
                val = self.exec_driver(self, vals[i])
                ret[key] = val
        return ret

    def exec_bin_op(self, node: ast.BinOp):
        """对二元运算符的处理
        具体的二元运算符的类型以及对应的执行方式定义在cls.bin_op中
        """
        left = self.exec_driver(self, node.left)
        right = self.exec_driver(self, node.right)
        try:
            return self.bin_op[type(node.op)](left, right)
        except:
            return None

    def exec_unary_op(self, node: ast.UnaryOp):
        val = self.exec_driver(self, node.operand)
        try:
            op = node.op
            if isinstance(op, ast.UAdd):
                return val
            elif isinstance(op, ast.USub):
                return -val
            elif isinstance(op, ast.Not):
                return not val
            elif isinstance(op, ast.Invert):
                return ~val
        except:
            return None

    # 判断当前环境所属模块是否是启动模块
    def booted(self) -> bool:
        return self.get_root_env().belongs.booted()

    # 调用dfs_locate的入口
    def locate(self, name: str):
        if name:
            name = name.split('.')
            root_env = self.get_root_env()
            site_package = root_env.belongs.get_root_pyunit()
            return site_package.dfs_locate(name)
        return None

    def dfs_locate(self, names: list[str]):
        """递归的一层一层的去定位一个变量/ImportObj对象/函数/类所在的位置"""
        if self.scanned == Environment.UNSCAN:
            self.exec()
        name = names[0]
        if name in self.imports:
            if len(names) != 1:
                return None
            else:
                return self.imports[name]
        elif name in self.variables:
            target = self.variables[name]
            if isinstance(target, (ClsEnv, FuncEnv)):
                if len(names) > 1:
                    return target.dfs_locate(names[1:])
                else:
                    return target
            else:
                if len(names) != 1:
                    return None
                else:
                    return target
        else:
            return None

    def get_cur_command(self) -> str:
        return self.parent_env.get_cur_command()

    # 获取当前环境在Python包中的完整路径
    def get_path(self) -> str:
        return f"{self.parent_env.get_path()}.{self.node.name}"

    def get_root_env(self):
        return self.parent_env.get_root_env()

    # 根据group,name获取真正的执行入口entry
    def get_entry(self, group, name):
        root_env = self.get_root_env()
        site_package = root_env.belongs.get_root_pyunit()
        return site_package.get_entry(group, name)

    def get_import_codes(self):
        import_codes = []
        import_codes.extend(self.parent_env.get_import_codes())
        import_codes.extend(self.import_codes)
        return import_codes

    def get_cls_env(self):
        return None

    # 在环境中查找具体的对象和变量，如果找不到，就在父环境中去找
    def find(self, name: str):
        if self.scanned == Environment.UNSCAN:
            self.exec()
        ok = False
        if name in self.variables:
            name = self.variables[name]
            ok = True
        elif name in self.imports:
            name = self.imports[name]
            ok = True
        elif self.parent_env:
            ok, name = self.parent_env.find(name)
        return ok, name


class PyUnit(metaclass=ABCMeta):
    def __init__(self, path: str, name: str, parent_node) -> None:
        self.name = name
        self.path = path
        self.parent_node: PyUnit = parent_node

    def get_path(self) -> str:
        if self.parent_node:
            path = self.parent_node.get_path()
            if path:
                return f"{path}.{self.name}"
        return self.name

    def get_root_pyunit(self):
        if self.parent_node:
            return self.parent_node.get_root_pyunit()
        return self

    def get_cur_command(self) -> str:
        return self.parent_node.get_cur_command()


class Package(PyUnit):
    """
    扫描python代码包的组织结构并以树的形式存储
    """

    def __init__(self, path: str, name: str, parent_node) -> None:
        super().__init__(path, name, parent_node)
        self.subunits = {}
        self.init: Module = None
        for f in os.listdir(path):
            if f == '__pycache__':
                continue
            filepath = os.path.join(path, f)
            if os.path.isfile(filepath) and (
                    FileType.filetype(filepath) == FileType.PYTHON or filepath.endswith('.py')):
                if f.endswith('.py'):
                    f = f[:-3]
                if f == '__init__':
                    self.init = Module(filepath, f, self)
                else:
                    self.subunits[f] = Module(filepath, f, self)
            elif os.path.isdir(filepath):
                self.subunits[f] = Package(filepath, f, self)

    def dfs_locate(self, names: list[str]):
        if self.init:
            ans = self.init.dfs_locate(names)
            if ans:
                return ans
        name = names[0]
        for subunit_name, subunit in self.subunits.items():
            if subunit_name == name:
                if len(names) > 1:
                    return subunit.dfs_locate(names[1:])
                else:
                    return subunit
        return None

    def get_boot_mod(self):
        for subunit in self.subunits.values():
            val = subunit.get_boot_mod()
            if val:
                return val
        return None


class SitePackage(PyUnit):
    """是源码中的python一级包的父目录的抽象，还包括了可执行的python命令在内"""

    def __init__(self, path: str) -> None:
        self.entry_points = {}
        self.packages = {}
        self.commands = []
        super().__init__(path, '', None)
        for f in os.listdir(path):
            filepath = os.path.join(path, f)
            if os.path.isdir(filepath):
                if filepath.endswith('egg-info'):
                    entry_path = os.path.join(filepath, 'entry_points.txt')
                    if not os.path.isfile(entry_path):
                        continue
                    group = None
                    with open(entry_path, mode='r') as entry_points:
                        for line in entry_points.readlines():
                            line = line.strip()
                            if line.startswith('[') and line.endswith(']'):
                                group = line[1:-1]
                                entry = {}
                                self.entry_points[group] = entry
                            elif line.find('=') != -1:
                                name, val = line.split('=')
                                entry[name.strip()] = val.strip().replace(':', '.')
                else:
                    self.packages[f] = Package(filepath, f, self)

    def dfs_locate(self, names: list[str]):
        name = names[0]
        for package_name, package in self.packages.items():
            if package_name == name:
                if len(names) > 1:
                    return package.dfs_locate(names[1:])
                else:
                    return package
        return None

    def get_entry(self, group, name):
        if self.entry_points and group in self.entry_points.keys():
            entry_points = self.entry_points[group]
            if name in entry_points.keys():
                return entry_points[name]
        return None

    def get_cur_command(self):
        return self.get_boot_mod()

    def get_boot_mod(self):
        """
        确定启动模块
        """
        for package in self.packages.values():
            val = package.get_boot_mod()
            if val:
                return val
        for commands in self.commands:
            val = commands.get_boot_mod()
            if val:
                return val
        return '__file__'

    def extend_commands(self, commands):
        self.commands.extend(commands)


class Module(PyUnit):
    def __init__(self, path: str, name: str, parent_node) -> None:
        super().__init__(path, name, parent_node)
        srcfile = open(self.path, mode='r')
        source = ''.join(srcfile.readlines())
        node = ast.parse(source, mode='exec')
        self.env = ModEnv(node, self)
        self.boot = False

    def exec(self):
        self.env.exec()

    def dfs_locate(self, names: list[str]):
        return self.env.dfs_locate(names)

    def booted(self) -> bool:
        return self.boot

    def get_cur_command(self) -> str:
        if self.boot:
            return self.path[self.path.rfind('/') + 1:]
        if self.parent_node:
            return self.parent_node.get_cur_command()
        return None

    def get_boot_mod(self) -> str:
        if self.boot:
            return self.path[self.path.rfind('/') + 1:]
        return None


class ModEnv(Environment):
    def __init__(self, node: ast.Module, mod: Module) -> None:
        super().__init__(node, None)
        self.belongs: Module = mod

    def get_path(self) -> str:
        return self.belongs.get_path()

    def get_root_env(self):
        return self

    def get_cur_command(self):
        return self.belongs.get_cur_command()

    def get_import_codes(self):
        return self.import_codes

    def exec(self, args: list = None, keywords: dict = None):
        super().exec(args, keywords)


class ClsEnv(Environment):
    def __init__(self, node: ast.ClassDef, parent_env) -> None:
        super().__init__(node, parent_env)

    def find(self, name: str):
        """类环境下的find需要在父环境中寻找之前先在基类中寻找
        对于基类中存在argparse,optparse的参数解析类时也要判断之前已经处理过的自定义的解析对象是否满足条件
        """
        if self.scanned == Environment.UNSCAN:
            self.exec()
        ok, ret = False, None
        if name in self.variables:
            ret = self.variables[name]
            ok = True
        elif name in self.imports:
            ret = self.imports[name]
            ok = True
        else:
            self.get_cls_env()
            if self.bases != Ellipsis and self.bases:
                for base in self.bases:
                    if isinstance(base, ClsEnv):
                        ok, ret = base.find(name)
                        if ok:
                            break
                    elif isinstance(base, ArgParser) or isinstance(base, OptParser):
                        if hasattr(base, name):
                            ret = getattr(base, name)
                            ok = True
                            break
            if not ok and self.parent_env:
                ok, ret = self.parent_env.find(name)
        return (ok, ret)

    # 获取类环境时处理一下基类bases
    def get_cls_env(self) -> Environment:
        if not hasattr(self, 'bases'):
            setattr(self, 'bases', ...)
            self.bases = [self.exec_driver(self, base)
                          for base in self.node.bases]
            for i in range(len(self.bases)):
                try:
                    if callable(self.bases[i]):
                        self.bases[i] = self.bases[i]()
                except:
                    log.warning("因模拟执行python代码时的输入参数未知以及所需系统环境的缺失导致的异常", log_file)
        return self

    def get_parent_cls(self):
        if not self.bases and self.node.bases:
            self.bases = [self.exec_driver(self, base) for base in self.node.bases]
        return self.bases

    def __str__(self) -> str:
        return f"Customized Class: {self.get_path()}"


class FuncEnv(Environment):
    """ 函数/方法的局部环境
    Attributes
        stack: 模拟了一个函数调用堆栈,对于多个函数之间的循环调用将直接退出,防止死循环
    """
    stack = []

    def __init__(self, node: ast.FunctionDef, parent_env) -> None:
        super().__init__(node, parent_env)

    def exec(self, args: list = [], keywords: dict = {}):
        """
        需要将函数调用时传递的参数和函数定义时可接收的参数进行对应,将参数放到variables中,然后调用父类Environment中的方法进行执行
        """
        if self.scanned == Environment.UNSCAN:
            self.scanned = Environment.SCANNING
        if self in FuncEnv.stack:
            return
        FuncEnv.stack.append(self)
        arguments = self.node.args
        start = 0
        if len(arguments.args) > 0 and arguments.args[0].arg in ('self', 'cls'):
            start = 1
        j = 0
        for i in range(start, len(arguments.args)):
            arg = arguments.args[i].arg
            if arg in keywords:
                self.variables[arg] = keywords[arg]
                keywords.pop(arg)
            elif j < len(args):
                self.variables[arg] = args[j]
                j += 1
            else:
                k = i - len(arguments.args) + len(arguments.defaults)
                if k >= 0:
                    self.variables[arg] = self.exec_driver(self, arguments.defaults[k])
                else:
                    self.variables[arg] = None
        if arguments.vararg:
            arg = arguments.vararg.arg
            self.variables[arg] = args[j:] if j < len(args) else None
        for i in range(len(arguments.kwonlyargs)):
            arg = arguments.kwonlyargs[i].arg
            if arg in keywords:
                self.variables[arg] = keywords[arg]
                keywords.pop(arg)
            elif arguments.kw_defaults[i]:
                self.variables[arg] = self.exec_driver(
                    self, arguments.kw_defaults[i])
            else:
                self.variables[arg] = None
        if arguments.kwarg:
            arg = arguments.kwarg.arg
            self.variables[arg] = keywords
        ret = super().exec(args, keywords)
        FuncEnv.stack.pop()
        return ret

    def get_cls_env(self) -> Environment:
        return self.parent_env.get_cls_env()

    def __str__(self) -> str:
        return f"Customized Function: {self.get_path()}"


class PyArgExtractor:
    def __init__(self, commands: list[str], basedir: str, logfile: str):
        """
        定位Python源码位置,初始化sitepackage对象,并将命令command对象传入到sitepackage中。但并非所有源码包都有存放Python包的sitepackage
        """
        global log_file
        log_file = logfile
        self.site_package = None
        status, output = subprocess.getstatusoutput(f"find {basedir} -type d -name site-packages")
        if status == 0 and output:
            for line in output.split('\n'):
                self.site_package = SitePackage(line)
                break
        self.commands = [Module(command, command[command.rfind('/') + 1:], self.site_package) for command in commands]
        if self.site_package:
            self.site_package.extend_commands(self.commands)
        self.basedir = basedir
        self.args = {command.name: [] for command in self.commands}
        self.usages = {command.name: '' for command in self.commands}
        self.nums = 0

    def get_cmds_args(self):
        """获取命令的参数信息
        Returns:
            content:    usage帮助信息
            commands:   格式化的参数
            value_map:  可用的值的map,格式:'命令,需要赋值的参数':值的列表
            help_map:   类型信息的map,格式:'命令,需要赋值的参数':类型
        """
        content, commands, value_map, help_map = '', [], {}, {}
        for command in self.commands:
            UniArgParser.CurCommand = command
            command.boot = True
            command.exec()
            command.boot = False
            if UniArgParser.finalParser:
                num = UniArgParser.finalParser.get_num()
                content = f"COMMAND: {command.name}\n{num}\n{UniArgParser.finalParser}"
                self.nums += num
                commands, value_map, help_map = UniArgParser.finalParser.getCmds_Vals()
                UniArgParser.finalParser = None
        return content, commands, value_map, help_map