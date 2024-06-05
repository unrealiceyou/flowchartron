from abc import ABC, abstractmethod
from typing import List, Tuple
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from flowchartron.elements_db import BlockStyle, BlockStyleDB

class IDIterator:
    def __iter__(self):
        self.a = 10
        return self

    def __next__(self):
        x = self.a
        self.a += 1
        return x

iteratorInstance = IDIterator()
blockID = iter(iteratorInstance)

class FlowChart:
    def __init__(self):
        self.elements: List[Element] = []

    def add_element(self, element: "Element"):
        self.elements.append(element.clone())

    def parse_XML(self, xml_string: str, style_db: BlockStyleDB):
        self.elements: List[Element] = []
        root = ET.fromstring(xml_string)

        A = self.__parse_XML_subChart__(root, style_db)
        for element in A.elements:
            self.elements.append(element)

    def __parse_XML_subChart__(self, root: ET.Element, style_db: BlockStyleDB) -> "SubChart":
        subChart = SubChart()

        for element in root:
            style_dict = style_db.get_styles(element.tag)
            behaviour_type = list(style_dict.values())[0]._behaviour_type

            match behaviour_type:
                case 'BasicBlock':
                    subChart.add_element(BasicBlock(element.attrib['label'], style_dict))

                case 'DecisionBlock':
                    decision_block = DecisionBlock(element.attrib['label'], style_dict)
                    for condition in element:
                        decision = Decision(condition.attrib['label'])
                        decision.subChart = self.__parse_XML_subChart__(condition, style_db)
                        decision_block.add_decision(decision)
                    subChart.add_element(decision_block)

                case 'WhileBlock':
                    style_dict = style_db.get_styles("WhileBlock")
                    while_block = WhileBlock(element.attrib['label'], style_dict)
                    while_block.subChart = self.__parse_XML_subChart__(element, style_db)
                    subChart.add_element(while_block)

                case 'ForBlock':
                    style_dict = style_db.get_styles("ForBlock")
                    for_block = ForBlock(element.attrib['label'], style_dict)
                    for_block.subChart = self.__parse_XML_subChart__(element, style_db)
                    subChart.add_element(for_block)

        return subChart

    def chart_compile(self, style_db: BlockStyleDB) -> str:
        drawio_flowchart = DrawioFlowChart()
        terminator_style = style_db.get_styles("TerminatorBlock")

        beginningBlock = BasicBlock("Начало", terminator_style)
        pos = beginningBlock.compile(drawio_flowchart, (0,0))

        oldEndID = beginningBlock._endID
        for element in self.elements:
            if element.get_name() == "TerminatorBlock": break
            pos = element.compile(drawio_flowchart, pos)
            drawio_flowchart.connect(oldEndID, element._startID, label = "")
            oldEndID = element._endID

        endingBlock = BasicBlock("Конец", terminator_style)
        endingBlock.compile(drawio_flowchart, pos)
        drawio_flowchart.connect(oldEndID, endingBlock._startID, label = "")

        return drawio_flowchart.xml_string()

    @staticmethod
    def get_behaviour_descs() -> str:
        L: List[str] = []
        for subclass in FlowChart.__subclasses__():
            L.append(f"{subclass.__name__}: {subclass.get_desc()}")

        return "\n".join(L)

class SubChart:
    def __init__(self):
        self.elements: List[Element] = []

    def add_element(self, element: "Element"):
        self.elements.append(element.clone())

    def get_startID(self):
        return self.elements[0]._startID

    def get_endID(self):
        return self.elements[-1]._endID

    def get_width(self) -> int:
        lwidthMax = 0
        rwidthMax = 0
        for element in self.elements:
            lwidth = element.get_relative_center()
            rwidth = element.get_width() - lwidth
            lwidthMax = max(lwidthMax, lwidth)
            rwidthMax = max(rwidthMax, rwidth)

        return lwidthMax + rwidthMax

    def get_relative_center(self) -> int:
        lwidthMax = 0
        for element in self.elements:
            lwidth = element.get_relative_center()
            lwidthMax = max(lwidthMax, lwidth)

        return lwidthMax

    def get_length(self) -> int:
        L = 0
        for element in self.elements:
            L += element.get_length() + 40
        L -= 40
        return L

    def compile(self, drawio_flowchart: "DrawioFlowChart", pos: Tuple[int, int]):
        oldEndID = 0
        for element in self.elements:
            pos = element.compile(drawio_flowchart, pos)
            if (oldEndID != 0): drawio_flowchart.connect(oldEndID, element._startID, "")
            oldEndID = element._endID
        return pos
            
