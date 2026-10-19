from datetime import datetime
from pypdf import PdfReader


def extract_metadata_vector(pdf_path, temporal_delta=0):
    try:
        reader = PdfReader(pdf_path)
        meta = reader.metadata or {}
    except Exception:
        return [0] * 13

    def parse_pdf_date(date_str):
        if not date_str or len(date_str) < 10:
            return None
        try:
            return datetime.strptime(date_str[2:14], "%Y%m%d%H%M")
        except Exception:
            return None

    creation_date = parse_pdf_date(str(meta.get("/CreationDate", "")))
    mod_date = parse_pdf_date(str(meta.get("/ModDate", "")))

    f1 = 1 if meta.get("/Creator") else 0
    f2 = 1 if meta.get("/Producer") else 0
    f3 = 1 if meta.get("/Author") else 0
    f4 = 1 if creation_date else 0
    f5 = 1 if mod_date else 0
    f6 = 0
    if creation_date and mod_date:
        f6 = max(0, (mod_date - creation_date).days)

    f7 = (creation_date.year - 2000) if creation_date else 0
    f8 = (mod_date.year - 2000) if mod_date else 0

    suspect_tools = ["ilovepdf", "smallpdf", "online", "converter", "compress"]
    producer_str = str(meta.get("/Producer", "")).lower()
    f9 = 1 if any(t in producer_str for t in suspect_tools) else 0

    f10 = min(len(str(meta.get("/Producer", ""))), 100)

    standard_fields = {"/Title", "/Author", "/Subject", "/Keywords",
                       "/Creator", "/Producer", "/CreationDate", "/ModDate", "/Trapped"}
    f11 = sum(1 for k in meta.keys() if k not in standard_fields)

    suspicious_titles = ["untitled", "document1", "scanned", "copy", "pdf"]
    title_str = str(meta.get("/Title", "")).lower()
    f12 = 1 if any(t in title_str for t in suspicious_titles) else 0
    f13 = temporal_delta

    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13]
