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

import argparse
import optparse
from typing import Any, Iterable, Sequence, Union, List, Tuple, Dict
import copy
import random
from copy import deepcopy

# 常量的定义
UNUSED = 0
USED = 1

# 在一次递归的搜索参数时判断是否需要继续的全局变量
MORE = False

# 参数的action是以下这些值的时候表明该参数不需要赋值
NOVALARGS = ['store_true', 'store_false', 'store_const',
             'version', 'append_const', 'count', 'callback', 'help']

# 用以简化一个参数解析对象里的属性，是默认值Ellipsis{...}时表明没有传递值过来，那么就可以从结果中去掉
def simplify(pair: dict):
    for key, val in list(pair.items()):
        if val == Ellipsis:
            pair.pop(key)
    return pair


class SubParserManager():
    def __init__(self, title=..., description=..., prog=..., parser_class=..., action=...,
                 option_string=..., dest=..., required=..., help=..., metavar=...) -> None:
        self.title = title
        self.description = description
        self.prog = prog
        self.parser_class = parser_class
        self.action = action
        self.option_string = option_string
        self.dest = dest
        self.required = required
        self.help = help if help != ArgParser.SUPPRESS else ArgParser.DEFAULTHELP
        self.metavar = metavar

        self.subparsers: List[SubParser] = []

    def add_parser(self,
                   command: str,
                   help: str = ...,
                   aliases: Sequence[str] = ...,
                   prog=...,
                   usage=...,
                   description=...,
                   epilog=...,
                   parents=...,
                   formatter_class=...,
                   prefix_chars=...,
                   fromfile_prefix_chars=...,
                   argument_default=...,
                   conflict_handler=...,
                   add_help=...,
                   allow_abbrev=...,
                   exit_on_error=...):
        subparser = SubParser(command, help=help, aliases=aliases, prog=prog, usage=usage, description=description,
                              epilog=epilog, parents=parents, formatter_class=formatter_class,
                              prefix_chars=prefix_chars,
                              fromfile_prefix_chars=fromfile_prefix_chars, argument_default=argument_default,
                              conflict_handler=conflict_handler, add_help=add_help, allow_abbrev=allow_abbrev,
                              exit_on_error=exit_on_error)
        self.subparsers.append(subparser)
        return subparser

    def add_helpdfs(self):
        for subparser in self.subparsers:
            subparser.add_helpdfs()

    def display(self, prefix=''):
        s = f'{prefix}Subcommands: '
        params = simplify({
            'title': self.title,
            'description': self.description,
            'prog': self.prog,
            'parser_class': self.parser_class,
            'action': self.action,
            'option_string': self.option_string,
            'dest': self.dest,
            'required': self.required,
            'help': self.help,
            'metavar': self.metavar
        })
        if params:
            s += str(params)
        prefix += '\t'
        for subparser in self.subparsers:
            s += f"\n{subparser.display(prefix)}"
        return s

    def get_num(self) -> int:
        return sum(subparser.get_num() for subparser in self.subparsers)

    def union(self, manager):
        if manager:
            self.subparsers.extend(manager.subparsers)

    def add_val_help(self, value_map, help_map):
        for subparser in self.subparsers:
            subparser.add_val_help(value_map, help_map)

    def yield_cmd(self, cmd):
        more = False
        n = len(cmd)
        for subparser in self.subparsers:
            more = subparser.yield_cmd(cmd)
            if more:
                break
            else:
                while len(cmd) > n:
                    cmd.pop()
        return more


