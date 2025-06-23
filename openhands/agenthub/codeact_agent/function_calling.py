"""
OpenHands CodeAct Agent 函数调用实现模块

技术栈:
- Python 3.12+ (核心语言)
- LiteLLM - 多LLM提供商统一接口
- JSON - 函数调用参数解析
- Function Calling - LLM原生函数调用机制
- 工具系统 - 各种专门化工具的集成

架构说明:
这个模块实现了CodeActAgent的函数调用功能，类似于CodeActResponseParser的功能。
它负责将LLM的函数调用响应转换为具体的Action对象，实现了从LLM输出到
系统操作的桥梁。

核心功能:
1. 函数调用解析 - 解析LLM的函数调用响应
2. Action转换 - 将函数调用转换为Action对象
3. 参数验证 - 验证函数调用参数的有效性
4. 错误处理 - 处理函数调用中的各种错误
5. 思考合并 - 将思考内容与操作结合
6. 工具映射 - 将函数名映射到具体工具

设计模式:
- 工厂模式: 根据函数名创建对应的Action
- 策略模式: 不同工具的不同处理策略
- 适配器模式: LLM响应到Action的适配
- 装饰器模式: 为Action添加思考内容
"""

import json

# LiteLLM响应类型
from litellm import (
    ModelResponse,
)

# CodeAct工具集导入
from openhands.agenthub.codeact_agent.tools import (
    BrowserTool,  # 浏览器工具
    FinishTool,  # 完成工具
    IPythonTool,  # Python执行工具
    LLMBasedFileEditTool,  # LLM文件编辑工具
    ThinkTool,  # 思考工具
    create_cmd_run_tool,  # 命令执行工具创建器
    create_str_replace_editor_tool,  # 字符串替换编辑工具创建器
)

# 异常处理
from openhands.core.exceptions import (
    FunctionCallNotExistsError,  # 函数调用不存在错误
    FunctionCallValidationError,  # 函数调用验证错误
)
from openhands.core.logger import openhands_logger as logger

# Action类型导入
from openhands.events.action import (
    Action,  # 基础Action类
    AgentDelegateAction,  # Agent委托Action
    AgentFinishAction,  # Agent完成Action
    AgentThinkAction,  # Agent思考Action
    BrowseInteractiveAction,  # 浏览器交互Action
    CmdRunAction,  # 命令执行Action
    FileEditAction,  # 文件编辑Action
    FileReadAction,  # 文件读取Action
    IPythonRunCellAction,  # IPython执行Action
    MessageAction,  # 消息Action
)
from openhands.events.action.mcp import MCPAction  # MCP Action
from openhands.events.event import FileEditSource, FileReadSource  # 文件操作源
from openhands.events.tool import ToolCallMetadata  # 工具调用元数据


def combine_thought(action: Action, thought: str) -> Action:
    """
    合并思考内容到Action中

    将LLM的思考内容与具体的操作Action结合，提供更丰富的上下文信息。
    如果Action已有思考内容，则将新的思考内容追加到前面。

    Args:
        action: 要添加思考内容的Action对象
        thought: 思考内容字符串

    Returns:
        Action: 包含思考内容的Action对象
    """
    # 检查Action对象是否有thought属性，如果没有则直接返回原始Action
    # 技术栈: Python对象属性检查 - hasattr函数用于动态检查对象属性
    if not hasattr(action, 'thought'):
        return action

    # 如果提供了新的思考内容且Action已有思考内容，则合并两者
    # 技术栈: Python字符串操作 - 使用f-string进行字符串格式化和拼接
    if thought and action.thought:
        action.thought = f'{thought}\n{action.thought}'
    # 如果只有新的思考内容，则直接赋值
    elif thought:
        action.thought = thought

    # 返回更新后的Action对象
    # 技术栈: 函数式编程 - 保持函数的纯粹性，不修改原始对象
    return action


