import re
from pathlib import Path


def output_template(
    output_dir: Path,
    media_format: str,
    allow_playlist: bool,
    output_title: str,
) -> str:
    custom_title = sanitize_filename(output_title)

    if allow_playlist:
        playlist_folder = custom_title or "%(playlist_title)s"
        return str(output_dir / playlist_folder / "%(playlist_index)03d - %(title)s.%(ext)s")

    target_ext = "mp3" if media_format == "mp3" else "mp4"
    base_name = custom_title or "%(title)s"

    if "%(" in base_name:
        return str(output_dir / f"{base_name}.%(ext)s")

    final_path = unique_path(output_dir / f"{base_name}.{target_ext}")
    return str(final_path.parent / f"{final_path.stem}.%(ext)s")


def sanitize_filename(value: str) -> str:
    value = value.strip()
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
