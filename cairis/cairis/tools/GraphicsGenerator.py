from tools.SVGGenerator import SVGGenerator

__author__ = 'Robin Quetin'

class GraphicsGenerator(object):
    def __init__(self, output_format='svg'):
        output_format = output_format.lower()
        if output_format == 'svg':
            self.ded_generator = SVGGenerator()
        else:
            raise RuntimeError('There is no generator registered for the provided output format.')

    def generate(self, dot_code, output_path=None, model_type=None):
        if output_path is None:
            return self.ded_generator.generate(dot_code, model_type)
        else:
            self.ded_generator.generate_file(dot_code, output_path, model_type)