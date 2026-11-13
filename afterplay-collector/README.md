# 애프터플레이 일일 수집기

매일 한국 시간 오전 7시에 문화·예술·음악 뉴스 제목과 링크를 모아 `docs/index.html` 페이지를 갱신합니다.

## 설정 순서
1. github.com 에서 가입하고 새 저장소(Repository)를 만듭니다. 이름은 자유, 공개(Public)로 만듭니다.
2. 저장소에서 Add file > Upload files 로 `collect.py`, `README.md`, `docs` 폴더를 올립니다.
3. Add file > Create new file 을 눌러 파일 이름에 `.github/workflows/daily.yml` 을 입력하고, 이 폴더의 `daily.yml` 내용을 붙여 넣어 저장합니다.
4. Settings > Pages 에서 Branch 를 `main`, 폴더를 `/docs` 로 지정합니다.
5. Actions 탭에서 `daily-culture-collect` 를 열고 Run workflow 로 처음 한 번 실행합니다.
6. 1~2분 뒤 Settings > Pages 에 나온 주소가 오늘의 이슈 페이지입니다.

## AI가 카드뉴스·후킹 제목·캡션까지 쓰게 하려면 (선택)
Anthropic API 키를 발급해 Settings > Secrets and variables > Actions 에 `ANTHROPIC_API_KEY` 로 등록하세요. 키가 없으면 제목과 링크만 모읍니다. API는 사용량만큼 별도 요금이 듭니다.
