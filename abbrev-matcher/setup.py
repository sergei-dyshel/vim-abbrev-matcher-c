from distutils.core import setup, Extension

module1 = Extension(
    'abbrev_matcher_c',
    extra_compile_args=['-O3', '-Wall', '-Wextra', '-Werror',
                        '-Wno-unused-parameter',
                        '-Wno-missing-field-initializers'],
    sources=['abbrev_matcher.c'])

setup(
    name='PackageName',
    version='1.0',
    description='This is a demo package',
    ext_modules=[module1])
