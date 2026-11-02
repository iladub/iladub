# HDC capabilities for the iladub contract compiler: research notes, 2026-10-30

Agent reports gathered in the 2026-10-30 brainstorm session (after `4b576f0`). Each section condenses one
report. Uses marked **(inf)** are the agents' or my inference, not the source's. Nothing here is measured on our
data.

## A. hyperdimensionalcomputing.ai (owner's chosen authority, see memory `hdc-labs-reference`)

**Site (29 posts, rss at /rss.xml).** It uses MAP (bipolar vectors, binding by multiply, bundling by add) with
TorchHD, LanceDB and nomic-embed-text, at D=4096 by default (sweep 2k–8k). Not covered anywhere: resonators /
factorization, FHRR, fractional power encoding, n-gram text encoding, calibration, analogy, document parsing.

**Operations that matter for us:**

- **Records** = Σ bind(role, value), kept as raw sums.
  - Unbind a role, then clean up against a per-role item memory.
  - An exact fact can be subtracted.
  - Scores split exactly per fact, which makes them explainable.
  - Sources: /blog/what-can-we-recover-from-a-bundled-hypervector, /blog/what-do-cleanup-and-crosstalk-mean-in-hdc.
- **Permutation** ρ^k encodes depth, position and step. MAP binding is commutative and self-inverse, so without it
  a hierarchy collapses. Source: /blog/permutation-in-hdc.
- **Graph triples** = src + ρ(rel) + ρ²(tgt). Queries are partial cues. The returned IDs are then validated
  exactly against the graph. Source: /blog/from-a-property-graph-to-associative-search.
- **Prototypes** = a bundle of labelled examples.
  - Store the raw examples (durable memory) and rebuild prototypes per context.
  - On synthetic data, one pooled prototype collapsed when context flipped the labels.
  - Source: /blog/durable-memory-transient-prototypes.
- **Capacity:**
  - Similarity to a member of a bundle is about 1/√n.
  - Exact recovery of 50 facts: 79% at D=512, 98% at 2048, 100% at 8192.
  - In all-pairs comparison, false positives explode unless a match requires at least 2 shared facts.
  - The noise floor for unrelated vectors has SD ≈ 1/√D.
  - Sources: /blog/testing-the-limits-of-bundling-capacity-1, -2.
- **Context weighting.** Binding the same context into both sides changes nothing. Weight features before
  encoding instead. Source: /blog/context-sensitive-retrieval.
- **Where meaning comes from.** Meaning comes from the encoder: random codebooks carry no synonymy. A projected
  embedding inherits the embedding model's blind spots. Roles and direction must be encoded explicitly. Source:
  /blog/where-does-meaning-in-a-hypervector-come-from.

**Limits the site states:**

- **"HDC proposes, the graph validates."** Top-k search always returns something.
- **Hard constraints stay outside HDC.** "Unknown" is a valid outcome. Source: /whats-possible/find-the-case-that-fits-now.
- **No multi-step reasoning.** HDC cannot find a feature its encoder never represented. Source:
  /blog/how-hdc-complements-deep-learning.
- **Escalation.** Escalate on a mismatch score of 1 − cos(observed, predicted). Source:
  /blog/a-category-is-something-a-system-does.

## B. Literature: factorization, analogy, KG, extraction

- **Resonator networks** (Frady/Kent/Olshausen/Sommer 2020, arXiv 2007.03748; IBM Nature Nanotech 2023) factor
  products of unknowns. **Not needed (inf):** our clause bundles are sums of pairs whose role is known, so one
  unbind plus cleanup is enough.
- **Analogy** (Kanerva "dollar of Mexico"; survey arXiv 2112.15424): mapping works only when both structures use
  the same roles. **(inf):** encode every clause on the shared ontology roles, then compare
  sim(clause49, clause64) and take per-role unbind diffs. Mapping across different role sets goes to the symbolic
  layer.
