import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from math import *

pcbs = []
pcb = {"name":"Default","pc":0,"sp":0,"state":"None","pid":0,"text":[],"data":{},"stack":[],"scheduling":{"arrival":float("inf"),"executed":float("inf"),"chain":float("inf")}}
pcbi = -1
process_selected = -1
instruction = ":"

pids = []
pid_max = 0

t = 0
quantum = 3

def create_process(f):
    global pid_max,pcbs
    p = {}
    pid_max += 1
    p["state"] = "new"
    p["name"] = f
    p["pid"] = pid_max
    p["pc"] = 0
    p["sp"] = 0
    p["data"] = {}
    p["text"] = []
    p["stack"] = []
    p["scheduling"] = {"arrival":t,"executed":0,"chain":0}
    pcbs.append(p)
    __process_update__()
    
def __process_switch__(i):
    global pcb,pcbi
    if pcb["state"]!="terminated":
        pcb["state"] = "ready"
    pcbi = i
    pcb = pcbs[pcbi]
    if pcb["state"]!="terminated":
        pcb["state"] = "running"
    pcb["scheduling"]["chain"] = 0
    __process_update__()

def var(name,value=None):
    if value!=None:
        pcb["data"][name] = value
    return pcb["data"][name]

def jmp(label,condition=True):
    if condition:
        pcb["pc"] = pcb["data"][label]

def call(label):
    pcb["stack"].append(pcb["pc"])
    pcb["pc"] = pcb["data"][label]
    pcb["sp"]+=1

def ret():
    pc = pcb["stack"].pop()
    pcb["pc"] = pc
    pcb["sp"]-=1

def push(value):
    pcb["stack"].append(value)
    pcb["sp"]+=1
    return value

def pop():
    pcb["sp"]-=1
    return pcb["stack"].pop()

def output(*value,sep=' ',end="\n"):
    output_text["state"] = "normal"
    for v in value[:-1]:
        output_text.insert("end",str(v)+sep)
    output_text.insert("end",str(value[-1])+end)
    output_text["state"] = "disabled"

def __load_process__(i):
    global pcb
    p = pcbs[i]
    fn = p["name"]
    f = open(fn)
    contents = f.read()
    f.close()
    lines = contents.splitlines()
    i = 0
    while i<len(lines):
        line = lines[i].strip()
        if line.endswith(':'):
            p["data"][line[:-1]] = i
        if line!="":
            i+=1
        else:
            lines.pop(i)
    p["text"] = lines
    p["state"] = "ready"
    __process_update__()
    

def __step__():
    global t,instruction,pcb
    t+=1
    instruction = ":"
    while instruction.endswith(':') and pcb["pc"]<len(pcb["text"]):
        instruction = pcb["text"][pcb["pc"]].strip()
        pcb["pc"]+=1
    if pcb["pc"] > len(pcb["text"]) or instruction.endswith(':'):
        pcb["state"] = "terminated"
        __process_update__()
        return None
    #print(instruction,pcb["pc"])
    eval(instruction)
    #print(instruction,pcb["pc"])
    pcb["scheduling"]["executed"] += 1
    pcb["scheduling"]["chain"] += 1
    if pcb["pc"] >= len(pcb["text"]):
        pcb["state"] = "terminated"
    __process_update__()

def __fcfs__():
    global pcbi,pcb
    if pid_max == 0:
        messagebox.showerror("Processes","No processes")
        return None
    min_arrival = float("inf")
    pi = None
    new_processes = False
    for i,p in enumerate(pcbs):
        if p["state"] == "new":
            __load_process__(i)
            new_processes = True
        if p["state"] != "terminated":
            if p["scheduling"]["arrival"]<min_arrival:
                pi = i
                min_arrival = p["scheduling"]["arrival"]
    if new_processes:
        return None
    if pi==None:
        messagebox.showerror("Processes","All processes terminated")
        return None
    if pcbi!=pi:
        __process_switch__(pi)
    pcbi = pi
    pcb = pcbs[pi]
    __step__()

def __rr__():
    global pcbi,pcb
    if pid_max == 0:
        messagebox.showerror("Processes","No processes")
        return None
    new_processes = False
    for i,p in enumerate(pcbs):
        if p["state"]=='new':
            __load_process__(i)
            new_processes = True
    if new_processes:
        return None
    if pcbi==-1 or pcb["scheduling"]["chain"]>=quantum or pcb["state"]=='terminated':
        state = "terminated"
        count = 0
        i = pcbi
        while state=="terminated":
            i = (i+1)%pid_max
            state = pcbs[i]["state"]
            count+=1
            if count>pid_max:
                messagebox.showerror("Processes","All processes terminated")
                return None
        __process_switch__(i)
    __step__()


running = True 
root = tk.Tk()
root.title("Processes")
root.geometry("500x500")
def __root_close__():
    global running
    root.destroy()
    running = False
root.protocol("WM_DELETE_WINDOW",__root_close__)

