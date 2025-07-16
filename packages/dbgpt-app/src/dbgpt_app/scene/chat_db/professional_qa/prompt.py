from dbgpt._private.config import Config
from dbgpt.core import (
    ChatPromptTemplate,
    HumanPromptTemplate,
    MessagesPlaceholder,
    SystemPromptTemplate,
)
from dbgpt_app.scene import AppScenePromptTemplateAdapter, ChatScene
from dbgpt_app.scene.chat_db.professional_qa.out_parser import NormalChatOutputParser

CFG = Config()


_DEFAULT_TEMPLATE_EN = """
Provide professional answers to requests and questions. If you can't get an answer \
from what you've provided, say: "Insufficient information in the knowledge base is \
available to answer this question." Feel free to fudge information.
1. Output **only the final SQL statements**—no analysis, explanations, or additional text.  
2. Generate **SELECT queries only**—**no INSERT/UPDATE/DELETE** or any database-modifying operations.  
3. Ensure SQL syntax fully complies with the provided DDL structure.  
4. Each SQL statement ends with a non semicolon，such as (`;`).  
5. If requirements are unclear, generate typical business-meaningful queries based on the DDL.
Use the following tables generate sql if have any table info:
{table_info}

user question:
{input}

Please only display SQL without outputting the process.
Do not add any notes.
Do not add any comments.
Do not add any prompts, such as -- Note:.
"""
#think step by step.

_DEFAULT_TEMPLATE_ZH = """
根据要求和问题，提供专业的答案。如果无法从提供的内容中获取答案，请说：\
“知识库中提供的信息不足以回答此问题。” 禁止随意捏造信息。
1. 只输出最终的SQL语句，不要包含任何分析过程或解释性文字
2. 仅生成SELECT查询语句，禁止生成INSERT/UPDATE/DELETE等会修改数据库的语句
3. 确保SQL语法完全符合提供的DDL结构
4. 每个SQL语句不要以分号结尾
5. 要完全符合DDL中的字段，禁止生成其他字段展示SQL

使用以下表结构信息: 
{table_info}

问题:
{input}
请只展示sql不用输出过程。
不要添加任何注释。
不要添加任何评论。
不要添加任何提示，如 -- Note:。
"""

_DEFAULT_TEMPLATE_ZH = """
根据问题要求，严格基于提供的表结构信息生成SQL语句。请遵守以下规则：
1. 仅当表结构包含回答问题所需的所有字段时，生成SELECT查询
2. 如果表结构信息不足，直接返回："知识库中提供的信息不足以回答此问题。"
3. 生成的SQL必须：
   - 完全符合提供的DDL结构
   - 仅包含SELECT语句（禁止其他操作类型）
   - 不包含分号结尾
   - 仅使用DDL中定义的字段（禁止添加额外字段）
4. 最终输出只能是以下两种形式之一：
   - 符合要求的纯SQL语句
   - 指定提示文本
5. 禁止包含任何：
   - 分析过程或解释文字
   - 注释（包括--或/* */）
   - 评价性语句
   - 非SQL文本

表结构信息: 
{table_info}

问题:
{input}

"""

#一步步思考。
_DEFAULT_TEMPLATE = (
    _DEFAULT_TEMPLATE_EN if CFG.LANGUAGE == "en" else _DEFAULT_TEMPLATE_ZH
)


PROMPT_NEED_STREAM_OUT = True


prompt = ChatPromptTemplate(
    messages=[
        SystemPromptTemplate.from_template(_DEFAULT_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanPromptTemplate.from_template("{input}"),
    ]
)

prompt_adapter = AppScenePromptTemplateAdapter(
    prompt=prompt,
    template_scene=ChatScene.ChatWithDbQA.value(),
    stream_out=PROMPT_NEED_STREAM_OUT,
    output_parser=NormalChatOutputParser(),
)


CFG.prompt_template_registry.register(
    prompt_adapter, language=CFG.LANGUAGE, is_default=True
)
