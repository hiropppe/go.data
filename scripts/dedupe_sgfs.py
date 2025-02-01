import os
import sys
import sgf
import shutil
import traceback
import unicodedata
import pandas as pd

from tqdm import tqdm


def get_result(props):
    if "RE" in props:
        re = props.get("RE")[0].strip()
        return unicodedata.normalize("NFKC", re)


def get_move(props):
    for c in ("W", "B"):
        if c in props:
            node_value = props[c][0]
            if node_value == '' or node_value == 'tt':
                return # ignore PASS
            else:
                x = node_value[0].upper()
                y = node_value[1].upper()
                return f"{c}[{x}{y}]"


def main(input_paths, output_dir):
    shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    input_paths = list(input_paths)
    dedupe_moves, dedupe_paths = [], []

    n_empties = 0
    n_parse_errors = 0
    n_unknown_results = 0
    n_other_errors = 0
    for input_path in tqdm(input_paths):
        input_path = input_path.strip()
        moves = []
        try:
            with open(input_path) as f:
                sgf_string = f.read().strip()
                if not sgf_string:
                    #tqdm.write("sgf_string is empty.", file=sys.stderr)
                    n_empties += 1
                    continue
                collection = sgf.parse(sgf_string)

            sgf_game = collection[0]

            winner = None
            for node in sgf_game.nodes:
                re = get_result(node.properties)
                if re:
                    winner = re.upper()

            if not (winner and any(c in winner for c in ("B", "W", "黒", "白", "黑"))):
                #tqdm.write(f"unknown [RE]sult. '{winner}'")
                n_unknown_results += 1

            if sgf_game.rest is None:
                continue

            for i, node in enumerate(sgf_game.rest):
                props = node.properties
                move = get_move(props)
                if move:
                    moves.append(move)

            dedupe_moves.append("".join(moves))
            dedupe_paths.append(input_path)
        except sgf.ParseException as exc:
            n_parse_errors += 1
            continue
        except Exception as exc:
            err, msg = type(exc).__name__, str(exc)
            #tqdm.write(f"{err} {msg}\n{sgf_string}", file=sys.stderr)
            tqdm.write(f"{err} {msg}", file=sys.stderr)
            #traceback.print_exc()
            n_other_errors += 1
            continue

    print(f"n_valids: {len(dedupe_paths)} n_empties: {n_empties} n_unknown_results: {n_unknown_results} n_parse_errors: {n_parse_errors} n_other_errors: {n_other_errors}")

    df = pd.DataFrame(dedupe_moves)
    dedupe_index = df[df.duplicated( ) == False].index
    for i in dedupe_index:
        accept_path = dedupe_paths[i]
        shutil.copy2(accept_path, output_dir)

    print(f"Deduped. {100*(1-len(dedupe_index)/len(df)):.3f}% ({len(dedupe_index)}/{len(df)})")


if __name__ == "__main__":
    input_paths = sys.stdin
    output_dir = sys.argv[1]
    main(input_paths, output_dir)
