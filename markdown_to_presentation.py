#!/usr/bin/env python3.6
import argparse
import contextlib
import json
import os.path
import shutil
import subprocess
import tempfile
import sys

import pkg_resources

from markdown_code_blocks import CodeRenderer
from markdown_code_blocks import highlight


MTPDIR = '.mtp'
MTPVERSION = os.path.join(MTPDIR, 'version')
MAKEFILE = f'''\
IMG = $(wildcard assets/*.png)
IMG_BUILD = $(patsubst assets/%,build/%,$(IMG))

all: index.htm build/presentation.css build/presentation.js $(IMG_BUILD)

build:
\tmkdir $@

build/%.png: assets/%.png build
\tcp $< $@

.mtp/package.json: {MTPVERSION}
\t{sys.executable} -m markdown_to_presentation run-backend $@

.mtp/node_modules: {MTPVERSION} .mtp/package.json
\t{sys.executable} -m markdown_to_presentation run-backend $@

.mtp/style.scss: {MTPVERSION}
\t{sys.executable} -m markdown_to_presentation run-backend $@

build/presentation.css: {MTPVERSION} assets/_app.scss assets/_theme.scss .mtp/style.scss .mtp/node_modules | build
\t{sys.executable} -m markdown_to_presentation run-backend $@

build/presentation.js: {MTPVERSION} .mtp/node_modules | build
\t{sys.executable} -m markdown_to_presentation run-backend $@

index.htm: {MTPVERSION} slides.md
\t{sys.executable} -m markdown_to_presentation run-backend $@
'''  # noqa: E501

VERSION = pkg_resources.get_distribution('markdown-to-presentation').version


@contextlib.contextmanager
def cwd(pth):
    pwd = os.getcwd()
    os.chdir(pth)
    try:
        yield
    finally:
        os.chdir(pwd)


def _read_mtp_version():
    try:
        return open(MTPVERSION).read()
    except OSError:
        return None


def _write_mtp_version():
    os.makedirs(MTPDIR, exist_ok=True)
    with open(MTPVERSION, 'w') as f:
        f.write(VERSION)


def run_build():
    # Acts as a major version which causes a full rebuild
    if _read_mtp_version() != VERSION:
        _write_mtp_version()

    makefile = MAKEFILE.encode()
    return subprocess.run(('make', '-f', '-'), input=makefile).returncode


def show_makefile():
    print(MAKEFILE)


USER = 'Travis-CI'
EMAIL = 'user@example.com'


