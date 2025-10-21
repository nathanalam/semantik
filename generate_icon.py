#!/usr/bin/env python3
"""
JPEG to ICNS Converter Script

This script converts JPEG images to ICNS format for macOS applications.
It creates multiple icon sizes required by the ICNS format and packages them
into a single ICNS file.

Usage:
    python generate_icon.py input.jpg output.icns
    python generate_icon.py input.jpg  # Uses same name with .icns extension

Requirements:
    - Pillow (PIL) for image processing
"""

import sys
import os
from PIL import Image
import argparse


def create_icns_from_jpeg(jpeg_path, icns_path=None):
    """
    Convert a JPEG image to ICNS format.

    Args:
        jpeg_path (str): Path to the input JPEG file
        icns_path (str): Path for the output ICNS file (optional)

    Returns:
        str: Path to the generated ICNS file
    """
    # Validate input file
    if not os.path.exists(jpeg_path):
        raise FileNotFoundError(f"Input file not found: {jpeg_path}")

    if not jpeg_path.lower().endswith((".jpg", ".jpeg")):
        raise ValueError("Input file must be a JPEG image")

    # Generate output path if not provided
    if icns_path is None:
        base_name = os.path.splitext(jpeg_path)[0]
        icns_path = f"{base_name}.icns"

    # ICNS requires multiple icon sizes
    icon_sizes = [16, 32, 64, 128, 256, 512, 1024]

    try:
        # Open the source image
        with Image.open(jpeg_path) as img:
            # Convert to RGBA if necessary (for transparency support)
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Create a temporary directory to store individual icon sizes
            temp_dir = os.path.join(os.path.dirname(icns_path), "temp_icons")
            os.makedirs(temp_dir, exist_ok=True)

            # Generate icons for each required size
            icon_files = []
            for size in icon_sizes:
                # Resize image maintaining aspect ratio
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)

                # Save as PNG (ICNS uses PNG internally)
                icon_file = os.path.join(temp_dir, f"icon_{size}x{size}.png")
                resized_img.save(icon_file, "PNG")
                icon_files.append(icon_file)

            # Create ICNS file using iconutil (macOS) or alternative method
            if sys.platform == "darwin":  # macOS
                # Use iconutil command line tool
                iconset_path = os.path.join(
                    os.path.dirname(icns_path),
                    f"{os.path.splitext(os.path.basename(icns_path))[0]}.iconset",
                )

                # Remove existing iconset if it exists
                if os.path.exists(iconset_path):
                    import shutil

                    shutil.rmtree(iconset_path)

                os.makedirs(iconset_path)

                # Copy icons to iconset with proper naming
                icon_mappings = {
                    16: ["icon_16x16.png"],
                    32: ["icon_16x16@2x.png", "icon_32x32.png"],
                    64: ["icon_32x32@2x.png"],
                    128: ["icon_128x128.png"],
                    256: ["icon_128x128@2x.png", "icon_256x256.png"],
                    512: ["icon_256x256@2x.png", "icon_512x512.png"],
                    1024: ["icon_512x512@2x.png"],
                }

                for size, filenames in icon_mappings.items:
                    source_file = os.path.join(temp_dir, f"icon_{size}x{size}.png")
                    for filename in filenames:
                        dest_file = os.path.join(iconset_path, filename)
                        if os.path.exists(source_file):
                            import shutil

                            shutil.copy2(source_file, dest_file)

                # Use iconutil to create ICNS
                import subprocess

                result = subprocess.run(
                    ["iconutil", "-c", "icns", iconset_path],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    raise RuntimeError(f"iconutil failed: {result.stderr}")

                # Move the generated ICNS to the desired location
                generated_icns = iconset_path.replace(".iconset", ".icns")
                if generated_icns != icns_path:
                    import shutil

                    shutil.move(generated_icns, icns_path)

            else:
                # For non-macOS systems, use Pillow to create a basic ICNS
                # Note: This creates a simplified ICNS that may not be fully compatible
                print("Warning: Running on non-macOS system. Creating simplified ICNS.")

                # Use the largest size for the ICNS
                largest_icon = max(
                    icon_files,
                    key=lambda f: int(os.path.basename(f).split("_")[1].split("x")[0]),
                )

                with Image.open(largest_icon) as final_img:
                    final_img.save(icns_path, "ICNS")

            # Clean up temporary files
            import shutil

            shutil.rmtree(temp_dir)

            print(f"✅ Successfully created ICNS file: {icns_path}")
            return icns_path

    except Exception as e:
        # Clean up on error
        if "temp_dir" in locals() and os.path.exists(temp_dir):
            import shutil

            shutil.rmtree(temp_dir)
        raise RuntimeError(f"Failed to create ICNS file: {str(e)}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert JPEG image to ICNS format for macOS applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_icon.py logo.jpg
    python generate_icon.py logo.jpg custom_icon.icns
    python generate_icon.py /path/to/image.jpg /path/to/output.icns
        """,
    )

    parser.add_argument("input", help="Input JPEG file path")
    parser.add_argument("output", nargs="?", help="Output ICNS file path (optional)")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        if args.verbose:
            print(f"Converting: {args.input}")
            if args.output:
                print(f"Output: {args.output}")

        result_path = create_icns_from_jpeg(args.input, args.output)

        if args.verbose:
            print(f"✅ Conversion completed successfully!")
            print(f"📁 Output file: {result_path}")
            print(f"📏 File size: {os.path.getsize(result_path)} bytes")

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
