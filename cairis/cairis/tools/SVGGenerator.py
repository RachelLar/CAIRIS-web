import os
from re import sub as substitute
from subprocess import check_output as cmd
from tempfile import mkstemp as make_tempfile

__author__ = 'Robin Quetin'


class SVGGenerator(object):
    def __init__(self):
        self.extension = 'svg'

    def generate(self, dot_code):
        fd, temp_abspath = make_tempfile(suffix=self.extension)
        temp_file = open(temp_abspath, 'wb')
        temp_file.write(dot_code)
        temp_file.close()
        os.close(fd)
        output = cmd(['dot', '-Tsvg', temp_abspath])
        os.remove(temp_abspath)
        output = self.process_output(str(output))
        return output

    def generate_file(self, dot_code, output_file):
        output = self.generate(dot_code)

        try:
            fs_output = open(output_file, 'rb')
            fs_output.write(output)
            fs_output.close()
        except Exception, ex:
            fs_output.close()
            raise ex

    def process_output(self, output):
        lines = output.split('\n')
        svg_start = -1

        for i in range(len(lines)):
            if svg_start == -1:
                if lines[i].find('<svg') > -1:
                    svg_start = i

            lines[i] = substitute("<!--.*?-->", "", lines[i])

        if svg_start > -1:
            lines = lines[svg_start:]

        return '\n'.join(lines)
