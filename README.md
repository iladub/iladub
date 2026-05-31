# iladub

> Semantic document compiling.

**iladub** (𒅍𒁾, Sumerian *íl* "to carry" + *dub* "tablet/document" — "tablet-bearer") is a toolkit for
compiling documents into semantic, structured representations.

It is the reference implementation of the **ET(K)L** method, whose persistent namespace is
[`https://w3id.org/etkl`](https://w3id.org/etkl).

> [!NOTE]
> Early development — APIs are not yet stable.

## Installation

```bash
pip install iladub
```

## Usage

```python
import iladub

print(iladub.__version__)
```

## Development

```bash
git clone https://github.com/iladub/iladub
cd iladub
pip install -e ".[dev]"
pytest
```

## Citation

If you use iladub or the ET(K)L method, please cite it — see [`CITATION.cff`](CITATION.cff).

## License

This project is dual-licensed:

- **Code** (the `iladub` package) — [Apache License 2.0](LICENSE)
- **Vocabulary / ontology** (everything under [`vocab/`](vocab/)) — [Creative Commons Attribution 4.0 International (CC-BY-4.0)](vocab/LICENSE)
