#!/usr/bin/env python3
"""Bulk-fix dimensions on local raster <img> elements without third-party packages.
Place this file beside index.html in the site's public_html folder and run it.
"""
from __future__ import annotations
import html as html_lib
import math
import re
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(r'''\s+([a-zA-Z_:][\w:.-]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))''')
LOGO_NAMES = {"rayyanlogo.png"}
EXCLUDED_DIRS = {".git", "node_modules", "_image_fix_backup", "image_fix_backup", "backups", "backup"}


def attrs(tag: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for m in ATTR_RE.finditer(tag):
        name = m.group(1).lower()
        value = next((x for x in m.groups()[1:] if x is not None), "")
        result.setdefault(name, html_lib.unescape(value))
    return result


def get_attr(tag: str, name: str) -> str | None:
    return attrs(tag).get(name.lower())


def set_attr(tag: str, name: str, value: str) -> str:
    pattern = re.compile(rf'''\s+{re.escape(name)}\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)''', re.IGNORECASE)
    replacement = f' {name}="{value}"'
    seen = False
    def sub(match: re.Match[str]) -> str:
        nonlocal seen
        if seen:
            return ""
        seen = True
        return replacement
    updated = pattern.sub(sub, tag)
    if not seen:
        pos = updated.rfind("/>")
        if pos >= 0:
            updated = updated[:pos].rstrip() + replacement + " " + updated[pos:]
        else:
            pos = updated.rfind(">")
            if pos >= 0:
                updated = updated[:pos].rstrip() + replacement + updated[pos:]
    return updated


def remove_attr(tag: str, name: str) -> str:
    pattern = re.compile(rf'''\s+{re.escape(name)}\s*(?:=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?''', re.IGNORECASE)
    return pattern.sub("", tag)


def image_dimensions(path: Path) -> tuple[int, int] | None:
    """Read common image dimensions using only Python's standard library."""
    try:
        with path.open("rb") as f:
            head = f.read(32)
            if len(head) >= 24 and head[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", head[16:24])
                return (w, h) if w > 0 and h > 0 else None
            if len(head) >= 10 and head[:6] in (b"GIF87a", b"GIF89a"):
                w, h = struct.unpack("<HH", head[6:10])
                return (w, h) if w > 0 and h > 0 else None
            if len(head) >= 26 and head[:2] == b"BM":
                dib_size = struct.unpack("<I", head[14:18])[0]
                if dib_size == 12:  # BITMAPCOREHEADER
                    w, h = struct.unpack("<HH", head[18:22])
                elif dib_size >= 40 and len(head) >= 26:
                    w, h = struct.unpack("<ii", head[18:26])
                    h = abs(h)
                else:
                    return None
                return (w, h) if w > 0 and h > 0 else None
            if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                kind = head[12:16]
                # Re-read enough bytes for all common WebP headers.
                if kind == b"VP8X":
                    with path.open("rb") as wf:
                        wf.seek(24)
                        dims = wf.read(6)
                    if len(dims) == 6:
                        w = 1 + int.from_bytes(dims[0:3], "little")
                        h = 1 + int.from_bytes(dims[3:6], "little")
                        return (w, h) if w > 0 and h > 0 else None
                if kind == b"VP8 ":
                    with path.open("rb") as wf:
                        wf.seek(26)
                        dims = wf.read(4)
                    if len(dims) == 4:
                        w = int.from_bytes(dims[0:2], "little") & 0x3FFF
                        h = int.from_bytes(dims[2:4], "little") & 0x3FFF
                        return (w, h) if w > 0 and h > 0 else None
                if kind == b"VP8L":
                    with path.open("rb") as wf:
                        wf.seek(20)
                        dims = wf.read(5)
                    if len(dims) == 5 and dims[0] == 0x2F:
                        w = 1 + dims[1] + ((dims[2] & 0x3F) << 8)
                        h = 1 + ((dims[2] & 0xC0) >> 6) + (dims[3] << 2) + ((dims[4] & 0x0F) << 10)
                        return (w, h) if w > 0 and h > 0 else None
            if len(head) >= 8 and head[:4] == b"\x00\x00\x01\x00":  # ICO
                width = head[6] or 256
                height = head[7] or 256
                return (width, height)
            if len(head) >= 4 and head[:2] == b"\xff\xd8":  # JPEG marker stream
                f.seek(2)
                sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
                while True:
                    byte = f.read(1)
                    if not byte:
                        break
                    if byte != b"\xff":
                        continue
                    marker_byte = f.read(1)
                    while marker_byte == b"\xff":
                        marker_byte = f.read(1)
                    if not marker_byte:
                        break
                    marker = marker_byte[0]
                    if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
                        continue
                    length_bytes = f.read(2)
                    if len(length_bytes) != 2:
                        break
                    segment_length = struct.unpack(">H", length_bytes)[0]
                    if segment_length < 2:
                        break
                    if marker in sof_markers:
                        sof = f.read(5)
                        if len(sof) < 5:
                            break
                        h = int.from_bytes(sof[1:3], "big")
                        w = int.from_bytes(sof[3:5], "big")
                        return (w, h) if w > 0 and h > 0 else None
                    # Length includes its own two bytes; we've already read those.
                    f.seek(segment_length - 2, 1)
                    if marker == 0xDA:  # start of scan before any supported SOF found
                        break
    except (OSError, ValueError, struct.error):
        return None
    return None


def resolve_local_image(src: str, html_file: Path) -> Path | None:
    src = html_lib.unescape(src.strip())
    if not src or src.startswith(("data:", "blob:", "//", "#")):
        return None
    parsed = urlsplit(src)
    if parsed.scheme.lower() in ("http", "https", "data", "blob", "file"):
        return None
    raw_path = unquote(parsed.path).replace("\\", "/")
    if not raw_path:
        return None
    candidates: list[Path] = []
    if raw_path.startswith("/"):
        candidates.append(ROOT / raw_path.lstrip("/"))
    else:
        candidates.append(html_file.parent / raw_path)
        candidates.append(ROOT / raw_path)
        candidates.append(ROOT / raw_path.lstrip("./"))
    root = ROOT.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            if not resolved.is_relative_to(root):
                continue
        except (OSError, ValueError):
            continue
        if resolved.is_file():
            return resolved
    return None


def dim_tag(tag: str, actual_w: int, actual_h: int, is_logo: bool) -> tuple[str, list[str]]:
    actions: list[str] = []
    old_w_txt, old_h_txt = get_attr(tag, "width"), get_attr(tag, "height")
    try:
        old_w = int(old_w_txt) if old_w_txt and int(old_w_txt) > 0 else None
    except ValueError:
        old_w = None
    try:
        old_h = int(old_h_txt) if old_h_txt and int(old_h_txt) > 0 else None
    except ValueError:
        old_h = None

    # The Rayyan logo should reserve its correct 4:1 ratio and not lazy-load above the fold.
    if is_logo:
        if old_w != actual_w or old_h != actual_h:
            tag = set_attr(tag, "width", str(actual_w))
            tag = set_attr(tag, "height", str(actual_h))
            actions.append(f"logo dimensions corrected to {actual_w}x{actual_h}")
        if (get_attr(tag, "loading") or "").lower() == "lazy":
            tag = set_attr(tag, "loading", "eager")
            actions.append("logo lazy-loading disabled")
        decoding_values = re.findall(r'''\sdecoding\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))''', tag, re.IGNORECASE)
        if len(decoding_values) > 1:
            tag = set_attr(tag, "decoding", next((x for x in decoding_values[0] if x), "async"))
            actions.append("duplicate decoding attribute removed")
        return tag, actions

    if old_w is None and old_h is None:
        tag = set_attr(tag, "width", str(actual_w))
        tag = set_attr(tag, "height", str(actual_h))
        actions.append(f"missing dimensions added as {actual_w}x{actual_h}")
    elif old_w is None and old_h is not None:
        derived_w = max(1, round(actual_w * old_h / actual_h))
        tag = set_attr(tag, "width", str(derived_w))
        actions.append(f"missing width added as {derived_w}")
    elif old_h is None and old_w is not None:
        derived_h = max(1, round(actual_h * old_w / actual_w))
        tag = set_attr(tag, "height", str(derived_h))
        actions.append(f"missing height added as {derived_h}")
    else:
        ratio_actual = actual_w / actual_h
        ratio_declared = old_w / old_h
        if abs(math.log(ratio_declared / ratio_actual)) > 0.04:
            tag = set_attr(tag, "width", str(actual_w))
            tag = set_attr(tag, "height", str(actual_h))
            actions.append(f"mismatched ratio corrected to {actual_w}x{actual_h}")
    return tag, actions


def main() -> None:
    if not (ROOT / "index.html").exists():
        print("لم أجد index.html بجانب الأداة. ضع الأداة داخل Fin/public_html بجانب index.html.")
        sys.exit(2)
    html_files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm"}
                  and not any(part.lower() in EXCLUDED_DIRS for part in p.relative_to(ROOT).parts)
                  and not p.relative_to(ROOT).as_posix().startswith("wp-json/")]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = ROOT.parent / f"{ROOT.name}_image_fix_backup_v2_{stamp}"
    report_path = ROOT.parent / f"{ROOT.name}_image_fix_report_v2_{stamp}.txt"
    changed_files = 0
    changed_tags = 0
    logo_tags_found = 0
    logo_tags_changed = 0
    changes: list[str] = []
    missing_files: set[str] = set()
    unsupported_files: set[str] = set()
    scanned_tags = 0
    for file in html_files:
        try:
            original = file.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            try:
                original = file.read_text(encoding="utf-8")
            except Exception as exc:
                changes.append(f"SKIPPED unreadable file: {file.relative_to(ROOT)} ({exc})")
                continue
        relative = file.relative_to(ROOT).as_posix()
        file_actions: list[str] = []
        def process(match: re.Match[str]) -> str:
            nonlocal changed_tags, scanned_tags, logo_tags_found, logo_tags_changed
            tag = match.group(0)
            info = attrs(tag)
            scanned_tags += 1
            candidates = [info.get(key, "") for key in ("src", "data-src", "data-lazy-src", "data-original", "data-echo")]
            image_path = None
            used_src = ""
            for candidate in candidates:
                if not candidate:
                    continue
                image_path = resolve_local_image(candidate, file)
                if image_path is not None:
                    used_src = candidate
                    break
            if image_path is None:
                src = info.get("src", "")
                if src and not src.startswith(("http://", "https://", "data:", "blob:")):
                    missing_files.add(f"{relative} | {src}")
                return tag
            if image_path.suffix.lower() == ".svg":
                return tag
            dims = image_dimensions(image_path)
            if not dims:
                unsupported_files.add(f"{relative} | {used_src} | {image_path.name}")
                return tag
            actual_w, actual_h = dims
            if actual_w <= 0 or actual_h <= 0:
                return tag
            is_logo = image_path.name.lower() in LOGO_NAMES or Path(urlsplit(used_src).path).name.lower() in LOGO_NAMES
            if is_logo:
                logo_tags_found += 1
            new_tag, actions = dim_tag(tag, actual_w, actual_h, is_logo)
            if actions:
                changed_tags += 1
                if is_logo:
                    logo_tags_changed += 1
                file_actions.extend([f"  {used_src}: {action}" for action in actions])
            return new_tag

        updated = IMG_RE.sub(process, original)
        if updated != original:
            backup_file = backup_root / file.relative_to(ROOT)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, backup_file)
            file.write_text(updated, encoding="utf-8", newline="")
            changed_files += 1
            changes.append(f"UPDATED {relative}")
            changes.extend(file_actions)
    if not changes:
        changes = ["No HTML edits were necessary."]
    report = [
        "Rayyan site image dimensions v2 report (no third-party packages required)",
        f"Website folder: {ROOT}",
        f"HTML pages scanned: {len(html_files)}",
        f"img elements scanned: {scanned_tags}",
        f"HTML files changed: {changed_files}",
        f"img elements updated: {changed_tags}",
        f"Rayyan logo img elements found: {logo_tags_found}",
        f"Rayyan logo img elements updated: {logo_tags_changed}",
        f"Backup folder (outside public_html): {backup_root if changed_files else 'not created'}",
        "",
        "CHANGES:", *changes, "",
        "Local image paths not found (review manually; the script does not rename files):",
        *(sorted(missing_files) if missing_files else ["None found."]), "",
        "Image formats whose dimensions could not be read automatically:",
        *(sorted(unsupported_files) if unsupported_files else ["None found."]), "",
        "Notes:",
        "- Uses Python standard library only; Pillow/pip are NOT required.",
        "- Reads dimensions for PNG, JPEG, GIF, WebP, BMP, and ICO files.",
        "- SVG files, CSS background images, and remote images are not changed.",
        "- rayyanlogo.png is set to its file dimensions and loading=lazy is changed to loading=eager.",
        "- Review the website on desktop and mobile after running. Restore changed files from the backup folder if needed.",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    print("\nاكتمل فحص وتعديل أبعاد الصور.")
    print("ملاحظة: لا تحتاج إلى تثبيت Pillow أو أي مكتبة إضافية.")
    print(f"صفحات HTML المفحوصة: {len(html_files)}")
    print(f"الصفحات المعدّلة: {changed_files}")
    print(f"عناصر الصور المعدّلة: {changed_tags}")
    print(f"عناصر شعار الريان التي تم العثور عليها: {logo_tags_found}")
    print(f"عناصر شعار الريان التي تم تعديلها: {logo_tags_changed}")
    print(f"تقرير النتائج: {report_path}")
    if changed_files:
        print(f"نسخة احتياطية للملفات المعدّلة: {backup_root}")
    if missing_files:
        print(f"هناك {len(missing_files)} مسار صورة محلي لم يتم العثور عليه؛ راجع التقرير.")
    if unsupported_files:
        print(f"هناك {len(unsupported_files)} صورة تعذرت قراءة أبعادها تلقائيًا؛ راجع التقرير.")
    print("افتح الموقع عبر Live Server واختبر الصور على الهاتف والحاسوب قبل رفعه.")

if __name__ == "__main__":
    main()
