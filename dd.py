import sys
import os
from datetime import datetime, timedelta
from collections import OrderedDict

import pyperclip
import matplotlib.pyplot as plt


class DayDayUp:
    DELIMITER = ' | '

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

    @property
    def log_path(self):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'record.txt')

    def duration(self, t):
        return timedelta(seconds=(t - self.start).seconds)

    def go(self):
        """
        ok: 结束此次学习
        回车：查看时长
        """
        self.start = datetime.now()
        print(f'内容 <{self.topic}> 于 {self.start_str} 开始...')

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
        record = self.DELIMITER.join([self.topic, str(self.duration(self.end)), self.start_str, self.end_str])
        with open(self.log_path, 'a') as f:
            f.write(record + '\n')
        print(f'内容 <{record}> 已写入日志。')

    def sum_up(self, show=False):
        # 创建最近30日的字典
        day_dict = OrderedDict()
        for n in range(0, 30):
            key = (datetime.today() - timedelta(days=n)).strftime('%Y-%m-%d')
            day_dict[key] = 0
        # print(day_dict)  # {日期：当日学习时长, 日期：当日学习时长, 日期：当日学习时长 。。。}

        # 暴力遍历日志，统计时长
        with open(self.log_path) as f:
            for line in f.readlines():
                # 拿到每一行的日期、时长，加入字典的value
                line = line.split(self.DELIMITER)  # ['测试', '1:23:45', '2020-02-08 23:10', '2020-02-08 23:10\n']
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

    def query_project_duration(self):
        """ 查询同名的项目所用的总时间，比如看了一本书一共用了多久 """
        # dq：列出所有项目列表，最近的排在最下面，前面标注编号
        projects = OrderedDict()  # {'project1': 3小时, 'project2': 6小时 ...}
        with open(self.log_path) as f:
            number = 1
            for line in f.readlines():
                key = line.split(self.DELIMITER)[0]
                if key not in projects:
                    projects[key] = 0
            # print(projects) # OrderedDict([('content', 0), ('content', 0), ('content', 0), ... ])

        id = OrderedDict()
        i = 1
        for key in projects:
            id[str(i)] = key
            i += 1
        # print(id) # {1: 'content', 2: 'content', 3: 'content' ... }

        for number, project in id.items():
            print(f'{number}\t→ {project}')

        # 输入查询命令，如 3，查询编号3的项目的有史以来的总时长
        project_number = input('输入查询命令，number-[days]:')
        project_name = id[project_number]

        with open(self.log_path) as f:
            for line in f.readlines():
                line = line.split(self.DELIMITER)  # ['测试', '1:23:45', '2020-02-08 23:10', '2020-02-08 23:10\n']
                if line[0] == project_name:
                    # 把 <时：分：秒> 转化成 <X.X小时>
                    duration = line[1].split(':')  # ['1', '23', '45'] 时分秒
                    duration = [int(x) for x in duration]  # [1, 23, 45]
                    minute = duration[1] + duration[2] / 60
                    hour = duration[0] + minute / 60
                    # 更新字典值
                    projects[project_name] += hour
        print(f'<{project_name}> 一共用时 {projects[project_name]:.1f} 小时')

    def change_last_record_content(self, t):
        """ 修改最新的一条记录的内容 """
        import re
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            content = lines[:-1]
            old = lines[-1]
        with open(self.log_path, 'w') as f:
            f.writelines(content)
            new = re.sub(r'(.*?)[\s]{1}[\|]{1}[\s]{1}', t + self.DELIMITER, old, 1)
            f.write(new)
        print(old, end='')
        print('↓ ↓ ↓ 修改成功 ↓ ↓ ↓'.center(len(new)))
        print(new, end='')


def main():
    # alias dd = "python /.../dd.py"
    # alias dl = "python /.../dd.py log"
    # alias da = "python /.../dd.py alter"
    # alias dq = "python /.../dd.py query"
    dd = DayDayUp()
    if len(sys.argv) == 2:
        if sys.argv[1].lower() == 'log':
            dd.sum_up(show=True)
        elif sys.argv[1].lower() == 'alter':
            print('请输入参数')
        elif sys.argv[1].lower() == 'alter':
            dd.change_last_record_content(' '.join(sys.argv[2:]))
        elif sys.argv[1].lower() == 'query':
            pass
        else:
            dd.topic = ' '.join(sys.argv[1:])
            dd.go()
    else:
        print("""\
    Usage:
      dd <content>   开始新的学习内容
      dl             查询学习时长
      da <content>   修改最近的一次提交内容为 content""")


if __name__ == '__main__':
    main()
