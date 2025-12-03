from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Button, TextArea
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from uvm_asm import full_asm
from uvm_interp import execute

DEMO = """load_const;100;5
read_value;5;10
write_value;10;15
unar_minus;5;20"""

TEMPLATE = """stack: %s
memory: %s
bytecode: %s"""

class UVMApp(App):
    CSS = """Screen {
    align: center middle;
    background: #1e1e1e;
}
TextArea {
    width: 90%;
    height: 40%;
    border: solid #404040;
    margin: 1;
}
Button {
    width: 20;
    height: 3;
    background: #0078d4;
    color: white;
    margin: 1;
}
#output {
    height: 40%;
}"""

    def compose(self) -> ComposeResult:
        yield TextArea(text=DEMO, id="input", language="text")
        yield Button(label="Запустить", id="main", variant="primary")
        yield TextArea(id="output", text="Результат появится здесь...", language="text")

    @on(Button.Pressed, "#main")
    def click(self) -> None:
        try:
            program = self.query_one("#input").text
            if not program.strip():
                self.query_one("#output").text = "Ошибка: программа пустая!"
                return
            bytecode, IR = full_asm(program)
            textcode = " ".join([hex(i) for i in bytecode])
            stack, memory = execute(bytecode)
            stack_str = str(stack)
            memory_str = str(memory[:32])
            self.query_one("#output").text = TEMPLATE % (stack_str, memory_str, textcode)
        except Exception as e:
            self.query_one("#output").text = f"Ошибка: {str(e)}"

if __name__ == "__main__":
    app = UVMApp()
    app.run()


#1 py uvm_asm.py -i emu-program.json -o output.bin -t 1
#2 py uvm_asm.py -i emu-program.json -o stage2.bin -t 0
#2 dir stage2.bin
#3 py uvm_asm.py -i array_copy.json -o array_copy.bin -t 0
#3 py uvm_interp.py -i array_copy.bin -o array_dump.xml -r "0-30"
#4 py uvm_asm.py -i test_negation.json -o negation.bin -t 0
#4 py uvm_interp.py -i negation.bin -o neg_dump.xml -r "0-10"
#5 py uvm_asm.py -i emu-program.json -o vector9.bin -t 0
#5 py uvm_interp.py -i vector9.bin -o vector_result.xml -r "0-8"
#5 py uvm_asm.py -i test1.json -o test1.bin -t 0
#5 py uvm_interp.py -i test1.bin -o test1.xml -r "0-15"
#5 py uvm_asm.py -i test2.json -o test2.bin -t 0
#5 py uvm_interp.py -i test2.bin -o test2.xml -r "0-15"
#5 py uvm_asm.py -i test3.json -o test3.bin -t 0
#5 py uvm_interp.py -i test3.bin -o test3.xml -r "0-15"
#6 pip install textual
#6 py uvm_ui.py
