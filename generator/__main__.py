# SPDX-License-Identifier: AGPL-3.0-only AND MIT

def main() -> None:
    """Main function"""
    from main import main as _main
    _main()


if __name__ == "__main__":
    # if python version is lower than 3.10, raise error
    import sys
    if sys.version_info < (3, 10):
        raise RuntimeError("Python version >= 3.10 is required.")
    main()
