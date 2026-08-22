# -*- coding: utf-8 -*-
"""The part of the standard library's `audioop` that `speech_recognition` uses.

`audioop` was one of the modules PEP 594 removed, and it went in Python 3.13 --
which is the Python NVDA 2026.1 runs.  Nothing replaced it in the standard
library, so a module that imports it stops working on that Python and takes
whatever it was doing with it.

`aifc` and `chunk` went the same way and are already vendored beside this file,
so this is the third of the three, done the same way and for the same reason.

Only the seven names `speech_recognition` actually calls are here:

    error  bias  byteswap  lin2lin  rms  ratecv  tomono

Adding the rest would be adding code nothing exercises.  These seven follow
CPython's own `Modules/audioop.c` -- the same 32-bit internal scale in
`lin2lin` and `ratecv`, the same truncation towards zero, the same wraparound
in `bias`, the same clipping in `tomono` -- and were checked sample for sample
against the real module over randomised input.

Sample widths 1, 2, 3 and 4 are supported, signed, little endian, which is
what the original supports and how WAV stores its frames.
"""

import array
import math
import sys

__all__ = ["error", "bias", "byteswap", "lin2lin", "ratecv", "rms", "tomono"]


class error(Exception):
    """What the original raises, and what callers catch by name."""


# 'i' is four bytes everywhere CPython builds, but the module is wrong rather
# than slow if that ever stops being true, so it is checked once here.
_TYPECODE = {1: "b", 2: "h", 4: "i"}
for _w, _c in list(_TYPECODE.items()):
    if array.array(_c).itemsize != _w:
        del _TYPECODE[_w]
del _w, _c

_MASK = {1: 0xFF, 2: 0xFFFF, 3: 0xFFFFFF, 4: 0xFFFFFFFF}
_MIN = {1: -0x80, 2: -0x8000, 3: -0x800000, 4: -0x80000000}
_MAX = {1: 0x7F, 2: 0x7FFF, 3: 0x7FFFFF, 4: 0x7FFFFFFF}


def _check(fragment, width):
    if width not in (1, 2, 3, 4):
        raise error("Size should be 1, 2, 3 or 4")
    if len(fragment) % width != 0:
        raise error("not a whole number of frames")


def _unpack(fragment, width):
    """-> the signed samples of `fragment`, in the file's own width."""
    if width in _TYPECODE:
        out = array.array(_TYPECODE[width])
        out.frombytes(bytes(fragment))
        if sys.byteorder != "little":
            out.byteswap()
        return out
    return [int.from_bytes(fragment[i:i + width], "little", signed=True)
            for i in range(0, len(fragment), width)]


def _pack(samples, width):
    """-> `samples` as bytes.  Values are truncated to `width`, as a C cast
    truncates, rather than clipped: everywhere this is used the caller has
    already brought the value into range."""
    if width in _TYPECODE:
        out = array.array(_TYPECODE[width],
                          [(s & _MASK[width]) - (_MASK[width] + 1)
                           if (s & _MASK[width]) > _MAX[width]
                           else (s & _MASK[width]) for s in samples])
        if sys.byteorder != "little":
            out.byteswap()
        return out.tobytes()
    out = bytearray()
    for s in samples:
        out += (s & _MASK[width]).to_bytes(width, "little")
    return bytes(out)


def _to32(sample, width):
    """-> the sample on the 32-bit scale audioop works in internally."""
    return sample << (32 - 8 * width)


def _from32(sample, width):
    return sample >> (32 - 8 * width)


def _bound(value, width):
    """Clip, then round towards minus infinity -- CPython's `fbound`.

    Flooring rather than truncating is not an accident there and the
    difference is audible at the sample level, so it is not one here either.
    """
    if value > _MAX[width]:
        return _MAX[width]
    if value < _MIN[width] + 1.0:
        return _MIN[width]
    return math.floor(value)


