"""Converts ST generated .icf linker files into basic .ld linker files"""

import pathlib
import re


def _strip_comments(text: str) -> str:
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'//[^\n]*', '', text)
    return text


def parse_icf(icf_file: str) -> tuple[dict, dict]:
    text = _strip_comments(icf_file)

    symbols: dict[str, str] = {}
    regions: dict[str, tuple[str, str]] = {}
    blocks:  dict[str, dict[str, str]] = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith('define'):
            continue

        # define symbol NAME = VALUE;
        m = re.match(r'define\s+symbol\s+(\w+)\s*=\s*(.+?)\s*;?\s*$', line)
        if m:
            symbols[m.group(1)] = m.group(2).strip()
            continue

        # define region NAME = mem:[from START to END];
        m = re.match(
            r'define\s+region\s+(\w+)\s*=\s*'
            r'mem\s*:\s*\[\s*from\s+(\w+)\s+to\s+(\w+)\s*\]\s*;?\s*$',
            line, re.IGNORECASE)
        if m:
            name = m.group(1)
            rname = re.sub(r'_region$', '', name, flags=re.IGNORECASE).upper()
            regions[rname] = (m.group(2), m.group(3))
            continue

        # define block NAME with prop = val, prop = val { };
        m = re.match(
            r'define\s+block\s+(\w+)\s+with\s+(.+?)\s*\{\s*\}\s*;?\s*$',
            line, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            props = {
                k.lower(): v
                for k, v in re.findall(r'(\w+)\s*=\s*(\w+)', m.group(2))
            }
            blocks[name] = props
            continue

    def resolve(v: str) -> str:
        return symbols.get(v, v)

    return (
        {name: (resolve(s), resolve(e)) for name, (s, e) in regions.items()},
        {name: {k: resolve(v) for k, v in props.items()}
         for name, props in blocks.items()},
    )


def icf_regions_to_ld_regions(icf_regions: dict) -> dict:
    out = {}
    for region, (start, end) in icf_regions.items():
        try:
            start_dec = int(start, 0)
            end_dec   = int(end,   0)
        except ValueError as e:
            raise ValueError(
                f"Region {region!r}: non-numeric bound {start!r}..{end!r}") from e

        length = end_dec - start_dec + 1
        if length % 1024 == 0:
            length_str = f'{length // 1024}K'
        elif (length - 1) % 1024 == 0:
            length_str = f'{(length - 1) // 1024}K'
        else:
            length_str = str(length)

        ld_name = 'FLASH' if region == 'ROM' else region
        out[ld_name] = (start, length_str)
    return out


def _memory_block(ld_regions: dict) -> str:
    lines = []
    if 'FLASH' in ld_regions:
        s, l = ld_regions['FLASH'];  lines.append(f'  FLASH  (rx)  : ORIGIN = {s}, LENGTH = {l}')
    if 'RAM' in ld_regions:
        s, l = ld_regions['RAM'];    lines.append(f'  RAM    (xrw) : ORIGIN = {s}, LENGTH = {l}')
    if 'CCMRAM' in ld_regions:
        s, l = ld_regions['CCMRAM']; lines.append(f'  CCMRAM (rwx) : ORIGIN = {s}, LENGTH = {l}')
    return '\n'.join(lines)


def create_ld(ld_regions: dict, blocks: dict) -> str:
    heap  = blocks.get('HEAP',   {}).get('size', '0x200')
    stack = blocks.get('CSTACK', {}).get('size', '0x400')
    mem   = _memory_block(ld_regions)

    return f"""\
MEMORY
{{
{mem}
}}

ENTRY(Reset_Handler)
_estack = ORIGIN(RAM) + LENGTH(RAM);

_Min_Heap_Size  = {heap};
_Min_Stack_Size = {stack};

SECTIONS
{{
  .isr_vector :
  {{
    . = ALIGN(512);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  }} >FLASH

  .text :
  {{
    . = ALIGN(4);
    *(.text) *(.text*)
    *(.glue_7) *(.glue_7t)
    *(.eh_frame)
    KEEP(*(.init))
    KEEP(*(.fini))
    . = ALIGN(4);
    _etext = .;
  }} >FLASH

  .rodata :
  {{
    . = ALIGN(4);
    *(.rodata) *(.rodata*)
    . = ALIGN(4);
  }} >FLASH

  .ARM.extab :
  {{
    . = ALIGN(4);
    *(.ARM.extab* .gnu.linkonce.armextab.*)
    . = ALIGN(4);
  }} >FLASH

  .ARM :
  {{
    . = ALIGN(4);
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
    . = ALIGN(4);
  }} >FLASH

  .preinit_array :
  {{
    . = ALIGN(4);
    PROVIDE_HIDDEN(__preinit_array_start = .);
    KEEP(*(.preinit_array*))
    PROVIDE_HIDDEN(__preinit_array_end = .);
    . = ALIGN(4);
  }} >FLASH

  .init_array :
  {{
    . = ALIGN(4);
    PROVIDE_HIDDEN(__init_array_start = .);
    KEEP(*(SORT(.init_array.*)))
    KEEP(*(.init_array*))
    PROVIDE_HIDDEN(__init_array_end = .);
    . = ALIGN(4);
  }} >FLASH

  .fini_array :
  {{
    . = ALIGN(4);
    PROVIDE_HIDDEN(__fini_array_start = .);
    KEEP(*(SORT(.fini_array.*)))
    KEEP(*(.fini_array*))
    PROVIDE_HIDDEN(__fini_array_end = .);
    . = ALIGN(4);
  }} >FLASH

  _sidata = LOADADDR(.data);
  .data :
  {{
    . = ALIGN(4);
    _sdata = .;
    *(.data) *(.data*)
    . = ALIGN(4);
    _edata = .;
  }} >RAM AT> FLASH

  . = ALIGN(4);
  .bss :
  {{
    _sbss = .;
    __bss_start__ = _sbss;
    *(.bss) *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;
    __bss_end__ = _ebss;
  }} >RAM

  ._user_heap_stack (NOLOAD) :
  {{
    . = ALIGN(8);
    PROVIDE(end  = .);
    PROVIDE(_end = .);
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  }} >RAM

  /DISCARD/ :
  {{
    *(.comment)
    *(.note*)
  }}

  .ARM.attributes 0 : {{ *(.ARM.attributes) }}
}}
"""


def icf_to_ld(icf_path: pathlib.Path, ld_path: pathlib.Path | None) -> None:
    with open(icf_path, 'rb') as f:
        icf_str = f.read().decode('utf-8', errors='ignore')

    icf_regions, blocks = parse_icf(icf_str)
    ld_regions = icf_regions_to_ld_regions(icf_regions)
    ld_str = create_ld(ld_regions, blocks)

    if ld_path:
        ld_path.write_text(ld_str)
    else:
        print(ld_str)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: icf_to_ld.py <input.icf> [output.ld]", file=sys.stderr)
        sys.exit(1)
    icf_to_ld(pathlib.Path(sys.argv[1]),
              pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None)