class Element(ABC):
    def __init__(self, label: str, style_dict: dict[str, BlockStyle]):
        self.label = label
        self._startID = next(blockID)
        self._endID = self._startID
        self._style_dict = style_dict

    @abstractmethod
    def compile(self, drawio_flowchart: "DrawioFlowChart", pos: Tuple[int, int]) -> Tuple[int, int]:
        pass

    @abstractmethod
    def clone(self) -> "Element":
        pass

    @abstractmethod
    def get_width(self) -> int:
        pass

    @abstractmethod
    def get_relative_center(self) -> int:
        pass

    @abstractmethod
    def get_length(self) -> int:
        pass

    def get_name(self) -> str:
        return list(self._style_dict.values())[0]._name

    @staticmethod
    def get_desc() -> str:
        return "This string will be overridden"

class BasicBlock(Element, FlowChart):
    def __init__(self, label: str, style_dict: dict[str, BlockStyle]):
        self.label = label
        self._startID = next(blockID)
        self._endID = self._startID
        self._style_dict = style_dict

    def clone(self) -> "BasicBlock":
        clone = BasicBlock(self.label, self._style_dict)
        return clone

    def get_width(self) -> int:
        return self._style_dict["block"]._width 

    def get_relative_center(self) -> int:
        return self._style_dict["block"]._width // 2

    def get_length(self) -> int:
        return self._style_dict["block"]._height

    def compile(self, drawio_flowchart: "DrawioFlowChart", pos: Tuple[int, int]) -> Tuple[int, int]:
        style = self._style_dict["block"]

        drawio_flowchart.put_block(
                ID=self._startID,
                label=self.label,
                style=style,
                x=pos[0],
                y=pos[1]
                )

        return (pos[0], pos[1] + style._height + 40)

    @staticmethod
    def get_desc() -> str:
        return "a block representing one operation"

class Decision:
    def __init__(self, label: str):
        self.label = label
        self.subChart = SubChart()

    def get_startID(self):
        return self.subChart.get_startID()

    def get_endID(self):
        return self.subChart.get_endID()

    def add_element(self, element: Element):
        self.subChart.add_element(element)

    def get_width(self) -> int:
        return self.subChart.get_width()

    def get_length(self) -> int:
        return self.subChart.get_length()

    def get_relative_center(self) -> int:
        return self.subChart.get_relative_center()

    def compile(self, root, pos: Tuple[int, int]) -> Tuple[int, int]:
        newPos = self.subChart.compile(root, pos);
        return newPos