def rms(fragment, width):
    """-> the root mean square of the fragment: how loud it is."""
    _check(fragment, width)
    if not fragment:
        return 0
    total = 0
    for sample in _unpack(fragment, width):
        total += sample * sample
    return int(math.sqrt(total / (len(fragment) // width)))


def bias(fragment, width, bias):
    """-> the fragment with `bias` added to every sample, wrapping around."""
    _check(fragment, width)
    mask = _MASK[width]
    return _pack([(sample + bias) & mask
                  for sample in _unpack(fragment, width)], width)


def byteswap(fragment, width):
    """-> the fragment with the byte order of every sample reversed."""
    _check(fragment, width)
    out = bytearray(len(fragment))
    for i in range(0, len(fragment), width):
        out[i:i + width] = fragment[i:i + width][::-1]
    return bytes(out)


def lin2lin(fragment, width, newwidth):
    """-> the fragment converted to a different sample width."""
    _check(fragment, width)
    if newwidth not in (1, 2, 3, 4):
        raise error("Size should be 1, 2, 3 or 4")
    if width == newwidth:
        return bytes(fragment)
    shift = 8 * (newwidth - width)
    if shift > 0:
        return _pack([sample << shift
                      for sample in _unpack(fragment, width)], newwidth)
    return _pack([sample >> -shift
                  for sample in _unpack(fragment, width)], newwidth)


def tomono(fragment, width, lfactor, rfactor):
    """-> a mono fragment, each frame the two channels weighted and summed."""
    _check(fragment, width)
    if len(fragment) % (width * 2) != 0:
        raise error("not a whole number of frames")
    samples = _unpack(fragment, width)
    return _pack([_bound(samples[i] * lfactor + samples[i + 1] * rfactor, width)
                  for i in range(0, len(samples), 2)], width)


def ratecv(fragment, width, nchannels, inrate, outrate, state,
           weightA=1, weightB=0):
    """-> (converted fragment, state), resampling from `inrate` to `outrate`.

    The state is what makes this usable on a stream: hand back what the last
    call returned and the join between the two buffers is not audible.
    """
    _check(fragment, width)
    if nchannels < 1:
        raise error("# of channels should be >= 1")
    bytes_per_frame = width * nchannels
    if weightA < 1 or weightB < 0:
        raise error("weightA should be >= 1, weightB should be >= 0")
    if len(fragment) % bytes_per_frame != 0:
        raise error("not a whole number of frames")
    if inrate <= 0 or outrate <= 0:
        raise error("sampling rate not > 0")

    d = math.gcd(inrate, outrate)
    inrate //= d
    outrate //= d
    d = math.gcd(weightA, weightB)
    weightA //= d
    weightB //= d

    if state is None:
        d = -outrate
        prev_i = [0] * nchannels
        cur_i = [0] * nchannels
    else:
        d, samps = state
        if len(samps) != nchannels:
            raise error("illegal state argument")
        prev_i = [int(p) for p, _ in samps]
        cur_i = [int(c) for _, c in samps]

    samples = _unpack(fragment, width)
    out = []
    pos = 0                                   # next input sample to consume
    total = len(samples)
    while True:
        while d < 0:
            if pos >= total:
                return (_pack(out, width),
                        (d, tuple(zip(prev_i, cur_i))))
            for chan in range(nchannels):
                prev_i[chan] = cur_i[chan]
                cur_i[chan] = _to32(samples[pos], width)
                pos += 1
                # A one-pole filter, off by default: weightB is 0 unless the
                # caller asks for smoothing.
                cur_i[chan] = int(
                    (float(weightA) * float(cur_i[chan]) +
                     float(weightB) * float(prev_i[chan])) /
                    (float(weightA) + float(weightB)))
            d += outrate
        while d >= 0:
            for chan in range(nchannels):
                out.append(_from32(int(
                    (float(prev_i[chan]) * float(d) +
                     float(cur_i[chan]) * float(outrate - d)) /
                    float(outrate)), width))
            d -= inrate
