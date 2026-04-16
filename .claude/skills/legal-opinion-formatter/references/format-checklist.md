# PIPA Legal Opinion Format Checklist

DOCX 생성 전 반드시 아래 항목을 확인한다.

## Document Architecture

- [ ] 비밀유지 마킹 포함 (사용자가 제외 요청하지 않은 경우)
- [ ] 날짜 및 수신인 블록 완성
- [ ] 건명(Re:) 라인에 쟁점 명확히 기재
- [ ] 수신인 인사 포함

## Content Sections (순서 준수)

- [ ] I. 서론 — 의견서 요청 배경, 검토 범위, 적용 법령
- [ ] II. 핵심 요약 — 결론 선행 제시, 리스크 수준
- [ ] III. 검토 사실관계 — 사실관계 + 정확성 전제 면책
- [ ] IV. 검토 쟁점 — 번호 매긴 법률 쟁점 목록
- [ ] V. 분석 — 쟁점별 분석, 조문 인용, Verification Status
- [ ] VI. 결론 — 쟁점별 결론 대응
- [ ] 리스크 매트릭스 (해당 시)
- [ ] 실무 권고사항 — 구체적, 시한 포함
- [ ] 한계 및 전제조건
- [ ] VII. 출처 목록 — Grade별 정리

## Citation Quality

- [ ] 모든 조문 인용에 `[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` 표시
- [ ] 모든 인용에 Grade 표시 (`[Grade A]`, `[Grade B]`)
- [ ] 조문 원문은 blockquote로 분리
- [ ] 웹서치 결과에 `[WEB]` 태그
- [ ] 출처 목록의 모든 항목이 본문에서 실제 인용됨
- [ ] 본문의 모든 인용이 출처 목록에 존재

## PIPA-Specific Rules

- [ ] KB에 없는 조문을 추측 인용하지 않음
- [ ] 조문 번호가 불확실하면 `[INSUFFICIENT]` 표시
- [ ] 해석이 분분한 경우 양쪽 모두 제시 (`[CONTRADICTED]`)
- [ ] Grade D 소스 (뉴스, AI 요약) 단독 사용하지 않음
- [ ] KB 미수집 법령은 `[미수집]` 표시 + 웹서치 시도 여부 기재

## Adversarial Cross-Verification

- [ ] 해석 질문인 경우 Dual-Pass 수행 여부 확인
- [ ] Pass B (반례) 결과가 분석에 반영됨
- [ ] 반례 존재 시 "단, ~의 경우 예외" 명시

## Typography & Layout

- [ ] 용지 A4 (210mm x 297mm)
- [ ] 여백: 상하 25mm, 좌 30mm, 우 25mm
- [ ] 본문 폰트: 바탕체/Times New Roman 11pt
- [ ] 제목 폰트: 맑은 고딕/Arial
- [ ] 행간 1.15배, 단락 후 6pt
- [ ] Heading 색상: Navy (#1B2A4A)
- [ ] 페이지 번호 "- X -" 형식

## Tone & Language

- [ ] 격식체 일관 (`~합니다`, `~입니다`, `~드립니다`)
- [ ] 법률 용어 정확 사용
- [ ] 필요 시 영문 병기 (예: 정보주체(data subject))
- [ ] 추측/일반론 배제

## Final Checks

- [ ] 면책 조항 포함 (법률 자문 면책 + AI 생성 고지)
- [ ] 서명 블록 완성
- [ ] 파일명 규칙 준수: `{YYYYMMDD}_pipa_opinion_{subject}_v{N}.docx`
- [ ] Markdown 사본 함께 저장
- [ ] `${PIPA_OUTPUT_DIR:-output/opinions/}` 디렉토리에 저장

## Red Flags to Avoid

- 정책 제안과 법률 결론을 구분 없이 혼합
- "~일 수 있습니다" 등 모호한 표현 (불확실성 태그 없이)
- 쟁점 제목 없는 긴 비구조화 단락
- 출처 목록에 없는 인용 코드 사용
- Grade C 소스를 `[EDITORIAL]` 표시 없이 인용
