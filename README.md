# *ReAlEd*: Relational Algebra for Education

A simple wrapper around `pandas` to demonstrate common relational algebra operations:

- selection
- projection
- renaming
- extending
- sorting
- grouping
- joining relations

## Initialization

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> r
     rowid    species     island  bill_length_mm  bill_depth_mm  flipper_length_mm  body_mass_g     sex  year
0        1     Adelie  Torgersen            39.1           18.7              181.0       3750.0    male  2007
1        2     Adelie  Torgersen            39.5           17.4              186.0       3800.0  female  2007
2        3     Adelie  Torgersen            40.3           18.0              195.0       3250.0  female  2007
3        4     Adelie  Torgersen             NaN            NaN                NaN          NaN     NaN  2007
4        5     Adelie  Torgersen            36.7           19.3              193.0       3450.0  female  2007
..     ...        ...        ...             ...            ...                ...          ...     ...   ...
339    340  Chinstrap      Dream            55.8           19.8              207.0       4000.0    male  2009
340    341  Chinstrap      Dream            43.5           18.1              202.0       3400.0  female  2009
341    342  Chinstrap      Dream            49.6           18.2              193.0       3775.0    male  2009
342    343  Chinstrap      Dream            50.8           19.0              210.0       4100.0    male  2009
343    344  Chinstrap      Dream            50.2           18.7              198.0       3775.0  female  2009
>>>
```

## Selection

Both `select` and `query` filter records by some criteria.
The query expression is parsed by `pandas`.

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> penguins.select("species == 'Adelie'")
     rowid species     island  bill_length_mm  bill_depth_mm  flipper_length_mm  body_mass_g     sex  year
0        1  Adelie  Torgersen            39.1           18.7              181.0       3750.0    male  2007
1        2  Adelie  Torgersen            39.5           17.4              186.0       3800.0  female  2007
2        3  Adelie  Torgersen            40.3           18.0              195.0       3250.0  female  2007
3        4  Adelie  Torgersen             NaN            NaN                NaN          NaN     NaN  2007
4        5  Adelie  Torgersen            36.7           19.3              193.0       3450.0  female  2007
..     ...     ...        ...             ...            ...                ...          ...     ...   ...
147    148  Adelie      Dream            36.6           18.4              184.0       3475.0  female  2009
148    149  Adelie      Dream            36.0           17.8              195.0       3450.0  female  2009
149    150  Adelie      Dream            37.8           18.1              193.0       3750.0    male  2009
150    151  Adelie      Dream            36.0           17.1              187.0       3700.0  female  2009
151    152  Adelie      Dream            41.5           18.5              201.0       4000.0    male  2009
>>>
```

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> penguins.select("species == 'Adelie' and island == 'Torgersen' and year == 2009 and body_mass_g >= 4000")
     rowid species     island  bill_length_mm  bill_depth_mm  flipper_length_mm  body_mass_g   sex  year
125    126  Adelie  Torgersen            40.6           19.0              199.0       4000.0  male  2009
127    128  Adelie  Torgersen            41.5           18.3              195.0       4300.0  male  2009
129    130  Adelie  Torgersen            44.1           18.0              210.0       4000.0  male  2009
```

Since each operation return a `Relation`, operations can be chained:

```python
>>> penguins.select("species == 'Adelie'").select("island == 'Torgersen'").select("year == 2009").select("body_mass_g >= 4000")
     rowid species     island  bill_length_mm  bill_depth_mm  flipper_length_mm  body_mass_g   sex  year
125    126  Adelie  Torgersen            40.6           19.0              199.0       4000.0  male  2009
127    128  Adelie  Torgersen            41.5           18.3              195.0       4300.0  male  2009
129    130  Adelie  Torgersen            44.1           18.0              210.0       4000.0  male  2009
```

## Projection

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> penguins.project(["species", "island"])
       species     island
0       Adelie  Torgersen
20      Adelie     Biscoe
30      Adelie      Dream
152     Gentoo     Biscoe
276  Chinstrap      Dream
>>>
```

## Renaming

```python

>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> penguins.rename("island", "location").project(["species", "location"]).head(3)
   species   location
0   Adelie  Torgersen
20  Adelie     Biscoe
30  Adelie      Dream
>>>
```

## Sorting

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> penguins.sort(["species"]).head(3)
    rowid species     island  bill_length_mm  ...  flipper_length_mm  body_mass_g     sex  year
0       1  Adelie  Torgersen            39.1  ...              181.0       3750.0    male  2007
97     98  Adelie      Dream            40.3  ...              196.0       4350.0    male  2008
98     99  Adelie      Dream            33.1  ...              178.0       2900.0  female  2008
>>>
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
```

```python
>>> penguins.sort(["species"]).sort(["body_mass_g"], ascending=False).head(3)
     rowid species  island  bill_length_mm  ...  flipper_length_mm  body_mass_g   sex  year
169    170  Gentoo  Biscoe            49.2  ...              221.0       6300.0  male  2007
185    186  Gentoo  Biscoe            59.6  ...              230.0       6050.0  male  2007
269    270  Gentoo  Biscoe            48.8  ...              222.0       6000.0  male  2009
```


## Extending

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
>>> penguins.extend("year_since_found", 2026-penguins.year)
     rowid    species     island  bill_length_mm  ...  body_mass_g     sex  year year_since_found
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

## Grouping and aggregation

```python
>>> from realed import Relation
>>> penguins = Relation("palmerpenguins.csv")
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
