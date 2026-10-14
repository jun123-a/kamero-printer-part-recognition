# Kamero — 프린터 부품 인식 웹앱

**한국어** | [English](README.en.md)

사진을 업로드하면 기존 YOLO 모델이 프린터 부품을 탐지하고, SQLite에서 부품 번호와 설명을 찾아 화면에 표시하는 캡스톤 프로젝트입니다.

[PV-ML-HPPK](https://github.com/snj0x03/PV-ML-HPPK)를 기반으로 제공받은 Kamero 프런트엔드를 연결했습니다. 현재는 **로컬 실행용 프로토타입**입니다.

## 주요 기능

- JPG/PNG 업로드 및 실제 YOLO 추론
- 탐지 박스와 부품 목록의 선택 연동, 확대·축소
- 신뢰도 60% 미만 결과에 경고 표시
- 서버 DB에서 40개 부품 카탈로그 조회 및 검색
- 결과 이미지, JSON, CSV를 ZIP으로 다운로드
- SQLite에 인식 결과와 결과 이미지 경로 저장
- 브라우저에 최근 인식 기록 최대 20개 저장
- 잘못된 인식에 대한 수정 의견을 다운로드 JSON에 포함

## 동작 구조

```text
브라우저: HTML / CSS / JavaScript
    │ POST /detect (원본 사진)
    ▼
FastAPI → YOLO 탐지 모델 → 클래스 ID
    │                         │
    │                  SQLite 부품 정보 조회
    ▼
부품 번호 + 설명 + 신뢰도 + 박스 좌표 + 기록 ID
    │
    ▼
화면에서 박스·목록 표시 및 결과 다운로드
```

미리보기는 긴 변 최대 1,280픽셀로 줄이지만 서버에는 원본 파일을 전송합니다. 서버는 EXIF 회전을 적용하고 JPG/PNG, 최대 10 MB, 최대 4천만 픽셀을 검사합니다.

## 빠른 시작 — Windows

이 프로젝트에서 검증한 환경은 **Python 3.13 / Windows**입니다. GPU 없이 CPU로도 실행할 수 있으며 처리 시간은 장비에 따라 다릅니다.

저장소를 다운로드하거나 복제한 뒤 프로젝트 폴더에서 실행합니다.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start-kamero.cmd
```

브라우저에서 **http://127.0.0.1:8000** 을 엽니다. HTML 파일을 직접 더블클릭하지 않습니다.

실행 파일은 현재 폴더의 가상환경을 사용합니다. 서버 창에서 Ctrl+C를 누르면 종료됩니다. 최초 시작 시 DB와 부품 정보가 자동 생성됩니다.

직접 실행하려면:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir app --host 127.0.0.1 --port 8000
```

서버 시작 시 다음 두 모델 파일이 필요합니다. 기존 저장소에 포함된 파일을 유지했습니다.

- `models/best_v26_det.pt`: 현재 화면에서 사용하는 탐지 모델
- `models/best_v26_cls.pt`: 기존 `/classify` API에서 사용하는 분류 모델

## 프로젝트 구조

```text
app/
  main.py                 # FastAPI, 모델 실행, DB 조회, 결과 저장
  database.py             # SQLite / SQLAlchemy 테이블
  seed_db.py              # 기존 40개 부품 등록
  test_integration.py     # API 통합 테스트
  static/
    index.html            # 화면 구조
    kamero.css            # 화면 디자인
    kamero.js             # 업로드, API 호출, 박스 선택, 내보내기
    hp_logo.png
    woosong_logo.png
  data/                   # 자동 생성되는 DB·이미지·설정 (Git 제외)
models/                   # 기존 학습 모델
notebooks/                # 기존 학습 노트북
scripts/                  # 기존 데이터 처리 스크립트
requirements.txt          # 실행 패키지
requirements-dev.txt      # 테스트 추가 패키지
start-kamero.cmd           # Windows 실행 파일
연결설명.md                # 연결 구현 상세 설명
```

## API

| 경로 | 역할 |
|---|---|
| `GET /` | 프런트엔드 제공 |
| `GET /api/health` | 서버 상태와 탐지 모델 파일명 |
| `GET /api/models` | 현재 지원하는 인식 범위 |
| `GET /api/parts` | DB 부품 카탈로그 |
| `POST /detect` | 사진 탐지 및 기록 저장 |
| `POST /classify` | 기존 전체 이미지 분류 API; 현재 화면에서는 미사용 |
| `DELETE /admin/clear-db` | 기존 인식·분류 기록과 결과 이미지 삭제; 부품 정보는 유지 |

`/detect`는 multipart 형식의 `file`과 선택적 `printer_model`을 받습니다. 현재 인식 범위는 `All parts (printer compatibility unverified)` 하나이며, 프린터별 필터는 없습니다.

주요 응답 예시 (실제 측정값이 아닌 설명용):

```json
{
  "record_id": 1,
  "model_version": "best_v26_det.pt",
  "bbox_format": "cxcywh_normalized",
  "parts": [{
    "class_id": 0,
    "class_name": "0",
    "part_number": "5PN77-67001",
    "description": "SVC_HP LaserJet Fuser 220V Kit",
    "confidence": 0.92,
    "bbox_norm": [0.5, 0.5, 0.4, 0.2],
    "compatibility": []
  }]
}
```

서버 좌표는 0~1 범위의 `[중심 x, 중심 y, 너비, 높이]`입니다. 화면은 왼쪽 위 기준으로 변환해 박스를 그립니다. 내보내기 JSON의 `bbox_norm_xywh`는 **왼쪽 위 기준**입니다.

기존 API 호환을 위해 `image`, `conf`, `cls`, `desc`, `bboxes`도 반환합니다.

## 검증

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s app -p test_integration.py
```

확인한 항목:

- API 통합 테스트 4개 통과: 화면·카탈로그·인식 범위, 응답과 DB 저장, 잘못된 입력, 실제 모델 호출
- JavaScript 문법과 응답 좌표 변환 검사 통과
- 브라우저에서 카탈로그 40개 표시 확인
- 브라우저에서 로고 이미지를 실제 모델에 전송하고 탐지 없음 안내 확인

양성 탐지의 좌표와 DB 대응은 고정된 테스트 출력으로 검사했습니다. 실제 부품 사진에 대한 정확도와 박스 위치의 육안 검증은 아직 남아 있습니다. 이 결과는 모델 정확도 평가가 아닙니다.

## 현재 제한과 다음 작업

- 프린터 모델별 호환 DB와 필터링은 미구현입니다.
- Swin 분류 및 YOLO 영역 자르기 → Swin 연결은 미구현입니다.
- History 화면은 브라우저 기록이며 서버 기록 조회 기능은 없습니다.
- 수정 의견은 다운로드 JSON에만 저장되며 서버 저장·재학습은 미구현입니다.
- 클래스 ID와 부품 번호의 대응은 원본 seed 데이터를 따릅니다. 정답 사진으로 확인해야 합니다.
- 탐지 임계값은 0.05로 낮게 설정되어 있습니다. 낮은 신뢰도의 결과는 직접 검토해야 합니다.
- 기존 관리 API에는 인증이 없습니다. 기본 실행 주소는 `127.0.0.1`이며 외부 서비스 공개 전 인증·접근 제어가 필요합니다.
- 기존 Docker 구성과 학습 노트북은 보존했지만 이번 연결 작업에서 실행 검증하지 않았습니다.

## 출처 및 라이선스

- 기반 코드와 학습 모델: [snj0x03/PV-ML-HPPK](https://github.com/snj0x03/PV-ML-HPPK)
- 프런트엔드: 프로젝트에서 제공받은 Kamero HTML을 기반으로 분리·연결
- 이번 변경: API 응답 확장, DB 카탈로그 연결, 원본 이미지 전송, 입력 검증, UI 상태 처리, 실행 파일과 통합 테스트 추가
- 원본의 MIT 라이선스 및 저작권 표기는 [LICENSE](LICENSE)에 유지했습니다.
- 원본 README는 [docs/upstream-readme.md](docs/upstream-readme.md)에 보존했습니다. 현재 연결 버전의 사용법은 이 문서를 기준으로 합니다.
- Ultralytics 등 외부 의존성과 로고·모델 등 자산의 이용 조건은 각 원출처를 따릅니다.

자세한 구현 설명은 [연결설명.md](연결설명.md)를 참고하세요.
