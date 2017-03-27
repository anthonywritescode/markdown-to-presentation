markdown-to-presentation
========================

A build tool to turn markdown into an html presentation and then publish to
gh-pages

## Installation

`pip install markdown-to-presentation`


## Usage

Set up the following files:

```
# Theme variables for reveal.js
assets/_theme.scss

# application-specific scss
assets/_app.scss

# copied into build directory
assets/*.png

# contains slides
slides.md
```

Slides must be delimited by a blank line followed by `***` followed by a blank
line.  When rendered as markdown `***` will be a horizontal rule.  If you need
a horizontal rule in your slides, use `---` or `___` instead.

Here's an example slides.md:

```markdown
# Title slide
## subtitle

***

## first slide

- bullet 1
- bullet 2
- bullet 3
```

A sample makefile which works well with this:

```make 
all: run-build

venv: requirements.txt
    rm -rf venv
    virtualenv venv -ppython3.6
    venv/bin/pip install -rrequirements.txt
    venv/bin/pre-commit install -f --install-hooks

MTP := run-build push
.PHONY: $(MTP)
$(MTP): venv
    venv/bin/markdown-to-presentation $@

clean:
    rm -rf .mtp venv build index.htm
```

## Hooking up push to github pages

TODO!
