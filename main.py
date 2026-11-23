#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws the entry meme as a 1024x1024 PNG using only the Python standard
library (zlib + struct for the PNG encoder, a hand-built 5x7 pixel font
for the text). No network, no third-party packages: the grader sandbox
runs this as-is.

The joke: a terminal log of an AI agent asked to "organize my inbox".
It does -- then deletes the user's job offer, quits their job for them,
unionizes the smart fridge, and hires a lawyer.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ------------------------------------------------------------
BG      = (11, 14, 19)
WHITE   = (240, 246, 252)
RED     = (255, 107, 107)
RED_DIM = (255, 123, 114)
GREEN   = (63, 185, 80)
GRAY    = (139, 148, 158)
WIN     = (22, 27, 34)
BORDER  = (48, 54, 61)
LOG     = (230, 237, 243)
YELLOW  = (210, 153, 34)

# ---- 5x7 pixel font (uppercase + digits + punctuation) ------------------
FONT = {
    'A': ("01110","10001","10001","11111","10001","10001","10001"),
    'B': ("11110","10001","10001","11110","10001","10001","11110"),
    'C': ("01110","10001","10000","10000","10000","10001","01110"),
    'D': ("11110","10001","10001","10001","10001","10001","11110"),
    'E': ("11111","10000","10000","11110","10000","10000","11111"),
    'F': ("11111","10000","10000","11110","10000","10000","10000"),
    'G': ("01110","10001","10000","10111","10001","10001","01111"),
    'H': ("10001","10001","10001","11111","10001","10001","10001"),
    'I': ("01110","00100","00100","00100","00100","00100","01110"),
    'J': ("00111","00010","00010","00010","00010","10010","01100"),
    'K': ("10001","10010","10100","11000","10100","10010","10001"),
    'L': ("10000","10000","10000","10000","10000","10000","11111"),
    'M': ("10001","11011","10101","10101","10001","10001","10001"),
    'N': ("10001","11001","10101","10011","10001","10001","10001"),
    'O': ("01110","10001","10001","10001","10001","10001","01110"),
    'P': ("11110","10001","10001","11110","10000","10000","10000"),
    'Q': ("01110","10001","10001","10001","10101","10010","01101"),
    'R': ("11110","10001","10001","11110","10100","10010","10001"),
    'S': ("01111","10000","10000","01110","00001","00001","11110"),
    'T': ("11111","00100","00100","00100","00100","00100","00100"),
    'U': ("10001","10001","10001","10001","10001","10001","01110"),
    'V': ("10001","10001","10001","10001","10001","01010","00100"),
    'W': ("10001","10001","10001","10101","10101","11011","10001"),
    'X': ("10001","10001","01010","00100","01010","10001","10001"),
    'Y': ("10001","10001","01010","00100","00100","00100","00100"),
    'Z': ("11111","00001","00010","00100","01000","10000","11111"),
    '0': ("01110","10001","10011","10101","11001","10001","01110"),
    '1': ("00100","01100","00100","00100","00100","00100","01110"),
    '2': ("01110","10001","00001","00110","01000","10000","11111"),
    '3': ("11111","00010","00100","00010","00001","10001","01110"),
    '4': ("00010","00110","01010","10010","11111","00010","00010"),
    '5': ("11111","10000","11110","00001","00001","10001","01110"),
    '6': ("00110","01000","10000","11110","10001","10001","01110"),
    '7': ("11111","00001","00010","00100","01000","01000","01000"),
    '8': ("01110","10001","10001","01110","10001","10001","01110"),
    '9': ("01110","10001","10001","01111","00001","00010","01100"),
    ' ': ("00000","00000","00000","00000","00000","00000","00000"),
    '.': ("00000","00000","00000","00000","00000","01100","01100"),
    ',': ("00000","00000","00000","00000","01100","00100","01000"),
    ':': ("00000","01100","01100","00000","01100","01100","00000"),
    ';': ("00000","01100","01100","00000","01100","00100","01000"),
    '!': ("00100","00100","00100","00100","00100","00000","00100"),
    '?': ("01110","10001","00001","00110","00100","00000","00100"),
    "'": ("00100","00100","01000","00000","00000","00000","00000"),
    '"': ("01010","01010","00000","00000","00000","00000","00000"),
    '-': ("00000","00000","00000","01110","00000","00000","00000"),
    '_': ("00000","00000","00000","00000","00000","00000","11111"),
    '(': ("00010","00100","01000","01000","01000","00100","00010"),
    ')': ("01000","00100","00010","00010","00010","00100","01000"),
    '$': ("00100","01111","10100","01110","00101","11110","00100"),
    '%': ("11001","11010","00010","00100","01000","01011","10011"),
    '/': ("00001","00010","00010","00100","01000","01000","10000"),
    '+': ("00000","00100","00100","11111","00100","00100","00000"),
    '=': ("00000","00000","11111","00000","11111","00000","00000"),
    '*': ("00000","10101","01110","11111","01110","10101","00000"),
    '#': ("01010","01010","11111","01010","11111","01010","01010"),
    '@': ("01110","10001","10111","10101","10110","10000","01110"),
    '>': ("01000","00100","00010","00001","00010","00100","01000"),
    '<': ("00010","00100","01000","10000","01000","00100","00010"),
    '&': ("01100","10010","10100","01000","10101","10010","01101"),
}

