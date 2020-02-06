#!/usr/bin/env python3

from datetime import datetime, timedelta
import time
import sys
import pyperclip
import matplotlib.pyplot as plt


class CalendarCreater:

    def __init__(self):
        self.start = None
        self.end = None
        self.topic = None
        # 辅助命令，查询近日时长 #TODO
        # if len(sys.argv) > 1:
        #     self.topic = ' '.join(sys.argv[1:])

    @property
    def start_str(self):
        return self.start.strftime("%Y-%m-%d %H:%M")

    @property
    def end_str(self):
        return self.end.strftime("%Y-%m-%d %H:%M")

    def go(self):
        """
        ok: 正常结束记录
        end: 特殊结束，附加 * 标志
        直接回车: 查看时长
        """
        self.start = datetime.now()
        self.topic = input(">>> ")
        print(f"内容：<{self.topic}>")
        print(f"{self.start_str} 开始")

        while True:
            command = input("等待命令（ok, end, 回车）：").lower().strip()
            if command == '':
                self.print_how_long()
            elif command == 'ok' or command == 'end':
                # 组合 str
                self.end = datetime.now()
                how_long = timedelta(seconds=(self.end - self.start).seconds)
                result = f'{self.topic} {self.start_str} - {self.end_str}'

                # 复制到剪贴板
                if command == 'ok':
                    pyperclip.copy(result)

                # 确认结束，输出总结
                self.print_how_long(end='')
                s = input('（结束请按回车，取消输入任意字符）：')
                if s == '':
                    print("-" * 20)
                    print(f"坚持了 {how_long}")
                    print("-" * 20)
                    print(result + "（已复制到剪贴板）")
                    print("-" * 20)
                    # 记录日志
                    self.log(command, how_long)
                    # 总结
                    self.sum_up()
                    break
            else:
                pass

    def print_how_long(self, end='\n'):
        print('已经过了', timedelta(seconds=(datetime.now() - self.start).seconds), end=end)

    def log(self, command, how_long):
        """ 记录日志 """
        delimiter = ' | '
        arr = [self.topic, str(how_long), self.start_str, self.end_str]
        if command == 'end':
            arr.insert(0, '*')
        with open('record.txt', 'a') as f:
            record = delimiter.join(arr)
            f.write(record + '\n')
            print(f'以下内容已写入日志：\n{record}\n' + '-' * 20)

    def sum_up(self):
        """ 30日时长总结（遍历日志方法写的太垃圾，待改善） """
        # 拿到最近七天的列表
        seven_days = []
        today = datetime.today()
        for delta in range(-29, 1): # -6 是最近七日   -29 是最近30日
            day_str = (today + timedelta(days=delta)).strftime('%Y-%m-%d')
            seven_days.append({day_str: timedelta(0)})
        # print(seven_days)  # [{'2020-01-31': None}, {'2020-02-01': None}, ...]

        # 遍历整个日志，拿到一个符合的，就在字典里相加
        with open('record.txt', 'r') as f:
            for line in f.readlines():
                line = line.split(' | ')
                if line[0].strip() != '*':
                    # print(line)
                    log_date = line[2].split(' ')[0]  # 2020-02-06
                    for day in seven_days:
                        for k, v in day.items():
                            if k == log_date:
                                time_list = line[1].split(':')
                                time_list = [int(x) for x in time_list]
                                day[k] = v + timedelta(hours=time_list[0], minutes=time_list[1], seconds=time_list[2])

        # 输出总结  （1:30约等于1.5小时）
        print('最近 30 日学习时长：')
        for day in seven_days:
            for k, v in day.items():
                v = str(v).split(':')
                v = [int(x) for x in v]
                if v[2] > 30:
                    v[1] += 1
                v = v[0] + v[1] / 60
                print(f'{k} → {v:.1f} 小时')
                # 直接转换成小时，供柱状图使用
                day[k] = v

        # print(seven_days)

        # 柱状图
        title = []
        data = []
        for day in reversed(seven_days):
            for k, v in day.items():
                title.append(k)
                data.append(v)
        plt.barh(title, data)
        plt.show()


if __name__ == '__main__':
    cc = CalendarCreater()
    cc.go()
