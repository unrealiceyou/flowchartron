import sqlite3
from typing import List

class BlockStyle:
    def __init__(self, 
                 name: str,
                 width: int,
                 height: int,
                 render_style: str,
                 stroke_width: int,
                 gpt_desc: str,
                 behaviour_type: str,
                 element_type: str,
                 font_family: str = "",
                 font_source: str = "",
                 direction: str = "east",
                 point_param: float = 0,
                 arc_param: float = 0,
                 ):

        if direction not in ["north", "south", "east", "west"]:
            raise ValueError

        self._name = name
        self._width = width
        self._height = height
        self._render_style = render_style
        self._stroke_width = stroke_width
        self._font_family = font_family
        self._font_source = font_source
        self._direction = direction
        self._point_param = point_param
        self._arc_param = arc_param
        self._gpt_desc = gpt_desc
        self._behaviour_type = behaviour_type
        self._element_type = element_type

    def drawio_style_string(self) -> str:
        L: List[str] = ["html=1", "whiteSpace=wrap"]
        L.append(f"shape={self._render_style}")
        L.append(f"strokeWidth={self._stroke_width}")
        if self._font_family != "": L.append(f"fontFamily={self._font_family}")
        if self._font_source != "": L.append(f"fontSource={self._font_source}")
        L.append(f"direction={self._direction}")
        if self._point_param != 0: L.append(f"size={self._point_param:.20f}")
        if self._arc_param != 0: L.append(f"rounded=1;absoluteArcSize=1;arcSize={self._arc_param:.20f}")
        return ";".join(L)

class BlockStyleDB:
    def __init__(self, file_name: str):
        self.con = sqlite3.connect(file_name)
        self.cur = self.con.cursor()

        self.cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='BLOCKS'")
        table_exists = self.cur.fetchone()
        if table_exists: return

        self.cur.execute(f'''CREATE TABLE BLOCKS (id INTEGER PRIMARY KEY, name TEXT, behaviour_type TEXT, element_type TEXT, gpt_desc TEXT, width INTEGER, height INTEGER, render_style TEXT, stroke_width INTEGER, font_family TEXT, font_source TEXT, direction TEXT, point_param REAL, arc_param REAL)''')

        font_family = "GOST Type A"
        font_source = "http%3A%2F%2Fmurena.io%2Fs%2FwJdr83WFBzcZGHY%2Fdownload%2FGOST.woff"
    
        self.add_style(BlockStyle(
            name="ProcessBlock",
            behaviour_type="BasicBlock",
            element_type="block",
            width=120,
            height=80,
            render_style="",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block containing basic arithmetic operations"
            ))

        self.add_style(BlockStyle(
            name="DisplayBlock",
            behaviour_type="BasicBlock",
            element_type="block",
            width=120,
            height=80,
            point_param=1/4,
            render_style="display",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block that shows messages to the user. for example: python's print"
            ))

        self.add_style(BlockStyle(
            name="ManualInputBlock",
            behaviour_type="BasicBlock",
            element_type="block",
            width=120,
            height=80,
            point_param=13,
            render_style="manualInput",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block that gets user input"
            ))

        self.add_style(BlockStyle(
            name="PredefinedProcessBlock",
            behaviour_type="BasicBlock",
            element_type="block",
            width=120,
            height=80,
            point_param=0.14,
            render_style="process",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block containing a predefined operation (i.e. a function or a method call)"
            ))

        self.add_style(BlockStyle(
            name="PreparationBlock",
            behaviour_type="BasicBlock",
            element_type="block",
            width=120,
            height=80,
            point_param=20/120,
            render_style="hexagon",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block containing preparations for a future operation, like defining a variable"
            ))

        self.add_style(BlockStyle(
            name="DataBlock",
            behaviour_type="BasicBlock",
            element_type="block",
            width=120,
            height=80,
            point_param=1/4,
            render_style="parallelogram",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block that defines any basic data exchange. for example, returning a value from a function"
            ))

        self.add_style(BlockStyle(
            name="DecisionBlock",
            behaviour_type="DecisionBlock",
            element_type="block",
            width=120,
            height=80,
            render_style="mxgraph.flowchart.decision",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block that defines if and case switch statements"
            ))

        self.add_style(BlockStyle(
            name="WhileBlock",
            behaviour_type="WhileBlock",
            element_type="block",
            width=120,
            height=80,
            render_style="mxgraph.flowchart.decision",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block that defines a while loop"
            ))
    
        self.add_style(BlockStyle(
            name="ForBlock",
            behaviour_type="ForBlock",
            element_type="beginning",
            width=120,
            height=80,
            point_param=20,
            render_style="loopLimit",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block that defines a for loop."
            ))
    
        self.add_style(BlockStyle(
            name="ForBlock",
            behaviour_type="ForBlock",
            element_type="end",
            width=120,
            height=80,
            point_param=20,
            render_style="loopLimit",
            stroke_width=2,
            direction="west",
            font_family=font_family,
            font_source=font_source,
            gpt_desc=""
            ))
    
        self.add_style(BlockStyle(
            name="TerminatorBlock",
            behaviour_type="BasicBlock",
            element_type="block",
            width=120,
            height=40,
            arc_param=120,
            render_style="",
            stroke_width=2,
            font_family=font_family,
            font_source=font_source,
            gpt_desc="a block that defines a termination of the program"
            ))

    def __del__(self):
        self.con.close()

    def get_decriptions(self) -> str:
        self.cur.execute(f"SELECT * from BLOCKS WHERE gpt_desc <> ''")
        rows = self.cur.fetchall()
        L: List[str] = []
        for row in rows:
            L.append(f"{row[1]}: {row[4]}, behaviour: {row[2]}")
        return "\n".join(L)

    def get_styles(self, block_name: str) -> dict[str, BlockStyle]:
        self.cur.execute(f'''SELECT * FROM BLOCKS WHERE name = ?''', (block_name,))
        unformatted_styles = self.cur.fetchall()
        
        style_dict: dict[str, BlockStyle] = {}
        for row in unformatted_styles:
            style_dict[row[3]] = BlockStyle(
                    name=row[1],
                    behaviour_type=row[2],
                    element_type=row[3],
                    gpt_desc=row[4],
                    width=row[5],
                    height=row[6],
                    render_style=row[7],
                    stroke_width=row[8],
                    font_family=row[9],
                    font_source=row[10],
                    direction=row[11],
                    point_param=row[12],
                    arc_param=row[13]
                    )
        return style_dict

    def add_style(self, style: BlockStyle):
        n = style._name
        bt = style._behaviour_type
        et = style._element_type
        gd = style._gpt_desc
        w = style._width
        h = style._height
        r = style._render_style
        s = style._stroke_width
        ff = style._font_family
        fs = style._font_source
        d = style._direction
        pp = style._point_param
        ap = style._arc_param
        self.cur.execute(f'''INSERT INTO BLOCKS (name, behaviour_type, element_type, gpt_desc, width, height, render_style, stroke_width, font_family, font_source, direction, point_param, arc_param) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (n, bt, et, gd, w, h, r, s, ff, fs, d, pp, ap))
        self.con.commit()

    def del_style(self, style_name: str):
        self.cur.execute(f'''DELETE FROM BLOCKS WHERE name = ?''', (style_name,))
        self.con.commit()
    
