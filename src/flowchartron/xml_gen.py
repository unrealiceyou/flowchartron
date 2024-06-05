import re
from flowchartron import diagramMaker, gpt
from PyQt5.QtCore import pyqtSignal

def extract_XML(gptString: str) -> str | None:
    pattern = """```xml([^`]*)```"""
    match = re.search(pattern, gptString)
    if (match == None): return None
    return match.group(1)

def generate_XML(program_source: str, progress_signal: pyqtSignal) -> str:
    chat = gpt.DuckChat()

    style_db = diagramMaker.BlockStyleDB("cool_db.db")
    skel_blocks_desc = diagramMaker.FlowChart.get_behaviour_descs()
    blocks_desc = style_db.get_decriptions()

    prompt_init = f"""
For the following code snippet create a flowchart XML in a code block using these blocks:
{skel_blocks_desc}

FlowChart format:
    ```xml
    <flowchart>
    <BasicBlock label="operation"/>
    <WhileBlock label="while">
        <BasicBlock label="label"/>
        <BasicBlock label="label"/>
    <WhileBlock/>
    <DecisionBlock label="condition">
        <condition label="label">
            <BasicBlock label="label"/>
        </condition>
    </DecisionBlock>
    </flowchart>
    ```
Code snippet:
{program_source}
"""
    progress_signal.emit(1)
    xmlString = chat.send_message(prompt_init)
    if (xmlString == None):
        progress_signal.emit(0)
        raise Exception("Не удалось получить базовую диаграмму!")

    progress_signal.emit(2)
    xmlString = chat.send_message(
            f"Please replace every BasicBlock in the following flowchart with these:\n{blocks_desc}\nHere is the FlowChart:\n{xmlString}"
            )
    if (xmlString == None):
        progress_signal.emit(0)
        raise Exception("Не удалось получить диаграмму с украшенными блоками!")
        
    progress_signal.emit(3)
    xmlString = chat.send_message(f"Please replace contents of label=\"something\" with short enough descriptions for flowcharts, while retaining the most context of their functionality in plain language':\n {xmlString}.")
    if xmlString == None:
        progress_signal.emit(0)
        raise Exception("Не удалось получить переведённую диаграмму!")

    progress_signal.emit(4)
    xmlString = chat.send_message(f"Please translate constents of label=\"something\" to Russian:\n {xmlString}")
    if xmlString == None:
        progress_signal.emit(0)
        raise Exception("Не удалось получить переведённую диаграмму!")

    progress_signal.emit(5)
    xmlString = chat.send_message(f"Check for unclosed tags in the following xml and correct them. Please return the new xml in a codeblock:\n {xmlString}")
    if xmlString == None:
        progress_signal.emit(0)
        raise Exception("Не удалось получить исправленную диаграмму!")

    XML = extract_XML(xmlString)
    if XML == None:
        progress_signal.emit(0)
        raise Exception("Не удалось извлечь диаграмму!")

    progress_signal.emit(0)
    return XML
