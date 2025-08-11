import os
import re
import pandas as pd

ks_folder = 'ks'
csv_folder = 'csv_outputs'
output_folder = 'ks_translated'
os.makedirs(output_folder, exist_ok=True)

block_pattern = re.compile(r'\[tb_start_text.*?\](.*?)\[_tb_end_text\]', re.DOTALL)
tag_pattern = re.compile(r'\[.*?\]')
jp_keep_pattern = re.compile(r'[ぁ-んァ-ン一-龯ー―〜～、「」。『』！？…・]+')

for filename in os.listdir(ks_folder):
    if not filename.endswith('.ks'):
        continue

    base = os.path.splitext(filename)[0]
    ks_path = os.path.join(ks_folder, filename)
    csv_path = os.path.join(csv_folder, f'{base}.csv')
    speaker_csv_path = os.path.join(csv_folder, f'{base}_speakers.csv')
    output_path = os.path.join(output_folder, filename)

    if not os.path.exists(csv_path) or not os.path.exists(speaker_csv_path):
        print(f"{filename}에 해당하는 csv 없음. 스킵.")
        continue

    df_dialogue = pd.read_csv(csv_path, encoding='utf-8-sig').fillna('')
    df_speaker = pd.read_csv(speaker_csv_path, encoding='utf-8-sig').fillna('')

    old_to_new = {
        str(old).strip(): str(new).strip()
        for old, new in zip(df_dialogue['old'], df_dialogue['new'])
    }
    speaker_to_new = {
        str(old).strip(): str(new).strip()
        for old, new in zip(df_speaker['old'], df_speaker['new'])
    }

    with open(ks_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_block(match):
        block = match.group(1)
        lines = block.strip().splitlines()
        new_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue

            if stripped.startswith('#'):
                key = stripped.strip()
                new_line = speaker_to_new.get(key, key)
                new_lines.append(new_line)
            else:
                tags = ''.join(tag_pattern.findall(stripped))
                no_tag = tag_pattern.sub('', stripped)
                jp_only = ''.join(jp_keep_pattern.findall(no_tag)).strip()

                replacement_text = old_to_new.get(jp_only, jp_only)
                full_line = replacement_text + tags if replacement_text else stripped
                new_lines.append(full_line)

        return match.group(0).replace(block, '\n'.join(new_lines))

    translated = re.sub(block_pattern, replace_block, content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated)

    print(f"{filename} → 번역 적용 완료")

input("\n완료.")