class DecisionBlock(Element, FlowChart):
    def __init__(self, label: str, style_dict: dict[str, BlockStyle]):
        self.label = label
        self._startID = next(blockID)
        self._endID = next(blockID)
        self._style_dict = style_dict 
        self.decisions: List[Decision] = []

    def get_width(self) -> int:
        if len(self.decisions) == 1:
            return self.decisions[0].get_width() + 20

        W = 0
        for decision in self.decisions:
            W += decision.get_width() + 40
        W -= 40
        return W

    def get_relative_center(self) -> int:
        N = len(self.decisions)
        dx = 0

        if (N % 2 == 0):
            C = N // 2 - 1
            for i in range(C + 1):
                dx += self.decisions[i].get_width() + 40
            dx -= 20
        else:
            C = (N - 1) // 2 - 1
            for i in range(C + 1):
                dx += self.decisions[i].get_width() + 40
            dx += self.decisions[C+1].get_relative_center()
        return dx

    def get_max_decision_height(self) -> int:
        L = self.decisions[0].get_length()
        for decision in self.decisions:
            L = max(L, decision.get_length())
        return L

    def get_length(self) -> int:
        return self.get_max_decision_height() + self._style_dict["block"]._height + 40

    def add_decision(self, decision: Decision):
        self.decisions.append(decision)

    def clone(self) -> "DecisionBlock":
        clone = DecisionBlock(self.label, self._style_dict)
        clone.decisions = self.decisions.copy()
        return clone

    def compile(self, drawio_flowchart: "DrawioFlowChart", pos: Tuple[int, int]) -> Tuple[int, int]:
        style = self._style_dict["block"]

        drawio_flowchart.put_block(
                ID=self._startID,
                label=self.label,
                style=style,
                x=pos[0],
                y=pos[1]
                )

        lowestDecisionY = pos[1] + self.get_max_decision_height() + style._height + 40

        drawio_flowchart.put_point(
                ID=self._endID,
                x=pos[0] + style._width // 2,
                y=lowestDecisionY + 20
                )

        N = len(self.decisions)
        startingPos = (
                pos[0] - self.get_relative_center() + style._width // 2,
                pos[1] + style._height + 40,
                )

        for i in range(N):
            decision = self.decisions[i]
            decision.compile(drawio_flowchart, startingPos)
            style_dict = decision.subChart.elements[-1]._style_dict

            if list(style_dict.values())[0]._name != "TerminatorBlock":
                drawio_flowchart.connect(
                        idA=decision.get_endID(), 
                        idB=self._endID, 
                        label="", 
                        constraintPos=(startingPos[0] + decision.get_relative_center(), lowestDecisionY + 20), 
                        endTip=(i >= N / 2)
                        )
            
            if (i == (N - 1) / 2):
                constraintPos = (startingPos[0] + style._width // 2, pos[1] + style._height)
            else:
                constraintPos = (startingPos[0] + decision.get_relative_center(), pos[1] + style._height // 2)

            decision_point_id = next(blockID)
            drawio_flowchart.put_point(decision_point_id, startingPos[0] + style._width // 2, startingPos[1] - 40)
            drawio_flowchart.connect(self._startID, decision_point_id, "", constraintPos)
            drawio_flowchart.connect(decision_point_id, decision.get_startID(), decision.label)
            startingPos = (startingPos[0] + decision.get_width() + 40, startingPos[1])

        if (N == 1):
            constraintPos = (pos[0] + self.decisions[0].get_width() + 20, pos[1] + style._height // 2)
            drawio_flowchart.connect(self._startID, self._endID, "Иначе", constraintPos, True)

        return (pos[0], lowestDecisionY + 40)

    @staticmethod
    def get_desc() -> str:
        return "a block representing if and case switch statements"

class WhileBlock(Element, FlowChart):
    def __init__(self, label: str, style_dict: dict[str, BlockStyle]):
        self.label = label
        self.subChart = SubChart()
        self._startID = next(blockID)
        self._endID = next(blockID)
        self._style_dict = style_dict

    def clone(self) -> "WhileBlock":
        clone = WhileBlock(self.label, self._style_dict)
        clone.subChart = self.subChart
        return clone

    def get_width(self) -> int:
        return self.subChart.get_width() + 20

    def get_relative_center(self) -> int:
        return self.subChart.get_relative_center()

    def get_length(self) -> int:
        return self._style_dict["block"]._height + self.subChart.get_length() + 40

    def compile(self, drawio_flowchart: "DrawioFlowChart", pos: Tuple[int, int]) -> Tuple[int, int]:
        style = self._style_dict["block"]
        main_block_id = next(blockID)

        drawio_flowchart.put_point(
                ID=self._startID,
                x=pos[0] + style._width // 2,
                y=pos[1] - 20
                )

        drawio_flowchart.put_block(
                ID=main_block_id,
                label=self.label,
                style=style,
                x=pos[0],
                y=pos[1]
                )

        drawio_flowchart.connect(self._startID, main_block_id)
        drawio_flowchart.connect(main_block_id, self.subChart.get_startID(), "Истина")

        endPos = self.subChart.compile(drawio_flowchart, (pos[0], pos[1] + style._height + 40))

        loop_point_id = next(blockID)
        drawio_flowchart.put_point(loop_point_id, endPos[0] + style._width // 2, endPos[1] - 20)
        drawio_flowchart.connect(self.subChart.get_endID(), loop_point_id)
        constr_pos = (
                pos[0] + style._width // 2 + self.subChart.get_width() - self.subChart.get_relative_center() + 20,
                endPos[1] - 20
                )
        drawio_flowchart.connect(loop_point_id, self._startID, "", constr_pos, True)

        drawio_flowchart.put_point(self._endID, endPos[0] + style._width // 2, endPos[1])
        constr_pos = (
                pos[0] + style._width // 2 - self.subChart.get_relative_center() - 20,
                pos[1] + style._height // 2
                )
        drawio_flowchart.connect(main_block_id, self._endID, "Иначе", constr_pos, True)

        return (endPos[0], endPos[1] + 20)

    @staticmethod
    def get_desc() -> str:
        return "a block representing while loops"

class ForBlock(Element, FlowChart):
    def __init__(self, label: str, style_dict: dict[str, BlockStyle]):
        self.label = label
        self.subChart = SubChart()
        self._startID = next(blockID)
        self._endID = next(blockID)
        self._style_dict = style_dict

    def clone(self) -> "ForBlock":
        clone = ForBlock(self.label, self._style_dict)
        clone.subChart = self.subChart
        return clone

    def get_width(self) -> int:
        return self.subChart.get_width() + 20

    def get_relative_center(self) -> int:
        return self.subChart.get_relative_center()

    def get_length(self) -> int:
        style_begin = self._style_dict["beginning"]
        style_end = self._style_dict["end"]

        return style_begin._height + self.subChart.get_length() + style_end._height + 80

    def compile(self, drawio_flowchart: "DrawioFlowChart", pos: Tuple[int, int]) -> Tuple[int, int]:
        style_begin = self._style_dict["beginning"]
        style_end = self._style_dict["end"]

        drawio_flowchart.put_block(self._startID, self.label, style_begin, pos[0], pos[1])
        end_pos = self.subChart.compile(drawio_flowchart, (pos[0], pos[1] + style_begin._height + 40))
        drawio_flowchart.connect(self._startID, self.subChart.get_startID())
        drawio_flowchart.put_block(self._endID, self.label, style_end, end_pos[0], end_pos[1])
        drawio_flowchart.connect(self.subChart.get_endID(), self._endID)

        return (end_pos[0], end_pos[1] + style_end._height + 40)

    @staticmethod
    def get_desc() -> str:
        return "a block representing for loops"

class DrawioFlowChart:
    def __init__(self):
        mxfile = ET.Element('mxfile')
        mxfile.set("host", "app.diagrams.net")
    
        diagram = ET.SubElement(mxfile, "diagram")
        diagram.set("name", "Page 1")
        diagram.set("id", "1")
    
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel")
        mxGraphModel.set("dx", "559")
        mxGraphModel.set("dy", "777")
        mxGraphModel.set("grid", "1")
        mxGraphModel.set("gridSize", "10")
        mxGraphModel.set("guides", "1")
        mxGraphModel.set("tooltips", "1")
        mxGraphModel.set("connect", "1")
        mxGraphModel.set("arrows", "1")
        mxGraphModel.set("fold", "1")
        mxGraphModel.set("page", "1")
        mxGraphModel.set("pageScale", "1")
        mxGraphModel.set("pageWidth", "827")
        mxGraphModel.set("pageHeight", "1129")
        mxGraphModel.set("math", "0")
        mxGraphModel.set("shadow", "0")

        self._mxfile = mxfile
        self._root = ET.SubElement(mxGraphModel, "root")

        # add the weird id = 0 and id = 1 blocks
        root_cell_0 = ET.SubElement(self._root, "mxCell")
        root_cell_0.set("id", "0")
        root_cell_1 = ET.SubElement(self._root, "mxCell")
        root_cell_1.set("id", "1")
        root_cell_1.set("parent", "0")


    def connect(self, idA: int, idB: int, label: str = "", constraintPos: Tuple[int, int] = (0,0), endTip: bool = False):
        arrow = ET.SubElement(self._root, "mxCell")
        arrow.set("id", str(next(blockID)))
        arrow.set("value", label)
        endArrow = "classicThin" if endTip else "none"        
        arrow.set("style", f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;endArrow={endArrow};endFill=0;fontFamily=GOST;fontSource=http%3A%2F%2Fmurena.io%2Fs%2FwJdr83WFBzcZGHY%2Fdownload%2FGOST.woff;")
        arrow.set("edge", "1")
        arrow.set("parent", "1")
        arrow.set("source", str(idA))
        arrow.set("target", str(idB))
        geometry = ET.SubElement(arrow, "mxGeometry")
        geometry.set("relative", "1")
        geometry.set("as", "geometry")

        if (constraintPos == (0, 0)): return
        pointsArray = ET.SubElement(geometry, "Array")
        pointsArray.set("as", "points")

        constraintPoint = ET.SubElement(pointsArray, "mxPoint")
        constraintPoint.set("x", str(constraintPos[0]))
        constraintPoint.set("y", str(constraintPos[1]))

    def put_point(self, ID: int, x: int, y: int):
        point = ET.SubElement(self._root, "mxCell")
        point.set("id", str(ID))
        point.set("value", "")
        point.set("style", "strokeWidth=2;html=1;shape=mxgraph.flowchart.start_2;whiteSpace=wrap;fontFamily=GOST;fontSource=http%3A%2F%2Fmurena.io%2Fs%2FwJdr83WFBzcZGHY%2Fdownload%2FGOST.woff;")
        point.set("vertex", "1")
        point.set("parent", "1")
        geometry = ET.SubElement(point, "mxGeometry")
        geometry.set("x", str(x))
        geometry.set("y", str(y))
        geometry.set("width", "0")
        geometry.set("height", "0")
        geometry.set("as", "geometry")

    def put_block(self, ID: int, label: str, style: BlockStyle, x: int, y: int):
        block = ET.SubElement(self._root, "mxCell")
        block.set("id", str(ID))
        block.set("value", label)
        block.set("style", style.drawio_style_string())
        block.set("vertex", "1")
        block.set("parent", "1")
        geometry = ET.SubElement(block, "mxGeometry")
        geometry.set("x", str(x))
        geometry.set("y", str(y))
        geometry.set("width", str(style._width))
        geometry.set("height", str(style._height))
        geometry.set("as", "geometry")

    def xml_string(self) -> str:
        xml_string = ET.tostring(self._mxfile, "unicode")
        return BeautifulSoup(xml_string, "xml").prettify()

