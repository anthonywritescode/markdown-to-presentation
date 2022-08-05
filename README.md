[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/anthonywritescode/markdown-to-presentation/main.svg)](https://results.pre-commit.ci/latest/github/anthonywritescode/markdown-to-presentation/main)

markdown-to-presentation
========================

A build tool to turn markdown into an html presentation and then publish to
gh-pages

## Installation

```bash
pip install markdown-to-presentation
```


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

If you need raw html in your slides, use a *special* `rawhtml` code block:

    ```rawhtml
    <div>this html will be <em>injected</em> directly</div>
    ```

A sample makefile which works well with this:

```make
all: run-build

venv: requirements.txt
    rm -rf venv
    virtualenv venv -ppython3
    venv/bin/pip install -rrequirements.txt
    venv/bin/pre-commit install -f --install-hooks

.PHONY: run-build
run-build: venv
    venv/bin/markdown-to-presentation run-build

.PHONY: push
push: venv
    venv/bin/markdown-to-presentation push index.htm build

clean:
    rm -rf .mtp venv build index.htm
```

## Hooking up push to github pages

Acquire a [push token](https://github.com/settings/tokens/new) which has the
`public_repo` permission.

Use [`travis encrypt`](https://docs.travis-ci.com/user/encryption-keys/) to
encrypt your push token as `GH_TOKEN=...`.  You'll need the yaml it spits out
to fill out your `.travis.yml`.

Make a `.travis.yml` which looks something like this:

```yaml
install: pip install virtualenv
script: make
after_success: make push
branches:
    except:
        - gh-pages
env:
    global:
        # GH_TOKEN
        - secure: ...
```

For your `make push` target, invoke something like this:

```makefile
.PHONY: push
push: venv
    venv/bin/markdown-to-presentation push index.htm build
```

consult the `markdown-to-presentation push --help` to get a full list of
options.
