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
Provide professional and accurate answers based on the provided table structure information according to the requirements and questions. Please follow the steps below to think:

1. Carefully analyze the problem: {input}
2. Check the table structure information: {table_info}
3. Determine whether the table structure contains the fields and data required to answer the question
If the table structure information is sufficient to answer the question, please provide a professional answer
If the table structure information is insufficient, please reply: "The information provided in the knowledge base is not sufficient to answer this question

be careful:
-The answer must be strictly based on the provided table structure information
-Prohibit any form of speculation or fabrication of information
-Ensure the professionalism and accuracy of the answers
-Step by step thinking
"""

_DEFAULT_TEMPLATE_ZH = """
根据要求和问题，基于提供的表结构信息，提供专业准确的答案。请按照以下步骤思考：

1. 仔细分析问题：{input}
2. 检查表结构信息：{table_info} 
3. 判断表结构中是否包含回答问题所需的字段和数据
4. 如果表结构信息足够回答问题，请给出专业解答
5. 如果无法从提供的内容中获取答案，请说：“知识库中提供的信息不足以回答此问题。” 禁止随意捏造信息。
6. 生成的SQL最后不需要分号结尾
7. 确保SQL语法完全符合提供的表结构信息

注意：
- 必须严格基于提供的表结构信息回答
- 禁止任何形式的猜测或编造信息
- 确保回答的专业性和准确性
- 如果有SQL生成，需要返回markdown格式的
- 一步步思考

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
    template_scene=ChatScene.ChatDialogueDbQA.value(),
    stream_out=PROMPT_NEED_STREAM_OUT,
    output_parser=NormalChatOutputParser(),
)


CFG.prompt_template_registry.register(
    prompt_adapter, language=CFG.LANGUAGE, is_default=True
)
