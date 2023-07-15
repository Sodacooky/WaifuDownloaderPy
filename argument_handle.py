# 交互式参数输入，只包括标签和页码范围
class InteractiveArgument:
    # 标签
    tags = []
    # 页码范围
    start_page, end_page = -1, -1

    # tags输入
    def input_tags(self):
        input_tags_list = input("输入空格间隔的tags(如: miko bare_shoulders): ").split(" ")
        if len(input_tags_list) < 1 or len(input_tags_list[0]) < 1:
            print("至少应有一个tag。")
            return False
        else:
            self.tags = input_tags_list
            print(f"Tag数量: {len(input_tags_list)}, Tag列表: {input_tags_list}")
            return True

    # 页码范围输入
    def input_page_range(self):
        range_input = list(map(int, input("输入空格间隔的开始和结束页(包括): ").split(" ")))
        if len(range_input) < 1:
            print("不正确的输入。")
            return False
        elif range_input[0] < 1 or range_input[1] < 1:
            print("页码应从1开始。")
            return False
        elif range_input[0] > range_input[1]:
            print("开始页不应大于结束页")
            return False
        else:
            print(f"从页 {range_input[0]} 到页 {range_input[1]}，总共 {range_input[1] - range_input[0] + 1} 页")
            self.start_page, self.end_page = range_input[0], range_input[1]
            return True
