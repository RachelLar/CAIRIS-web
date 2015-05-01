import os
from re import sub as substitute
import string
from subprocess import check_output as cmd
from tempfile import mkstemp as make_tempfile
from xml.dom import minidom

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
            line = lines[i]
            if svg_start == -1:
                if lines[i].find('<svg') > -1:
                    svg_start = i

            line = substitute("<!--.*?-->", "", line)

            line = line.replace('fill="none"', 'fill="white"')

            href_exists = -1
            href_exists = line.find('<a xlink:href="', href_exists+1)
            while href_exists > -1:
                start_index = line.find('"', href_exists)
                end_index = line.find('"', start_index+1)
                bracket_index = line.find('#', start_index+1)
                is_valid = start_index < bracket_index < end_index

                if is_valid:
                    old_link = line[start_index+1:end_index]
                    parts = old_link.split('#')
                    type = parts[0]
                    object = ''.join(parts[1:])
                    new_link = '/api/{0}s/name/{1}'.format(type, object)
                    line = line.replace(old_link, new_link)

                href_exists = line.find('<a xlink:href="', href_exists+1)

            lines[i] = line

        if svg_start > -1:
            lines = lines[svg_start:]

        svg_text = '\n'.join(lines)
        svg_doc = minidom.parseString(svg_text)
        svg_text = svg_doc.toprettyxml(indent='  ')
        svg_lines = svg_text.replace('\r\n', '\n').split('\n')
        svg_filtered = list()
        for svg_line in svg_lines:
            if svg_line.strip(' ').strip('\t') != '':
                svg_filtered.append(svg_line)

        return '\n'.join(svg_filtered[1:])