class Argument():
    def __init__(self, *name_or_flags: str, action=..., nargs=..., const=...,
                 default: Any = ..., type=..., choices=..., required: bool = ...,
                 help=..., metavar: Union[str, tuple[str, ...]] = ...,
                 dest: str = ..., version: str = ..., **kwargs: Any) -> None:
        self.args = name_or_flags
        self.action = action
        self.nargs = nargs
        self.const = const
        self.default = default
        self.type = type
        self.choices = choices
        self.required = required
        # 默认参数的处理
        self.help = help if help != ArgParser.SUPPRESS else ArgParser.DEFAULTHELP
        self.metavar = metavar
        self.dest = dest
        self.version = version
        self.used = UNUSED

    def __str__(self) -> str:
        args = list(filter(lambda x: x is not None, self.args))
        if not args:
            return ''
        s = ','.join(self.args)
        keywords = simplify({
            'action': self.action,
            'nargs': self.nargs,
            'const': self.const,
            'default': self.default,
            'type': self.type,
            'choices': self.choices,
            'required': self.required,
            'help': self.help,
            'metavar': self.metavar,
            'dest': self.dest,
            'version': self.version
        })
        if keywords:
            s = f"{s}\n{keywords}"
        return s

    def get_num(self) -> int:
        return 1

    def add_val_help(self, value_map, help_map):
        args = list(filter(lambda x: x is not None, self.args))
        if not args:
            return
        args.sort(key=lambda x: len(x))
        label = args[-1].lstrip('-').replace('-', '_').upper()
        if self.metavar and self.metavar != Ellipsis:
            label = self.metavar.upper()
        elif self.dest and self.dest != Ellipsis:
            label = self.dest
        key = f"{UniArgParser.get_cmd_name()},{label}"
        if self.choices is not None and self.choices != Ellipsis:
            value_map[key] = self.choices
        else:
            value_map[key] = []
        if self.default is not None and self.default != Ellipsis:
            value_map[key].append(self.default)
        if self.const is not None and self.const != Ellipsis:
            value_map[key] = self.const
        if not value_map[key]:
            value_map.pop(key)
        if self.type and self.type != Ellipsis:
            help_map[key] = self.type

    def yield_cmd(self, cmd):
        global MORE
        args = list(filter(lambda x: x is not None, self.args))
        if not args:
            return False
        required = (self.required == True or (not args[0].startswith(
            '-') and self.nargs != '?')) and self.default == Ellipsis
        if required or (MORE and self.used == UNUSED):
            args.sort(key=lambda x: len(x))
            label = args[-1].lstrip('-').replace('-', '_').upper()
            if self.metavar and self.metavar != Ellipsis:
                label = self.metavar.upper()
            elif self.dest and self.dest != Ellipsis:
                label = self.dest.upper()
            if self.action in NOVALARGS or '-h' in args or '--help' in args:
                cmd.append(args[-1])
            elif not args[0].startswith('-'):
                cmd.append(label)
            else:
                cmd.extend([args[-1], label])
            self.used = USED
            if not required:
                return True
        return False


# 分组参数，和普通参数没有区别，只是提供一个整体的抽象表述，某些参数聚集在一个组中有个统一的title和description，可能表示这些参数有某些联系或者是完成一个功能的相关参数
class GroupArg(Argument):
    def __init__(self, title=..., description=..., *name_or_flags: str, **kwargs: Any) -> None:
        super().__init__(*name_or_flags, **kwargs)
        self.arguments = []
        self.title = title
        self.description = description

    def add_argument(self,
                     *name_or_flags: str,
                     action=...,
                     nargs=...,
                     const=...,
                     default: Any = ...,
                     type=...,
                     choices=...,
                     required: bool = ...,
                     help=...,
                     metavar: Union[str, tuple[str, ...]] = ...,
                     dest: str = ...,
                     version: str = ...,
                     **kwargs: Any):
        self.arguments.append(Argument(*name_or_flags, action=action, nargs=nargs, const=const,
                                       default=default, type=type, choices=choices, required=required,
                                       help=help, metavar=metavar, dest=dest, version=version, **kwargs))

    def get_num(self) -> int:
        return len(self.arguments)

    def __str__(self) -> str:
        info = {}
        s = f'arg group: {len(self.arguments)}'
        if self.title and self.title != Ellipsis:
            info['title'] = self.title
        if self.description and self.description != Ellipsis:
            info['description'] = self.description
        if info:
            s += f" {info}"
        for arg in self.arguments:
            s += f"\n{arg}"
        return s

    def add_val_help(self, value_map, help_map):
        for argument in self.arguments:
            argument.add_val_help(value_map, help_map)

    def yield_cmd(self, cmd):
        global MORE
        more = False
        for argument in self.arguments:
            more = more or argument.yield_cmd(cmd)
            if more:
                MORE = False
        return more


