#!/usr/bin/env bash
# Finish a generated wallpaper for Dreamcoder: centre-crop to 16:9, upscale to
# 3840x2160 in linear light, add native-resolution paper grain (additive,
# ~1.4 code values RMS; SoftLight is broken in ImageMagick 7.1.2), then quantise
# to 8 bits with an ordered dither so smooth paper gradients never band.
# Deterministic: the same input always yields the same bytes.
set -euo pipefail

readonly WIDTH=3840
readonly HEIGHT=2160
readonly GRAIN_SEED=1729

usage() {
  echo "usage: finish-wallpaper.sh INPUT OUTPUT" >&2
  echo "Crop to 16:9, upscale to ${WIDTH}x${HEIGHT}, add paper grain, dither to 8-bit PNG." >&2
}

main() {
  if [[ $# -ne 2 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    [[ $# -eq 1 && ("${1}" == "-h" || "${1}" == "--help") ]] && exit 0
    exit 2
  fi
  local input="$1" output="$2"
  if ! command -v magick >/dev/null 2>&1; then
    echo "finish-wallpaper: ImageMagick (magick) is required" >&2
    exit 2
  fi
  if [[ ! -f "${input}" ]]; then
    echo "finish-wallpaper: input not found: ${input}" >&2
    exit 1
  fi

  local w h crop_w crop_h
  read -r w h < <(magick identify -format "%w %h\n" "${input}[0]")
  if (( w * 9 > h * 16 )); then
    crop_h="${h}"
    crop_w=$(( h * 16 / 9 ))
  else
    crop_w="${w}"
    crop_h=$(( w * 9 / 16 ))
  fi

  local tmp
  tmp="$(mktemp "${TMPDIR:-/tmp}/finish-wallpaper.XXXXXX.png")"
  trap 'rm -f "${tmp}"' EXIT

  magick "${input}[0]" -auto-orient -depth 16 -colorspace sRGB \
    -gravity center -crop "${crop_w}x${crop_h}+0+0" +repage \
    -colorspace RGB -filter Lanczos -resize "${WIDTH}x${HEIGHT}!" -colorspace sRGB \
    \( -size "${WIDTH}x${HEIGHT}" xc:"#808080" -seed "${GRAIN_SEED}" -attenuate 0.25 \
       +noise Gaussian -blur 0x0.7 -colorspace gray \) \
    -compose Mathematics -define compose:args=0,1,1,-0.501961 -composite \
    -ordered-dither o8x8,256 -depth 8 -strip \
    -define png:exclude-chunks=date,time \
    "PNG24:${tmp}"
  mv -f "${tmp}" "${output}"
  trap - EXIT
  echo "finished ${output}"
}

main "$@"
