import re
from elasticsearch import Elasticsearch
from elasticsearch import helpers

def extract_aciklamalar(text):
    """
    Grab the AÇIKLAMALAR section, regardless of Roman numeral prefix.
    """
    match = re.search(r"[IVXLCDM]+\.\-\s*AÇIKLAMALAR(.*?)(?:[IVXLCDM]+\.\-|$)", 
                      text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_speech_summaries(aciklamalar_text):
    """Parse the list of speech summaries from the AÇIKLAMALAR section (multiline safe)."""
    pattern = re.compile(
        r"(\d+)\.\-\s*(.*?)\s+Milletvekili\s+(.*?)’?(?:ın|in|un|ün|nın|nin),\s*(.*?)açıklaması\s+(\d+(?::\d+)?)",
        re.UNICODE | re.IGNORECASE | re.DOTALL
    )

    speeches = []
    for match in pattern.finditer(aciklamalar_text):
        speeches.append({
            "speech_no": match.group(1),
            "province": match.group(2).strip(),
            "speech_giver": match.group(3).strip(),
            "speech_title": re.sub(r"\s+", " ", match.group(4)).strip(),  # normalize whitespace
            "page_ref": match.group(5)
        })
    return speeches

def extract_full_speech(text, speech_no, province, speaker):
    """
    Find the full speech: locate the *second occurrence* of the summary
    and grab everything until the next summary or next section.
    """
    start_pattern = re.compile(
        rf"{speech_no}\.\-\s*{province}\s+Milletvekili\s+{re.escape(speaker)}.*?açıklaması",
        re.UNICODE | re.DOTALL
    )

    matches = list(start_pattern.finditer(text))
    if len(matches) < 2:
        return None  # didn't find the repeated occurrence

    # Take the second occurrence (real speech)
    start_match = matches[1]
    start_idx = start_match.end()

    # End marker: next speech or next Roman numeral section
    end_pattern = re.compile(
        r"(?:^\s*\d+\.\-\s*.*?Milletvekili|^[IVXLCDM]+\.\-)",
        re.MULTILINE | re.UNICODE
    )

    end_match = end_pattern.search(text, start_idx)
    end_idx = end_match.start() if end_match else len(text)

    speech_block = text[start_idx:end_idx].strip()
    return speech_block if speech_block else None

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    with open("TPT/TXTs/d28-y1_txts/tbmm28002014.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()
        
    es = Elasticsearch(hosts=["http://localhost:9200"])
    index_name = "parliament_speeches"
    session_id = "d28-y1" #to be automated 
    actions = [] #for bulk insert

    # Step 1: extract summaries
    aciklamalar = extract_aciklamalar(raw_text)
    print("Extracted AÇIKLAMALAR section:")
    print(aciklamalar[:1000] + "...\n")  # print first 500 chars of the section
    summaries = extract_speech_summaries(aciklamalar)
    print(f"Found {len(summaries)} speech summaries.\n")

    # Step 2: attach full speech content
    for s in summaries:
        speech_text = extract_full_speech(raw_text, s["speech_no"], s["province"], s["speech_giver"])
        s["content_preview"] = speech_text[:100] + "..." if speech_text else None  # only preview first 500 chars
        s["content_length"] = len(speech_text) if speech_text else 0

    # Step 3: inspect
    for s in summaries:
        print("="*80)
        print(f"Speech {s['speech_no']} | {s['speech_giver']} ({s['province']})")
        print(f"Title : {s['speech_title']}")
        print(f"Page  : {s['page_ref']}")
        print(f"Chars : {s['content_length']}")
        print("--- Content Preview ---")
        print(s['content_preview'])
        doc = {
        "_index": index_name,
        "_id": f"{session_id}-{s['speech_no']}",  # deterministic unique ID
        "_source": {
            "session_id": session_id,
            "speech_no": int(s["speech_no"]),
            "province": s["province"],
            "speech_giver": s["speech_giver"],
            "speech_title": s["speech_title"],
            "page_ref": s["page_ref"],
            "content": speech_text if speech_text else ""
        }
    }
        actions.append(doc)

    # Bulk insert
    if actions:
        success, failed = helpers.bulk(es, actions, stats_only=True)
        print(f"✅ Indexed {success} documents, ❌ failed {failed}")
    else:
        print("⚠️ No documents to index")