# 互斥组参数，在分组参数的基础上多了一个组内参数不能同时被使用的限制
class ExclusiveGroupArg(GroupArg):
    def __init__(self, required=...) -> None:
        super().__init__()
        self.required = required
        self.arguments = []

    def __str__(self) -> str:
        if len(self.arguments) == 0:
            return ''
        s = f'exclusive arg group: {len(self.arguments)}'
        for arg in self.arguments:
            s += f"\n{arg}"
        return s

    def yield_cmd(self, cmd):
        global MORE
        more = False
        for argument in self.arguments:
            more = argument.yield_cmd(cmd)
            if more:
                return True
        if self.required == True:
            index = random.randint(0, len(self.arguments) - 1)
            self.arguments[index].used = UNUSED
            self.arguments[index].yield_cmd(cmd)
            return False
        return more


# 和argparse的ArgumentParser对应的类
class ArgParser:
    SUPPRESS = argparse.SUPPRESS
    DEFAULTHELP = 'show this help message and exit'

    def __init__(self,
                 prog=...,
                 usage=...,
                 description=...,
                 epilog=...,
                 parents=...,
                 formatter_class=...,
                 prefix_chars=...,
                 fromfile_prefix_chars=...,
                 argument_default=...,
                 conflict_handler=...,
                 add_help=...,
                 allow_abbrev=...,
                 exit_on_error=...) -> None:
        self.arguments = []
        self.subparserManager = None
        self.ArgumentParser(prog, usage, description, epilog, parents, formatter_class, prefix_chars,
                            fromfile_prefix_chars, argument_default, conflict_handler, add_help, allow_abbrev,
                            exit_on_error)

    def __str__(self) -> str:
        params = simplify({
            'prog': self.prog,
            'usage': self.usage,
            'description': self.description,
            'epilog': self.epilog,
            'parents': self.parents,
            'formatter_class': self.formatter_class,
            'prefix_chars': self.prefix_chars,
            'fromfile_prefix_chars': self.fromfile_prefix_chars,
            'argument_default': self.argument_default,
            'conflict_handler': self.conflict_handler,
            'add_help': self.add_help,
            'allow_abbrev': self.allow_abbrev,
            'exit_on_error': self.exit_on_error
        })
        s = f"{params}" if params else ''
        for arg in self.arguments:
            if s:
                s += f"\n{arg}"
            else:
                s = f"{arg}"
        if self.subparserManager:
            if s:
                s += f"\n{self.subparserManager.display()}"
            else:
                s = self.subparserManager.display()
        return s

    def get_num(self) -> int:
        numInArgs = sum(arg.get_num() for arg in self.arguments)
        numInSubparser = self.subparserManager.get_num() if self.subparserManager else 0
        return numInArgs + numInSubparser

    def ArgumentParser(self, prog=..., usage=..., description=..., epilog=..., parents=...,
                       formatter_class=..., prefix_chars=..., fromfile_prefix_chars=..., argument_default=...,
                       conflict_handler=..., add_help=..., allow_abbrev=..., exit_on_error=...):
        if not prog:
            prog = UniArgParser.get_cmd_name()
        self.prog = prog
        self.usage = usage
        self.description = description
        self.epilog = epilog
        self.parents = ...
        self.formatter_class = formatter_class
        self.prefix_chars = prefix_chars
        self.fromfile_prefix_chars = fromfile_prefix_chars
        self.argument_default = argument_default
        self.conflict_handler = conflict_handler
        self.add_help = add_help
        self.allow_abbrev = allow_abbrev
        self.exit_on_error = exit_on_error
        if parents != Ellipsis and parents:
            for parent in parents:
                if isinstance(parent, (ArgParser, SubParser)):
                    self.arguments.extend(deepcopy(parent.arguments))
                    if self.subparserManager:
                        self.subparserManager.union(
                            deepcopy(parent.subparserManager))
                    else:
                        self.subparserManager = deepcopy(
                            parent.subparserManager)
                elif isinstance(parent, (GroupArg, ExclusiveGroupArg)):
                    self.arguments.append(deepcopy(parent))
                else:
                    raise RuntimeError("unknown parent type")
        return self

    def add_argument(self, *name_or_flags: str, action=..., nargs=..., const=..., default: Any = ..., type=...,
                     choices=..., required: bool = ..., help=..., metavar: Union[str, tuple[str, ...]] = ...,
                     dest: str = ..., version: str = ..., **kwargs: Any):
        self.arguments.append(Argument(*name_or_flags, action=action, nargs=nargs, const=const,
                                       default=default, type=type, choices=choices, required=required,
                                       help=help, metavar=metavar, dest=dest, version=version, **kwargs))

    def add_subparsers(self, title=..., description=..., prog=..., parser_class=..., action=...,
                       option_string=..., dest=..., required=..., help=..., metavar=...):
        self.subparserManager = SubParserManager(
            title, description, prog, parser_class, action, option_string, dest, required, help, metavar)
        return self.subparserManager

    def add_mutually_exclusive_group(self, required=...):
        arg = ExclusiveGroupArg(required)
        self.arguments.append(arg)
        return arg

    def add_argument_group(self, title=..., description=...):
        arg = GroupArg(title, description)
        self.arguments.append(arg)
        return arg

    def set_defaults(self, **kwargs):
        self.argument_default = kwargs

    # 递归的判断命令以及子命令是否有-h这样的帮助选项
    def add_helpdfs(self):
        if self.add_help == Ellipsis or self.add_help:
            self.add_argument('-h', '--help', help=ArgParser.DEFAULTHELP)
        if self.subparserManager:
            self.subparserManager.add_helpdfs()

    def parse_args(self, args=..., values=...):
        self.add_helpdfs()
        UniArgParser.finalParser = copy.deepcopy(self)

    def parse_intermixed_args(self, args=..., values=...):
        self.parse_args(args, values)

    def parse_known_intermixed_args(self, args=..., values=...):
        self.parse_args(args, values)

    def parse_known_args(self, args=..., values=...):
        self.parse_args(args, values)

    def add_val_help(self, value_map: Dict, help_map: Dict):
        for argument in self.arguments:
            argument.add_val_help(value_map, help_map)
        if self.subparserManager:
            self.subparserManager.add_val_help(value_map, help_map)

    def yield_cmd(self, cmd):
        """
        :return: 返回是否取到了更多的非必选且之前没有选过的参数
        """
        global MORE
        more = False
        for argument in self.arguments:
            more = more or argument.yield_cmd(cmd)
            if more:
                MORE = False
        if more:
            return more
        if self.subparserManager:
            more = self.subparserManager.yield_cmd(cmd)
        return more

    def getCmds_Vals(self) -> Tuple[List, Dict, Dict]:
        global MORE
        commands, value_map, help_map = [], {}, {}
        """
        每次循环生成一个可行的命令格式, 在循环开始的时候设置全局变量MORE为True,然后递归的进行处理
        递归的每一层对应着命令的层级,每次先处理当前层的arguments,直到所有非必选的arguments都被选过之后在进入子命令去处理
        """
        while True:
            MORE = True
            cmd = [UniArgParser.get_cmd_name()]
            if self.yield_cmd(cmd):
                commands.append(cmd)
            else:
                break
        # 递归的获取参数可用的值的信息以及类型信息
        self.add_val_help(value_map, help_map)
        return commands, value_map, help_map


