from datetime import datetime, timedelta
import sys

import pyperclip


class DayDayUp():

    def __init__(self):
        # 学习内容
        self.content = None
        # 开始时间
        self.start = None
        # 结束时间
        self.end = None
        # 学习时长（x.xx小时）两位小数
        self.duration = None

    def go(self):
        """ 启动。ok: 结束此次学习。 回车：查看持续时长 """

        self.start = datetime.now().replace(microsecond=0)
        print(f'内容 <{self.content}> 于 {self.start} 开始...')

        while True:
            command = input('等待命令...（ok、回车）：').lower().strip()
            if command == '':
                print(f'已经坚持了 {datetime.now().replace(microsecond=0) - self.start}')
            elif command == 'ok':
                # 输出信息、拷贝到剪贴板
                self.output()
                # 日常杂项临时记录的记录，回车不写入。学习时间yes写入
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
        self.end = datetime.now().replace(microsecond=0)
        text = f'{self.content} {self.start} - {self.end.time()}'
        pyperclip.copy(text)
        print('-' * 50)
        print('本次时长:', self.end - self.start)
        print('-' * 50 + '\n' + text + '  （已复制到剪贴板）\n' + '-' * 50)


def main():
    # 用终端启动：
    # alias dd = "python /.../dd.py"
    # alias dl = "python /.../dd.py log"
    # alias dq = "python /.../dd.py query"

    dd = DayDayUp()

    # argv = ['dd']
    argv = ['dd', '测试']

    if len(argv) == 1 and argv[0] == 'dd':
        print("""\
Usage:
  dd <content>   开始新的学习内容
  dl [days]      默认查询最近30日学习时长
  dq             查询每个项目的总时长""")
    elif len(argv) == 1 and argv[0] == 'dl':
        pass
    elif len(argv) == 1 and [0] == 'dq':
        pass
    else:
        dd.content = ' '.join(argv[1:])
        dd.go()


if __name__ == '__main__':
    main()
