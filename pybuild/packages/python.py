from ..builder import Builder
from ..source import GitSource, URLSource
from ..package import Package
from ..patch import LocalPatch, RemotePatch
from ..util import target_arch

python = Package('python')
main_source = GitSource(python, 'https://github.com/python/cpython/')
python.sources = [
    main_source,
    # http://bugs.python.org/issue29440
    URLSource(python, 'http://bugs.python.org/file46517/gdbm.patch'),
]
python.patches = [
    RemotePatch(main_source, 'gdbm'),
    LocalPatch(main_source, 'ncurses-headers'),
    # http://bugs.python.org/issue29436
    LocalPatch(main_source, 'nl_langinfo'),
    LocalPatch(main_source, 'cppflags'),
    LocalPatch(main_source, 'ldflags-last'),
    LocalPatch(main_source, 'skip-build'),
    # http://bugs.python.org/issue29176
    LocalPatch(main_source, 'curses-tempfile'),
]


class PythonBuilder(Builder):
    source = main_source

    def __init__(self):
        super(PythonBuilder, self).__init__()

        self.env['CONFIG_SITE'] = python.filesdir / 'config.site'

    def prepare(self):
        self.run(['autoreconf', '--install', '--verbose', '--force'])

        self.run_with_env([
            './configure',
            '--prefix=/usr',
            '--host=' + target_arch().ANDROID_TARGET,
            # CPython requires explicit --build
            '--build=x86_64-linux-gnu',
            '--disable-ipv6',
            '--with-system-ffi',
            '--with-system-expat',
            '--without-ensurepip',
        ])

    def build(self):
        self.run(['make'])
        self.run(['make', 'altinstall', f'DESTDIR={self.DESTDIR}'])


python.builder = PythonBuilder()