class SubParser(ArgParser):
    def __init__(self,
                 name: str,
                 help: str = ...,
                 aliases: Sequence[str] = ...,
                 prog=...,
                 usage=...,
                 description=...,
                 epilog=...,
                 parents=...,
                 formatter_class=...,
                 prefix_chars=...,
                 fromfile_prefix_chars=...,
                 argument_default=...,
                 conflict_handler=...,
                 add_help=...,
                 allow_abbrev=...,
                 exit_on_error=...) -> None:
        super().__init__(prog, usage, description, epilog, parents, formatter_class, prefix_chars,
                         fromfile_prefix_chars, argument_default, conflict_handler, add_help, allow_abbrev,
                         exit_on_error)
        self.name = name
        self.help = help if help != ArgParser.SUPPRESS else ArgParser.DEFAULTHELP
        self.aliases = aliases
        self.cur = False

    def add_helpdfs(self):
        if self.add_help == Ellipsis or self.add_help:
            self.add_argument('-h', '--help', help=ArgParser.DEFAULTHELP)

    def display(self, prefix=''):
        s = f"{prefix}Subcommand: {self.name}\t"
        params = simplify({
            'help': self.help,
            'alias': self.aliases,
            'prog': self.prog,
            'usage': self.usage,
            'description': self.description,
            'epilog': self.epilog,
            'parents': self.parents,
            'formatter_class': self.formatter_class,
            'prefix_chars': self.prefix_chars,
            'fromfile_prefix_chars': self.fromfile_prefix_chars,
            'argument_default': self.argument_default,
            'conflict_handler': self.conflict_handler,
            'add_help': self.add_help,
            'allow_abbrev': self.allow_abbrev,
            'exit_on_error': self.exit_on_error
        })
        if params:
            s += f"{params}"
        for arg in self.arguments:
            s += '\n'
            s += "\n".join(f"{prefix}{line}" for line in str(arg).split('\n') if line)
        if self.subparserManager:
            s += f"\n{self.subparserManager.display(prefix)}"
        return s

    def yield_cmd(self, cmd):
        global MORE
        more = False
        name = f"^{self.name}"
        n = len(cmd)
        for argument in self.arguments:
            more = argument.yield_cmd(cmd) or more
            if more:
                if n != -1:
                    cmd.insert(n, name)
                    n = -1
                MORE = False
        if more:
            return more
        if isinstance(self.argument_default, dict) and 'func' in self.argument_default and not self.cur and len(
                cmd) == n:
            self.cur = True
            cmd.insert(n, name)
            MORE = False
            return True
        if self.subparserManager:
            cmd.insert(n, name)
            more = self.subparserManager.yield_cmd(cmd)
        return more


