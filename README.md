# Mini Programming Language Lexer and Parser

A small command-line language-processing project written in Python. It demonstrates lexical analysis and basic syntax validation for a simple custom language.

## Supported language elements

- Data-type keywords: `int` and `string`.
- Identifiers, integer literals, quoted string literals, arithmetic operators (`+`, `-`, `*`, `/`), assignment (`=`), and semicolons.
- Variable declarations such as:

```text
int total;
string title;
```

- Assignment statements such as:

```text
total = 7 + 5;
title = "example";
```

## Components

- **Lexical analysis:** Uses Python regular expressions to recognize tokens and report unknown characters or malformed type/name combinations.
- **Basic symbol tracking:** Tracks declared variable names and reports selected uses of undefined variables.
- **Syntax analysis:** Checks supported declaration and assignment statement patterns and reports syntax errors.
- **Token output:** Prints tokens extracted from accepted lines.

## Run

```bash
python CompilerProject.py
```

Enter source statements line by line. Type `end` on a separate line to finish input and display the analysis results.

## Scope and limitations

This is an educational Lexer/Parser prototype, not a complete compiler. It does not generate machine code or an executable, and its expression parser does not implement full operator precedence, parentheses, or a complete semantic-analysis phase.

## Requirements

Python 3 only. The project uses the standard library and has no third-party package requirements.

## License

No license has been specified.