- **KG/ontology HDC** (HDReason 2403.05763, PathHD 2512.09369, Fanizzi & d'Amato NAI 2025 [unread, 403]): this
  is link prediction, not OWL semantics. A bundle of subclasses is fuzzy, not entailment. **(inf):** OWL and SHACL
  stay the truth, and HDC is only an approximate "find similar" index.
- **Extraction / slot filling:** no HDC work exists. HDC encodes structure but does not find it. **(inf):** use
  regex or a grammar for dates and periods, gazetteers for parties and ports, and Haiku (stand-in for a small
  local model) for the rest. HDC classifies and encodes afterwards.

## C. Literature: calibration and the three-way decision

- No HDC paper applies Platt or isotonic calibration.
  - ConformalHDC (arXiv 2602.21446, preprint 2026) argues that softmax on HDC similarities discards the
    information needed to abstain.
  - HDUQ-HAR (Sci. Reports 2026) feeds sim₁, the margin and dispersion into conformal prediction.
- **Out-of-distribution detection:** HDFF (WACV 2023, 2112.05341), ODHD (DAC 2022) and LifeHD (2403.04759) set
  thresholds from the distribution of in-class similarities.
- **Conformal prediction** (Angelopoulos & Bates 2107.07511; Bates et al. AoS 2023 conformal p-values):
  - Split CP is valid at any n, with α ≥ 1/(n+1).
  - Per-class (Mondrian) CP needs about ⌈1/α⌉−1 points per class. Otherwise, pool at the gUFO parent.
- **Recipe (inf):**
  1. Noise gate: z = sim₁·√D against Φ⁻¹(1−α/K). Below it, answer NONE OF THESE and fall back to gUFO.
     Record D, K and α.
  2. Run split conformal on SME-validated answers.
  3. Decide by set size: 1 means ACCEPT, 0 means NONE OF THESE, 2 or more means ASK (Jev or the SME, with the
     set as the candidate list).
  4. Choose α from the cost of a wrong accept.
  5. Recompute the quantiles after each SME batch, and watch drift per form family.
  6. Use Venn-Abers if Jev needs probabilities.

  This replaces hand-tuned thresholds under iladub CLAUDE.md §8.

## D. Literature: text encoding

**What exists:**

- **Language ID** with letter n-gram HDC reaches 97.4–97.8% on 21 languages.
  - Joshi, Halseth, Kanerva 2016: https://redwood.berkeley.edu/wp-content/uploads/2021/08/LanguageGeometry.pdf
  - Rahimi et al., ISLPED 2016, reaches 96.7% at about half the energy.
- **HyperEmbed** (arXiv 2003.01821): topic F1 on par with explicit n-grams, using about 100× less memory and
  running about 100× faster.
- **Intent classification** (arXiv 2010.05223): comparable to the state of the art.
- **Gaps:**
  - No head-to-head comparison of HDC against sentence embeddings.
  - No legal or long-document HDC study.
  - Nothing tests synonyms or negation directly.
- **Word order:** permutation (Sahlgren 2008) matches or beats BEAGLE convolution (Recchia 2015,
  PMC4405220).
- **Projecting a pretrained embedding** into HDC is thinly studied. It preserves geometry but adds no semantics.

**Traceability and cost:**

- Lexical scores split linearly per n-gram, so the top contributing n-grams can be listed.
- A projected embedding is opaque at its 768-d vector.
- Lexical encoding is integer add, multiply and roll, so it runs on a plain CPU. A 137M-parameter embedder costs
  per-clause transformer inference and adds a model artifact to version.

**Failure modes (inf):**

- Lexical bundles miss synonyms.
- They are near-blind to "shall not", because one token barely moves a bundle.
- Near-verbatim boilerplate is where they are strongest.

**Recommendation (inf):** a lexical MAP base made of:

- character 3–4-grams;
- word bigrams with permuted order;
- an explicit NEG/modal feature, e.g. bind(NEG, verb) for "shall not / unless / except".

A projected nomic embedding is an optional, separately weighted channel. Keep it only if the A/B below justifies
it, and report its score separately so explanations stay lexical.

**A/B design:**

- **Split:** hold out whole GAFTA forms, using the gold clause types.
- **Arms:**
  - (a) char n-grams;
  - (b) (a) plus permuted words plus NEG;
  - (c) projected embedding;
  - (d) (b) plus (c), sweeping the weight.
- **Baselines:** TF-IDF plus SVM; embedding plus logistic regression.
- **Metrics:**
  - macro-F1;
  - a minimal-pair contrast set (shall / shall not, Buyer / Seller, paraphrase);
  - the top-1 vs top-2 margin;
  - CPU p50/p95 latency;
  - attribution faithfulness: does deleting the top n-grams flip the label?
- **Decision rule:** adopt (b) unless (c) or (d) wins by at least 3 macro-F1 points, a margin set in advance.

## E. Literature: layout and continuous encoding

- **No HDC/VSA work exists on document layout, OCR reading order, forms or table structure recognition.** iladub
  would be new ground. The closest work is arXiv 2606.13871, which queries tables that are already structured.
- **Fractional power encoding:** z(x) = bˣ, and ⟨z(x), z(y)⟩ is a kernel K(x−y). The phase distribution sets the
  kernel shape (sinc or Gaussian).
  - Frady et al., VFA, arXiv 2109.03429.
  - torchhd provides `FractionalPower(distribution, bandwidth, vsa='FHRR')`, `Level`, `Thermometer` (for ordinal
    values) and `Sinusoid`. holovec has equivalents.
- **2D encoding:** Spatial Semantic Pointers, S(x, y) = Xˣ ⊛ Yʸ (Komer et al., CogSci 2019).
  - Region vectors and relational queries such as "below-left of 3" (Lu et al., CogSci 2019).
  - Factoring a scene into template ⊛ translation (Renner et al., NMI 2024, 2208.12880).
- **Thresholds become statistics:**
  - SSP similarity is a quasi kernel density estimate (Furlong & Eliasmith 2022/2023).
  - The bandwidth comes from the data, e.g. Silverman/Scott rules or cross-validation per page and per axis.
    This replaces gap factors, percentiles and 0.25×median.
- **Proposed uses (inf):**
  - **Contracts:**
    - Indentation levels are peaks of a kernel density estimate of left-edge x values, built as ΣFPE(x).
    - Clause depth is Thermometer-encoded and checked against the numbering grammar, so the semantics confirm
      the layout.
  - **Tables:**
    - Columns are peaks of the density estimate of token x-centres.
    - Header depth is FPE(y), with the bandwidth taken from row pitch.
    - Aggregates are proposed by layout and decided by arithmetic.
    - Repeats are high-similarity rows under Σ cell ⊛ S(col).
- **Caveats:**
  - Sinc side lobes cause aliasing, so prefer a Gaussian kernel.
  - Use D of about 1–4k.
  - First check that kernel-derived levels reproduce today's segmentation on the corpus, before any heuristic
    code is deleted.
