import os
import re
import pandas as pd

ks_folder = 'ks'
output_folder = 'csv_outputs'
os.makedirs(output_folder, exist_ok=True)

# 대사 블록 추출 정규식
block_pattern = re.compile(r'\[tb_start_text.*?\](.*?)\[_tb_end_text\]', re.DOTALL)

# 정제용 정규식
tag_pattern = re.compile(r'\[.*?\]')  # 대괄호 안 제거
jp_keep_pattern = re.compile(r'[ぁ-んァ-ン一-龯ー―〜～、「」。『』！？…・]+')

total_lines = 0

for filename in os.listdir(ks_folder):
    if filename.endswith('.ks'):
        filepath = os.path.join(ks_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = block_pattern.findall(content)

        dialogue_rows = []
        speaker_rows = []
        seen_speakers = set()

        for block in blocks:
            lines = block.strip().splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    if line not in seen_speakers:
                        seen_speakers.add(line)
                        speaker_rows.append({'old': line, 'new': ''})
                else:
                    # 정제 작업 시작
                    line_no_tags = tag_pattern.sub('', line)
                    jp_only = ''.join(jp_keep_pattern.findall(line_no_tags))
                    if jp_only:
                        dialogue_rows.append({'old': jp_only, 'new': ''})
                        total_lines += 1

        base = os.path.splitext(filename)[0]

        if dialogue_rows:
            df = pd.DataFrame(dialogue_rows)
            df.to_csv(os.path.join(output_folder, f'{base}.csv'), index=False, encoding='utf-8-sig')
            print(f"✅ {filename} → 대사 {len(dialogue_rows)}줄 저장 (정제 완료)")

        if speaker_rows:
            df_s = pd.DataFrame(speaker_rows)
            df_s.to_csv(os.path.join(output_folder, f'{base}_speakers.csv'), index=False, encoding='utf-8-sig')
            print(f"🗣 {filename} → 캐릭터명 {len(speaker_rows)}개 저장")

print(f"\n📊 전체 정제된 대사 줄 수: {total_lines}줄")
input("\n작업 완료. 엔터를 누르면 종료합니다.")
