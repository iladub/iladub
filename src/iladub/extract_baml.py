"""Multi-agent BAML extraction: run focused, typed extractors in parallel and
merge their outputs into one OfferExtraction. The LLM is boxed by BAML's types."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from baml_client import sync_client


@dataclass(frozen=True)
class CodedConcept:
    value: str
    source_quote: str
    confidence: float


@dataclass
class OfferExtraction:
    organ: CodedConcept | None = None
    ejection_fraction: CodedConcept | None = None
    cause_of_death: CodedConcept | None = None
    size_metric: CodedConcept | None = None
    abo_group: CodedConcept | None = None
    hla_typing: CodedConcept | None = None
    serology: CodedConcept | None = None
    projected_transport_minutes: CodedConcept | None = None


def _cc(obj) -> CodedConcept | None:
    if obj is None:
        return None
    return CodedConcept(value=obj.value, source_quote=obj.source_quote,
                        confidence=obj.confidence)


def extract_offer(doc_text: str) -> OfferExtraction:
    b = sync_client.b
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_clin = pool.submit(b.ExtractDonorClinical, doc_text)
        f_imm = pool.submit(b.ExtractImmunology, doc_text)
        f_log = pool.submit(b.ExtractLogistics, doc_text)
        clin, imm, log = f_clin.result(), f_imm.result(), f_log.result()
    return OfferExtraction(
        organ=_cc(clin.organ),
        ejection_fraction=_cc(clin.ejectionFraction),
        cause_of_death=_cc(clin.causeOfDeath),
        size_metric=_cc(clin.sizeMetric),
        abo_group=_cc(imm.aboGroup),
        hla_typing=_cc(imm.hlaTyping),
        serology=_cc(imm.serology),
        projected_transport_minutes=_cc(log.projectedTransportMinutes),
    )
