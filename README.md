# SmartStitch

SmartStitch combines webtoon, manhwa and manhua images and splits them into pages for editing. This fork of [MechTechnology/SmartStitch](https://github.com/MechTechnology/SmartStitch) adds a refreshed interface and a conservative detector that looks for full-width white or black bands before cutting.

## Features

- Interface in English, Portuguese and Spanish, with system, light and dark themes.
- Safe-band detection to reduce cuts through lettering, balloons and artwork.
- WebP pages are kept below 16,000 pixels high. If no safe band exists within that limit, SmartStitch makes a cut and warns you to review it.
- PNG, WebP, JPEG, PSD and other output formats; batch processing and profiles.

A uniform band cannot guarantee that every balloon or drawing remains intact. Review the generated pages, especially when a forced-cut warning appears. WebP also has a maximum **width** of 16,383 pixels; choose a smaller width or a different format if needed.

## Download for Windows

When a Windows build has been published, find it under this repository's **Releases**. For the portable ZIP, extract the entire folder and run `SmartStitch.exe`; the files beside the executable are required.

## Build from source on Windows

Install Python 3.10 with the Python launcher, then run `compilar-windows.bat`. The application is created in `dist/SmartStitch/`. Optionally open `INNO-SETUP.iss` in Inno Setup 6 to create an installer after the application has been built. The GitHub Actions workflow also builds a portable Windows ZIP as a workflow artifact.

## Credits and license

Based on [SmartStitch](https://github.com/MechTechnology/SmartStitch), created by MechTechnology. Distributed under the original [MIT license](LICENSE).