def push(paths, *, master_branch, pages_branch):
    paths = ['.travis.yml'] + paths
    if os.environ.get('TRAVIS_BRANCH') != master_branch:
        print(f'Abort: not building {master_branch}')
        return 0
    if os.environ.get('TRAVIS_PULL_REQUEST') != 'false':
        print(f'Abort: building a pull request')
        return 0

    token = os.environ['GH_TOKEN']
    repo = os.environ['TRAVIS_REPO_SLUG']
    remote = f'https://{token}@github.com/{repo}'
    with tempfile.TemporaryDirectory() as tmpdir:
        with cwd(tmpdir):
            print('Cloning...', flush=True)
            proc_ret = subprocess.run(
                ('git', 'clone', remote, '.'),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if proc_ret.returncode:
                print('git clone failed', flush=True)
                return proc_ret.returncode

            print(f'Checkout out {pages_branch}...', flush=True)
            subprocess.check_call(('git', 'checkout', pages_branch))

            print('Removing existing files...', flush=True)
            all_files = subprocess.check_output(('git', 'ls-files'))
            all_files = all_files.decode().splitlines()
            subprocess.check_call(('git', 'rm', '--quiet', *all_files))

        print('Copying new files...', flush=True)
        subprocess.check_call(('rsync', '-avrRq', *paths, tmpdir))

        with cwd(tmpdir):
            print('Committing...', flush=True)
            subprocess.check_call(('git', 'add', '.'))
            subprocess.check_call(('git', 'config', 'user.name', USER))
            subprocess.check_call(('git', 'config', 'user.email', EMAIL))
            build_number = os.environ['TRAVIS_BUILD_NUMBER']
            subprocess.check_call((
                'git', 'commit', '-m',
                f'Deployed {build_number} to Github Pages',
            ))
            print('Pushing...', flush=True)
            return subprocess.call(
                ('git', 'push', 'origin', 'HEAD'),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )


def _make_package_json(target):
    with open(target, 'w') as f:
        f.write(json.dumps({
            'name': 'presentation',
            'version': '0.0.0',
            'author': 'Anthony Sottile',
            'dependencies': {'reveal.js': '2.6.2'},
        }))


def _make_node_modules(target):
    with cwd(MTPDIR):
        subprocess.check_call(('npm', 'install'))
        subprocess.check_call(('npm', 'prune'))
    os.utime(target)


def _make_presentation_css(target):
    return subprocess.call((
        sys.executable, '-m', 'sassc',
        '-t', 'compressed',
        '.mtp/style.scss', target,
    ))


def _make_presentation_js(target):
    # For now, the only js is reveal
    shutil.copy('.mtp/node_modules/reveal.js/js/reveal.min.js', target)


STYLE_SCSS = '''\
// vs.css: https://github.com/richleland/pygments-css

.highlight .hll { background-color: #ffffcc }
.highlight .c { color: #008000 } /* Comment */
.highlight .err { border: 1px solid #FF0000 } /* Error */
.highlight .k { color: #0000ff } /* Keyword */
.highlight .cm { color: #008000 } /* Comment.Multiline */
.highlight .cp { color: #0000ff } /* Comment.Preproc */
.highlight .c1 { color: #008000 } /* Comment.Single */
.highlight .cs { color: #008000 } /* Comment.Special */
.highlight .ge { font-style: italic } /* Generic.Emph */
.highlight .gh { font-weight: bold } /* Generic.Heading */
.highlight .gp { font-weight: bold } /* Generic.Prompt */
.highlight .gs { font-weight: bold } /* Generic.Strong */
.highlight .gu { font-weight: bold } /* Generic.Subheading */
.highlight .kc { color: #0000ff } /* Keyword.Constant */
.highlight .kd { color: #0000ff } /* Keyword.Declaration */
.highlight .kn { color: #0000ff } /* Keyword.Namespace */
.highlight .kp { color: #0000ff } /* Keyword.Pseudo */
.highlight .kr { color: #0000ff } /* Keyword.Reserved */
.highlight .kt { color: #2b91af } /* Keyword.Type */
.highlight .s { color: #a31515 } /* Literal.String */
.highlight .nc { color: #2b91af } /* Name.Class */
.highlight .ow { color: #0000ff } /* Operator.Word */
.highlight .sb { color: #a31515 } /* Literal.String.Backtick */
.highlight .sc { color: #a31515 } /* Literal.String.Char */
.highlight .sd { color: #a31515 } /* Literal.String.Doc */
.highlight .s2 { color: #a31515 } /* Literal.String.Double */
.highlight .se { color: #a31515 } /* Literal.String.Escape */
.highlight .sh { color: #a31515 } /* Literal.String.Heredoc */
.highlight .si { color: #a31515 } /* Literal.String.Interpol */
.highlight .sx { color: #a31515 } /* Literal.String.Other */
.highlight .sr { color: #a31515 } /* Literal.String.Regex */
.highlight .s1 { color: #a31515 } /* Literal.String.Single */
.highlight .ss { color: #a31515 } /* Literal.String.Symbol */

// git diff highlights

.highlight .gi { color: #070; }
.highlight .gd { color: #911; }

// reveal.js

@import 'node_modules/reveal.js/css/reveal';
@import 'node_modules/reveal.js/css/theme/template/mixins';
@import 'node_modules/reveal.js/css/theme/template/settings';

@import '../assets/theme';

@import 'node_modules/reveal.js/css/theme/template/theme';

.reveal {
    pre {
        background-color: #f5f5f1;
        color: #333;
        border: 1px solid #ccccc8;
        border-radius: 4px;
        padding: 5px;
        box-shadow: none;
        overflow-x: auto;

        code {
            background-color: #f5f5f1;
        }
    }

    h1, h2, h3, h4, h5, h6 {
        code {
            text-transform: none;
        }
    }

    .controls {
        left: 10px;
        right: auto;

        .navigate-up, .navigate-down {
            display: none;
        }
    }

    li {
        padding-bottom: .5em;
    }

    section img {
        background: none;
        border: 0;
        box-shadow: none;
    }

    section ul ol {
        padding-left: 1em;
    }

    table {
        border-collapse: collapse;
        margin: auto;

        td, th {
            border-width: 1px;
            border-style: solid;
            padding: .25em;
        }

        thead {
            font-weight: bold;
        }
    }
}


// application code

@import '../assets/app';
'''


def _make_style_scss(target):
    with open(target, 'w') as f:
        f.write(STYLE_SCSS)


INDEX_TMPL = '''\
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="build/presentation.css">
    </head>
    <body>
        <div class="reveal">
            <div class="slides">{slides}</div>
        </div>
        <script src="build/presentation.js"></script>
        <script>
            Reveal.initialize({{
                transition: 'linear',
                keyboard: {{39: 'next', 37: 'prev'}}
            }});
        </script>
    </body>
</html>
'''

SLIDE_DELIM = '\n***\n\n'


class RawHTMLRenderer(CodeRenderer):
    def block_code(self, code, lang):
        if lang == 'rawhtml':
            return code
        else:
            return super().block_code(code, lang)


def _to_slide(md):
    highlighted = highlight(md, Renderer=RawHTMLRenderer)
    return f'<section>{highlighted}</section>'


def _make_index_htm(target):
    contents = open('slides.md').read()
    html = INDEX_TMPL.format(slides=''.join(
        _to_slide(slide) for slide in contents.split(SLIDE_DELIM)
    ))
    with open(target, 'w') as f:
        f.write(html)


BACKENDS = {
    '.mtp/package.json': _make_package_json,
    '.mtp/node_modules': _make_node_modules,
    '.mtp/style.scss': _make_style_scss,
    'build/presentation.css': _make_presentation_css,
    'build/presentation.js': _make_presentation_js,
    'index.htm': _make_index_htm,
}


def run_backend(target):
    def _make_old():
        print(f'make old {target}')
        if os.path.exists(target):
            os.utime(target, (0, 0))

    def _make_new():
        print(f'make new {target}')
        if os.path.exists(target):
            os.utime(target)

    try:
        ret = BACKENDS[target](target)
    except Exception:
        _make_old()
        raise
    else:
        if ret:
            _make_old()
        else:
            _make_new()
        return ret


def main(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    subparsers.add_parser('run-build')
    subparsers.add_parser('show-makefile')
    push_parser = subparsers.add_parser('push')
    push_parser.add_argument('paths', nargs='+')
    push_parser.add_argument('--master-branch', default='master')
    push_parser.add_argument('--pages-branch', default='gh-pages')

    run_backend_parser = subparsers.add_parser('run-backend')
    run_backend_parser.add_argument('target')

    args = parser.parse_args(argv)

    if args.command == 'run-build':
        return run_build()
    elif args.command == 'show-makefile':
        return show_makefile()
    elif args.command == 'push':
        return push(
            args.paths,
            master_branch=args.master_branch, pages_branch=args.pages_branch,
        )
    elif args.command == 'run-backend':
        return run_backend(args.target)
    else:
        raise NotImplementedError(f'unknown command {args.command}')


if __name__ == '__main__':
    exit(main())
