# *ReAlEd*: Relational Algebra for Education

A simple wrapper around `pandas` to demonstrate common relational algebra operations:

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

This implementation is a thin layer above the underlying `DataFrame` with some error handling and data cleaning added to make the resulting operations match those of the relational algebra.

Each operation returns a new relation without modifying the original.
Operations can be chained in various combinations.

It is a rewrite of [Brad Miller's reframe](https://github.com/bnmnetp/reframe) with the following major differences:

- expanded list of operations (various joins)
- the more recent version of `pandas` as a dependency
- composition used instead of inheritance

## Initialization

A new relation can be created from a CSV file, a `DataFrame`, or another `Relation`.
Some arguments can be passed to the constructor in order to override defaults used by `pandas`:

```python
penguins = Relation("palmerpenguins.csv")
penguins = Relation("palmerpenguins.csv", sep=",")
```

Test data includes [Palmer penguins](https://allisonhorst.github.io/palmerpenguins/) and information about a couple Palmer islands to demonstrate multi-relation operations.

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> penguins
     rowid    species     island  bill_length_mm  ...  flipper_length_mm  body_mass_g     sex  year
0        1     Adelie  Torgersen            39.1  ...              181.0       3750.0    male  2007
1        2     Adelie  Torgersen            39.5  ...              186.0       3800.0  female  2007
2        3     Adelie  Torgersen            40.3  ...              195.0       3250.0  female  2007
3        4     Adelie  Torgersen             NaN  ...                NaN          NaN     NaN  2007
4        5     Adelie  Torgersen            36.7  ...              193.0       3450.0  female  2007
..     ...        ...        ...             ...  ...                ...          ...     ...   ...
339    340  Chinstrap      Dream            55.8  ...              207.0       4000.0    male  2009
340    341  Chinstrap      Dream            43.5  ...              202.0       3400.0  female  2009
341    342  Chinstrap      Dream            49.6  ...              193.0       3775.0    male  2009
342    343  Chinstrap      Dream            50.8  ...              210.0       4100.0    male  2009
343    344  Chinstrap      Dream            50.2  ...              198.0       3775.0  female  2009
>>> islands = Relation("palmerislands.csv")
>>> islands
   id       island  explored                              expedition         name_origin
0   1       Amsler      1955    Falkland Islands Dependencies Survey     Margaret Amsler
1   2       Anvers      1832               Southern Ocean Expedition    Antwerp province
2   3       Biscoe      1832               Southern Ocean Expedition         John Biscoe
3   4  Christiania      1898            Belgian Antarctic Expedition                Oslo
4   5        Dream      1956  British Naval Hydrographic Survey Unit    Natural features
5   6    Torgersen      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
>>>
```

Certain helper methods and properties are available:

- property `data`: internal `DataFrame`
- property `columns`: names of the attributes
- property `dim`: dimensions of the relation (rows, columns)
- property `one`: the first record of the relation as a dictionary
- method `to_csv`: export the `data` to a csv file
- method `copy`: deep copy of the `data`
- method `cleanup`: removal of empty records
- method `equals`: comparison of two relations
- method `minus`: difference between two relations
- method `intersection`: intersection of two relations

## Selection (`select`)

Selection is a simplified version of the `query` method available in `pandas.DataFrame`.
It only takes one argument, the query expression.

```python
>>> islands.select("expedition == 'Southern Ocean Expedition'")
   id  island  explored                 expedition       name_origin
1   2  Anvers      1832  Southern Ocean Expedition  Antwerp province
2   3  Biscoe      1832  Southern Ocean Expedition       John Biscoe
>>> 
```

```python
>>> penguins.select("species == 'Adelie' and island == 'Torgersen' and year == 2009 and body_mass_g >= 4000")
     rowid species     island  bill_length_mm  bill_depth_mm  flipper_length_mm  body_mass_g   sex  year
125    126  Adelie  Torgersen            40.6           19.0              199.0       4000.0  male  2009
127    128  Adelie  Torgersen            41.5           18.3              195.0       4300.0  male  2009
129    130  Adelie  Torgersen            44.1           18.0              210.0       4000.0  male  2009
```

Since each operation returns a `Relation`, operations can be chained:

```python
>>> penguins.select("species == 'Adelie'").select("island == 'Torgersen'").select("year == 2009").select("body_mass_g >= 4000")
     rowid species     island  bill_length_mm  bill_depth_mm  flipper_length_mm  body_mass_g   sex  year
125    126  Adelie  Torgersen            40.6           19.0              199.0       4000.0  male  2009
127    128  Adelie  Torgersen            41.5           18.3              195.0       4300.0  male  2009
129    130  Adelie  Torgersen            44.1           18.0              210.0       4000.0  male  2009
```

A separate method,`query`, is also available.
It passes all provided named arguments and keyword arguments to the `query` method of the `pandas.DataFrame`.

## Projection (`project`)

For the sake of consistency names of attributes must be a list of strings, even if a single attribute is being projected.

```python
>>> penguins.project(["island"])
       island
0   Torgersen
20     Biscoe
30      Dream
>>> penguins.project(["species", "island"])
       species     island
0       Adelie  Torgersen
20      Adelie     Biscoe
30      Adelie      Dream
152     Gentoo     Biscoe
276  Chinstrap      Dream
>>>
```

## Renaming (`rename`)

If the old name is not among the attributes or the new name is already there, a `ValueError` is raised.

```python
>>> penguins.rename("island", "location").project(["species", "location"])
       species   location
0       Adelie  Torgersen
20      Adelie     Biscoe
30      Adelie      Dream
152     Gentoo     Biscoe
276  Chinstrap      Dream
>>>
```

## Sorting (`sort`)

```python
>>> islands.sort(["explored"])
   id       island  explored                              expedition         name_origin
1   2       Anvers      1832               Southern Ocean Expedition    Antwerp province
2   3       Biscoe      1832               Southern Ocean Expedition         John Biscoe
3   4  Christiania      1898            Belgian Antarctic Expedition                Oslo
0   1       Amsler      1955    Falkland Islands Dependencies Survey     Margaret Amsler
5   6    Torgersen      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
4   5        Dream      1956  British Naval Hydrographic Survey Unit    Natural features
>>> islands.sort(["explored"], ascending=False)
   id       island  explored                              expedition         name_origin
4   5        Dream      1956  British Naval Hydrographic Survey Unit    Natural features
0   1       Amsler      1955    Falkland Islands Dependencies Survey     Margaret Amsler
5   6    Torgersen      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
3   4  Christiania      1898            Belgian Antarctic Expedition                Oslo
1   2       Anvers      1832               Southern Ocean Expedition    Antwerp province
2   3       Biscoe      1832               Southern Ocean Expedition         John Biscoe
```

```python
>>> penguins.sort(["species", "rowid"]).head(3)
   rowid species     island  bill_length_mm  ...  flipper_length_mm  body_mass_g     sex  year
0      1  Adelie  Torgersen            39.1  ...              181.0       3750.0    male  2007
1      2  Adelie  Torgersen            39.5  ...              186.0       3800.0  female  2007
2      3  Adelie  Torgersen            40.3  ...              195.0       3250.0  female  2007
```

Be mindful of the order of sorting operations.

```python
>>> penguins.sort(["body_mass_g"], ascending=False).sort(["species"]).head(3)
     rowid species     island  bill_length_mm  ...  flipper_length_mm  body_mass_g     sex  year
111    112  Adelie     Biscoe            45.6  ...              191.0       4600.0    male  2009
76      77  Adelie  Torgersen            40.9  ...              191.0       3700.0  female  2008
14      15  Adelie  Torgersen            34.6  ...              198.0       4400.0    male  2007
>>> penguins.sort(["species"]).sort(["body_mass_g"], ascending=False).head(3)
     rowid species  island  bill_length_mm  ...  flipper_length_mm  body_mass_g   sex  year
169    170  Gentoo  Biscoe            49.2  ...              221.0       6300.0  male  2007
185    186  Gentoo  Biscoe            59.6  ...              230.0       6050.0  male  2007
269    270  Gentoo  Biscoe            48.8  ...              222.0       6000.0  male  2009
```

## Extending (`extend`)

The new name cannot match the name of an existing attribute.
New data must be a of type `pandas.Series`.

```python
>>> penguins.extend("years_since_study", 2026-penguins["year"])
     rowid    species     island  bill_length_mm  ...  body_mass_g     sex  year years_since_study
0        1     Adelie  Torgersen            39.1  ...       3750.0    male  2007               19
1        2     Adelie  Torgersen            39.5  ...       3800.0  female  2007               19
2        3     Adelie  Torgersen            40.3  ...       3250.0  female  2007               19
3        4     Adelie  Torgersen             NaN  ...          NaN     NaN  2007               19
4        5     Adelie  Torgersen            36.7  ...       3450.0  female  2007               19
..     ...        ...        ...             ...  ...          ...     ...   ...              ...
339    340  Chinstrap      Dream            55.8  ...       4000.0    male  2009               17
340    341  Chinstrap      Dream            43.5  ...       3400.0  female  2009               17
341    342  Chinstrap      Dream            49.6  ...       3775.0    male  2009               17
342    343  Chinstrap      Dream            50.8  ...       4100.0    male  2009               17
343    344  Chinstrap      Dream            50.2  ...       3775.0  female  2009               17
>>>
```

## Grouping (`groupby`) and aggregation

Grouping without an aggregate function eliminates duplicates in the chosen categories.

```python
>>> penguins.groupby(["species"])
     species
0     Adelie
1  Chinstrap
2     Gentoo
```

Typically, grouping is followed by an aggregate function `count`, `sum`, `min`, `max`, `mean` (`avg`), or `median`.
The aggregate function is added as a prefix to the name of the resulting column.

```python
>>> penguins.groupby(["species"]).count("rowid")
     species  count_rowid
0     Adelie          152
1  Chinstrap           68
2     Gentoo          124
>>> penguins.groupby(["island"]).count("rowid")
      island  count_rowid
0     Biscoe          168
1      Dream          124
2  Torgersen           52
>>> penguins.groupby(["species", "island"]).count("rowid")
     species     island  count_rowid
0     Adelie     Biscoe           44
1     Adelie      Dream           56
2     Adelie  Torgersen           52
3  Chinstrap      Dream           68
4     Gentoo     Biscoe          124
>>> penguins.groupby(["island"]).sum("body_mass_g")
      island  sum_body_mass_g
0     Biscoe         787575.0
1      Dream         460400.0
2  Torgersen         189025.0
>>> penguins.groupby(["island"]).min("body_mass_g")
      island  min_body_mass_g
0     Biscoe           2850.0
1      Dream           2700.0
2  Torgersen           2900.0
>>> penguins.groupby(["island"]).max("body_mass_g")
      island  max_body_mass_g
0     Biscoe           6300.0
1      Dream           4800.0
2  Torgersen           4700.0
>>> penguins.groupby(["island"]).mean("body_mass_g")
      island  mean_body_mass_g
0     Biscoe       4716.017964
1      Dream       3712.903226
2  Torgersen       3706.372549
>>> penguins.groupby(["island"]).avg("body_mass_g")
      island  avg_body_mass_g
0     Biscoe      4716.017964
1      Dream      3712.903226
2  Torgersen      3706.372549
>>> penguins.groupby(["island"]).median("body_mass_g")
      island  median_body_mass_g
0     Biscoe              4775.0
1      Dream              3687.5
2  Torgersen              3700.0
```

## Cartesian product (`product`)

Two relations must have disjoint attributes for this operation to work.

```python
>>> penguins.product(islands.rename("island", "name"))
      rowid    species  ...                              expedition         name_origin
0         1     Adelie  ...    Falkland Islands Dependencies Survey     Margaret Amsler
1         1     Adelie  ...               Southern Ocean Expedition    Antwerp province
2         1     Adelie  ...               Southern Ocean Expedition         John Biscoe
3         1     Adelie  ...            Belgian Antarctic Expedition                Oslo
4         1     Adelie  ...  British Naval Hydrographic Survey Unit    Natural features
...     ...        ...  ...                                     ...                 ...
2059    344  Chinstrap  ...               Southern Ocean Expedition    Antwerp province
2060    344  Chinstrap  ...               Southern Ocean Expedition         John Biscoe
2061    344  Chinstrap  ...            Belgian Antarctic Expedition                Oslo
2062    344  Chinstrap  ...  British Naval Hydrographic Survey Unit    Natural features
2063    344  Chinstrap  ...    Falkland Islands Dependencies Survey  Torstein Torgersen
```

## Concatenation (`union`)

Attributes of both relations must be the same.

```python
>>> penguins.select("species == 'Adelie'").union(penguins.select("species == 'Gentoo'"))
     rowid species     island  bill_length_mm  ...  flipper_length_mm  body_mass_g     sex  year
0        1  Adelie  Torgersen            39.1  ...              181.0       3750.0    male  2007
1        2  Adelie  Torgersen            39.5  ...              186.0       3800.0  female  2007
2        3  Adelie  Torgersen            40.3  ...              195.0       3250.0  female  2007
3        4  Adelie  Torgersen             NaN  ...                NaN          NaN     NaN  2007
4        5  Adelie  Torgersen            36.7  ...              193.0       3450.0  female  2007
..     ...     ...        ...             ...  ...                ...          ...     ...   ...
271    272  Gentoo     Biscoe             NaN  ...                NaN          NaN     NaN  2009
272    273  Gentoo     Biscoe            46.8  ...              215.0       4850.0  female  2009
273    274  Gentoo     Biscoe            50.4  ...              222.0       5750.0    male  2009
274    275  Gentoo     Biscoe            45.2  ...              212.0       5200.0  female  2009
275    276  Gentoo     Biscoe            49.9  ...              213.0       5400.0    male  2009
```

## Natural join (`naturaljoin` or `njoin`)

There must be at least one common attribute in both relations.

```python
>>> penguins.njoin(islands)
     rowid    species     island  ...  explored                              expedition         name_origin
0        1     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
1        2     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
2        3     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
3        4     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
4        5     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
..     ...        ...        ...  ...       ...                                     ...                 ...
339    340  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
340    341  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
341    342  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
342    343  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
343    344  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
```

## Equijoin (`equijoin` or `ejoin`)

A simple version of the theta-join that checks two attributes for equality.
Both left and right attributes must be strings.

```python
>>> penguins.ejoin(islands, "island", "island")
     rowid    species     island  ...  explored                              expedition         name_origin
0        1     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
1        2     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
2        3     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
3        4     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
4        5     Adelie  Torgersen  ...      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
..     ...        ...        ...  ...       ...                                     ...                 ...
339    340  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
340    341  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
341    342  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
342    343  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
343    344  Chinstrap      Dream  ...      1956  British Naval Hydrographic Survey Unit    Natural features
```

## Semijoin (`semijoin` or `sjoin`)

Both left and right attributes must be strings.

```python
>>> islands.sjoin(penguins, "island", "island")
   id     island  explored                              expedition         name_origin
2   3     Biscoe      1832               Southern Ocean Expedition         John Biscoe
4   5      Dream      1956  British Naval Hydrographic Survey Unit    Natural features
5   6  Torgersen      1955    Falkland Islands Dependencies Survey  Torstein Torgersen
```

## Antijoin (`antijoin` or `ajoin`)

Both left and right attributes must be strings.

```python
>>> islands.ajoin(penguins, "island", "island")
   id       island  explored                            expedition       name_origin
0   1       Amsler      1955  Falkland Islands Dependencies Survey   Margaret Amsler
1   2       Anvers      1832             Southern Ocean Expedition  Antwerp province
3   4  Christiania      1898          Belgian Antarctic Expedition              Oslo
```

## Outer join (`outerjoin` or `ojoin`)

Full outer join.

```python
>>> islands.ojoin(penguins)
     id     island  explored  ... body_mass_g     sex    year
0     1     Amsler      1955  ...         NaN     NaN     NaN
1     2     Anvers      1832  ...         NaN     NaN     NaN
2     3     Biscoe      1832  ...      3400.0  female  2007.0
3     3     Biscoe      1832  ...      3600.0    male  2007.0
4     3     Biscoe      1832  ...      3800.0  female  2007.0
..   ..        ...       ...  ...         ...     ...     ...
342   6  Torgersen      1955  ...      4300.0    male  2009.0
343   6  Torgersen      1955  ...      3050.0  female  2009.0
344   6  Torgersen      1955  ...      4000.0    male  2009.0
345   6  Torgersen      1955  ...      3325.0  female  2009.0
346   6  Torgersen      1955  ...      3500.0    male  2009.0
>>> penguins.ojoin(islands)
     rowid species     island  ...  explored                            expedition         name_origin
0      NaN     NaN     Amsler  ...      1955  Falkland Islands Dependencies Survey     Margaret Amsler
1      NaN     NaN     Anvers  ...      1832             Southern Ocean Expedition    Antwerp province
2     21.0  Adelie     Biscoe  ...      1832             Southern Ocean Expedition         John Biscoe
3     22.0  Adelie     Biscoe  ...      1832             Southern Ocean Expedition         John Biscoe
4     23.0  Adelie     Biscoe  ...      1832             Southern Ocean Expedition         John Biscoe
..     ...     ...        ...  ...       ...                                   ...                 ...
342  128.0  Adelie  Torgersen  ...      1955  Falkland Islands Dependencies Survey  Torstein Torgersen
343  129.0  Adelie  Torgersen  ...      1955  Falkland Islands Dependencies Survey  Torstein Torgersen
344  130.0  Adelie  Torgersen  ...      1955  Falkland Islands Dependencies Survey  Torstein Torgersen
345  131.0  Adelie  Torgersen  ...      1955  Falkland Islands Dependencies Survey  Torstein Torgersen
346  132.0  Adelie  Torgersen  ...      1955  Falkland Islands Dependencies Survey  Torstein Torgersen
```
