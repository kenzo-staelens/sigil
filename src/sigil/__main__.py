import sys

from sigil.cli_tools.init import create_project


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--help":
        print("Usage: sigil init <project_name>")
        sys.exit(0)

    if args[0] == "init" and len(args) >= 2:
        create_project(args[1])
    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: sigil init <project_name>")
        sys.exit(1)

if __name__ == "__main__":
    main()