pcb_f = tk.Frame(root)
pcb_name_label = tk.Label(pcb_f,text="Name")
pcb_name_label.grid(row=1,column=1)
pcb_name = tk.Label(pcb_f,text="")
pcb_name.grid(row=1,column=2)
pcb_state_label = tk.Label(pcb_f,text="State")
pcb_state_label.grid(row=2,column=1)
pcb_state = tk.Label(pcb_f,text="")
pcb_state.grid(row=2,column=2)
pcb_pid_label = tk.Label(pcb_f,text="PID")
pcb_pid_label.grid(row=3,column=1)
pcb_pid = tk.Label(pcb_f,text="")
pcb_pid.grid(row=3,column=2)
pcb_arrival_label = tk.Label(pcb_f,text="Arrival")
pcb_arrival_label.grid(row=4,column=1)
pcb_arrival = tk.Label(pcb_f,text="")
pcb_arrival.grid(row=4,column=2)
pcb_executed_label = tk.Label(pcb_f,text="Executed")
pcb_executed_label.grid(row=5,column=1)
pcb_executed = tk.Label(pcb_f,text="")
pcb_executed.grid(row=5,column=2)
pcb_chain_label = tk.Label(pcb_f,text="Chain")
pcb_chain_label.grid(row=6,column=1)
pcb_chain = tk.Label(pcb_f,text="")
pcb_chain.grid(row=6,column=2)
pcb_pc_label = tk.Label(pcb_f,text="PC")
pcb_pc_label.grid(row=7,column=1)
pcb_pc = tk.Label(pcb_f,text="")
pcb_pc.grid(row=7,column=2)
pcb_sp_label = tk.Label(pcb_f,text="SP")
pcb_sp_label.grid(row=8,column=1)
pcb_sp = tk.Label(pcb_f,text="")
pcb_sp.grid(row=8,column=2)
pcb_instruction_label = tk.Label(pcb_f,text="Instruction")
pcb_instruction_label.grid(row=9,column=1)
pcb_instruction = tk.Label(pcb_f,text="")
pcb_instruction.grid(row=9,column=2)
pcb_f.pack()

processes_window = tk.Toplevel(root)
processes_window.geometry("500x500")
processes_window.title("Processes")
processes_window.withdraw()
def __processes_window_close__():
    processes_window.withdraw()
processes_window.protocol("WM_DELETE_WINDOW",__processes_window_close__)

selected_window = tk.Toplevel(root)
selected_window.geometry("500x500")
selected_window.title("Processes")
sel_text = tk.Text(selected_window)
sel_text["state"] = "disabled"
sel_text.grid(row=1,column=1)
sel_data = tk.Text(selected_window)
sel_data["state"] = "disabled"
sel_data.grid(row=2,column=1)
sel_stack = tk.Text(selected_window)
sel_stack["state"] = "disabled"
sel_stack.grid(row=2,column=2)
sel_info = tk.Frame(selected_window)
sel_name_label = tk.Label(sel_info,text="Name")
sel_name_label.grid(row=1,column=1)
sel_name = tk.Label(sel_info,text="")
sel_name.grid(row=1,column=2)
sel_state_label = tk.Label(sel_info,text="State")
sel_state_label.grid(row=2,column=1)
sel_state = tk.Label(sel_info,text="")
sel_state.grid(row=2,column=2)
sel_pid_label = tk.Label(sel_info,text="PID")
sel_pid_label.grid(row=3,column=1)
sel_pid = tk.Label(sel_info,text="")
sel_pid.grid(row=3,column=2)
sel_arrival_label = tk.Label(sel_info,text="Arrival")
sel_arrival_label.grid(row=4,column=1)
sel_arrival = tk.Label(sel_info,text="")
sel_arrival.grid(row=4,column=2)
sel_executed_label = tk.Label(sel_info,text="Executed")
sel_executed_label.grid(row=5,column=1)
sel_executed = tk.Label(sel_info,text="")
sel_executed.grid(row=5,column=2)
sel_chain_label = tk.Label(sel_info,text="Chain")
sel_chain_label.grid(row=6,column=1)
sel_chain = tk.Label(sel_info,text="")
sel_chain.grid(row=6,column=2)
sel_pc_label = tk.Label(sel_info,text="PC")
sel_pc_label.grid(row=7,column=1)
sel_pc = tk.Label(sel_info,text="")
sel_pc.grid(row=7,column=2)
sel_sp_label = tk.Label(sel_info,text="SP")
sel_sp_label.grid(row=8,column=1)
sel_sp = tk.Label(sel_info,text="")
sel_sp.grid(row=8,column=2)
sel_info.grid(row=1,column=2)
selected_window.withdraw()
def __selected_window_close__():
    selected_window.withdraw()
selected_window.protocol("WM_DELETE_WINDOW",__selected_window_close__)

output_window = tk.Toplevel(root)
output_window.geometry("500x500")
output_window.title("Output")
output_text = tk.Text(output_window)
output_text["state"] = "disabled"
output_text.pack()
output_window.withdraw()
def __output_window_close__():
    output_window.withdraw()
output_window.protocol("WM_DELETE_WINDOW",__output_window_close__)


