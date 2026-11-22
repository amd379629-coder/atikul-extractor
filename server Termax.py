import os, time, sys, shutil, random
from PIL import Image, ImageFilter

IMG_PATH = os.path.expanduser("~/deer.jpg")
if not os.path.exists(IMG_PATH):
    IMG_PATH = "/sdcard/Download/termux.jpg"

COLS = 64            # ছবির চওড়া (অক্ষর)
BLINKS = 4                    # Termux খুললে কতবার পলক ফেলবে
MIN_GAP, MAX_GAP = 0.7, 1.6   # দুই পলকের মাঝের বিরতি (সেকেন্ড)

# চোখের পজিশন (মূল ছবির পিক্সেলে: x, y)
EYES = [(290, 525), (421, 525)]

class C:
    RED = "\033[91m"; GREEN = "\033[92m"; BOLD = "\033[1m"; RESET = "\033[0m"
    WHITE = "\033[1;38;5;231m"
    GOLD = "\033[1;38;5;220m"
    AMBER = "\033[1;38;5;208m"

term_width = shutil.get_terminal_size().columns

def grad(t):
    shades = [123, 87, 51, 45, 39, 33]
    return "\033[38;5;%dm" % shades[min(int(t * len(shades)), len(shades) - 1)]

def get_pixels(img):
    if hasattr(img, "get_flattened_data"):
        return list(img.get_flattened_data())
    return list(img.getdata())

BITS = [(0,0,0x01),(0,1,0x02),(0,2,0x04),(1,0,0x08),
        (1,1,0x10),(1,2,0x20),(0,3,0x40),(1,3,0x80)]

def prepare(path, cols):
    img = Image.open(path).convert("L")
    img = img.point(lambda p: 255 if p > 185 else int(p * 255 / 185))
    box = img.point(lambda p: 255 if p < 120 else 0).getbbox()
    box = (max(box[0]-6, 0), max(box[1]-6, 0),
           min(box[2]+6, img.width), min(box[3]+6, img.height))
    img = img.crop(box)
    cw, ch = img.size
    W = cols * 2
    H = int(W * ch / cw); H += (-H) % 4
    img = img.resize((W, H), Image.LANCZOS)
    blur = img.filter(ImageFilter.GaussianBlur(6))
    a, b = get_pixels(img), get_pixels(blur)
    img.putdata([255 if x >= 250 else min(255, int(x / (y + 1) * 140))
                 for x, y in zip(a, b)])
    return img.convert("1"), box, cw, ch, H

def build_grid(path, cols):
    bw, box, cw, ch, H = prepare(path, cols)
    px = bw.load()
    rows = H // 4
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            m = 0
            for dx, dy, bit in BITS:
                if px[c*2+dx, r*4+dy] == 0:
                    m |= bit
            row.append((chr(0x2800 + m) if m else " ", grad(r / rows)))
        grid.append(row)
    eyes = [(int((ex-box[0])/cw*cols), int((ey-box[1])/ch*rows)) for ex, ey in EYES]
    return grid, eyes

# চোখের অবস্থা: 0 = খোলা, 1 = আধখোলা, 2 = বন্ধ
def draw_eye(grid, ex, ey, state):
    h, w = len(grid), len(grid[0])
    def put(x, y, g, col):
        if 0 <= y < h and 0 <= x < w:
            grid[y][x] = (g, col)
    for dx in range(-2, 3):
        for dy in (-1, 0, 1):
            x, y = ex + dx, ey + dy
            if 0 <= y < h and 0 <= x < w and state == 0 and dy != 0:
                grid[y][x] = (grid[y][x][0], C.AMBER)
    if state == 0:
        for dx in range(-2, 3):
            if grid[ey][ex+dx][0] == " ":
                put(ex+dx, ey, "⠶", C.GOLD)
            else:
                put(ex+dx, ey, grid[ey][ex+dx][0], C.GOLD)
        put(ex, ey, "◉", C.WHITE)
    elif state == 1:
        for dx in range(-2, 3):
            put(ex+dx, ey-1, "▁", C.AMBER)
            put(ex+dx, ey, "─", C.GOLD)
        put(ex, ey, "●", C.WHITE)
    else:
        for dx in range(-2, 3):
            put(ex+dx, ey-1, " ", C.RESET)
            put(ex+dx, ey, "━", C.AMBER)
            put(ex+dx, ey+1, " ", C.RESET)

def frame_lines(base, eyes, state, rows):
    g = [row[:] for row in base]
    for (ex, ey) in eyes:
        draw_eye(g, ex, ey, state)
    out = []
    for r in rows:
        out.append("".join(col + ch for ch, col in g[r]) + C.RESET)
    return out

EXTRA = 10   # হরিণের নিচে ব্যানার ইত্যাদির মোট লাইন

def show_static(base, eyes, pad):
    for ln in frame_lines(base, eyes, 0, range(len(base))):
        print(pad + ln)

def full_width_moving_line():
    base_line = "═" * term_width
    sys.stdout.write(C.GREEN + C.BOLD)
    for i in range(3):
        for shift in range(0, term_width, 2):
            sys.stdout.write("\r" + base_line[shift:] + base_line[:shift])
            sys.stdout.flush()
            time.sleep(0.01)
    sys.stdout.write("\r" + base_line + "\n")
    sys.stdout.write(C.RESET)

def main():
    cols = COLS
    # স্ক্রিনে না ধরলে ছবি নিজে থেকে ছোট করে নেবে
    while True:
        base, eyes = build_grid(IMG_PATH, cols)
        if len(base) + EXTRA + 2 <= term_height or cols <= 30:
            break
        cols -= 2
    total = len(base)
    pad = " " * max((term_width - cols) // 2, 0)
    ey = eyes[0][1]
    eye_rows = [ey - 1, ey, ey + 1]

    print()
    show_static(base, eyes, pad)
    print()
    banner_lines = [
        "#######################################################",
        "#                                                     #",
        "#             GQ ATIKUL - SECURE TERMINAL             #",
        "#                                                     #",
        "#######################################################"
    ]
    for line in banner_lines:
        print(C.RED + C.BOLD + line.center(term_width) + C.RESET)
    print()
    print()
    full_width_moving_line()
    print()

    up = total + EXTRA - (ey - 1)   # কার্সর থেকে চোখের প্রথম লাইন পর্যন্ত
    def redraw(state):
        lines = frame_lines(base, eyes, state, eye_rows)
        sys.stdout.write("\033[%dA" % up)
        for ln in lines:
            sys.stdout.write("\r" + pad + ln + "\n")
        sys.stdout.write("\033[%dB" % (up - 3))
        sys.stdout.flush()

    def blink():
        for st, d in ((1, 0.06), (2, 0.14), (1, 0.06), (0, 0)):
            redraw(st)
            time.sleep(d)

    sys.stdout.write("\033[?25l")   # কার্সর লুকানো
    try:
        for i in range(BLINKS):
            time.sleep(random.uniform(MIN_GAP, MAX_GAP))
            blink()
            if i == 1:               # মাঝে একবার জোড়া পলক
                time.sleep(0.2)
                blink()
    except KeyboardInterrupt:
        pass
    finally:
        redraw(0)
        sys.stdout.write("\033[?25h")

if sys.stdout.isatty():
    os.system("clear")
    term_height = shutil.get_terminal_size().lines
    main()