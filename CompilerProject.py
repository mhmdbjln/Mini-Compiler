import re

#قسمت اول: اسکنر

# اینا کلمات کلیدی هستن که تو زبان ما تعریف شدن
keywords = {'int', 'string'}

# عملگرهای مجاز
operators = {'+', '-', '*', '/', '='}

# علامتی که میگه ورودی تموم شده
end_marker = 'end'

# اینجا متغیرهای تعریف شده رو نگه میداریم
defined_vars = set()

# الگوهای مختلف برای تشخیص توکن‌ها
token_patterns = {
    'KEYWORD': r'\b(?:int|string)\b',
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    'NUMBER': r'\b\d+\b',
    'STRING': r'"[^"]*"',
    'OPERATOR': r'[+\-*/=]',
    'SEMICOLON': r';'
}

# این ترکیب کلیه الگوهاست که با هم چک میشن
combined_pattern = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns.items()))

# لیست نهایی توکن‌ها
all_tokens = []

# همه خطوطی که ورودی گرفته میشن اینجا ذخیره میشن
lines = []

# توکن‌های هر خط جدا ذخیره میشن
line_tokens = []

# لیست خطاهای اسکنر
scanner_errors = []

# لیست خطاهای استفاده از متغیر تعریف نشده
undefined_var_errors = []

print("Enter your code (type 'end' to finish input):")

# ورودی گرفتن خط به خط تا وقتی 'end' وارد شد
while True:
    line = input()
    if line.strip() == end_marker:
        break
    lines.append(line)

print()  # یه خط فاصله برای زیبا شدن خروجی

lexical_error_lines = set()  # شماره خطوطی که توشون خطای لغوی بوده

# حالا میریم خط به خط چک کنیم و توکن‌ها رو پیدا کنیم
for line_num, line in enumerate(lines):
    has_lexical_error = False
    current_line_tokens = []

    # اینجا چک می‌کنیم که نکنه نوع داده و اسم متغیر چسبیده باشن (مثل inta)
    if re.search(r'\b(?:int|string)(?=[a-zA-Z0-9_])', line):
        msg = f"[Error] Data type concatenated to variable name: {line}"
        scanner_errors.append(msg)
        lexical_error_lines.add(line_num)
        has_lexical_error = True

    # اینجا بررسی میکنیم که آیا تعریف متغیر داره (مثلاً int x)
    declaration_match = re.match(r'\s*(int|string)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
    if declaration_match:
        var_name = declaration_match.group(2)
        defined_vars.add(var_name)

    # میریم تو خط، هر جا تونستیم توکن بخونیم، به لیست اضافه می‌کنیم
    pos = 0
    while pos < len(line):
        match = combined_pattern.match(line, pos)
        if match:
            kind = match.lastgroup
            value = match.group()
            if kind == 'NUMBER':
                value = int(value)
            current_line_tokens.append((kind, value))
            pos = match.end()
        elif line[pos].isspace():
            pos += 1  # اگه اسپیس بود رد میشیم
        else:
            msg = f"[Error] Unknown character at position {pos}: '{line[pos]}'"
            scanner_errors.append(msg)
            lexical_error_lines.add(line_num)
            has_lexical_error = True
            break

    # اگه خطا داشتیم، این خط رو توکن‌هامون نادیده می‌گیریم
    if has_lexical_error:
        line_tokens.append(None)
        continue

    # حالا میخوایم چک کنیم که متغیری استفاده نشده نباشه
    all_ids = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line)
    ids_to_check = [v for v in all_ids if v not in keywords]
    if not line.strip().startswith(tuple(keywords)):
        for var in ids_to_check:
            # اگه این متغیر داخل رشته بود، مهم نیست
            if re.search(r'"[^"]*' + re.escape(var) + r'[^"]*"', line):
                continue
            if var not in defined_vars:
                msg = f"[Error] Use of undefined variable: {var}"
                scanner_errors.append(msg)
                undefined_var_errors.append((line_num, var))
                lexical_error_lines.add(line_num)
                has_lexical_error = True

    if has_lexical_error:
        line_tokens.append(None)
    else:
        line_tokens.append(current_line_tokens)

# قسمت دوم:پارسر

def parse_line(tokens):
    # اگه توکنی نداشت، یعنی خطا داشتیم قبلا
    if not tokens:
        return False, ["This line contains lexical errors."]

    reasons = []
    i = 0
    n = len(tokens)

    # تابعی که چک میکنه توکن بعدی همونیه که انتظار داریم یا نه
    def match(expected_type, expected_value=None):
        nonlocal i
        if i < n:
            t_type, t_value = tokens[i]
            if t_type == expected_type and (expected_value is None or t_value == expected_value):
                i += 1
                return True
        return False

    # این تابع میگه آیا عبارت سمت راست انتساب درست هست یا نه
    def parse_expression():
        nonlocal i
        if i >= n:
            return False
        if tokens[i][0] in {'IDENTIFIER', 'NUMBER', 'STRING'}:
            i += 1
        else:
            return False
        while i < n and tokens[i][0] == 'OPERATOR' and tokens[i][1] in {'+', '-', '*', '/'}:
            i += 1
            if i < n and tokens[i][0] in {'IDENTIFIER', 'NUMBER', 'STRING'}:
                i += 1
            else:
                return False
        return True

    # چک می‌کنیم ببینیم خط تعریف متغیره یا نه (مثل int x;)
    if match('KEYWORD'):
        if match('IDENTIFIER'):
            if match('SEMICOLON'):
                return True, []
            else:
                reasons.append("Missing semicolon in declaration.")
        else:
            reasons.append("Expected identifier after type keyword.")
        return False, reasons

    # اگه تعریف نبود، میریم دنبال انتساب (x = 3 + 2;)
    if match('IDENTIFIER'):
        if match('OPERATOR', '='):
            if not parse_expression():
                reasons.append("Invalid expression in assignment.")
            elif not match('SEMICOLON'):
                reasons.append("Missing semicolon at end of assignment.")
            else:
                return True, []
        else:
            reasons.append("Expected '=' after identifier in assignment.")
        return False, reasons

    # اگه هیچ کدوم از الگوها درست نبود یعنی خط کد ما نیست
    reasons.append("This does not match any valid statement pattern in our language.")
    return False, reasons


# اینجا بررسی می‌کنیم هر خط درست هست یا نه

syntax_errors_found = False
syntax_error_outputs = []

for idx, tokens_in_line in enumerate(line_tokens):
    if idx in lexical_error_lines:
        syntax_error_outputs.append(f"[Syntax Error] Line {idx + 1} is not accepted by the language. Reasons:\n  - Reason 1: This line contains lexical errors.")
        syntax_errors_found = True
        continue

    success, reasons = parse_line(tokens_in_line)
    if not success:
        syntax_errors_found = True
        msg = f"[Syntax Error] Line {idx + 1} is not accepted by the language. Reasons:\n"
        for i, r in enumerate(reasons, 1):
            msg += f"  - Reason {i}: {r}\n"
        syntax_error_outputs.append(msg.strip())
    else:
        all_tokens.extend(tokens_in_line)


# چاپ نهایی

if scanner_errors:
    print("Scanner errors detected:")
    for err in scanner_errors:
        print(err)

if syntax_error_outputs:
    print("\nParser errors detected:")
    for out in syntax_error_outputs:
        print(out)

if not scanner_errors and not syntax_errors_found:
    print("\nThe code is fully accepted by the language.\n")

print("\nExtracted tokens:")
for t in all_tokens:
    print(t)
