# brand

Logos, icons and preview images of [eizedev](https://github.com/eizedev) and his projects, with
the scripts that draw them. Every image here is generated, so a change is made in a build script
and the image is rebuilt, never edited by hand.

![aiosynologysrm overview](aiosynologysrm/overview.png)

## What is where

| Folder | What |
| --- | --- |
| [`eizedev/`](eizedev/) | the personal ❯e_ logo: avatar, icons, marks, wordmarks, social preview, favicons |
| [`aiosynologysrm/`](aiosynologysrm/) | icon, README header and social preview of [aiosynologysrm](https://github.com/eizedev/aiosynologysrm) |
| [`ha-synology-srm-router/`](ha-synology-srm-router/) | Home Assistant icon, README header and social preview of [ha-synology-srm-router](https://github.com/eizedev/ha-synology-srm-router); same mark as aiosynologysrm |
| [`docs-site/`](docs-site/) | design and build of the documentation websites (GitHub Action) |
| [`lib/brand.py`](lib/brand.py) | shared palette, font outlines, SVG and PNG output |
| [`fonts/`](fonts/) | DejaVu Sans Mono Bold with its license |

Each project folder has a `build.py`, an `overview.png` contact sheet to review all variants at a
glance, and its output files.

## Style

All marks use the [One Dark](https://github.com/joshdick/onedark.vim) palette on dark
backgrounds and One Light on light ones. Lettering is DejaVu Sans Mono Bold, converted to paths,
so the SVGs look the same everywhere without the font installed.

| Role | Dark | Light |
| --- | --- | --- |
| Background | `#272e3d` | `#ffffff` |
| Green | `#98c379` | `#50a14f` |
| Blue | `#61afef` | `#4078f2` |
| Yellow | `#e5c07b` | `#c18401` |
| Text | `#e6e9ef` | `#1f2430` |

## Building

You need [uv](https://docs.astral.sh/uv/) and `rsvg-convert` (macOS: `brew install librsvg`,
Debian/Ubuntu: `apt install librsvg2-bin`). The scripts declare their own Python dependencies.

```sh
uv run eizedev/build.py
uv run aiosynologysrm/build.py
uv run ha-synology-srm-router/build.py
```

## Documentation websites

Every project's documentation site is built with [Zensical](https://zensical.org/) and the design in
[`docs-site/site.css`](docs-site/site.css): the icon's colours (router blue, access point green, mesh
yellow) on cards and headings, a hero on the start page, plain tables with visible code. The
action in [`docs-site/`](docs-site/action.yml) adds the design and builds the site strictly into
`site/`; the Zensical version is pinned in [`docs-site/requirements.txt`](docs-site/requirements.txt).
Dependabot keeps both current here, and in each project the action reference, so a change to the
design reaches a project as a Dependabot pull request after a new tag here.

A project needs:

- `zensical.toml`, starting from [`docs-site/example/zensical.toml`](docs-site/example/zensical.toml)
  (`extra_css = ["assets/site.css"]`, `font = false`, the two palettes);
- its pages in `docs/`, the icon as `docs/assets/icon.svg` (the hero shows it);
  `docs/assets/site.css` in `.gitignore`, the action copies it in;
- a workflow that checks out the project, runs `eizedev/brand/docs-site@<sha> # vX.Y.Z`, uploads
  `site/` with `actions/upload-pages-artifact` and deploys it with `actions/deploy-pages`;
- the start page markup from [`docs-site/example/docs/index.md`](docs-site/example/docs/index.md)
  (`hero`, `cards`).

Local preview, from the project's root:

```sh
curl -fsSo docs/assets/site.css https://raw.githubusercontent.com/eizedev/brand/main/docs-site/site.css
uvx zensical@<version from docs-site/requirements.txt> serve
```

## Using the images in a project

Copy the generated files the project needs into that project's repository (for example
`assets/`) and reference them relatively, so the README also works in forks. Keep the source here.

## Adding a project

Create `<project>/build.py` next to the existing ones, import the shared parts from
`lib/brand.py`, write the output into the project folder and add a row to the table above. Icons
that are shown small get a simplified variant from 32 px down, as `aiosynologysrm` does.

## License

Scripts are MIT, the ❯e_ logo is all rights reserved, project images are CC BY 4.0. Details: [LICENSE.md](LICENSE.md).