# 和optparse的OptionParse对象对应，这里采用了继承的方式，在此基础上添加自定义的对参数的处理逻辑
class Option(optparse.Option):
    ATTRS = ['action',
             'type',
             'dest',
             'default',
             'nargs',
             'const',
             'choices',
             'callback',
             'callback_args',
             'callback_kwargs',
             'help',
             'metavar']

    def __init__(self, *opts, **attrs: Any) -> None:
        self.attrs = {key: val for key,
                                   val in attrs.items() if key in self.ATTRS}
        super().__init__(*opts, **attrs)

    def __str__(self) -> str:
        opts = []
        opts.extend(self._short_opts)
        opts.extend(self._long_opts)
        s = ','.join(opts)
        return f"{s}\n{self.attrs}" if self.attrs else s


class OptParser(optparse.OptionParser):
    SUPPRESS_HELP = optparse.SUPPRESS_HELP
    SUPPRESS_USAGE = optparse.SUPPRESS_USAGE

    # optionparser中有帮助的信息的标签
    ATTRS = [
        'usage',
        'version',
        'description',
        'prog',
        'epilog']

    def __init__(self,
                 usage: str = None,
                 option_list: Iterable[optparse.Option] = None,
                 option_class: type[optparse.Option] = Option,
                 version: str = None,
                 conflict_handler: str = "error",
                 description: str = None,
                 formatter: optparse.HelpFormatter = None,
                 add_help_option: bool = True,
                 prog: str = None,
                 epilog: str = None) -> None:
        if not prog:
            prog = UniArgParser.get_cmd_name()
        super().__init__(usage=usage, option_list=option_list, option_class=option_class, version=version,
                         conflict_handler=conflict_handler, description=description,
                         formatter=formatter, add_help_option=add_help_option, prog=prog, epilog=epilog)

    def OptionParser(self, *args, **kwargs):
        if args and len(args) == 1 and ('usage' not in kwargs or not kwargs['usage']):
            kwargs['usage'] = args[0]
        super().__init__(**kwargs)
        return self

    def add_option(self, *args, **kwargs):
        opt = Option(*args, **kwargs)
        super().add_option(opt)

    def OptionGroup(self, parser, title, description=None):
        return OptGroup(parser, title, description)

    def parse_args(self, args=None, vals=None):
        if self.usage:
            self.usage = self.usage.replace(
                '%prog', UniArgParser.get_cmd_name())
        UniArgParser.finalParser = copy.deepcopy(self)
        super().parse_args()

    def get_num(self) -> int:
        num = len(self.option_list)
        for group in self.option_groups:
            if isinstance(group, OptGroup):
                num += group.get_num()
            else:
                num += len(group.option_list)
        return num

    def __str__(self) -> str:
        attrs = {attr: getattr(self, attr)
                 for attr in self.ATTRS if getattr(self, attr)}
        s = f"{attrs}" if attrs else ''
        for option in self.option_list:
            if s:
                s += f"\n{option}"
            else:
                s = str(option)
        for group in self.option_groups:
            if s:
                s += f"\n\n{group}"
            else:
                s = str(group)
        return s

    # optparse包的option都是可选项，直接遍历
    def getCmds_Vals(self) -> Tuple[List, Dict, Dict]:
        if not UniArgParser.CurCommand:
            return None
        name = UniArgParser.get_cmd_name()
        cmds, vals, typeVals, options = [], {}, {}, []
        options.extend(self.option_list)
        for groups in self.option_groups:
            options.extend(groups.option_list)
        for option in options:
            opts = []
            opts.extend(option._short_opts)
            opts.extend(option._long_opts)
            opts.sort(key=lambda x: len(x))
            label = opts[-1].lstrip('-').replace('-', '_').upper()
            if 'metavar' in option.attrs:
                label = option.attrs['metavar'].upper()
            elif 'dest' in option.attrs:
                label = option.attrs['dest'].upper()
            if ('action' in option.attrs and option.attrs['action'] in NOVALARGS) or '-h' in opts or '--help' in opts:
                cmds.append([f"{name}", opts[0]])
            else:
                cmds.append([f"{name}", opts[0], label])
            key = f"{name},{label}"
            if 'choices' in option.attrs:
                vals[key] = option.attrs['choices'] if option.attrs['choices'] else []
            else:
                vals[key] = []
            if 'default' in option.attrs and option.attrs['default'] is not None:
                vals[key].append(option.attrs['default'])
            # if 'const' in option.attrs and option.attrs['const'] is not None:
            #     vals[key] = option.attrs['const']
            if not vals[key]:
                vals.pop(key)
            if 'type' in option.attrs:
                typeVals[key] = option.attrs['type']
        return (cmds, vals, typeVals)


