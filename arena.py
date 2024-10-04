import tkinter as tk
import textwrap
import pandas as pd
import random

CELL_WIDTH = 80
N_SCENARIO = 23

scenario_idx = 0
report = {
    1: [0] * N_SCENARIO,
    2: [0] * N_SCENARIO,
}

A_is_1 = False

def wrap_text(text, role="User"):
    if role == "User":
        return textwrap.fill(text, CELL_WIDTH, initial_indent="User:  ", subsequent_indent="       ")
    elif role == "Agent":
        return textwrap.fill(text, CELL_WIDTH, initial_indent="Agent: ", subsequent_indent="       ")
    else:
        return ""

def get_data_from_csv(file_path1, file_path2):
    df1 = pd.read_csv(file_path1)
    df2 = pd.read_csv(file_path2)

    data1 = []
    data2 = []

    for _, row in df1.iterrows():
        user_say = wrap_text(row['person_say'], role="User")
        agent_say = wrap_text(row['animal_say'], role="Agent")
        data1.append([user_say, agent_say])
    for _, row in df2.iterrows():
        user_say = wrap_text(row['person_say'], role="User")
        agent_say = wrap_text(row['animal_say'], role="Agent")
        data2.append([user_say, agent_say])
    
    data = []
    if len(data1) > len(data2):
        data2 += [["", ""] for _ in range(len(data1) - len(data2))]
    else:
        data1 += [["", ""] for _ in range(len(data2) - len(data1))]
        
    for i in range(max(len(data1), len(data2))):
        data.append([data1[i][0], data2[i][0]])
        data.append([data1[i][1], data2[i][1]])

    return data

def get_all_data(dir1, dir2, N:int):
    data_list = []
    for i in range(N):
        file_path1 = f"./report/Sparky/{dir1}/report_sparky_{i+1}.csv"
        file_path2 = f"./report/Sparky/{dir2}/report_sparky_{i+1}.csv"
        data = get_data_from_csv(file_path1, file_path2)
        data_list.append(data)
    return data_list

data_list = get_all_data('V0_0929_02', 'V0_0924_02', N_SCENARIO)

def get_data():
    return data_list[scenario_idx]

def on_submit(result, result_label):
    result_label.config(text=f"Result: {result}")
    if result > 2:
        report[1][scenario_idx] = result
        report[2][scenario_idx] = result
    else:
        if A_is_1:
            report[1][scenario_idx] = result
            report[2][scenario_idx] = 3 - result 
        else:
            report[2][scenario_idx] = result
            report[1][scenario_idx] = 3 - result

def on_next_clicked(frame):
    global scenario_idx
    global A_is_1
    scenario_idx = (scenario_idx + 1) % N_SCENARIO
    refresh_table(frame)
    A_is_1 = random.randint(0, 1) == 0   

def on_prev_clicked(frame):
    global scenario_idx
    global A_is_1
    scenario_idx = (scenario_idx - 1) % N_SCENARIO
    refresh_table(frame)
    A_is_1 = random.randint(0, 1) == 0

def refresh_table(scrollable_frame):
    # 清除现有的表格内容
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # 重新生成表头
    header_A = tk.Label(scrollable_frame, text="A", font=("Monaco", 16, "bold"), width=CELL_WIDTH, borderwidth=1, relief="solid")
    header_B = tk.Label(scrollable_frame, text="B", font=("Monaco", 16, "bold"), width=CELL_WIDTH, borderwidth=1, relief="solid")
    header_A.grid(row=0, column=0)
    header_B.grid(row=0, column=1)

    # 获取新的数据
    data = get_data()

    # 重新生成表格内容
    for row_index, row_data in enumerate(data, start=1):
        cell = tk.Label(scrollable_frame, text=row_data[0], width=CELL_WIDTH+7, borderwidth=1, relief="solid", anchor="w", justify="left", font=("Monaco", 14))
        cell.grid(row=row_index, column=0 if A_is_1 else 1, sticky="w")

        cell = tk.Label(scrollable_frame, text=row_data[1], width=CELL_WIDTH+7, borderwidth=1, relief="solid", anchor="w", justify="left", font=("Monaco", 14))
        cell.grid(row=row_index, column=1 if A_is_1 else 0, sticky="w")

def display_interface(col_width=40):
    root = tk.Tk()
    root.title("Agent Arena")
    root.geometry("1000x700")  # 设置窗口大小

    # 设置列宽
    cell_width = col_width

    # 创建包含 Canvas 的框架
    outer_frame = tk.Frame(root)
    outer_frame.pack(fill=tk.BOTH, expand=True)

    # 创建 Canvas 以支持滚动
    canvas = tk.Canvas(outer_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 创建滚动条
    scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    # 创建一个框架，在其中放置可滚动的内容
    scrollable_frame = tk.Frame(canvas)

    # 当 scrollable_frame 的大小发生变化时，更新 Canvas 的 scrollregion
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # 在 Canvas 中创建一个窗口来显示 scrollable_frame，初始位置设为中心
    window_id = canvas.create_window((canvas.winfo_width() // 2, 0), window=scrollable_frame, anchor="n")

    # 动态更新 Canvas 中窗口的位置
    def update_canvas_position(event):
        canvas_width = event.width
        canvas.coords(window_id, canvas_width // 2, 0)

    # 绑定 Canvas 大小变化事件
    canvas.bind("<Configure>", update_canvas_position)

    # 初始化表格内容
    refresh_table(scrollable_frame)

    # 将 Canvas 和滚动条连接
    canvas.configure(yscrollcommand=scrollbar.set)

    # 选项按钮部分
    button_frame = tk.Frame(root)
    button_frame.pack(side="bottom", pady=10)

    result_label = tk.Label(root, text="Result: ", font=("Monaco", 12))

    # 创建四个按钮，使用 grid 布局让每个按钮在一个独立的列中，并设定相同的宽度
    btn1 = tk.Button(button_frame, text="1. A is Better", command=lambda: on_submit(1, result_label), width=cell_width // 2, font=("Monaco", 12))
    btn2 = tk.Button(button_frame, text="2. B is Better", command=lambda: on_submit(2, result_label), width=cell_width // 2, font=("Monaco", 12))
    btn3 = tk.Button(button_frame, text="3. Tie", command=lambda: on_submit(3, result_label), width=cell_width // 2, font=("Monaco", 12))
    btn4 = tk.Button(button_frame, text="4. Both are Bad", command=lambda: on_submit(4, result_label), width=cell_width // 2, font=("Monaco", 12))

    btn1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    btn2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    btn3.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
    btn4.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    # 让按钮在水平方向上等宽
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_columnconfigure(3, weight=1)

    # 显示结果
    result_label.pack(side="bottom", pady=10)

    # 控制按钮部分
    control_frame = tk.Frame(root)
    control_frame.pack(side="bottom", pady=10)

    btn_prev = tk.Button(control_frame, text="prev", command=lambda: on_prev_clicked(scrollable_frame), width=cell_width // 2, font=("Monaco", 12))
    btn_next = tk.Button(control_frame, text="next", command=lambda: on_next_clicked(scrollable_frame), width=cell_width // 2, font=("Monaco", 12))
  
    btn_prev.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    btn_next.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    control_frame.grid_columnconfigure(0, weight=1)
    control_frame.grid_columnconfigure(1, weight=1)
    def on_close():
        print(report[1])
        print(report[2])
        root.destroy() 
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()

# 运行界面，传入不同的列宽度
display_interface(col_width=CELL_WIDTH)