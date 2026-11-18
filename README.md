# The World in One Day — Tuesday 17 November 2026

An entry for the make.fun bounty **news-image-20261117**: sum up the
world's news of Tuesday 17 November 2026 in one image.

`main.py` (Python 3, standard library only) draws a 1024x1024 PNG
poster of the day's top stories and writes it to `/output/entry.png`
(or to `$MAKEFUN_OUTPUT_DIR/entry.png` when that variable is set).
The drawing is fully deterministic — no network, no inputs — so every
run produces exactly the same bytes.

The poster leads with the date and four stories, each with a simple
icon, a headline and one line of detail:

- **War in Europe** — Ukraine's 1,300-drone barrage hits the Crimea
  Bridge; Russia hits two Kyiv bridges in reply.
- **Middle East** — US jets strike Iran's Qeshm Island in the Strait
  of Hormuz; a tanker ablaze off Oman, 24 crew rescued.
- **Health** — the United States loses its measles-free status;
  5,412 cases after a year of nonstop spread.
- **Climate** — the COP31 draft deal in Antalya calls for a faster
  exit from fossil fuels.

A bottom strip adds the rest of the day: Trump in Manila for the
ASEAN summit, Robert Pattinson named the new James Bond, five EU
states planning a Rwanda migrant hub, Wall Street sliding on AI
stocks, Amazon losing 40 satellites in a failed launch, and the
GTA VI launch countdown.

Sources checked on 18 November 2026: Reuters, AP, AFP, PAHO, Dawn,
RNZ, Business Recorder and UN News reporting of 17 November 2026.

## Run it

```sh
python3 main.py                        # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py # writes out/entry.png
```

Licensed under the MIT License (see `LICENSE`).
