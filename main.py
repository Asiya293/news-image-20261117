#!/usr/bin/env python3
"""Sum up 17 November 2026's world news in one image.

Entry for the make.fun bounty "news-image-20261117". Running this program
writes a single 1024x1024 PNG poster to /output/entry.png (or to
$MAKEFUN_OUTPUT_DIR/entry.png when that variable is set, for local runs).

The poster is drawn entirely with the Python standard library: a tiny
5x7 pixel font, a small RGB canvas with shape primitives, and a PNG
writer built on zlib. There is no network access and no input, so every
run writes exactly the same bytes.

The stories shown are the day's verified headlines (17 Nov 2026):
  * Ukraine's 1,300-drone barrage hits the Crimea Bridge; Russia
    strikes two bridges in Kyiv in reply (Dawn, RNZ, Business Recorder).
  * US jets strike Iran's Qeshm Island in the Strait of Hormuz; a gas
    tanker burns off Oman and Iran drones a US radar in Bahrain
    (Reuters via Profile News, AFP via Korea Herald, Arab News).
  * The United States loses its measles elimination status after
    twelve months of uninterrupted spread, 5,412 cases (PAHO via
    Profile News and UN News; Dawn).
  * The COP31 draft deal in Antalya calls for accelerated action to
    exit fossil fuels (RNZ, AFP via Korea Herald).
  Plus a strip: Trump in Manila for the ASEAN summit, Robert
  Pattinson named the new James Bond, five EU states planning a
  Rwanda migrant-return hub, Wall Street sliding on AI stocks,
  Amazon losing 40 satellites in a failed launch, and the GTA VI
  launch countdown.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- font
# A 5x7 pixel font. Each glyph is seven rows; each row is a 5-bit
# number whose high bit is the leftmost pixel. Authored by hand for
# this entry so the program needs no font file at run time.

FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11100, 0b10010, 0b10001, 0b10001, 0b10001, 0b10010, 0b11100),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": (0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b01010, 0b10001),
    "Y": (0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0, 0b00100),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "+": (0, 0b00100, 0b00100, 0b01110, 0b00100, 0b00100, 0),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
    "•": (0, 0, 0b01110, 0b01110, 0b01110, 0, 0),
}

GLYPH_W = 5
GLYPH_H = 7


def normalize(text):
    """Map the few non-ASCII marks we use onto font glyphs."""
    return (
        text.replace("—", "-")
        .replace("–", "-")
        .replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .upper()
    )


# ------------------------------------------------------------- canvas

class Canvas:
    """A minimal RGB canvas with the shape primitives the poster needs."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.px = bytearray(bytes(colour) * (width * height))

    def set_px(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i : i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.px[i : i + len(row)] = row

    def frame_rect(self, x, y, w, h, thickness, colour):
        self.fill_rect(x, y, w, thickness, colour)
        self.fill_rect(x, y + h - thickness, w, thickness, colour)
        self.fill_rect(x, y, thickness, h, colour)
        self.fill_rect(x + w - thickness, y, thickness, h, colour)

    def line(self, x0, y0, x1, y1, colour, thickness=1):
        # Bresenham, stamped with a square brush of the given thickness.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = thickness // 2
        while True:
            self.fill_rect(x0 - r, y0 - r, thickness, thickness, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, radius, colour):
        r2 = radius * radius
        for yy in range(cy - radius, cy + radius + 1):
            dy = yy - cy
            span = int((r2 - dy * dy) ** 0.5)
            self.fill_rect(cx - span, yy, 2 * span + 1, 1, colour)

    def ring(self, cx, cy, radius, thickness, colour):
        for yy in range(cy - radius, cy + radius + 1):
            for xx in range(cx - radius, cx + radius + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (radius - thickness) ** 2 <= d2 <= radius * radius:
                    self.set_px(xx, yy, colour)

    def fill_polygon(self, points, colour):
        ys = [p[1] for p in points]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.fill_rect(
                    int(nodes[i]), yy, int(nodes[i + 1]) - int(nodes[i]) + 1, 1, colour
                )

    # ---------------------------------------------------------- text

    def text_width(self, text, scale, tracking=1):
        if not text:
            return 0
        return len(text) * (GLYPH_W + tracking) * scale - tracking * scale

    def draw_text(self, x, y, text, scale, colour, tracking=1):
        text = normalize(text)
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(GLYPH_H):
                bits = glyph[row]
                for col in range(GLYPH_W):
                    if bits & (1 << (GLYPH_W - 1 - col)):
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, colour
                        )
            cx += (GLYPH_W + tracking) * scale
        return cx - tracking * scale

    def draw_text_centred(self, cx, y, text, scale, colour, tracking=1):
        w = self.text_width(normalize(text), scale, tracking)
        return self.draw_text(cx - w // 2, y, text, scale, colour, tracking)

    def wrap(self, text, scale, max_width, tracking=1):
        words = normalize(text).split()
        lines = []
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if self.text_width(trial, scale, tracking) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines


def save_png(canvas, path):
    """Write the canvas as a PNG using only zlib and struct."""

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    raw = bytearray()
    stride = canvas.width * 3
    for yy in range(canvas.height):
        raw.append(0)  # filter type 0 on every scanline
        start = yy * stride
        raw += canvas.px[start : start + stride]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# ------------------------------------------------------------- poster

INK = (10, 22, 40)
PANEL = (17, 34, 57)
FRAME = (96, 116, 148)
WHITE = (245, 247, 250)
SUB = (168, 188, 214)
GOLD = (242, 193, 66)
CRIMSON = (190, 26, 48)
ORANGE = (214, 116, 24)
TEAL = (0, 150, 150)
GREEN = (46, 160, 74)

STORIES = [
    {
        "tag": "WAR IN EUROPE",
        "colour": CRIMSON,
        "headline": "UKRAINE'S 1,300-DRONE BARRAGE HITS CRIMEA BRIDGE",
        "sub": "RUSSIA HITS TWO KYIV BRIDGES IN REPLY",
        "icon": "bridge",
    },
    {
        "tag": "MIDDLE EAST",
        "colour": ORANGE,
        "headline": "US JETS STRIKE IRAN'S QESHM ISLAND",
        "sub": "TANKER ABLAZE OFF OMAN - 24 CREW RESCUED",
        "icon": "tanker",
    },
    {
        "tag": "HEALTH",
        "colour": TEAL,
        "headline": "US LOSES MEASLES-FREE STATUS",
        "sub": "5,412 CASES AFTER A YEAR OF NONSTOP SPREAD",
        "icon": "cross",
    },
    {
        "tag": "CLIMATE",
        "colour": GREEN,
        "headline": "COP31 DRAFT: SPEED UP EXIT FROM FOSSIL FUELS",
        "sub": "UN TALKS IN ANTALYA CALL FOR FASTER ACTION",
        "icon": "globe",
    },
]

ALSO = (
    "TRUMP IN MANILA FOR ASEAN SUMMIT • PATTINSON NAMED NEW JAMES BOND • "
    "FIVE EU STATES PLAN RWANDA MIGRANT HUB • WALL ST SLIDES ON AI STOCKS • "
    "AMAZON LOSES 40 SATELLITES • GTA VI COUNTDOWN: LAUNCH THURSDAY"
)


def icon_bridge(cv, x, y):
    # A bridge deck on two towers over waves, drones overhead.
    cv.fill_rect(x + 8, y + 58, 88, 6, WHITE)
    cv.fill_rect(x + 26, y + 30, 6, 34, WHITE)
    cv.fill_rect(x + 72, y + 30, 6, 34, WHITE)
    for t in range(0, 21):
        ax = x + 10 + t * 4
        ay = y + 58 - int(14 * (1 - ((t - 10) / 10) ** 2))
        cv.fill_rect(ax, ay, 4, 4, WHITE)
    for dx in (18, 52, 82):
        cv.line(x + dx - 5, y + 8, x + dx + 5, y + 18, WHITE, 3)
        cv.line(x + dx - 5, y + 18, x + dx + 5, y + 8, WHITE, 3)
    for wy in (78, 90):
        for wx in range(10, 90, 16):
            cv.line(x + wx, y + wy, x + wx + 8, y + wy - 5, WHITE, 3)
            cv.line(x + wx + 8, y + wy - 5, x + wx + 16, y + wy, WHITE, 3)


def icon_tanker(cv, x, y):
    # A tanker hull with containers and a flame above it.
    hull = [(x + 8, y + 66), (x + 96, y + 66), (x + 86, y + 84), (x + 18, y + 84)]
    cv.fill_polygon(hull, WHITE)
    cv.fill_rect(x + 22, y + 50, 26, 16, WHITE)
    cv.fill_rect(x + 54, y + 50, 26, 16, WHITE)
    flame = [
        (x + 52, y + 6),
        (x + 64, y + 24),
        (x + 60, y + 38),
        (x + 52, y + 44),
        (x + 44, y + 38),
        (x + 40, y + 24),
    ]
    cv.fill_polygon(flame, GOLD)
    cv.fill_circle(x + 52, y + 34, 6, ORANGE)


def icon_cross(cv, x, y):
    # A bold medical cross inside a ring.
    cv.ring(x + 52, y + 52, 46, 7, WHITE)
    cv.fill_rect(x + 42, y + 26, 20, 52, WHITE)
    cv.fill_rect(x + 26, y + 42, 52, 20, WHITE)


def icon_globe(cv, x, y):
    # A globe with meridians and a leaf across it.
    cv.ring(x + 52, y + 52, 46, 6, WHITE)
    cv.line(x + 6, y + 52, x + 98, y + 52, WHITE, 4)
    cv.line(x + 52, y + 6, x + 52, y + 98, WHITE, 4)
    for off in (24, -24):
        cv.line(x + 52 + off, y + 12, x + 52 + off, y + 92, WHITE, 3)
    leaf = [(x + 30, y + 78), (x + 44, y + 44), (x + 78, y + 30),
            (x + 74, y + 66), (x + 56, y + 80)]
    cv.fill_polygon(leaf, (140, 230, 150))
    cv.line(x + 34, y + 76, x + 72, y + 36, GREEN, 4)


ICONS = {
    "bridge": icon_bridge,
    "tanker": icon_tanker,
    "cross": icon_cross,
    "globe": icon_globe,
}


def build_poster():
    cv = Canvas(WIDTH, HEIGHT, INK)
    cv.frame_rect(14, 14, WIDTH - 28, HEIGHT - 28, 5, FRAME)

    # Masthead.
    cv.fill_rect(36, 36, 952, 80, CRIMSON)
    cv.draw_text_centred(512, 55, "THE WORLD IN ONE DAY", 6, WHITE)

    # The date, the point of the whole picture.
    cv.draw_text_centred(512, 128, "TUESDAY", 5, GOLD)
    cv.draw_text_centred(512, 168, "17 NOVEMBER 2026", 9, WHITE)
    cv.draw_text_centred(512, 242, "THE DAY'S TOP STORIES IN ONE PICTURE", 4, SUB)
    cv.fill_rect(36, 284, 952, 3, GOLD)

    # Four story rows.
    row_y = 296
    for story in STORIES:
        cv.fill_rect(36, row_y, 952, 136, PANEL)
        cv.fill_rect(52, row_y + 16, 104, 104, story["colour"])
        ICONS[story["icon"]](cv, 52, row_y + 16)
        cv.draw_text(180, row_y + 10, story["tag"], 3, story["colour"])
        lines = cv.wrap(story["headline"], 5, 792)
        for i, line in enumerate(lines[:2]):
            cv.draw_text(180, row_y + 36 + i * 40, line, 5, WHITE)
        cv.draw_text(180, row_y + 114, story["sub"], 3, SUB)
        row_y += 144

    # The rest of the day, in small print.
    cv.draw_text(36, 878, "ALSO ON TUESDAY:", 3, GOLD)
    items = cv.wrap(ALSO, 3, 952)
    for i, line in enumerate(items[:4]):
        cv.draw_text(36, 902 + i * 23, line, 3, WHITE)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = save_png(build_poster(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
