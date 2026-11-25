# Codex brief: improve four Careers page photos

## Goal

Four photos on `careers.html` are LinkedIn copies, 800px wide, shown at up to 550px. On high-density screens they look soft. Make each one twice the size, cleaner and better lit, **without changing who or what is in it**.

These are real, identifiable people who agreed to these photos. A slightly soft photo that looks like them is a success. A sharp photo that doesn't is a failure.

## Files

`Photos/` is gitignored. Read from `Photos/careers/source/`. Write to `Photos/careers/improved/`.

| Source | Size | Output | Output size |
|---|---|---|---|
| `mun-debate.jpg` | 800×449 | `mun-debate.png` | 1600×898 |
| `mun-room.jpg` | 800×450 | `mun-room.png` | 1600×900 |
| `wellness.jpg` | 800×600 | `wellness.png` | 1600×1200 |
| `money-session.jpg` | 800×600 | `money-session.png` | 1600×1200 |

Ignore the other files in `source/`. They are already large enough for where they appear.

If `Photos/careers/originals/` has a photo with the same name, use that instead: only resize it to 1600px wide and apply the light correction in step 4. Don't enlarge or sharpen it.

## Rules

1. **No generative image models.** Nothing that takes a prompt, redraws, inpaints or outpaints.
2. **No face restoration.** No GFPGAN, CodeFormer, or `face_enhance` option. They invent features.
3. **No retouching.** No skin smoothing, teeth or eye work, slimming, or blemish removal. Skin tones must stay true: never lighten anyone's skin.
4. **Nothing added, removed, moved or cropped.** Same framing, same people, same objects. Keep the aspect ratio.
5. **Text stays as it is.** "THANK YOU" (cut off in the original) and "Financial Literacy for women" on the screens must read exactly as before. If small text is unreadable in the source, leave it unreadable.
6. No added grain, blur, vignette, filters or colour grading beyond step 4.

## Method

Write one Python script, `Photos/careers/improve.py`. Use Pillow, numpy and OpenCV. If you want Real-ESRGAN, ask before downloading the package or its weights, and name the source and size.

1. **Clean.** Remove JPEG blocking and colour noise gently, mostly in the chroma channels (for example `cv2.fastNlMeansDenoisingColored` with a luminance strength of 3 or less).
2. **Enlarge 2×.**
   - Default: Lanczos.
   - If Real-ESRGAN is approved: run `realesr-general-x4v3` with face enhancement off, resize to 2×, then blend 50% with the Lanczos version for the background.
   - **Inside every face and hand, use 100% Lanczos**, with a feathered mask (about 12px) so no edge shows. Detect faces, then check the boxes by eye and add any that were missed: profiles, people seen from behind, and people in the distance.
3. **Sharpen lightly.** Luminance only, unsharp mask with a radius of about 1.2px and an amount of 40% or less, and half that inside faces. No halos.
4. **Correct the light.** Global adjustments only:
   - `mun-debate`, `mun-room`: reduce the orange cast a little and lift the shadows. Keep the room warm. Don't clip the projector screen.
   - `wellness`: neutralise the grey-green cast, and raise exposure slightly.
   - `money-session`: lift the mid-tones and reduce the grey haze. Keep the screen readable.
   - The four should look like one set, next to the art workshop photos on the same page.

## Checks

Run these in the script and print the results. Fix anything that fails.

1. **Same content.** Before step 4, shrink each result to its source size and compare luminance with the source: SSIM of at least 0.95 overall, and at least 0.97 inside each face box.
2. **Same people.** Count people by eye in the source and in the result. The numbers must match (`wellness` has seven).
3. **No clipping.** After step 4, the share of pixels that are pure white or pure black must not rise by more than 0.5 points.
4. **Size and mode.** Exact output sizes from the table, 8-bit RGB, sRGB, with EXIF and GPS data removed.

## Comparison sheets

For each photo, save `Photos/careers/improved/_compare-<name>.jpg`: source (enlarged with plain bicubic) on the left, result on the right, at the same scale. Below them, put a side-by-side crop of **every** face at 200%.

Look at every face crop before finishing. If anyone looks like a different person, or their eyes, mouth, glasses, teeth or expression have changed, use plain Lanczos for that face and run it again.

## Don't

- Don't edit, build or commit anything in the website. Only write inside `Photos/careers/`. Claude will convert the files to WebP and put them on the page after a person approves the sheets.
- Don't upload the photos to any outside service.

## Report back

1. What you did to each photo, and which enlarging method you used.
2. The check results.
3. Any photo where the improvement isn't worth using. It is fine to say the source is better.
