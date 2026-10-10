import os
import glob
import re
import configparser

CONFIG_FILE = "fnamer.ini"

def load_or_create_config():
    """Load settings from fnamer.ini or create default settings if missing."""
    config = configparser.ConfigParser()
    
    if not os.path.exists(CONFIG_FILE):
        config["SETTINGS"] = {
            "extension": ".mp4",
            "padding": "3",
            "sort_order": "asc",
            "dry_run": "False"
        }
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
        print(f"Created default configuration file: {CONFIG_FILE}\n")
    else:
        config.read(CONFIG_FILE)
        
    return config["SETTINGS"]

def get_file_creation_time(filepath):
    stat = os.stat(filepath)
    if hasattr(stat, 'st_birthtime'):
        return stat.st_birthtime
    return stat.st_ctime

def sort_key(filename, ext, padding):
    """
    Creates a sort key that orders base files and insertion files logically:
    Example sorting order:
      001.mp4   --> (1, 0, 0.0)
      002.mp4   --> (2, 0, 0.0)
      002-1.mp4 --> (2, 1, 0.0)
      002-2.mp4 --> (2, 2, 0.0)
      003.mp4   --> (3, 0, 0.0)
      xyz.mp4   --> (999999, 0, creation_time) [Unnumbered files drop to the end]
    """
    name_without_ext = os.path.splitext(filename)[0]
    
    # Match sequential base files (e.g., 001, 002)
    base_match = re.match(rf"^(\d{{{padding}}})$", name_without_ext)
    if base_match:
        return (int(base_match.group(1)), 0, 0.0)

    # Match insertion pattern (e.g., 002-1, 002-2, 002-10)
    insert_match = re.match(rf"^(\d{{{padding}}})-(\d+)$", name_without_ext)
    if insert_match:
        base_num = int(insert_match.group(1))
        sub_num = int(insert_match.group(2))
        return (base_num, sub_num, 0.0)

    # Unnumbered/raw files go to the end, ordered by creation time
    ctime = get_file_creation_time(filename)
    return (999999, 0, ctime)

def rename_files():
    settings = load_or_create_config()
    
    ext = settings.get("extension", ".mp4")
    if not ext.startswith("."):
        ext = "." + ext
        
    padding = settings.getint("padding", 3)
    dry_run = settings.getboolean("dry_run", False)

    # 1. Gather files
    all_files = [f for f in glob.glob(f"*{ext}") if os.path.isfile(f)]

    if not all_files:
        print(f"No {ext} files found in the current directory.")
        return

    # 2. Check if any insertion files (e.g., 002-1.mp4) are present
    insert_pattern = re.compile(rf"^\d{{{padding}}}-\d+{re.escape(ext)}$")
    has_insertions = any(insert_pattern.match(f) for f in all_files)

    # 3. Sort files based on pattern matching or creation date
    all_files.sort(key=lambda f: sort_key(f, ext, padding))

    # Determine starting offset
    first_file = all_files[0]
    first_name = os.path.splitext(first_file)[0]
    
    if first_name.isdigit():
        suggested_offset = int(first_name)
    else:
        suggested_offset = 1

    print(f"Found {len(all_files)} file(s) to process.")
    if has_insertions:
        print("Detected insertion pattern(s) (e.g., 002-1.mp4). Resequencing sequence...")

    # Prompt user for starting offset
    start_input = input(f"Enter starting number offset [Default = {suggested_offset}]: ").strip()
    offset = int(start_input) if start_input.isdigit() else suggested_offset

    if dry_run:
        print("\n*** DRY RUN MODE (No files will actually be renamed) ***\n")

    # 4. Generate planned renames
    renames = []
    current_num = offset
    
    for original_path in all_files:
        new_name = f"{current_num:0{padding}d}{ext}"
        if original_path != new_name:
            renames.append((original_path, new_name))
        current_num += 1

    if not renames:
        print("All files are already perfectly sequenced! No changes needed.")
        return

    print("\nPlanned Renames:")
    for src, dst in renames:
        print(f"  {src:<20} -->  {dst}")

    if dry_run:
        print("\nDry run completed.")
        return

    confirm = input("\nProceed with renaming? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return

    # 5. Two-step safety rename to prevent file overwrite collisions
    temp_mapping = []
    for idx, (src, dst) in enumerate(renames):
        temp_name = f"__temp_{idx}_{src}"
        os.rename(src, temp_name)
        temp_mapping.append((temp_name, dst))

    for temp_name, dst in temp_mapping:
        os.rename(temp_name, dst)

    print(f"\nSuccessfully re-sequenced and renamed {len(renames)} files!")

if __name__ == "__main__":
    rename_files()