from langchain.agents import create_agent
from agent.tools.middleware import monitor_tool, log_before_model, prompt_switch
from agent.tools.agent_tools import (rag_summarize, query_prompt_switch,chat_prompt_switch)
from agent.mcp.multi_mcp import get_mcp_tools
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from utils.logger_handler import logger


class ReactAgent(object):
    def __init__(self):
        # 获取自定义工具
        custom_tools = [
            rag_summarize,
            query_prompt_switch,
            chat_prompt_switch
        ]
        
        # 获取 MCP 工具
        mcp_tools = get_mcp_tools()
        
        # 记录加载的工具数量
        logger.info(f"[ReactAgent]加载了 {len(custom_tools)} 个自定义工具")
        logger.info(f"[ReactAgent]加载了 {len(mcp_tools)} 个 MCP 工具")
        
        # 合并所有工具
        all_tools = custom_tools + mcp_tools
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompt(),
            tools=all_tools,
            middleware=[monitor_tool, log_before_model, prompt_switch],
        )

    async def execute_stream(self, query):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        async for chunk in self.agent.astream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]  # 有历史记录所以取最后一条
            if latest_message.content:
                # 确保 content 是字符串
                content = latest_message.content
                if isinstance(content, str):
                    yield content.strip() + "\n"
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
                    if text_parts:
                        yield "\n".join(text_parts).strip() + "\n"
                else:
                    yield str(content).strip() + "\n"

# if __name__ == '__main__':
#     agent = ReactAgent()
#     for chunk in agent.execute_stream("给我生成我的使用报告"):
#         print(chunk, end="", flush=True)
