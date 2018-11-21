# coding=utf-8

'''
Systrace file cannot open when size more than 300MB when you put it into chrome.
you should cut the big size file into some sub files which can be ok for chrome.
this module will do that for you
'''
import argparse
import io
import os
from collections import OrderedDict

OVERFLOW_SIZE_MB = 50  # MB
FLAG_TRACE_BEGIN = "tracer: nop"
FLAG_TRACE_TAIL_INFO = (
    u"""
      </script>
<!-- END TRACE -->
</body>
</html>
    """
)


def get_file_size(path):
    if not os.path.exists(path):
        raise Exception(path, "is not exist !!")
    size = os.path.getsize(path)
    print(path, "size: ", size, "Byte")
    return size


class SimpleSpliter(object):
    def __init__(self, threshold_size, file_path):
        self.file_path = file_path
        self.total_size_byte = get_file_size(file_path)
        self.threshold_size_byte = threshold_size
        self.new_file_dir = OrderedDict()
        self.head_info_list = []
        self.head_info_size_byte = 0
        self.cache_head_done = False

    def init_new_file_list(self):
        file_folder_path = os.path.abspath(os.path.dirname(self.file_path))
        file_base_name = os.path.basename(self.file_path)
        file_order = 0
        total_size = self.total_size_byte
        while total_size > 0:
            file_order += 1
            new_file_path = self.build_new_file_path(file_folder_path,
                                                     file_order, file_base_name)
            if total_size > self.threshold_size_byte:
                self.new_file_dir[new_file_path] = self.threshold_size_byte
            else:
                self.new_file_dir[new_file_path] = total_size
            total_size -= self.threshold_size_byte

    @staticmethod
    def build_new_file_path(file_folder_path, file_order, file_base_name):
        prefix_name, suffix_name = os.path.splitext(file_base_name)
        return os.path.join(file_folder_path,
                            "".join([prefix_name, "_{}".format(file_order), suffix_name]))

    def cache_head_info(self, line):
        if FLAG_TRACE_BEGIN in line.lower():
            self.head_info_list.append(line)
            self.cache_head_done = True
        if not self.cache_head_done:
            self.head_info_list.append(line)
            self.head_info_size_byte += len(line)

    def main(self):
        if self.total_size_byte < self.threshold_size_byte:
            print(
                "The file size < overflow_size({} MB),no need split !!".format(
                        (int)((self.threshold_size_byte / 1024) / 1024)))
            return
        self.init_new_file_list()
        # split file

        new_file_one = io.open(self.new_file_dir.keys()[0], "w", encoding="utf-8")
        new_file_two = io.open(self.new_file_dir.keys()[1], "w", encoding="utf-8")

        print("new_file_one", new_file_one, "new_file_two:", new_file_two)
        with io.open(self.file_path, "r", encoding="utf-8") as old_file:
            count = 0
            second_file_head_filled = False
            for line in old_file:
                self.cache_head_info(line)
                if count == 0:
                    new_file_one.write(line)
                    if self.new_file_dir[self.new_file_dir.keys()[0]] > 0:
                        self.new_file_dir[self.new_file_dir.keys()[0]] -= len(line)
                    else:
                        new_file_one.write(FLAG_TRACE_TAIL_INFO)
                        count = 1
                elif count == 1:
                    if not second_file_head_filled:
                        new_file_two.writelines(self.head_info_list)
                        new_file_two.write(line)
                        second_file_head_filled = True
                    else:
                        new_file_two.write(line)
                        self.new_file_dir[self.new_file_dir.keys()[1]] -= len(line)

        new_file_one.close()
        new_file_two.close()


def build_test():
    file = "./test/testing_trace.html"
    with open(file, "w+") as f:
        for i in range(100):
            f.write("{} haha many {}\n".format(i, "NB" * 50))
            if i == 50:
                f.write("# tracer: nop\n")
        f.write(FLAG_TRACE_TAIL_INFO)


def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threshold", type=int, dest="threshold",
                        help="split threshold size(MB)")
    parser.add_argument("-p", "--path", type=str, dest="path", help="your systrace full path")
    args = parser.parse_args()
    threshold_size = args.threshold
    path = args.path
    if (not threshold_size) or (not path):
        raise Exception(
                "threshold or path is None: threshold={},path={}".format(threshold_size, path))
    print("threshold={},path={}".format(threshold_size, path))
    replace_path = path.replace("\\", "/")
    print("replace_path:", replace_path)
    return threshold_size, replace_path


if __name__ == "__main__":
    threshold_size_mb, file_path = get_arg()
    splitter = SimpleSpliter(threshold_size_mb * 1024 * 1024, file_path)
    splitter.main()