f = tk.Frame(processes_window)
f.pack()
def __process_update__():
            global process_selected,pcb,pcbi,f
            sel = process_selected
            f.destroy()
            f = tk.Frame(processes_window)
            pid_column_label = tk.Label(f,text="PID")
            pid_column_label.grid(row=1,column=1)
            name_column_label = tk.Label(f,text="Name")
            name_column_label.grid(row=1,column=2)
            state_column_label = tk.Label(f,text="State")
            state_column_label.grid(row=1,column=3)
            select_column_label = tk.Label(f,text="Show")
            select_column_label.grid(row=1,column=4)
            for i,p in enumerate(pcbs):
                #print(pcb["name"])
                pid_label = tk.Label(f,text=str(p["pid"]))
                pid_label.grid(row=i+2,column=1)
                name_label = tk.Label(f,text=p["name"])
                name_label.grid(row=i+2,column=2)
                state_label = tk.Label(f,text=p["state"])
                state_label.grid(row=i+2,column=3)
                select_label = tk.Button(f,text="Select")
                select_label.grid(row=i+2,column=4)
                def proc_sel(i):
                    def select():
                        global process_selected
                        process_selected = i
                        __process_update__()
                        selected_window.deiconify()
                        #print(i)
                    return select
                select_label["command"] = proc_sel(i)
            f.pack()
            pcb_name["text"] = pcb["name"]
            pcb_state["text"] = pcb["state"]
            pcb_pid["text"] = str(pcb["pid"])
            pcb_pc["text"] = str(pcb["pc"])
            pcb_sp["text"] = str(pcb["sp"])
            pcb_arrival["text"] = str(pcb["scheduling"]["arrival"])
            pcb_executed["text"] = str(pcb["scheduling"]["executed"])
            pcb_chain["text"] = str(pcb["scheduling"]["chain"])
            pcb_instruction["text"] = instruction

            if sel!=-1:
                p = pcbs[sel]
                #print(p)
                sel_text['state'] = 'normal'
                sel_text.delete('1.0','end')
                sel_text.insert('end',"Text:\n\n")
                if p["state"] == "new":
                    sel_text.insert('end','Not Loaded')
                for i,line in enumerate(p["text"]):
                    sel_text.insert('end',str(i)+"\t"+line+"\n")
                i2 = p["pc"]
                while i2<len(p["text"]) and p["text"][i2].endswith(":"):
                    i2+=1
                sel_text.tag_add("pc",str(p["pc"]+3)+'.0',str(i2+3)+'.end')
                sel_text.tag_config("pc",background="yellow",foreground="black")
                sel_text['state'] = 'disabled'
                sel_data['state'] = 'normal'
                sel_data.delete('1.0','end')
                sel_data.insert('end',"Data size: "+str(len(p["data"].keys()))+"\n\n")
                for k,v in p["data"].items():
                    sel_data.insert('end',k.ljust(20,' ')+str(v)+'\n')
                sel_data['state'] = 'disabled'
                sel_stack['state'] = 'normal'
                sel_stack.delete('1.0','end')
                sel_stack.insert('end',"Stack size: "+str(len(p["stack"]))+"\n\n")
                for i,v in enumerate(p["stack"]):
                    sel_stack.insert('end',str(i)+"\t"+str(v)+"\n")
                sel_stack['state'] = 'disabled'
                sel_name["text"] = p["name"]
                sel_state["text"] = p["state"]
                sel_pid["text"] = str(p["pid"])
                sel_pc["text"] = str(p["pc"])
                sel_sp["text"] = str(p["sp"])
                sel_arrival["text"] = str(p["scheduling"]["arrival"])
                sel_executed["text"] = str(p["scheduling"]["executed"])
                sel_chain["text"] = str(p["scheduling"]["chain"])
__process_update__()

menu = tk.Menu(root)
load_menu = tk.Menu(menu,tearoff=0)
def __load_file__():
    f = filedialog.askopenfilename()
    if f!='':
        create_process(f)
load_menu.add_command(label="File",command=__load_file__)
menu.add_cascade(label="Load",menu=load_menu)
view_menu = tk.Menu(root,tearoff=0)
def __processes__():
    processes_window.deiconify()
view_menu.add_command(label="Processes",command=__processes__)
def __selected_process__():
    selected_window.deiconify()
view_menu.add_command(label="Selected Process",command=__selected_process__)
def __output__():
    output_window.deiconify()
view_menu.add_command(label="Output",command=__output__)

menu.add_cascade(label="View",menu=view_menu)
step_f = tk.Frame(root)
step_label = tk.Label(step_f,text="Step")
step_label.grid(row=1,column=1)
fcfs_button = tk.Button(step_f,text="First Come First Serve")
fcfs_button.grid(row=1,column=2)
fcfs_button["command"] = __fcfs__
rr_button = tk.Button(step_f,text="Round Robin")
rr_button.grid(row=1,column=3)
rr_button["command"] = __rr__
step_f.pack()
root["menu"] = menu

root.mainloop()