def response_to_actions(
    response: ModelResponse, mcp_tool_names: list[str] | None = None
) -> list[Action]:
    """
    将LLM的响应转换为OpenHands的Action对象列表

    技术栈:
    - Python类型注解 - 使用类型提示增强代码可读性和IDE支持
    - 函数式编程 - 将输入转换为新的输出，不修改原始数据
    - JSON解析 - 处理LLM函数调用的参数
    - 错误处理 - 使用异常处理验证和处理错误情况
    """
    actions: list[Action] = []
    # 验证响应格式，确保只有一个选择
    # 技术栈: Python断言 - 使用assert进行运行时验证
    assert len(response.choices) == 1, 'Only one choice is supported for now'
    choice = response.choices[0]
    assistant_msg = choice.message

    # 检查是否存在工具调用
    # 技术栈: 动态属性检查 - 使用hasattr检查对象属性
    if hasattr(assistant_msg, 'tool_calls') and assistant_msg.tool_calls:
        # 提取LLM响应中的思考内容
        # 技术栈:
        # - 类型检查 - 使用isinstance进行类型检查
        # - 字符串处理 - 文本内容提取和拼接
        thought = ''
        if isinstance(assistant_msg.content, str):
            thought = assistant_msg.content
        elif isinstance(assistant_msg.content, list):
            for msg in assistant_msg.content:
                if msg['type'] == 'text':
                    thought += msg['text']

        # 处理每个工具调用，转换为OpenHands的Action对象
        # 技术栈:
        # - 迭代处理 - 使用enumerate获取索引和值
        # - 日志记录 - 使用logger进行调试信息记录
        for i, tool_call in enumerate(assistant_msg.tool_calls):
            action: Action
            logger.debug(f'Tool call in function_calling.py: {tool_call}')

            # 解析函数调用参数
            # 技术栈:
            # - JSON解析 - 使用json.loads解析字符串为Python对象
            # - 异常处理 - 使用try/except捕获和处理解析错误
            # - 自定义异常 - 使用FunctionCallValidationError提供更具体的错误信息
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.decoder.JSONDecodeError as e:
                raise FunctionCallValidationError(
                    f'Failed to parse tool call arguments: {tool_call.function.arguments}'
                ) from e

            # ================================================
            # CmdRunTool (Bash)
            # ================================================
            # 处理命令行工具调用
            # 技术栈:
            # - 工具系统 - 使用create_cmd_run_tool创建命令行工具
            # - 参数验证 - 检查必要参数是否存在
            # - 异常处理 - 使用自定义异常提供明确的错误信息

            if tool_call.function.name == create_cmd_run_tool()['function']['name']:
                # 验证必要参数
                # 技术栈: 字典键检查 - 使用in操作符检查键是否存在
                if 'command' not in arguments:
                    raise FunctionCallValidationError(
                        f'Missing required argument "command" in tool call {tool_call.function.name}'
                    )

                # 将字符串参数转换为布尔值
                # 技术栈:
                # - 字典方法 - 使用get方法获取值并提供默认值
                # - 字符串比较 - 使用==操作符进行字符串比较
                is_input = arguments.get('is_input', 'false') == 'true'

                # 创建命令行动作对象
                # 技术栈: 对象实例化 - 使用类构造函数创建对象实例
                action = CmdRunAction(command=arguments['command'], is_input=is_input)

                # 设置硬超时（如果提供）
                # 技术栈:
                # - 类型转换 - 使用float()将字符串转换为浮点数
                # - 异常处理 - 捕获类型转换错误并提供友好错误信息
                # - 方法调用 - 使用对象方法设置属性
                if 'timeout' in arguments:
                    try:
                        action.set_hard_timeout(float(arguments['timeout']))
                    except ValueError as e:
                        raise FunctionCallValidationError(
                            f"Invalid float passed to 'timeout' argument: {arguments['timeout']}"
                        ) from e

            # ================================================
            # IPythonTool (Jupyter)
            # ================================================
            # 处理IPython工具调用（Jupyter交互式执行）
            # 技术栈:
            # - Jupyter集成 - 与IPython内核交互
            # - 代码执行 - 执行Python代码片段
            elif tool_call.function.name == IPythonTool['function']['name']:
                # 验证必要参数
                # 技术栈: 参数验证 - 检查必要参数是否存在
                if 'code' not in arguments:
                    raise FunctionCallValidationError(
                        f'Missing required argument "code" in tool call {tool_call.function.name}'
                    )
                # 创建IPython执行动作
                # 技术栈: 对象实例化 - 创建特定类型的Action对象
                action = IPythonRunCellAction(code=arguments['code'])

            # 处理代理委托（将任务委托给浏览代理）
            # 技术栈:
            # - 代理委托模式 - 将特定任务委托给专门的代理
            # - 多代理协作 - 不同代理之间的任务分配
            elif tool_call.function.name == 'delegate_to_browsing_agent':
                action = AgentDelegateAction(
                    agent='BrowsingAgent',
                    inputs=arguments,
                )

            # ================================================
            # AgentFinishAction
            # ================================================
            # 处理代理完成动作（标记任务完成）
            # 技术栈:
            # - 状态管理 - 管理代理任务的完成状态
            # - 可选参数处理 - 使用get方法获取可选参数
            elif tool_call.function.name == FinishTool['function']['name']:
                action = AgentFinishAction(
                    final_thought=arguments.get('message', ''),
                    task_completed=arguments.get('task_completed', None),
                )

            # ================================================
            # LLMBasedFileEditTool (LLM-based file editor, deprecated)
            # ================================================
            # 处理基于LLM的文件编辑工具（已弃用）
            # 技术栈:
            # - 文件操作 - 读取和修改文件内容
            # - 参数验证 - 检查必要参数
            # - 枚举类型 - 使用FileEditSource枚举表示实现来源
            elif tool_call.function.name == LLMBasedFileEditTool['function']['name']:
                # 验证必要参数
                # 技术栈: 参数验证 - 检查多个必要参数
                if 'path' not in arguments:
                    raise FunctionCallValidationError(
                        f'Missing required argument "path" in tool call {tool_call.function.name}'
                    )
                if 'content' not in arguments:
                    raise FunctionCallValidationError(
                        f'Missing required argument "content" in tool call {tool_call.function.name}'
                    )

                # 创建文件编辑动作
                # 技术栈:
                # - 对象实例化 - 创建FileEditAction对象
                # - 可选参数处理 - 使用get方法提供默认值
                # - 枚举使用 - 使用FileEditSource枚举指定实现来源
                action = FileEditAction(
                    path=arguments['path'],
                    content=arguments['content'],
                    start=arguments.get('start', 1),
                    end=arguments.get('end', -1),
                    impl_source=arguments.get(
                        'impl_source', FileEditSource.LLM_BASED_EDIT
                    ),
                )

            # 处理字符串替换编辑器工具
            # 技术栈:
            # - 工具系统 - 使用create_str_replace_editor_tool创建编辑器工具
            # - 条件表达式 - 使用复合条件判断工具类型
            elif (
                tool_call.function.name
                == create_str_replace_editor_tool()['function']['name']
            ):
                # 验证必要参数
                # 技术栈: 参数验证 - 检查多个必要参数
                if 'command' not in arguments:
                    raise FunctionCallValidationError(
                        f'Missing required argument "command" in tool call {tool_call.function.name}'
                    )
                if 'path' not in arguments:
                    raise FunctionCallValidationError(
                        f'Missing required argument "path" in tool call {tool_call.function.name}'
                    )
                # 提取基本参数
                # 技术栈:
                # - 变量赋值 - 从字典中提取值
                # - 字典推导式 - 使用推导式过滤字典
                path = arguments['path']
                command = arguments['command']
                other_kwargs = {
                    k: v for k, v in arguments.items() if k not in ['command', 'path']
                }

                # 根据命令类型创建不同的动作
                # 技术栈:
                # - 条件分支 - 使用if-else根据命令类型选择不同处理
                # - 枚举使用 - 使用FileReadSource枚举指定实现来源
                if command == 'view':
                    # 创建文件读取动作
                    # 技术栈: 对象实例化 - 创建FileReadAction对象
                    action = FileReadAction(
                        path=path,
                        impl_source=FileReadSource.OH_ACI,
                        view_range=other_kwargs.get('view_range', None),
                    )
                else:
                    # 处理编辑命令
                    # 技术栈:
                    # - 字典操作 - 使用pop方法移除不需要的键
                    # - 参数清理 - 移除不适用于当前操作的参数
                    if 'view_range' in other_kwargs:
                        # Remove view_range from other_kwargs since it is not needed for FileEditAction
                        other_kwargs.pop('view_range')

                    # 过滤出有效参数
                    # 技术栈:
                    # - 参数验证 - 验证参数是否在允许列表中
                    # - 集合操作 - 使用set进行成员检查
                    # - 工具定义访问 - 从工具定义中获取有效参数列表
                    valid_kwargs = {}
                    # Get valid parameters from the str_replace_editor tool definition
                    str_replace_editor_tool = create_str_replace_editor_tool()
                    valid_params = set(
                        str_replace_editor_tool['function']['parameters'][
                            'properties'
                        ].keys()
                    )

                    # 遍历并验证每个参数
                    # 技术栈:
                    # - 迭代处理 - 使用items()方法遍历键值对
                    # - 条件检查 - 使用if-else进行条件分支
                    for key, value in other_kwargs.items():
                        if key in valid_params:
                            valid_kwargs[key] = value
                        else:
                            raise FunctionCallValidationError(
                                f'Unexpected argument {key} in tool call {tool_call.function.name}. Allowed arguments are: {valid_params}'
                            )

                    # 创建文件编辑动作
                    # 技术栈:
                    # - 对象实例化 - 创建FileEditAction对象
                    # - 参数解包 - 使用**操作符解包字典作为关键字参数
                    # - 枚举使用 - 使用FileEditSource枚举指定实现来源
                    action = FileEditAction(
                        path=path,
                        command=command,
                        impl_source=FileEditSource.OH_ACI,
                        **valid_kwargs,
                    )
            # ================================================
            # AgentThinkAction
            # ================================================
            # 处理代理思考动作
            # 技术栈:
            # - 思考机制 - 允许代理记录思考过程
            # - 可选参数处理 - 使用get方法获取可选参数
            elif tool_call.function.name == ThinkTool['function']['name']:
                action = AgentThinkAction(thought=arguments.get('thought', ''))

            # ================================================
            # BrowserTool
            # ================================================
            # 处理浏览器工具调用
            # 技术栈:
            # - 浏览器自动化 - 执行浏览器交互操作
            # - 参数验证 - 检查必要参数
            elif tool_call.function.name == BrowserTool['function']['name']:
                # 验证必要参数
                # 技术栈: 参数验证 - 检查必要参数是否存在
                if 'code' not in arguments:
                    raise FunctionCallValidationError(
                        f'Missing required argument "code" in tool call {tool_call.function.name}'
                    )
                # 创建浏览交互动作
                # 技术栈: 对象实例化 - 创建BrowseInteractiveAction对象
                action = BrowseInteractiveAction(browser_actions=arguments['code'])

            # ================================================
            # MCPAction (MCP)
            # ================================================
            # 处理MCP（多云平台）动作
            # 技术栈:
            # - 多云集成 - 与多个云平台交互
            # - 动态工具调用 - 根据工具名称动态调用相应功能
            elif mcp_tool_names and tool_call.function.name in mcp_tool_names:
                # 创建MCP动作
                # 技术栈: 对象实例化 - 创建MCPAction对象
                action = MCPAction(
                    name=tool_call.function.name,
                    arguments=arguments,
                )
            else:
                # 处理未注册工具错误
                # 技术栈:
                # - 异常处理 - 使用自定义异常提供明确错误信息
                # - 错误信息格式化 - 包含详细上下文信息
                raise FunctionCallNotExistsError(
                    f'Tool {tool_call.function.name} is not registered. (arguments: {arguments}). Please check the tool name and retry with an existing tool.'
                )

            # 只为第一个动作添加思考内容
            # 技术栈:
            # - 索引检查 - 使用索引确定第一个动作
            # - 函数调用 - 调用combine_thought函数合并思考内容
            if i == 0:
                action = combine_thought(action, thought)

            # 添加工具调用元数据
            # 技术栈:
            # - 元数据管理 - 为动作添加元数据
            # - 对象属性赋值 - 设置对象的属性
            action.tool_call_metadata = ToolCallMetadata(
                tool_call_id=tool_call.id,
                function_name=tool_call.function.name,
                model_response=response,
                total_calls_in_response=len(assistant_msg.tool_calls),
            )
            # 将动作添加到结果列表
            # 技术栈: 列表操作 - 使用append方法添加元素
            actions.append(action)
    else:
        # 处理没有工具调用的情况（纯文本响应）
        # 技术栈:
        # - 条件分支 - 使用else处理替代情况
        # - 字符串转换 - 使用str()确保内容是字符串
        actions.append(
            MessageAction(
                content=str(assistant_msg.content) if assistant_msg.content else '',
                wait_for_response=True,
            )
        )

    # 为所有动作添加响应ID
    # 技术栈:
    # - 迭代处理 - 使用for循环遍历列表
    # - 对象属性赋值 - 设置对象的属性
    # - 元数据管理 - 关联动作与原始响应
    for action in actions:
        action.response_id = response.id

    # 确保至少有一个动作
    # 技术栈: 断言验证 - 使用assert确保结果符合预期
    assert len(actions) >= 1
    return actions
