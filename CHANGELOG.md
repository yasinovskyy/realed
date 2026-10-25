# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Calendar Versioning](https://calver.org/).

## [Unreleased]

### Added

`exact` parameter to `equals` to consider index when comparing relations

## Fixed

Invoke `pandas.DataFrame.to_html` instead of `pandas.DataFrame._repr_html_` when `Relation._repr_html_` is called.

## 2026.10.1 - 2026-10-23

### Added

`_repr_html_` to make relations look like dataframes when rendered in notebooks.

`drop_duplicates` as a pass-through to `pandas.DataFrame.drop_duplicates`

## Fixed

Relation representation in Jupyter notebooks.

## 2026.10 - 2026-10-21

Update the Relation constructor to handle chunks.

### Added

Test cases for various ways to make relations.

### Fixed

Relation constructor can handle chunks now.

## 2026.8 - 2026-08-01

Initial release.

### Added

- Selection (`select`)
- Projection (`project`)
- Renaming (`rename`)
- Extending (`extend`)
- Sorting (`sort`)
- Grouping (`groupby`)
- Cartesian product (`product`)
- Concatenation (`union`)
- Natural join (`njoin`)
- Equijoin (`ejoin`)
- Semijoin (`sjoin`)
- Antijoin (`ajoin`)
- Outer join (`ojoin`)

[unreleased]: https://github.com/yasinovskyy/realed/compare/v2026.10.1...HEAD
