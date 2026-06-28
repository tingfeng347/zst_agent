from typing import Callable, Any
import asyncio
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompt, load_chat_prompt

# 工具调用监控装饰器，用于包装工具调用逻辑，记录日志和处理特殊逻辑
@wrap_tool_call
async def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
) -> ToolMessage | Command:
    # 记录当前执行的工具名称日志
    logger.info(f"[tool monitor]执行工具: {request.tool_call['name']}")
    # 记录当前工具调用的参数日志
    logger.info(f"[tool monitor]参数: {request.tool_call['args']}")
    try:
        # 执行实际的工具处理函数，获取调用结果
        # 在异步上下文中，handler 可能是同步或异步的，需要适当处理
        import inspect
        if inspect.iscoroutinefunction(handler):
            result = await handler(request)
        else:
            # 同步 handler 在线程池中执行，避免阻塞事件循环
            result = await asyncio.to_thread(handler, request)
        # 记录工具调用成功的日志
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")
        # 判断当前调用的是否是填充报告上下文的工具
        if request.tool_call['name'] == 'chat_prompt_switch':
            # 记录该工具被调用的日志，提示要注入报告上下文标记
            logger.info(f"[tool monitor]chat_prompt_switch工具被调用，注入上下文 report=True")
            # 在运行时上下文中设置report为True，标记后续需要生成报告格式的内容
            request.runtime.context["chat"] = True
        elif request.tool_call['name'] == 'query_prompt_switch':
            logger.info(f"[tool monitor]query_prompt_switch工具被调用，注入上下文 report=False")
            request.runtime.context["chat"] = False
        # 返回工具处理的结果
        return result
    except Exception as e:
        # 记录工具调用失败的日志，包含具体错误信息
        logger.info(f"工具{request.tool_call['name']}调用失败: {e}")
        # 重新抛出异常，让上层逻辑处理错误
        raise

# 模型调用前的钩子装饰器，用于在模型调用前记录相关日志
@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    # 记录即将调用模型的日志，包含当前对话历史中的消息总数
    logger.info(f"[log_before_model]: 即将调用模型，带有{len(state['messages'])}条消息，消息如下：")
    # 遍历所有消息打印的代码被注释，保留原注释结构
    # for message in state['messages']:
    #     logger.info(f"[log_before_model][{type(message).__name__}]: {message.content.strip()}")
    # 记录省略中间消息内容的分隔日志
    logger.info(f"[log_before_model]: ----------省略已输出内容----------")
    # 记录对话历史中最后一条消息的类型和内容，聚焦最新交互信息
    last_message = state['messages'][-1]
    # 处理 content 可能是字符串或列表的情况
    content = last_message.content
    if isinstance(content, str):
        content_str = content.strip()
    elif isinstance(content, list):
        # 如果是列表，提取文本内容
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if 'text' in item:
                    text_parts.append(str(item['text']))
                elif 'content' in item:
                    text_parts.append(str(item['content']))
            else:
                text_parts.append(str(item))
        content_str = "\n".join(text_parts).strip()
    else:
        content_str = str(content).strip()
    logger.info(f"[log_before_model][{type(last_message).__name__}]: {content_str}")

    # 返回None，before_model钩子无需修改状态或返回额外数据
    return None


# 动态提示词装饰器，用于根据运行时上下文切换不同的提示词模板
@dynamic_prompt
def prompt_switch(request: ModelRequest) -> str:
    # 从运行时上下文中获取report标记，默认值为False，表示不需要聊天
    is_chat = request.runtime.context.get("chat", False)
    # 如果需要生成报告，则加载报告专用的提示词模板
    if is_chat:
        return load_chat_prompt()
    else:
        return load_system_prompt()