class OptGroup(optparse.OptionGroup):
    def __init__(self, parser, title, description=None) -> None:
        super().__init__(parser, title, description=description)

    def add_option(self, *args, **kwargs):
        opt = Option(*args, **kwargs)
        super().add_option(opt)

    def get_num(self) -> int:
        return len(self.option_list)

    def __str__(self) -> str:
        params = {
            'title': self.title
        }
        if self.description:
            params['description'] = self.description
        s = f"Group: {params}"
        for option in self.option_list:
            s += f"\n{option}"
        return s


class UniArgParser:
    PARSERS = ('argparse.ArgumentParser',
               'optparse.OptionParser', 'argparse', 'optparse')

    finalParser = None
    CurCommand = None

    @classmethod
    def build(cls, parser: str, args=[], keywords={}):
        """
        工厂方法,根据传入的parser的不同创建不同的参数处理对象
        """
        if parser in cls.PARSERS:
            return ArgParser(**keywords) if parser.startswith('argparse') else OptParser(**keywords)
        return None

    @classmethod
    def get_cmd_name(cls):
        """
        获取当前处理的命令的名字
        """
        if cls.CurCommand:
            curCmd = cls.CurCommand
            return curCmd.path[curCmd.path.rfind('/') + 1:]
        return "%prog"