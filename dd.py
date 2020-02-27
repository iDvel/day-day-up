#!/usr/local/bin/python3

from datetime import datetime, timedelta
import pyperclip
from collections import OrderedDict
import matplotlib.pyplot as plt
import sys


class DayDayUp:

    def __init__(self):
        # 开始时间
        self.start = None
        # 结束时间
        self.end = None
        # 学习内容
        self.topic = None

    @property
    def start_str(self):
        return self.start.strftime("%Y-%m-%d %H:%M")

    @property
    def end_str(self):
        return self.end.strftime("%Y-%m-%d %H:%M")

    @property
    def end_str_time_only(self):
        return self.end.strftime("%H:%M")

    def duration(self, t):
        return timedelta(seconds=(t - self.start).seconds)

    def go(self):
        """
        ok: 结束此次学习
        回车：查看时长
        """
        self.start = datetime.now()
        self.topic = input('>>> ')

        print(f'<{self.topic}> 于 {self.start_str} 开始...')

        while True:
            command = input('等待命令...（ok、回车）：').lower().strip()

            if command == '':
                print('已经坚持了', self.duration(datetime.now()))
            elif command == 'ok':
                # 输出信息、拷贝到剪贴板
                self.output()
                # 日常杂项记录不写入，学习时间写入
                if input('是否写入日志？（yes、回车）').lower().strip() == 'yes':
                    # 写入日志
                    self.log()
                    # 总结（条形图）
                    self.sum_up()
                break

    def output(self):
        """
        输出内容: 内容 2020-02-27 11:02 - 2020-02-27 11:17  （已复制到剪贴板）
        改进:     内容 2020-02-27 11:02 - 11:17  （已复制到剪贴板）
        （适应 Fantastical App）
        """
        self.end = datetime.now()
        text = f'{self.topic} {self.start_str} - {self.end_str_time_only}'
        pyperclip.copy(text)
        print('本次时长:', self.duration(self.end))
        print('-' * 50 + '\n' + text + '  （已复制到剪贴板）\n' + '-' * 50)

    def log(self):
        delimiter = ' | '
        record = delimiter.join([self.topic, str(self.duration(self.end)), self.start_str, self.end_str])
        with open('record.txt', 'a') as f:
            f.write(record + '\n')
        print(f'内容 <{record}> 已写入日志。')

    def sum_up(self, show=False):
        # 创建最近 xx 日的字典
        day_dict = OrderedDict()
        for n in range(0, 30):
            key = (datetime.today() - timedelta(days=n)).strftime('%Y-%m-%d')
            day_dict[key] = 0
        # print(day_dict)  # {日期：当日学习时长, 日期：当日学习时长, 日期：当日学习时长 。。。}

        # 暴力遍历日志，统计时长
        with open('record.txt', 'r') as f:
            for line in f.readlines():
                # 拿到每一行的日期、时长，加入字典的value
                line = line.split(' | ')  # ['测试', '1:23:45', '2020-02-08 23:10', '2020-02-08 23:10\n']
                day = line[2][:10]  # '2020-02-08'
                if day in day_dict:
                    # 把 <时：分：秒> 转化成 <X.X小时>
                    duration = line[1].split(':')  # ['1', '23', '45'] 时分秒
                    duration = [int(x) for x in duration]  # [1, 23, 45]
                    minute = duration[1] + duration[2] / 60
                    hour = duration[0] + minute / 60
                    # 更新字典值
                    day_dict[day] += hour

        if show:
            for k, v in reversed(day_dict.items()):
                print(f'{k} → {v:.1f} 小时')

        # 条形图
        title = []
        data = []
        for k, v in day_dict.items():
            title.append(k)
            data.append(v)
        plt.title = '这个参数有用吗？？？'
        plt.barh(title, data)
        plt.show()


if __name__ == '__main__':
    dd = DayDayUp()
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'log':
            dd.sum_up(show=True)
        else:
            print('只支持 <log> 命令')
            sys.exit()
    else:
        dd.go()
