# Python NLP Service — Data Collection

## 職責

從 Reddit API 收集癌症相關社群貼文，以及解析 MIMIC-III 臨床筆記，作為情緒分析的輸入資料。

## 資料來源一：Reddit

### 目標 Subreddit

| Subreddit | 說明 |
|---|---|
| r/cancer | 癌症病患主論壇 |
| r/breastcancer | 乳癌社群 |
| r/leukemia | 血癌社群 |
| r/lymphoma | 淋巴癌社群 |
| r/coloncancer | 大腸癌社群 |

### 使用套件

```python
# PRAW (Python Reddit API Wrapper)
pip install praw
```

### 收集邏輯

```python
import praw
from datetime import datetime, timezone

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

def collect_new_posts(subreddit_name: str, limit: int = 100) -> list[dict]:
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.new(limit=limit):
        posts.append({
            "post_id": post.id,
            "external_user_id": hash_user_id(post.author.name),
            "subreddit": subreddit_name,
            "title": post.title,
            "body": post.selftext,
            "posted_at": datetime.fromtimestamp(post.created_utc, tz=timezone.utc),
            "score": post.score,
            "num_comments": post.num_comments,
        })
    return posts
```

### 隱私處理

- `external_user_id` 必須 hash，不存明文 Reddit 用戶名
- 使用 SHA-256 + salt：`hash_user_id(username) = sha256(salt + username)`
- salt 存在環境變數 `REDDIT_HASH_SALT`，不進版本控制

### 頻率限制

- Reddit API 免費版：每分鐘 60 requests
- 排程設定：每小時執行一次，每次每個 subreddit 抓 100 則新貼文
- 總量估計：5 subreddits × 100 = 500 則/小時

## 資料來源二：MIMIC-III

### 說明

MIMIC-III 是 MIT 開放的去識別化臨床資料集，包含 ICU 病患的護理紀錄、醫師筆記等。需在 PhysioNet 申請（免費，約 1–2 週審核）。

申請地址：https://physionet.org/content/mimiciii/

### 相關資料表

| 資料表 | 說明 | 用途 |
|---|---|---|
| NOTEEVENTS | 醫師與護理師的文字筆記 | 情緒分析輸入 |
| DIAGNOSES_ICD | ICD 診斷碼 | 篩選癌症病患 |
| ADMISSIONS | 入院記錄 | 時間軸對齊 |

### 癌症病患篩選（ICD-9 碼）

```python
CANCER_ICD9_CODES = [
    "140", "141", "142",  # 唇、口腔、咽
    "150", "151", "152",  # 食道、胃、小腸
    "153", "154",          # 大腸、直腸
    "162",                 # 肺
    "174", "175",          # 乳房
    "185",                 # 前列腺
    "204", "205", "206",  # 白血病
]
```

### 解析邏輯

```python
import pandas as pd

def load_cancer_notes(mimic_path: str) -> pd.DataFrame:
    notes = pd.read_csv(f"{mimic_path}/NOTEEVENTS.csv")
    diagnoses = pd.read_csv(f"{mimic_path}/DIAGNOSES_ICD.csv")

    cancer_subjects = diagnoses[
        diagnoses["ICD9_CODE"].str.startswith(tuple(CANCER_ICD9_CODES))
    ]["SUBJECT_ID"].unique()

    cancer_notes = notes[
        (notes["SUBJECT_ID"].isin(cancer_subjects)) &
        (notes["CATEGORY"].isin(["Nursing", "Physician", "Discharge summary"]))
    ]
    return cancer_notes[["SUBJECT_ID", "HADM_ID", "CHARTDATE", "TEXT"]]
```

## 輸出格式

兩個資料來源最終統一為相同格式再進入情緒分類：

```python
@dataclass
class RawTextRecord:
    external_user_id: str   # hash 後的用戶識別
    source: str              # "reddit" | "mimic"
    record_id: str           # post_id 或 note row_id
    text: str                # 待分析文字
    recorded_at: datetime    # 發文或記錄時間
```

## 錯誤處理

| 情境 | 處理方式 |
|---|---|
| Reddit API rate limit | 自動 sleep 60 秒後重試，最多 3 次 |
| Reddit API 憑證失效 | 記錄 ERROR log，跳過本次排程 |
| MIMIC 檔案不存在 | 啟動時檢查，缺失則禁用 MIMIC 來源 |
| 貼文內容為空 | 過濾掉，不進入後續分析 |

## 相關 Spec

- [Service Overview](2026-05-19-service-overview.md)
- [Emotion Classification](2026-05-19-emotion-classification.md)
