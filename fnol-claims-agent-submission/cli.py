import sys
import json
import argparse
from pathlib import Path
from fnol_agent.agent import ClaimsProcessingAgent

def main():
    parser = argparse.ArgumentParser(description="Autonomous FNOL Insurance Claims Processing Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Process single file command
    proc_parser = subparsers.add_parser("process", help="Process a single FNOL document (.pdf or .txt)")
    proc_parser.add_argument("file_path", help="Path to FNOL document")
    proc_parser.add_argument("--pretty", action="store_true", default=True, help="Format JSON output with indentation")

    # Process batch directory command
    batch_parser = subparsers.add_parser("batch", help="Batch process a directory of FNOL documents")
    batch_parser.add_argument("dir_path", help="Path to folder containing .pdf or .txt FNOL files")

    args = parser.parse_args()
    agent = ClaimsProcessingAgent()

    if args.command == "process":
        file_path = Path(args.file_path)
        if not file_path.exists():
            print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
            sys.exit(1)
        
        result = agent.process_file(str(file_path))
        print(json.dumps(result.to_dict(), indent=2 if args.pretty else None))

    elif args.command == "batch":
        dir_path = Path(args.dir_path)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"Error: Directory '{dir_path}' does not exist or is not a directory.", file=sys.stderr)
            sys.exit(1)

        files = list(dir_path.glob("*.pdf")) + list(dir_path.glob("*.txt"))
        if not files:
            print(f"No .pdf or .txt files found in '{dir_path}'.")
            return

        print(f"Processing {len(files)} FNOL documents in '{dir_path}'...\n" + "="*70)
        for f in sorted(files):
            result = agent.process_file(str(f))
            print(f"\n[FILE]: {f.name}")
            print(f"  Route:     {result.recommendedRoute}")
            print(f"  Missing:   {result.missingFields if result.missingFields else 'None'}")
            print(f"  Reasoning: {result.reasoning}")
            print("-" * 70)

if __name__ == "__main__":
    main()