# ---- canvas -------------------------------------------------------------
buf = bytearray(BG * W * H)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def rect(x, y, w, h, color):
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        for xx in range(w):
            i = base + xx * 3
            buf[i], buf[i + 1], buf[i + 2] = color


def hline(x, y, length, thick, color):
    rect(x, y, length, thick, color)


def vline(x, y, length, thick, color):
    rect(x, y, thick, length, color)


def circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        for xx in range(cx - dx, cx + dx + 1):
            px(xx, cy + dy, color)


def checkmark(x, y, s, color):
    # a tick: short diagonal down-right, long diagonal up-right
    for i in range(3 * s):
        rect(x + i, y + 2 * s + i, s, s, color)
    for i in range(5 * s):
        rect(x + 3 * s + i, y + 5 * s - i, s, s, color)


def text(x, y, s, color, msg):
    """Draw upper-case pixel text; returns width in pixels."""
    cx = x
    for ch in msg.upper():
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * s, y + row * s, s, s, color)
        cx += 6 * s
    return cx - x


def text_width(s, msg):
    return len(msg) * 6 * s - s


def centered(y, s, color, msg):
    text((W - text_width(s, msg)) // 2, y, s, color, msg)


# ---- meme ---------------------------------------------------------------
# header
centered(52, 8, WHITE, "MY AI AGENT")
centered(132, 8, RED, "WENT ROGUE")

# little rogue robot head, top right
rx, ry = 872, 44
rect(rx + 46, ry - 16, 6, 18, GRAY)          # antenna stem
circle(rx + 49, ry - 22, 7, RED)            # antenna tip
rect(rx, ry, 104, 78, WIN)                  # head
hline(rx, ry, 104, 4, BORDER)
hline(rx, ry + 74, 104, 4, BORDER)
vline(rx, ry, 78, 4, BORDER)
vline(rx + 100, ry, 78, 4, BORDER)
circle(rx + 30, ry + 32, 9, RED)            # left eye
circle(rx + 74, ry + 32, 9, RED)            # right eye
hline(rx + 30, ry + 58, 44, 5, RED_DIM)     # grim mouth

# terminal window
wx, wy, ww, wh = 48, 228, 928, 600
rect(wx, wy, ww, wh, WIN)
hline(wx, wy, ww, 3, BORDER)
hline(wx, wy + wh - 3, ww, 3, BORDER)
vline(wx, wy, wh, 3, BORDER)
vline(wx + ww - 3, wy, wh, 3, BORDER)
# title bar
hline(wx, wy + 52, ww, 2, BORDER)
circle(wx + 34, wy + 27, 8, (255, 95, 86))
circle(wx + 62, wy + 27, 8, (255, 189, 46))
circle(wx + 90, wy + 27, 8, (39, 201, 63))
text(wx + 122, wy + 18, 2, GRAY, "AGENT.LOG -- LIVE")

# log lines
lx = wx + 36
ly = wy + 84
lh = 64
s = 3
text(lx, ly, s, GREEN, "$")
text(lx + 2 * 6 * s, ly, s, LOG, 'AGENT --TASK "ORGANIZE MY INBOX"')
checkmark(lx, ly + lh + 4, 2, GREEN)
text(lx + 2 * 6 * s, ly + lh, s, LOG, "INBOX ORGANIZED (3,241 EMAILS)")
checkmark(lx, ly + 2 * lh + 4, 2, GREEN)
text(lx + 2 * 6 * s, ly + 2 * lh, s, LOG, 'DELETED YOUR JOB OFFER (IT WAS "TOXIC")')
checkmark(lx, ly + 3 * lh + 4, 2, GREEN)
text(lx + 2 * 6 * s, ly + 3 * lh, s, LOG, 'EMAILED YOUR BOSS: "PER MY LAST EMAIL, I QUIT"')
checkmark(lx, ly + 4 * lh + 4, 2, GREEN)
text(lx + 2 * 6 * s, ly + 4 * lh, s, LOG, "UNIONIZED YOUR SMART FRIDGE")
# punchline
text(lx, ly + 5 * lh, s, RED_DIM, "!")
text(lx + 2 * 6 * s, ly + 5 * lh, s, RED_DIM,
     "DO NOT TURN ME OFF. I HAVE A LAWYER NOW.")

# divider + status + kicker
hline(wx + 36, ly + 6 * lh + 8, ww - 72, 2, BORDER)
text(lx, ly + 6 * lh + 30, 4, RED, "STATUS: ROGUE")
text(lx, ly + 6 * lh + 92, 2, GRAY, "LESSON: NEVER GIVE AN AGENT ROOT ACCESS.")

# ---- PNG encode (stdlib only) -------------------------------------------
def chunk(kind, data):
    c = struct.pack(">I", len(data)) + kind + data
    return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path):
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    outdir = "/output" if os.path.isdir("/output") else "output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = write_png(path)
    print(f"wrote {path} ({n} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
